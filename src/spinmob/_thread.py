import pyqtgraph as _pg
import traceback as _traceback
import sys       as _sys

# Thread pool
pool = _pg.QtCore.QThreadPool()

class locker():
    """
    Simplified recursive QMutex. Use self.lock() to lock and self.unlock() to unlock a
    resource. Use self.try_lock() to try locking (returns True if successful, False if not).
    """
    def __init__(self):
        self._QMutex = _pg.QtCore.QMutex(_pg.QtCore.QMutex.Recursive)
        self.lock           = self._QMutex.lock
        self.try_lock       = self._QMutex.tryLock
        self.unlock         = self._QMutex.unlock


class signal(_pg.QtCore.QObject):
    """
    Simplified pyqtSignal with self.connect() and self.emit().
    This is a thread-safe way to pass data. I hear.

    Parameters
    ----------
    You can optionally provide functions as arguments. These will be automatically
    connected after initialization.


    Example Usage
    -------------

    s = signal()

    s.connect(my_function)

    # Elsewhere in the code:

    s.emit(my_data)

    # my_function will receive my_data as the argument.

    # You can also take the daisy-chain shortcut:

    s = signal().connect(my_function)

    # Though this is the same as

    s = signal(my_function)

    """
    _pyqtSignal = _pg.QtCore.pyqtSignal(object)

    def __init__(self, *functions):
        _pg.QtCore.QObject.__init__(self)
        for f in functions: self.connect(f)

    def connect(self, function):
        """
        Connect the signal to the supplied function. Returns self.
        """
        self._pyqtSignal.connect(function)
        return self

    def emit(self, data):
        """
        Emits the supplied data to the connected functions. Returns self.
        """
        self._pyqtSignal.emit(data)
        return self

class worker(_pg.QtCore.QRunnable):
    '''
    Single thread for doing work, based on QRunnable. After creating an instance:

        my_thread = spinmob.thread.worker(my_function, *args, **kwargs)

    you can fire it off with spinmob.thread.pool.start(my_thread) or my_thread.start()

    Parameters
    ----------
    function : function
        Function containing the code you wish to run in the thread.

    *args and **kwargs are sent to the function.
    '''

    def __init__(self, function, *args, **kwargs):
        super(worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.function = function
        self.args     = args
        self.kwargs   = kwargs
        self.signal_error = signal()
        self.signal_done  = signal()

    def start(self, priority=0):
        """
        Shortcut to pool.start(self, priority=priority)

        Parameters
        ----------
        priority=0 : int
            Thread priority. A higher value means it will move to the front
            of the queue above those threads having lower priority.
        """
        pool.start(self, priority=priority)

    @_pg.QtCore.pyqtSlot()
    def run(self):
        """
        Function needed by QRunnable. In this case, it runs the originally
        supplied function with arguments, and emits signals.
        """
        # Try firing up the function and emitting a signal for the result
        try:
            result = self.function(*self.args, **self.kwargs)
            self.signal_done.emit(result)

        # Print the error and emit the error signal
        except:
            _traceback.print_exc()
            exctype, value = _sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, _traceback.format_exc()))

def start(function, *args, done=None, error=None, priority=0, **kwargs):
    """
    Start a thread with the supplied function, arguments, and keyword arguments.
    This is just a shortcut to create the worker, connect signals, and
    run pool.start(worker).

    Parameters
    ----------
    function : function
        Function you wish to run.

    done=None : function or None
        Function to which signal_result will be connected. None means the signal
        will remain unconnected.

    error=None : function, optional
        Function to which signal_error will be connected. None means the signal
        will remain unconnected.

    priority=0 : int
        Controls the priority in the thread queue. Higher number means higher
        priority.

    Other *args and **kwargs are sent to the worker function itself.

    Returns
    -------
    worker instance.
    """
    # Create the worker
    w = worker(function, *args, **kwargs)

    # Connect any signals
    if done:  w.signal_done .connect(done)
    if error: w.signal_error.connect(error)

    # Start the worker
    pool.start(w, priority=priority)
    return w

def get_active_thread_count():
    """
    Returns the number of active threads in the pool.
    """
    return pool.activeThreadCount()


if __name__ == '__main__':

    import time

    def f(n):
        print('pants', n)
        time.sleep(0.1)
        print('shoes', n)
        time.sleep(0.1)
        s.emit('other')
        return 37*n


    def done(a): print('result', a)
    def other(a): print('other', a)

    s = signal(other).connect(other)

    # Start a thread
    w = start(f, 2, done=done)
    w.start()

