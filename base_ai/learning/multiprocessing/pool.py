import time
import math
from multiprocessing import Pool

if __name__ == '__main__':
    start = time.perf_counter()
    result1 = [math.factorial(x) for x in range(12000)]
    end = time.perf_counter()

    print(end-start)

    start = time.perf_counter()
    with Pool(5) as p: 
        result2 = p.map(math.factorial, list(range(12000)))
    end = time.perf_counter()

    print(end-start)