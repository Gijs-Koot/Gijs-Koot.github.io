---
layout: post
title: Pommodoro timer in Elisp
date: 2021-09-09
published: true
categories: elisp, emacs, time
---

<p>
I wrote a <a href="https://todoist.com/productivity-methods/pomodoro-technique">pommodoro</a> timer in <a href="https://www.emacswiki.org/emacs/LearnEmacsLisp">elisp</a>. Elisp is the language of Emacs,
the 40 year old editor that is still going! Elisp is to Emacs what
Javascript is to Visual Studio Code if that means more to you ;).
</p>

<p>
The pommodoro technique is new to me. It is a time management
technique that consists of five simple steps. 
</p>

<ol class="org-ol">
<li>Get a to-do list and a timer.</li>
<li>Set your timer for 25 minutes, and focus on a single task until the
timer rings.</li>
<li>When your session ends, mark off one pomodoro and record what you
completed.</li>
<li>Then enjoy a five-minute break.</li>
<li>After four pomodoros, take a longer, more restorative 15-30 minute
break.</li>
</ol>

<p>
The functionality consists of two global variables and two
functions. I use a variable for the timer itself, and a variable that
can be used to customize the time. I use <code>defvar</code>, which allows me to
add documentation to a variable as well. All the code I added to
<code>init.el</code>.
</p>

<div class="org-src-container">
<pre class="src src-elisp"><span style="color: #ffffff;">(</span><span style="color: #b6a0ff;">defvar</span> <span style="color: #00d3d0;">pommodoro-timeout</span> <span style="color: #79a8ff;">"25m"</span> <span style="color: #b0d6f5;">"Duration of a pommodoro timer"</span><span style="color: #ffffff;">)</span>
<span style="color: #ffffff;">(</span><span style="color: #b6a0ff;">defvar</span> <span style="color: #00d3d0;">pommodoro-current-timer</span> nil <span style="color: #b0d6f5;">"The current pommodoro timer"</span><span style="color: #ffffff;">)</span>
</pre>
</div>

<p>
Then I have two function that I can call when in Emacs. These I have
tied to <code>F2</code> and <code>F3</code>, so that they are really easy to reach. With
<code>pommodoro-start-timer</code> I am prompted for a title and then a timer is
set with that title. With <code>pommodoro-show-timer</code> a message appears in
the minibuffer that reminds me of the current timer and when it will
be finished.
</p>

<div class="org-src-container">
<pre class="src src-elisp"><span style="color: #ffffff;">(</span><span style="color: #b6a0ff;">defun</span> <span style="color: #feacd0;">pommodoro-start-timer</span> <span style="color: #ff62d4;">()</span>
  <span style="color: #b0d6f5;">"Start a pommodoro timer which shows a notification after 25 minutes"</span>
  <span style="color: #ff62d4;">(</span><span style="color: #b6a0ff;">interactive</span><span style="color: #ff62d4;">)</span>
  <span style="color: #ff62d4;">(</span><span style="color: #b6a0ff;">catch</span> '<span style="color: #00bcff;">cancel</span>
    <span style="color: #3fdfd0;">(</span><span style="color: #b6a0ff;">progn</span>
      <span style="color: #fba849;">(</span><span style="color: #b6a0ff;">if</span> <span style="color: #9f80ff;">(</span><span style="color: #b6a0ff;">and</span> pommodoro-current-timer <span style="color: #4fe42f;">(</span>time-less-p <span style="color: #fe6060;">(</span>current-time<span style="color: #fe6060;">)</span>
                <span style="color: #fe6060;">(</span>timer--time pommodoro-current-timer<span style="color: #fe6060;">)</span><span style="color: #4fe42f;">)</span><span style="color: #9f80ff;">)</span>
    <span style="color: #9f80ff;">(</span><span style="color: #b6a0ff;">if</span> <span style="color: #4fe42f;">(</span>yes-or-no-p <span style="color: #79a8ff;">"There is a current pommodoro running, do you want to cancel it? "</span><span style="color: #4fe42f;">)</span>
        <span style="color: #4fe42f;">(</span>cancel-timer pommodoro-current-timer<span style="color: #4fe42f;">)</span> <span style="color: #4fe42f;">(</span><span style="color: #b6a0ff;">throw</span> '<span style="color: #00bcff;">cancel</span> t<span style="color: #4fe42f;">)</span><span style="color: #9f80ff;">)</span><span style="color: #fba849;">)</span>
      <span style="color: #fba849;">(</span><span style="color: #b6a0ff;">setq</span> pommodoro-current-timer
      <span style="color: #9f80ff;">(</span>run-at-time pommodoro-timeout nil #'shell-command
       <span style="color: #4fe42f;">(</span>format <span style="color: #79a8ff;">"notify-send -i messagebox_info -u critical 'Pommodoro done' %s"</span>
         <span style="color: #fe6060;">(</span>read-string <span style="color: #79a8ff;">"Task description: "</span><span style="color: #fe6060;">)</span><span style="color: #4fe42f;">)</span><span style="color: #9f80ff;">)</span><span style="color: #fba849;">)</span><span style="color: #3fdfd0;">)</span><span style="color: #ff62d4;">)</span><span style="color: #ffffff;">)</span>
</pre>
</div>

<p>
This function sets a timer with <code>run-at-time</code>, based on a description
that you have to enter (<code>read-string</code>). There is one additional
functionality, if there is a currently running timer, I am prompted to
be sure I want to cancel that one. The notification is sent using
<code>shell-command</code>, using the Linux utility <code>notify-send</code>. There is a
package <code>notifications</code> in Emacs which works well, except for one
thing, I couldn't get the notifications to show when in full-screen
mode.
</p>

<p>
This is the function for seeing how much time there is left in the
current pommodoro which is very simple at the moment. 
</p>

<div class="org-src-container">
<pre class="src src-elisp"><span style="color: #ffffff;">(</span><span style="color: #b6a0ff;">defun</span> <span style="color: #feacd0;">pommodoro-show-timer</span> <span style="color: #ff62d4;">()</span>
  <span style="color: #ff62d4;">(</span><span style="color: #b6a0ff;">interactive</span><span style="color: #ff62d4;">)</span>
  <span style="color: #ff62d4;">(</span>message <span style="color: #79a8ff;">"Pommodoro done at %s"</span>
     <span style="color: #3fdfd0;">(</span>format-time-string <span style="color: #79a8ff;">"%T"</span> <span style="color: #fba849;">(</span>timer--time pommodoro-current-timer<span style="color: #fba849;">)</span><span style="color: #3fdfd0;">)</span><span style="color: #ff62d4;">)</span><span style="color: #ffffff;">)</span>
</pre>
</div>

<p>
And finally the keybindings are set with
</p>

<div class="org-src-container">
<pre class="src src-elisp"><span style="color: #ffffff;">(</span>global-set-key <span style="color: #ff62d4;">(</span>kbd <span style="color: #79a8ff;">"&lt;f2&gt;"</span><span style="color: #ff62d4;">)</span> #'pommodoro-start-timer<span style="color: #ffffff;">)</span>
<span style="color: #ffffff;">(</span>global-set-key <span style="color: #ff62d4;">(</span>kbd <span style="color: #79a8ff;">"&lt;f3&gt;"</span><span style="color: #ff62d4;">)</span> #'pommodoro-show-timer<span style="color: #ffffff;">)</span>
</pre>
</div>

<p>
I'll be trying to stick with the technique and this home-brewn
functionality for a while! Let's see how it works. Three improvements
I want to add right away are
</p>

<ul class="org-ul">
<li>The <code>pommodoro-show-timer</code> function should show the name of the
current task as well</li>
<li>The icon should be a tomato</li>
<li>The <code>pommodoro-show-timer</code> function should show the relative time
until running out instead of the actual time ("5m to go!" instead of
"done at 22:04:23")</li>
</ul>

<p>
Thanks for reading! If you want to
reach out, post an issue to the <a href="https://github.com/Gijs-Koot/Gijs-Koot.github.io">Github repository of this website</a> or
contact me on Twitter!
</p>
