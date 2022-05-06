---
layout: post
title: Using Futures and the ProcessPoolExecutor in python
date: 2021-09-16
published: true
categories: python multiprocessing
---

<div id="outline-container-org0804d4f" class="outline-2">
<h2 id="org0804d4f">When to use <code>ProcessPoolExecutor</code></h2>
<div class="outline-text-2" id="text-org0804d4f">
<p>
Using the <code>ProcessPoolExecutor</code> in <code>concurrent.futures</code> is a quick way
to divide your workload over multiple processes. This is useful if you
have a couple of tasks that you want to run in parallel to save
time. Compared to the <code>ThreadPoolExecutor</code>, the process pool is a bit
more primitive, basically, the whole process is forked into multiple
copies that each do their own business, with the
<code>concurrent.futures.ProcessPoolExecutor</code> taking care of cleaning up
and basic communication between the tasks.
</p>

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-left"><code>ProcessPoolExecutor</code></th>
<th scope="col" class="org-left"><code>ThreadPoolExecutor</code></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">strength</td>
<td class="org-left">Parallel CPU bound tasks</td>
<td class="org-left">Parellel IO bound tasks</td>
</tr>

<tr>
<td class="org-left">weakness</td>
<td class="org-left">Memory usage</td>
<td class="org-left">Limited to single CPU due to GIL</td>
</tr>
</tbody>
</table>

<p>
You should use the <code>ProcessPoolExecutor</code> over the <code>ThreadPoolExecutor</code>
if your tasks are CPU bound. The weakness of copying the process is
that you also copy it's memory which may add up, there is a bit more
overhead when compared to splitting into threads, but, the big
advantage is that multiple processes each can use up to 100% of a
single CPU core, while, due to the limitations of the Global
Interpreter Lock, multiple threads will not saturate multiple
CPU's. There's a couple of holes in this simplified model, for
example, python code can sometimes release the GIL, notably <code>numpy</code>
code, in which case threads can also effectively use multiple
GPU's. But for now, let's not worry about those details too much and
learn how to use multiprocessing easily in python.
</p>
</div>

<div id="outline-container-orgecc74a1" class="outline-3">
<h3 id="orgecc74a1">Basic multiprocessing with <code>os.fork</code></h3>
<div class="outline-text-3" id="text-orgecc74a1">
<p>
First, to get started, have a look at this demonstration of
<code>os.fork</code>. In practical terms, this duplicates the running
process. Two copies of the same program will run, basically identical,
except for their <code>pid</code>, their process id.
</p>

<div class="org-src-container">
<pre class="src src-bash">cat ./src/fork.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #b6a0ff;">import</span> os

os.fork<span style="color: #ffffff;">()</span>

<span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>os.getpid<span style="color: #ff62d4;">()</span><span style="color: #ffffff;">)</span>
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash">python3 ./src/fork.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #00bcff;">18359</span>
<span style="color: #00bcff;">18360</span>
</pre>
</div>

<p>
It is definitely possible to write some multiprocessing code directly
on this primitive system.
</p>

<div class="org-src-container">
<pre class="src src-bash">cat ./src/fork_mp.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #b6a0ff;">import</span> os
<span style="color: #b6a0ff;">import</span> time
<span style="color: #b6a0ff;">import</span> sys

<span style="color: #00d3d0;">tasks</span> = <span style="color: #f78fe7;">list</span><span style="color: #ffffff;">(</span><span style="color: #f78fe7;">range</span><span style="color: #ff62d4;">(</span><span style="color: #00bcff;">10</span><span style="color: #ff62d4;">)</span><span style="color: #ffffff;">)</span>

<span style="color: #00d3d0;">part_a</span> = tasks<span style="color: #ffffff;">[</span>:<span style="color: #00bcff;">5</span><span style="color: #ffffff;">]</span>
<span style="color: #00d3d0;">part_b</span> = tasks<span style="color: #ffffff;">[</span><span style="color: #00bcff;">5</span>:<span style="color: #ffffff;">]</span>

<span style="color: #00d3d0;">res</span> = os.fork<span style="color: #ffffff;">()</span>

<span style="color: #b6a0ff;">if</span> res == <span style="color: #00bcff;">0</span>:
    <span style="color: #a8a8a8;"># </span><span style="color: #a8a8a8;">main process</span>
    <span style="color: #b6a0ff;">for</span> task <span style="color: #b6a0ff;">in</span> part_a:
        <span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>f<span style="color: #79a8ff;">"I am process </span>{os.getpid()}<span style="color: #79a8ff;"> working on task </span>{task}<span style="color: #79a8ff;">"</span><span style="color: #ffffff;">)</span>
        time.sleep<span style="color: #ffffff;">(</span>.<span style="color: #00bcff;">2</span><span style="color: #ffffff;">)</span>
        sys.stdout.flush<span style="color: #ffffff;">()</span>
<span style="color: #b6a0ff;">else</span>:
    <span style="color: #a8a8a8;"># </span><span style="color: #a8a8a8;">child process</span>
    <span style="color: #b6a0ff;">for</span> task <span style="color: #b6a0ff;">in</span> part_b:
        <span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>f<span style="color: #79a8ff;">"I am process </span>{os.getpid()}<span style="color: #79a8ff;"> working on task </span>{task}<span style="color: #79a8ff;">"</span><span style="color: #ffffff;">)</span>
        time.sleep<span style="color: #ffffff;">(</span>.<span style="color: #00bcff;">2</span><span style="color: #ffffff;">)</span>
        sys.stdout.flush<span style="color: #ffffff;">()</span>

</pre>
</div>

<p>
This program divides the tasks between the two processes. I added a
<code>time.sleep(0.2)</code> for every task, so the tasks in total take two
seconds. The script however takes approximately 1 second to run,
saving exactly one second over running the tasks in a single process.
</p>

<p>
We use the output of <code>os.fork</code> to determine which of the processes we
are, if the result is 0, we are the main process, and if the result is
different, we know we are in the child process.
</p>

<div class="org-src-container">
<pre class="src src-bash">python3 ./src/fork_mp.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python">I am process <span style="color: #00bcff;">18377</span> working on task <span style="color: #00bcff;">0</span>
I am process <span style="color: #00bcff;">18376</span> working on task <span style="color: #00bcff;">5</span>
I am process <span style="color: #00bcff;">18377</span> working on task <span style="color: #00bcff;">1</span>
I am process <span style="color: #00bcff;">18376</span> working on task <span style="color: #00bcff;">6</span>
I am process <span style="color: #00bcff;">18377</span> working on task <span style="color: #00bcff;">2</span>
I am process <span style="color: #00bcff;">18376</span> working on task <span style="color: #00bcff;">7</span>
I am process <span style="color: #00bcff;">18376</span> working on task <span style="color: #00bcff;">8</span>
I am process <span style="color: #00bcff;">18377</span> working on task <span style="color: #00bcff;">3</span>
I am process <span style="color: #00bcff;">18376</span> working on task <span style="color: #00bcff;">9</span>
I am process <span style="color: #00bcff;">18377</span> working on task <span style="color: #00bcff;">4</span>
</pre>
</div>

<p>
These examples show at a lower level than the <code>ProcessPoolExecutor</code>
how multiprocessing works. However, if you want to extend the latter
approach into working code that deals with failures, passes the tasks
to the processes consistently and also collects the results, you can
see it'll get quite a bit more complicated. Enter the
<code>ProcessPoolExecutor</code>, which does all those hard things for you! 
</p>

<div class="org-src-container">
<pre class="src src-bash">cat ./src/ppool_demo.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #b6a0ff;">from</span> concurrent.futures <span style="color: #b6a0ff;">import</span> ProcessPoolExecutor
<span style="color: #b6a0ff;">import</span> time
<span style="color: #b6a0ff;">import</span> os

<span style="color: #00d3d0;">tasks</span> = <span style="color: #f78fe7;">range</span><span style="color: #ffffff;">(</span><span style="color: #00bcff;">10</span><span style="color: #ffffff;">)</span>
<span style="color: #00d3d0;">start</span> = time.time<span style="color: #ffffff;">()</span>


<span style="color: #b6a0ff;">def</span> <span style="color: #feacd0;">do_work</span><span style="color: #ffffff;">(</span>task<span style="color: #ffffff;">)</span>:
    <span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>f<span style="color: #79a8ff;">"I am process </span>{os.getpid()}<span style="color: #79a8ff;"> working on task </span>{task}<span style="color: #79a8ff;">"</span><span style="color: #ffffff;">)</span>
    time.sleep<span style="color: #ffffff;">(</span>.<span style="color: #00bcff;">2</span><span style="color: #ffffff;">)</span>


<span style="color: #b6a0ff;">with</span> ProcessPoolExecutor<span style="color: #ffffff;">(</span>max_workers=<span style="color: #00bcff;">4</span><span style="color: #ffffff;">)</span> <span style="color: #b6a0ff;">as</span> pool:
    <span style="color: #b6a0ff;">for</span> task <span style="color: #b6a0ff;">in</span> tasks:
        pool.submit<span style="color: #ffffff;">(</span>do_work, task<span style="color: #ffffff;">)</span>

<span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>f<span style="color: #79a8ff;">"Main process done after </span>{time.time() - start:.2f}<span style="color: #79a8ff;">s"</span><span style="color: #ffffff;">)</span>
</pre>
</div>

<p>
In only three lines you can start 4 workers that divide the work as
evenly as possible.
</p>

<ul class="org-ul">
<li><code>pool.submit</code> sends a task to one of the workers</li>
<li>The context manager (<code>with</code> block) waits until all the workers are
done before proceeding</li>
</ul>

<p>
This example takes 0.6 seconds. We have four workers, 10 tasks, so
some workers get 2 tasks and some get 3 tasks, and the workers with 3
tasks take 3 * 0.2 seconds to finish.
</p>

<div class="org-src-container">
<pre class="src src-bash">python ./src/ppool_demo.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python">
</pre>
</div>

<p>
Note that in the output, the processes seem ordered. However, this is
a subtle effect of buffering of the <code>stdout</code>. Each process has its own
buffer and they flush all their output in one go, making it look like
they run in succession. You can surpress this behaviour by manually
triggering the flushes as I showed earlier with <code>sys.stdout.flush()</code>.
</p>

<p>
Here, it is crucial that <code>pool.submit</code> is non-blocking, if you call
the function the main process doesn't wait until the worker is
done. This allows us to schedule all the work to the workers quickly.
</p>

<p>
There are three things I want to explain in this post
</p>

<ul class="org-ul">
<li>How you can collect return values of the tasks (using
<code>concurrent.futures.Future</code>)</li>
<li>What happens if workers run into an exception and how you can deal
with it</li>
</ul>
</div>
</div>

<div id="outline-container-org6424cf4" class="outline-3">
<h3 id="org6424cf4">Collecting return values</h3>
<div class="outline-text-3" id="text-org6424cf4">
<p>
In the examples above, I simply fired off the tasks and showed that
they were doing something by printing statements to <a href="https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)">stdout</a>. But in a
practical situation, you typically want to collect the results of the
work. To do that with a <code>ProcessPoolExecutor</code>, you will need to deal
with <code>concurrent.futures.Future</code>. If you have experience with
Javascript for example, dealing with futures is very common, but you
can write quite a bit of python code without encountering these.
</p>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #b6a0ff;">from</span> concurrent.futures <span style="color: #b6a0ff;">import</span> ProcessPoolExecutor

<span style="color: #b6a0ff;">def</span> <span style="color: #feacd0;">work</span><span style="color: #ffffff;">(</span>word<span style="color: #ffffff;">)</span>:
    <span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>word<span style="color: #ffffff;">)</span>
    <span style="color: #b6a0ff;">return</span> <span style="color: #f78fe7;">len</span><span style="color: #ffffff;">(</span>word<span style="color: #ffffff;">)</span>

<span style="color: #b6a0ff;">with</span> ProcessPoolExecutor<span style="color: #ffffff;">(</span>max_workers=<span style="color: #00bcff;">1</span><span style="color: #ffffff;">)</span> <span style="color: #b6a0ff;">as</span> pool:
    result = pool.submit<span style="color: #ffffff;">(</span>work, <span style="color: #79a8ff;">"hello"</span><span style="color: #ffffff;">)</span>
    <span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>result<span style="color: #ffffff;">)</span>
</pre>
</div>

<p>
The result of a <code>pool.submit</code> is an instance of <a href="https://docs.python.org/3/library/concurrent.futures.html#future-objects"><code>Future</code></a>. A <code>Future</code> is a
reference to work in progress. Its most fundamental method is
<code>Future.result</code>. From the official documentation
</p>

<blockquote>
<p>
Return the value returned by the call. If the call hasn’t yet
completed then this method will wait up to timeout seconds. If the
call hasn’t completed in timeout seconds, then a
concurrent.futures.TimeoutError will be raised. timeout can be an int
or float. If timeout is not specified or None, there is no limit to
the wait time.
</p>

<p>
If the future is cancelled before completing then CancelledError will
be raised.
</p>

<p>
If the call raised an exception, this method will raise the same
exception.
</p>
</blockquote>

<p>
It is important to understand that this method is <b>blocking</b>, as
opposed to the <code>pool.submit</code> method I used earlier. A mistake I have
seen often is the following:
</p>

<div class="org-src-container">
<pre class="src src-bash">cat ./src/block_mistake.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #b6a0ff;">from</span> concurrent.futures <span style="color: #b6a0ff;">import</span> ProcessPoolExecutor
<span style="color: #b6a0ff;">import</span> time

<span style="color: #00d3d0;">tasks</span> = <span style="color: #f78fe7;">range</span><span style="color: #ffffff;">(</span><span style="color: #00bcff;">10</span><span style="color: #ffffff;">)</span>
<span style="color: #00d3d0;">results</span> = <span style="color: #f78fe7;">list</span><span style="color: #ffffff;">()</span>
<span style="color: #00d3d0;">start</span> = time.time<span style="color: #ffffff;">()</span>


<span style="color: #b6a0ff;">def</span> <span style="color: #feacd0;">do_work</span><span style="color: #ffffff;">(</span>task<span style="color: #ffffff;">)</span>:
    time.sleep<span style="color: #ffffff;">(</span><span style="color: #00bcff;">0</span>.<span style="color: #00bcff;">1</span><span style="color: #ffffff;">)</span>
    <span style="color: #b6a0ff;">return</span> task ** <span style="color: #00bcff;">2</span>


<span style="color: #b6a0ff;">with</span> ProcessPoolExecutor<span style="color: #ffffff;">(</span>max_workers=<span style="color: #00bcff;">10</span><span style="color: #ffffff;">)</span> <span style="color: #b6a0ff;">as</span> pool:
    <span style="color: #b6a0ff;">for</span> task <span style="color: #b6a0ff;">in</span> tasks:
        future = pool.submit<span style="color: #ffffff;">(</span>do_work, task<span style="color: #ffffff;">)</span>
        results.append<span style="color: #ffffff;">(</span>future.result<span style="color: #ff62d4;">()</span><span style="color: #ffffff;">)</span>  <span style="color: #a8a8a8;"># </span><span style="color: #a8a8a8;">collect results</span>

<span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>f<span style="color: #79a8ff;">"Done after </span>{time.time() - start}<span style="color: #79a8ff;">"</span><span style="color: #ffffff;">)</span>
</pre>
</div>

<p>
Can you spot the mistake? The problem is that before scheduling the
next task, the main process waits the result of the task just
scheduled. This script takes 1 second to run, because in effect, all
tasks are run in succession.
</p>

<div class="org-src-container">
<pre class="src src-bash">python ./src/block_mistake.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python">
</pre>
</div>

<p>
Instead, the results should be collected after the process pool
context is done scheduling the tasks.
</p>

<div class="org-src-container">
<pre class="src src-bash">cat ./src/block_fixed.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #b6a0ff;">from</span> concurrent.futures <span style="color: #b6a0ff;">import</span> ProcessPoolExecutor
<span style="color: #b6a0ff;">import</span> time

<span style="color: #00d3d0;">start</span> = time.time<span style="color: #ffffff;">()</span>

<span style="color: #00d3d0;">tasks</span> = <span style="color: #f78fe7;">range</span><span style="color: #ffffff;">(</span><span style="color: #00bcff;">10</span><span style="color: #ffffff;">)</span>
<span style="color: #00d3d0;">futures</span> = <span style="color: #f78fe7;">list</span><span style="color: #ffffff;">()</span>


<span style="color: #b6a0ff;">def</span> <span style="color: #feacd0;">do_work</span><span style="color: #ffffff;">(</span>task<span style="color: #ffffff;">)</span>:
    time.sleep<span style="color: #ffffff;">(</span><span style="color: #00bcff;">0</span>.<span style="color: #00bcff;">1</span><span style="color: #ffffff;">)</span>
    <span style="color: #b6a0ff;">return</span> task ** <span style="color: #00bcff;">2</span>


<span style="color: #b6a0ff;">with</span> ProcessPoolExecutor<span style="color: #ffffff;">(</span>max_workers=<span style="color: #00bcff;">10</span><span style="color: #ffffff;">)</span> <span style="color: #b6a0ff;">as</span> pool:
    <span style="color: #b6a0ff;">for</span> task <span style="color: #b6a0ff;">in</span> tasks:
        futures.append<span style="color: #ffffff;">(</span>pool.submit<span style="color: #ff62d4;">(</span>do_work, task<span style="color: #ff62d4;">)</span><span style="color: #ffffff;">)</span>

results = <span style="color: #ffffff;">[</span>future.result<span style="color: #ff62d4;">()</span> <span style="color: #b6a0ff;">for</span> future <span style="color: #b6a0ff;">in</span> futures<span style="color: #ffffff;">]</span>

<span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>results<span style="color: #ffffff;">)</span>
<span style="color: #f78fe7;">print</span><span style="color: #ffffff;">(</span>f<span style="color: #79a8ff;">"Done after </span>{time.time() - start}<span style="color: #79a8ff;">"</span><span style="color: #ffffff;">)</span>
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash">python ./src/block_fixed.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-python">
</pre>
</div>
</div>
</div>

<div id="outline-container-org1d86d84" class="outline-3">
<h3 id="org1d86d84">Dealing with exceptions in child processes</h3>
<div class="outline-text-3" id="text-org1d86d84">
<p>
If a child process raises a unhandled <code>Exception</code>, this exception is
passed to the main process when calling <code>Future.result</code>. In the
example below, you can see how to catch those errors when unpacking
the results of the process workers.
</p>

<div class="org-src-container">
<pre class="src src-bash">cat ./src/error_example.py
</pre>
</div>

<pre class="example">
from concurrent.futures import ProcessPoolExecutor
from random import random

tasks = range(10)
futures = list()


def do_work(task):
    if random() &gt; .5:
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
</pre>

<div class="org-src-container">
<pre class="src src-bash">python ./src/error_example.py
</pre>
</div>

<pre class="example">
[0, 1, 4, 9, 16, 'Failed with OW!!', 'Failed with OW!!', 'Failed with OW!!', 64, 81]
</pre>

<p>
Thanks for reading! If you want to reach out, post an issue to the
<a href="https://github.com/Gijs-Koot/Gijs-Koot.github.io">Github repository of this website</a> or contact me on Twitter!
</p>
</div>
</div>
</div>
