from typing import Any
from typing import Callable
from typing import Generator
from typing import Iterable


def pp_tqdm_imap(func: Callable,
                 *iterables: Iterable,
                 no_par: bool = False,
                 **kwargs: Any) -> list[Any]:
    """Performs a parallel ordered imap with tqdm progress."""
    return list(_tqdm_imap(func, *iterables, no_par=no_par, **kwargs))


def pp_imap(func: Callable,
            *iterables: Iterable,
            no_par: bool = False,
            **kwargs: Any) -> list[Any]:
    """Performs a parallel ordered imap."""
    return list(_map(func, *iterables, no_par=no_par, **kwargs))


def _map(func: Callable,
         *iterables: Iterable,
         no_par: bool = False,
         **kwargs: Any) -> Generator:
    from os import cpu_count

    from multiprocess.pool import Pool

    num_cpus = kwargs.pop('num_cpus', None)
    initializer = kwargs.pop('initializer', None)
    initargs = kwargs.pop('initargs', None)

    if no_par:
        if initializer is not None:
            if initargs is not None:
                initializer(*initargs)
            else:
                initializer()

        for result in map(func, *iterables):
            yield result
    else:
        if num_cpus is None:
            num_cpus = cpu_count()
        elif type(num_cpus) == float:
            num_cpus = int(round(num_cpus * cpu_count()))

        with Pool(processes=num_cpus, initializer=initializer, initargs=initargs) as pool:
            for result in pool.imap(func, *iterables):
                yield result


def _tqdm_imap(func: Callable,
               *iterables: Iterable,
               no_par: bool = False,
               **kwargs: Any) -> Generator:
    from os import cpu_count
    from typing import Sized

    from multiprocess.pool import Pool
    from tqdm import tqdm

    progress = kwargs.pop('progress', None)
    num_cpus = kwargs.pop('num_cpus', None)
    initializer = kwargs.pop('initializer', None)
    initargs = kwargs.pop('initargs', None)
    total = kwargs.pop('total', min(len(iterable) for iterable in iterables if isinstance(iterable, Sized)))

    if progress is None:
        progress = tqdm(total=total, **kwargs)

    if no_par:
        if initializer is not None:
            if initargs is not None:
                initializer(*initargs)
            else:
                initializer()

        for result in map(func, *iterables):
            yield result
            progress.update()
    else:
        if num_cpus is None:
            num_cpus = cpu_count()
        elif type(num_cpus) == float:
            num_cpus = int(round(num_cpus * cpu_count()))

        with Pool(num_cpus, initializer=initializer, initargs=initargs) as pool:
            for item in pool.imap(func, *iterables):
                yield item
                progress.update()

    progress.close()
