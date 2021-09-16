import os
import time
import sys

tasks = list(range(10))

part_a = tasks[:5]
part_b = tasks[5:]

res = os.fork()

if res == 0:
    # main process
    for task in part_a:
        print(f"I am process {os.getpid()} working on task {task}")
        time.sleep(.2)
        sys.stdout.flush()
else:
    # child process
    for task in part_b:
        print(f"I am process {os.getpid()} working on task {task}")
        time.sleep(.2)
        sys.stdout.flush()
        
