import time
import math
from multiprocessing import Process

def watchdog(interval):
    while True:
        print(f"[{time.strftime('%X')}] heartbeat")
        time.sleep(interval)

if __name__ == "__main__":
    p = Process(target=watchdog, args=(5,), daemon=True)
    p.start()
    start = time.perf_counter()
    result = [math.factorial(x) for x in range(12000)]
    end = time.perf_counter()

    print(end-start)
    print("Main work done, exiting.")