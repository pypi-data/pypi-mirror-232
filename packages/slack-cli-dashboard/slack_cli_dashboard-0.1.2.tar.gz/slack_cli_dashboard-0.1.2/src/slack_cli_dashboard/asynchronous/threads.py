import threading

"""
When running pytest, errors in threads were not propagating back.
This was causing silent failures, a solution is using this Threading subclass found here:
https://gist.github.com/sbrugman/59b3535ebcd5aa0e2598293cfa58b6ab
"""


class TestableThread(threading.Thread):
    """Wrapper around `threading.Thread` that propagates exceptions."""

    def __init__(self, name, target, *args, **kwargs):
        threading.Thread.__init__(self, name=name, target=target, *args, **kwargs)
        self.exc = None

    def run(self):
        """Method representing the thread's activity.
        You may override this method in a subclass. The standard run() method
        invokes the callable object passed to the object's constructor as the
        target argument, if any, with sequential and keyword arguments taken
        from the args and kwargs arguments, respectively.
        """
        try:
            threading.Thread.run(self)
        except BaseException as e:
            self.exc = e
            raise e
        finally:
            pass

    def join(self, timeout=None):
        """Wait until the thread terminates.
        This blocks the calling thread until the thread whose join() method is
        called terminates -- either normally or through an unhandled exception
        or until the optional timeout occurs.
        When the timeout argument is present and not None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof). As join() always returns None, you must call
        is_alive() after join() to decide whether a timeout happened -- if the
        thread is still alive, the join() call timed out.
        When the timeout argument is not present or None, the operation will
        block until the thread terminates.
        A thread can be join()ed many times.
        join() raises a RuntimeError if an attempt is made to join the current
        thread as that would cause a deadlock. It is also an error to join() a
        thread before it has been started and attempts to do so raises the same
        exception.
        """
        super(TestableThread, self).join(timeout)
        if self.exc:
            raise self.exc
