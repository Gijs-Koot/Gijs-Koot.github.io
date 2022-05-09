---
layout: post
title: Partial batch failure with SQS driven Lambda functions
date: 2022-05-09
published: true
categories: AWS SQS 
---

<p>
When you have a lambda that is driven by a SQS queue, like <a href="https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html">this</a>, your lambda can
receive up to ten messages per batch. Your handler can look like this, handling
all of the messages in a single event in a for loop.
</p>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #4f97d7; font-weight: bold;">def</span> <span style="color: #bc6ec5; font-weight: bold;">lambda_handler</span><span style="color: #4f97d7;">(</span>event: <span style="color: #4f97d7;">dict</span>, context: <span style="color: #4f97d7;">dict</span><span style="color: #4f97d7;">)</span> -&gt; <span style="color: #a45bad;">None</span>:
    <span style="color: #4f97d7; font-weight: bold;">for</span> msg <span style="color: #4f97d7; font-weight: bold;">in</span> event<span style="color: #4f97d7;">[</span><span style="color: #2d9574;">"Records"</span><span style="color: #4f97d7;">]</span>:
        handle_msg<span style="color: #4f97d7;">(</span>msg<span style="color: #4f97d7;">)</span>
</pre>
</div>

<p>
If you do nothing and all messages are handled without exceptions, the messages
will be deleted from the SQS queue automatically for you. Logically, if there is
an error, the messages will not be deleted. They will be put back to the queue,
or, depending on the arrangement, they will be sent to the <a href="https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html">dead letter queue</a>.
But if your handler function raises an exception, the whole batch will be
failed, including the messages that have been processed already. This is
typically not the behaviour you want, and to solve this you have to delete or
put messages to the queue, keeping track of the failures and succesfully handled
messages yourself. This is not very obvious, and you can find some questions on
how to handle this properly <a href="https://stackoverflow.com/questions/55497907/how-do-i-fail-a-specific-sqs-message-in-a-batch-from-a-lambda">here</a> and <a href="https://stackoverflow.com/questions/56234199/splittling-sqs-lambda-batch-into-partial-success-partial-failure">here.</a>
</p>

<p>
AWS has introduced a new possibility for handling this, pretty recently, in
<a href="https://aws.amazon.com/about-aws/whats-new/2021/11/aws-lambda-partial-batch-response-sqs-event-source/">December 2021</a>. If you include the failed messages in a lambda response called
<code>batchItemFailures</code>, only those will be reposted to the queue (or the dead
letter queue). In <code>python</code>, this looks like this. 
</p>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #4f97d7; font-weight: bold;">def</span> <span style="color: #bc6ec5; font-weight: bold;">lambda_handler</span><span style="color: #4f97d7;">(</span>event: <span style="color: #4f97d7;">dict</span>, context: <span style="color: #4f97d7;">dict</span><span style="color: #4f97d7;">)</span> -&gt; <span style="color: #4f97d7;">dict</span>:
    batch_item_failures = <span style="color: #4f97d7;">[]</span>  <span style="color: #2aa1ae; background-color: #292e34;"># </span><span style="color: #2aa1ae; background-color: #292e34;">list of things that failed</span>

    <span style="color: #4f97d7; font-weight: bold;">for</span> msg <span style="color: #4f97d7; font-weight: bold;">in</span> event<span style="color: #4f97d7;">[</span><span style="color: #2d9574;">"Records"</span><span style="color: #4f97d7;">]</span>:
        <span style="color: #4f97d7; font-weight: bold;">try</span>:
            handle_msg<span style="color: #4f97d7;">(</span>msg<span style="color: #4f97d7;">)</span>
        <span style="color: #4f97d7; font-weight: bold;">except</span> <span style="color: #ce537a; font-weight: bold;">Exception</span> <span style="color: #4f97d7; font-weight: bold;">as</span> e:  <span style="color: #2aa1ae; background-color: #292e34;"># </span><span style="color: #2aa1ae; background-color: #292e34;">more specific is better</span>
            batch_item_failures.append<span style="color: #4f97d7;">(</span>msg<span style="color: #bc6ec5;">[</span><span style="color: #2d9574;">"messageId"</span><span style="color: #bc6ec5;">]</span><span style="color: #4f97d7;">)</span>

    <span style="color: #4f97d7; font-weight: bold;">return</span> <span style="color: #4f97d7;">{</span>
        <span style="color: #2d9574;">"batchItemFailures"</span>: batch_item_failures
    <span style="color: #4f97d7;">}</span>
</pre>
</div>
