import threading
import timeit
from concurrent.futures import ThreadPoolExecutor

from helpers import decode_raw, decode_raw_av


def bench_decode():
    path = 'test.h264'
    N = 80
    with open(path, 'rb') as file:
        raw = file.read()
    print('Single Threaded Decoding')
    print('This Library:', timeit.timeit(lambda: decode_raw(raw), number=N))
    print('PyAV:', timeit.timeit(lambda: decode_raw_av(path), number=N))


def time_threaded(func, n, N):
    def wrapper():
        executor = ThreadPoolExecutor(max_workers=n)
        futures = [executor.submit(func) for _ in range(N)]
        for future in futures:
            future.result()

    return timeit.timeit(wrapper, number=1)


def bench_multithreaded_decode():
    path = 'test.h264'
    with open(path, 'rb') as file:
        raw = file.read()

    N = 80
    n = 3

    print('Multithreaded Decoding')
    print('This Library:', time_threaded(lambda: decode_raw(raw), n, N))
    print('PyAV:', time_threaded(lambda: decode_raw_av(path), n, N))


if __name__ == '__main__':
    bench_decode()
    bench_multithreaded_decode()