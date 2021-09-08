---
layout: post
title: Popping balloons (2)
date: 2021-09-08
published: true
categories: julia probability risk
---

<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>

<div id="outline-container-org77d1cb6" class="outline-2">
<h2 id="org77d1cb6">Expected value of a single balloon</h2>
<div class="outline-text-2" id="text-org77d1cb6">
This is a follow up to the <a class="prev" href="{{page.previous.url}}">previous</a> post on the same game

<p>
Let us assume, as before, that the balloon pops at a certain level
\(M\), and we believe \(M \sim \text{uniform}(1, 21)\). \(M = 1\) means the
balloon will pop immediately after we pump it once. 
</p>

<p>
I figured out in the last post that the optimal strategy in this case
is to push 10 or 11 times, then stop. But what is then the expected
value of this game?  There are two options, either we reach 10 pushes
without popping the balloon, or it pops before we get there. Let's
call our cashout \(B\), and the expected value is
</p>

\begin{align}
\mathbb{E}\left(B\right) &= \mathbb{P}\left(\text{reach 10
pushes}\right) \cdot 10 \\
&= \mathbb{P}(M > 10) \cdot 10 = 5
\end{align}

<p>
This is a simple formula, the expected value is the probability of
reaching the goal times the goal set. Using this, we can easily
evaluate other strategies. For example, what if our
strategy is to play 11 times?
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">11 * (9 / 20)
</pre>
</div>

<pre class="example">
4.95
</pre>


<p>
Plotting the expected value for all strategies, it follows a parabole,
topping out at 10 as calculated before.
</p>

<div class="org-src-container">
<pre class="src src-ess-julia"><span style="color: #b6a0ff;">using</span> Plots

bar(x -&gt; (x * (20 - x) / 20), 0:20, labels=<span style="color: #79a8ff;">"expected value"</span>, color=<span style="color: #79a8ff;">"purple"</span>)
</pre>
</div>


<div id="org49470da" class="figure">
<p><img src="/assets/images/uniformexpected.png" alt="uniformexpected.png" />
</p>
</div>
</div>

<div id="outline-container-org011668b" class="outline-3">
<h3 id="org011668b">A different distribution for \(M\)</h3>
<div class="outline-text-3" id="text-org011668b">
<p>
Now what if I believe \(M\) to follow a Poisson distribution, and let's
take 11 as the parameter as an example. First a plot of the distribution of \(M\).
</p>

<div class="org-src-container">
<pre class="src src-ess-julia"><span style="color: #b6a0ff;">using</span> Distributions

belief = Poisson(11)

bar(x -&gt; pdf(belief, x), -10:30, labels=<span style="color: #79a8ff;">"probability"</span>, color=<span style="color: #79a8ff;">"brown"</span>)
</pre>
</div>


<div id="orgac698f4" class="figure">
<p><img src="/assets/images/poissondist.png" alt="poissondist.png" />
</p>
</div>

<p>
And these are the expected values of playing on until a certain payoff
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">belief = Poisson(11)

expected = x -&gt; (1 - cdf(belief, x)) * x

bar(expected, 0:20, labels=<span style="color: #79a8ff;">"expected value"</span>, color=<span style="color: #79a8ff;">"yellow"</span>)
</pre>
</div>


<div id="orgcbce420" class="figure">
<p><img src="/assets/images/poissonexp.png" alt="poissonexp.png" />
</p>
</div>

<p>
The optimal strategy is to play 8 rounds. The interesting thing is
that the two underlying distributions I analyzed have the same
average, but with a Poisson distribution it is optimal to stop before
reaching the average round at which the balloon pops. 
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">mean(Uniform(1, 21)), mean(Poisson(11))
</pre>
</div>

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-right" />
</colgroup>
<tbody>
<tr>
<td class="org-right">11.0</td>
</tr>

<tr>
<td class="org-right">11.0</td>
</tr>
</tbody>
</table>
</div>
</div>

<div id="outline-container-org5de8d4c" class="outline-3">
<h3 id="org5de8d4c">Summary</h3>
<div class="outline-text-3" id="text-org5de8d4c">
<p>
In this post I used a much more straightforward formula to find the
optimal strategy, and was able to calculate expected payoffs for
different strategies for two different distributions. How the shape of
the distribution influences the optimal strategy is interesting, can
this be generalized to other distributions? Thanks for reading this
post, if you want to reach out, post an issue to the <a href="https://github.com/Gijs-Koot/Gijs-Koot.github.io">Github repository
of this website</a> or contact me on Twitter!
</p>
</div>
</div>
</div>
