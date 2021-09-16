from concurrent.futures import ProcessPoolExecutor
import time

start = time.time()

tasks = range(10)
futures = list()


def do_work(task):
    time.sleep(0.1)
    return task ** 2


with ProcessPoolExecutor(max_workers=10) as pool:
    for task in tasks:
        futures.append(pool.submit(do_work, task))

results = [future.result() for future in futures]

print(results)
print(f"Done after {time.time() - start}")
