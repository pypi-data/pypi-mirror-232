#!/usr/bin/env python
# pylint: disable=invalid-name,missing-docstring,unused-import,unused-variable,unused-argument,line-too-long
# pylint: disable=too-many-locals,unnecessary-pass,pointless-string-statement,using-constant-test
# pylint: disable=multiple-statements,logging-fstring-interpolation,multiple-imports,wrong-import-position
# pylint: disable=import-outside-toplevel

import sys
from random import randint, random
from typing import Any, Callable, Dict, Generic, List, TypeVar

import eventlet as hub

from eventlet_promise.thenable import Thenable, raise_


class PromiseJS(Thenable):
    """
    A PromiseJS represents the eventual result of an asynchronous operation.
    The primary way of interacting with a promise is through its then method,
    which registers callbacks to receive either a promise's eventual value or
    the reason why the promise cannot be fulfilled.

    A promise has an state, which can be either 'pending', 'fulfilled', or 'rejected'.

    A promise has three internal properties:
    - _state is either 'pending', 'fulfilled', or 'rejected'.
    - _fate is either 'resolved' or 'unresolved'.
    - _value is the result of the operation. Initially undefined.
    - _callbacks is a list of functions to call when the promise is resolved or rejected.

    A promise is in one of three different states:
    - pending: initial state, neither fulfilled nor rejected.
    - fulfillled: meaning that the operation completed successfully.
    - rejected: meaning that the operation failed.

    A pending promise can either be fulfilled with a value, or rejected with a
    reason (error). When either of these options happens, the associated
    handlers queued up by a promise's then method are called.

    The promise is said to be settled if it is either fulfilled or rejected,
    but not pending. Once settled, a promise can not be resettled.
    
    Arguments:
    - executor is a function with the signature executor(resolve, reject).
        - resolve is a function with the signature resolve(result).
        - reject is a function with the signature reject(reason).
        An `executor` call is expected to do one of the following:
        - Call resolveFunc(result) side-effect if it successfully completes.
        - Call rejectFunc(reason) side-effect if it fails to complete.
        - Register callbacks to be called when the promise is resolved or rejected.

    Note: This class implements promises which are fulfilled or rejected like in JS.
          `hub.sleep(0)` needs to be called to switch settling threads of the promise.
    """
    def __init__(self, executor : Callable[[Callable[[Any], None], Callable[[Any], None]], None]):
        super().__init__()
        executor = executor or (lambda _, __: None)
        self.execute(executor)

    @staticmethod
    def resolve(value : Any) -> 'PromiseJS':
        if isinstance(value, PromiseJS):
            return value
        return PromiseJS(lambda resolveFunc, _: resolveFunc(value))

    @staticmethod
    def reject(reason : Any):
        return PromiseJS(lambda _, rejectFunc: rejectFunc(reason))

    @staticmethod
    def all(promises : List['PromiseJS']):
        def executor(resolveFunc, rejectFunc):
            def chainExecute(promises : List['PromiseJS'], results, resolveFunc, rejectFunc):
                assert promises, 'No promises to chain'
                promises = list(promises)
                promise_ : PromiseJS = promises.pop(0)
                nextPromise : PromiseJS = promises[0] if promises else None
                promise_.then(lambda x, nextPromise=nextPromise:
                    nextPromise.waitExecute(chainExecute,
                            promises, results + [x],
                            resolveFunc, rejectFunc
                    ) if nextPromise
                    else resolveFunc(results + [x])
                , rejectFunc)
            return hub.spawn(chainExecute, promises, [], resolveFunc, rejectFunc)
        return PromiseJS(executor)

    @staticmethod
    def allSettled(promises : List['PromiseJS']) -> 'PromiseJS':
        if not promises:
            return PromiseJS.resolve([])
        def executor(resolveFunc, rejectFunc):
            def chainExecute(promises : List['PromiseJS'], results, resolveFunc, rejectFunc):
                assert promises, 'No promises to chain'
                promises = list(promises)
                promise_ : PromiseJS = promises.pop(0)
                nextPromise : PromiseJS = promises[0] if promises else None
                promise_.finally_(lambda x, nextPromise=nextPromise:
                    nextPromise.waitExecute(chainExecute,
                        promises, results + [{
                            'status': promise_.getState(),
                            'value' if promise_.isFulfilled() else 'reason': x
                        }],
                        resolveFunc, rejectFunc
                    ) if nextPromise
                    else resolveFunc(results + [{
                        'status': promise_.getState(),
                        'value' if promise_.isFulfilled() else 'reason': x
                    }])
                )
            return hub.spawn(chainExecute, promises, [], resolveFunc, resolveFunc)
        return PromiseJS(executor)

    @staticmethod
    def any(promises : List['PromiseJS']):
        promises = list(promises)
        def executor(resolveFunc, rejectFunc):
            for promise_ in promises:
                promise_ : PromiseJS
                promise_.waitExecute(promise_.then, lambda x: resolveFunc(x, True))
            def anyFulfilled(settledValues):
                for settledValue in settledValues:
                    if settledValue['status'] == 'fulfilled':
                        resolveFunc(settledValue['value'], True)
                return rejectFunc(Exception(f'{PromiseJS.any}: No promises resolved'))
            PromiseJS.allSettled(promises).then(anyFulfilled)     # safe
        return PromiseJS(executor)

    @staticmethod
    def race(promises : List):
        promises = list(promises)
        def executor(resolveFunc, rejectFunc):
            for promise_ in promises:
                promise_ : PromiseJS
                promise_.waitExecute(promise_.finally_, lambda x: resolveFunc(x, True))
        return PromiseJS(executor)

    def then(self, onFulfilled : Callable[[Any], Any] = None, onRejected : Callable[[Any], Any] = None):
        """
        Before accessing result, at least once, `eventlet.sleep` must be called.
        """
        onFulfilled = onFulfilled if callable(onFulfilled) else (lambda value: value)
        onRejected = onRejected if callable(onRejected) else raise_
        try:
            if self.isFulfilled():
                value = onFulfilled(self._value)
                promise_ = PromiseJS(lambda resolveFunc, _: self.waitExecute(resolveFunc, value))
                # hub.sleep(0)
                return promise_
            if self.isRejected():
                value = onRejected(self._value)     # pylint: disable=assignment-from-no-return
                promise_ = PromiseJS(lambda _, rejectFunc: self.waitExecute(rejectFunc, value))
                # hub.sleep(0)
                return promise_
            promise_ = PromiseJS(None)        # either way, the promise is attached
            promise_.referenceTo(self, onFulfilled, onRejected)
            return promise_
        except Exception as error:          # pylint: disable=broad-except
            return PromiseJS.reject(error)

    def catch(self, onRejected : Callable[[Any], Any] = None):
        return self.then(None, onRejected)

    def finally_(self, onFinally : Callable[[Any], Any] = None):
        return self.then(onFinally, onFinally)


def async_(func : Callable[..., Any]):
    """
    Note: This decorator is not needed if the function returns a PromiseJS.
    Not yet tested.
    """
    def wrapper(*args, **kwargs):
        return PromiseJS.resolve(func(*args, **kwargs))
    return wrapper


def await_(promise_ : PromiseJS):
    """
    Note: Use only inside a separate coroutine.
    """
    while promise_.isPending():
        hub.sleep(0)
    return promise_.getValue()


if __name__ == '__main__':
    def executor_(resolveFunc : Callable[[Any], None], rejectFunc : Callable[[Any], None]):      # match, timeout
        t1, t2 = 5, 6
        # print(t := 1.5 * random())
        hub.spawn_after(t1, lambda: print('\tResolving') or resolveFunc(t1))
        hub.spawn_after(t2, lambda: print('\tRejecting') or rejectFunc(TimeoutError("Timed out")))

    # promise = PromiseJS(None)
    promise = PromiseJS(executor_)
    new_promise = promise.then()
    attached = PromiseJS.resolve(new_promise).then(lambda x: x + 1).then(lambda x: x + 1)
    p1 = PromiseJS.resolve(1).then(2).then()
    p2 = PromiseJS.reject(1).then(2, 2).then().then()
    p3 = p1.then()

    print(promise)
    print(new_promise)
    print(attached)
    print(p1)
    print(p2)
    print(p3)

    p_all = PromiseJS.all([p1, p3, new_promise, promise])
    print('all', p_all)
    p_settled = PromiseJS.allSettled([p1, p2, p3, new_promise, promise])
    print('allSettled', p_settled)
    p_any = PromiseJS.any([p2, promise.then(), new_promise, promise, p3.then()])
    print('any', p_any)
    p_race = PromiseJS.race([new_promise.then(), new_promise.then(), p3.then()])
    print('race', p_race)

    print('\nFinished\n')
    hub.sleep(1)

    c = 0
    while True:
        hub.sleep(0)
        try:
            print()
            print(promise)
            print(new_promise)
            print(attached)
            print(p1)
            print(p2)
            print(p3)
            print('all', p_all)
            print('allSettled', p_settled)
            print('any', p_any)
            print('race', p_race)
            hub.sleep(3)
        except KeyboardInterrupt:
            sys.exit(0)
        if (c := c + 1) == 10:
            break
