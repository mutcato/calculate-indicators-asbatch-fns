import time
from functools import wraps


def split(lst, batch_size:int=10):
    """ Split a list into batches """
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

def timeit(my_func):
    @wraps(my_func)
    def timed(*args, **kw):

        tstart = time.time()
        output = my_func(*args, **kw)
        tend = time.time()

        print(
            '"{}" took {:.3f} ms to execute\n'.format(
                my_func.__name__, (tend - tstart) * 1000
            )
        )
        return output

    return timed