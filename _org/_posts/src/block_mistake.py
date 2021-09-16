from concurrent.futures import ProcessPoolExecutor
import time

tasks = range(10)
results = list()
start = time.time()


def do_work(task):
    time.sleep(0.1)
    return task ** 2


with ProcessPoolExecutor(max_workers=10) as pool:
    for task in tasks:
        future = pool.submit(do_work, task)
        results.append(future.result())  # collect results

print(f"Done after {time.time() - start}")
