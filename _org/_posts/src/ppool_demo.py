from concurrent.futures import ProcessPoolExecutor
import time
import os

tasks = range(10)
start = time.time()


def do_work(task):
    print(f"I am process {os.getpid()} working on task {task}")
    time.sleep(.2)


with ProcessPoolExecutor(max_workers=4) as pool:
    for task in tasks:
        pool.submit(do_work, task)

print(f"Main process done after {time.time() - start:.2f}s")
