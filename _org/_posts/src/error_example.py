from concurrent.futures import ProcessPoolExecutor
from random import random

tasks = range(10)
futures = list()


def do_work(task):
    if random() > .5:
        return task ** 2
    else:
        raise Exception("OW!")


with ProcessPoolExecutor(max_workers=10) as pool:
    for task in tasks:
        futures.append(pool.submit(do_work, task))

results = list()

for future in futures:
    try:
        results.append(future.result())
    except Exception as e:
        results.append(f"Failed with {e}!")

print(results)
