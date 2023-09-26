from typing import Any
from typing import Callable
from typing import Iterable
from typing import Optional

from tqdm import tqdm


def pp_tqdm_map(func: Callable,
                iterable: Iterable,
                progress: Optional[tqdm] = None,
                processes: Optional[int | float] = None,
                chunksize: Optional[int] = None,
                initializer: Optional[Callable] = None,
                initargs: Optional[tuple] = None,
                no_par: bool = False,
                **kwargs: Any) -> list[Any]:
    """Performs an ordered map using processes with progress bar."""
    return _map(func=func,
                iterable=iterable,
                map_type='map',
                use_thread=False,
                progress=progress,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=True,
                **kwargs)


def pp_tqdm_imap(func: Callable,
                 iterable: Iterable,
                 progress: Optional[tqdm] = None,
                 processes: Optional[int | float] = None,
                 chunksize: Optional[int] = None,
                 initializer: Optional[Callable] = None,
                 initargs: Optional[tuple] = None,
                 no_par: bool = False,
                 **kwargs: Any) -> list[Any]:
    """Performs an ordered imap using processes with progress bar."""
    return _map(func=func,
                iterable=iterable,
                map_type='imap',
                use_thread=False,
                progress=progress,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=True,
                **kwargs)


def pp_tqdm_imap_unordered(func: Callable,
                           iterable: Iterable,
                           progress: Optional[tqdm] = None,
                           processes: Optional[int | float] = None,
                           chunksize: Optional[int] = None,
                           initializer: Optional[Callable] = None,
                           initargs: Optional[tuple] = None,
                           no_par: bool = False,
                           **kwargs: Any) -> list[Any]:
    """Performs an unordered imap using processes with progress bar."""
    return _map(func=func,
                iterable=iterable,
                map_type='imap_unordered',
                use_thread=False,
                progress=progress,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=True,
                **kwargs)


def pp_map(func: Callable,
           iterable: Iterable,
           processes: Optional[int | float] = None,
           chunksize: Optional[int] = None,
           initializer: Optional[Callable] = None,
           initargs: Optional[tuple] = None,
           no_par: bool = False,
           **kwargs: Any) -> list[Any]:
    """Performs an ordered map using processes."""
    return _map(func=func,
                iterable=iterable,
                map_type='map',
                use_thread=False,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=False,
                **kwargs)


def pp_imap(func: Callable,
            iterable: Iterable,
            processes: Optional[int | float] = None,
            chunksize: Optional[int] = None,
            initializer: Optional[Callable] = None,
            initargs: Optional[tuple] = None,
            no_par: bool = False,
            **kwargs: Any) -> list[Any]:
    """Performs an ordered imap using processes."""
    return _map(func=func,
                iterable=iterable,
                map_type='imap',
                use_thread=False,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=False,
                **kwargs)


def pp_imap_unordered(func: Callable,
                      iterable: Iterable,
                      processes: Optional[int | float] = None,
                      chunksize: Optional[int] = None,
                      initializer: Optional[Callable] = None,
                      initargs: Optional[tuple] = None,
                      no_par: bool = False,
                      **kwargs: Any) -> list[Any]:
    """Performs an unordered imap using processes."""
    return _map(func=func,
                iterable=iterable,
                map_type='imap_unordered',
                use_thread=False,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=False,
                **kwargs)


def pt_tqdm_map(func: Callable,
                iterable: Iterable,
                progress: Optional[tqdm] = None,
                processes: Optional[int | float] = None,
                chunksize: Optional[int] = None,
                initializer: Optional[Callable] = None,
                initargs: Optional[tuple] = None,
                no_par: bool = False,
                **kwargs: Any) -> list[Any]:
    """Performs an ordered map using threads with progress bar."""
    return _map(func=func,
                iterable=iterable,
                map_type='map',
                use_thread=True,
                progress=progress,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=True,
                **kwargs)


def pt_tqdm_imap(func: Callable,
                 iterable: Iterable,
                 progress: Optional[tqdm] = None,
                 processes: Optional[int | float] = None,
                 chunksize: Optional[int] = None,
                 initializer: Optional[Callable] = None,
                 initargs: Optional[tuple] = None,
                 no_par: bool = False,
                 **kwargs: Any) -> list[Any]:
    """Performs an ordered imap using threads with progress bar."""
    return _map(func=func,
                iterable=iterable,
                map_type='imap',
                use_thread=True,
                progress=progress,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=True,
                **kwargs)


def pt_tqdm_imap_unordered(func: Callable,
                           iterable: Iterable,
                           progress: Optional[tqdm] = None,
                           processes: Optional[int | float] = None,
                           chunksize: Optional[int] = None,
                           initializer: Optional[Callable] = None,
                           initargs: Optional[tuple] = None,
                           no_par: bool = False,
                           **kwargs: Any) -> list[Any]:
    """Performs an unordered imap using threads with progress bar."""
    return _map(func=func,
                iterable=iterable,
                map_type='imap_unordered',
                use_thread=True,
                progress=progress,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=True,
                **kwargs)


def pt_map(func: Callable,
           iterable: Iterable,
           processes: Optional[int | float] = None,
           chunksize: Optional[int] = None,
           initializer: Optional[Callable] = None,
           initargs: Optional[tuple] = None,
           no_par: bool = False,
           **kwargs: Any) -> list[Any]:
    """Performs an ordered map using threads."""
    return _map(func=func,
                iterable=iterable,
                map_type='map',
                use_thread=True,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=False,
                **kwargs)


def pt_imap(func: Callable,
            iterable: Iterable,
            processes: Optional[int | float] = None,
            chunksize: Optional[int] = None,
            initializer: Optional[Callable] = None,
            initargs: Optional[tuple] = None,
            no_par: bool = False,
            **kwargs: Any) -> list[Any]:
    """Performs an ordered imap using threads."""
    return _map(func=func,
                iterable=iterable,
                map_type='imap',
                use_thread=True,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=False,
                **kwargs)


def pt_imap_unordered(func: Callable,
                      iterable: Iterable,
                      processes: Optional[int | float] = None,
                      chunksize: Optional[int] = None,
                      initializer: Optional[Callable] = None,
                      initargs: Optional[tuple] = None,
                      no_par: bool = False,
                      **kwargs: Any) -> list[Any]:
    """Performs an unordered imap using threads."""
    return _map(func=func,
                iterable=iterable,
                map_type='imap_unordered',
                use_thread=True,
                processes=processes,
                chunksize=chunksize,
                initializer=initializer,
                initargs=initargs,
                no_par=no_par,
                use_tqdm=False,
                **kwargs)


def _map(func: Callable,
         iterable: Iterable,
         map_type: str,
         use_thread: bool = False,
         progress: Optional[tqdm] = None,
         processes: Optional[int | float] = None,
         chunksize: Optional[int] = None,
         initializer: Optional[Callable] = None,
         initargs: Optional[tuple] = None,
         no_par: bool = False,
         use_tqdm: bool = False,
         **kwargs: Any) -> list[Any]:
    """Returns a list of results for concurrent map operations.
    """
    from multiprocess.pool import Pool
    from multiprocess.pool import ThreadPool
    from os import cpu_count

    total = len(list(iterable))
    progress_needs_close = False
    if use_tqdm:
        if progress is None:
            # Determine length of tqdm (equal to length of the shortest iterable)
            total = kwargs.pop('total', total)
            progress = tqdm(total=total, **kwargs)
            progress_needs_close = True

    if no_par:
        if initializer is not None:
            if initargs is not None:
                initializer(*initargs)
            else:
                initializer()

        results = []
        for result in map(func, iterable):
            results.append(result)
            if use_tqdm:
                progress.update()
    else:
        if processes is None:
            my_processes = cpu_count()
        elif type(processes) == float:
            my_processes = int(round(processes * cpu_count()))
        else:
            my_processes = int(processes)

        if chunksize is None:
            chunksize = max(1, min(total // my_processes, 10))

        my_processes = min(my_processes, total)

        if use_thread:
            p = ThreadPool
        else:
            p = Pool

        with p(processes=my_processes, initializer=initializer, initargs=initargs) as pool:
            par_func = getattr(pool, map_type)

            results = []
            for result in par_func(func, iterable, chunksize=chunksize):
                results.append(result)
                if use_tqdm:
                    progress.update()

    if progress_needs_close:
        progress.close()

    return results


def pp_tqdm_apply_async(func: Callable,
                        iterable: Iterable,
                        progress: Optional[tqdm] = None,
                        processes: Optional[int | float] = None,
                        initializer: Optional[Callable] = None,
                        initargs: Optional[tuple] = None,
                        fixedargs: Optional[Iterable] = None,
                        no_par: bool = False,
                        **kwargs: Any) -> list[Any]:
    """Performs an apply async using processes with progress bar."""
    return _apply_async(func=func,
                        iterable=iterable,
                        use_thread=False,
                        progress=progress,
                        processes=processes,
                        initializer=initializer,
                        initargs=initargs,
                        fixedargs=fixedargs,
                        no_par=no_par,
                        use_tqdm=True,
                        **kwargs)


def pp_apply_async(func: Callable,
                   iterable: Iterable,
                   processes: Optional[int | float] = None,
                   initializer: Optional[Callable] = None,
                   initargs: Optional[tuple] = None,
                   fixedargs: Optional[Iterable] = None,
                   no_par: bool = False,
                   **kwargs: Any) -> list[Any]:
    """Performs an apply async using processes."""
    return _apply_async(func=func,
                        iterable=iterable,
                        use_thread=False,
                        processes=processes,
                        initializer=initializer,
                        initargs=initargs,
                        fixedargs=fixedargs,
                        no_par=no_par,
                        use_tqdm=False,
                        **kwargs)


def pt_tqdm_apply_async(func: Callable,
                        iterable: Iterable,
                        progress: Optional[tqdm] = None,
                        processes: Optional[int | float] = None,
                        initializer: Optional[Callable] = None,
                        initargs: Optional[tuple] = None,
                        fixedargs: Optional[Iterable] = None,
                        no_par: bool = False,
                        **kwargs: Any) -> list[Any]:
    """Performs an apply async using threads with progress bar."""
    return _apply_async(func=func,
                        iterable=iterable,
                        use_thread=True,
                        progress=progress,
                        processes=processes,
                        initializer=initializer,
                        initargs=initargs,
                        fixedargs=fixedargs,
                        no_par=no_par,
                        use_tqdm=True,
                        **kwargs)


def pt_apply_async(func: Callable,
                   iterable: Iterable,
                   processes: Optional[int | float] = None,
                   initializer: Optional[Callable] = None,
                   initargs: Optional[tuple] = None,
                   fixedargs: Optional[Iterable] = None,
                   no_par: bool = False,
                   **kwargs: Any) -> list[Any]:
    """Performs an apply async using threads."""
    return _apply_async(func=func,
                        iterable=iterable,
                        use_thread=True,
                        processes=processes,
                        initializer=initializer,
                        initargs=initargs,
                        fixedargs=fixedargs,
                        no_par=no_par,
                        use_tqdm=False,
                        **kwargs)


def _apply_async(func: Callable,
                 iterable: Iterable,
                 use_thread: bool = False,
                 progress: Optional[tqdm] = None,
                 processes: Optional[int | float] = None,
                 initializer: Optional[Callable] = None,
                 initargs: Optional[tuple] = None,
                 fixedargs: Optional[Iterable] = None,
                 no_par: bool = False,
                 use_tqdm: bool = False,
                 **kwargs: Any) -> list[Any]:
    """Returns a list of results for concurrent apply_async operations.
    """
    from multiprocess.pool import Pool
    from multiprocess.pool import ThreadPool
    from os import cpu_count

    progress_needs_close = False
    total = len(list(iterable))
    if use_tqdm:
        if progress is None:
            # Determine length of tqdm (equal to length of the shortest iterable)
            total = kwargs.pop('total', total)
            progress = tqdm(total=total, **kwargs)
            progress_needs_close = True

    if no_par:
        if initializer is not None:
            if initargs is not None:
                initializer(*initargs)
            else:
                initializer()

        results = []
        for item in iterable:
            if fixedargs is None:
                results.append(func(item))
            else:
                results.append(func(item, *fixedargs))
            if use_tqdm:
                progress.update()
    else:
        if processes is None:
            my_processes = cpu_count()
        elif type(processes) == float:
            my_processes = int(round(processes * cpu_count()))
        else:
            my_processes = int(processes)

        if use_thread:
            pool = ThreadPool(processes=my_processes, initializer=initializer, initargs=initargs)
        else:
            pool = Pool(processes=my_processes, initializer=initializer, initargs=initargs)

        if fixedargs is None:
            jobs = [pool.apply_async(func=func, args=(item,)) for item in iterable]
        else:
            jobs = [pool.apply_async(func=func, args=(item, *fixedargs)) for item in iterable]
        pool.close()

        results = []
        for job in jobs:
            results.append(job.get())
            if use_tqdm:
                progress.update()

    if progress_needs_close:
        progress.close()

    return results
