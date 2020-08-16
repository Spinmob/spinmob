import pyqtgraph as _pg
import traceback as _traceback
import sys       as _sys

# Thread pool
pool = _pg.QtCore.QThreadPool()

class _signals(_pg.QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.

    Signals
    -------
    error
        `tuple` (exctype, value, traceback.format_exc() )

    done
        `object` data returned from processing, if any
    '''
    error = _pg.QtCore.pyqtSignal(tuple)
    done  = _pg.QtCore.pyqtSignal(object)

class worker(_pg.QtCore.QRunnable):
    '''
    Single thread for doing work, based on QRunnable. After creating an instance:

        my_thread = spinmob.thread.worker(my_function, *args, **kwargs)

    you can fire it off with spinmob.thread.pool.start(my_thread).

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
        self._signals = _signals()
        self.signal_error = self._signals.error
        self.signal_done  = self._signals.done

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

def start(function, *args, done=None, error=None, **kwargs):
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
    pool.start(w)
    return w


if __name__ == '__main__':

    import time
    def f(n):
        print('pants', n)
        time.sleep(1.0)
        print('shoes', n)
        return 37*n

    def done(*a): print('result', a)

    # Start a thread
    w = start(f, 2, done=done)

