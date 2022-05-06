---
layout: post
title: Adding log odds to combine statistics
date: 2021-10-07
published: true
categories: julia statistics covid
---

<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>

<div id="outline-container-org3c385eb" class="outline-2">
<h2 id="org3c385eb">Adding log odds to combine statistics</h2>
<div class="outline-text-2" id="text-org3c385eb">
</div>

<div id="outline-container-orgccf76f3" class="outline-3">
<h3 id="orgccf76f3">Edit</h3>
<div class="outline-text-3" id="text-orgccf76f3">
<p>
<span class="underline">Update: see my next post for a much more straightforward calculation</span>
</p>

<a href="{{page.next.url}}">Corrected post on same calculation</a>

<p>
There is a small difference in the final answer that I cannot explain
yet. 
</p>
</div>
</div>

<div id="outline-container-orgb55f2d3" class="outline-3">
<h3 id="orgb55f2d3">Original post, please spot the mistake and let me know</h3>
<div class="outline-text-3" id="text-orgb55f2d3">
<p>
This is an answer to a <a href="https://stats.stackexchange.com/questions/546774/how-to-combine-state-level-covid-19-vaccination-rates-with-national-demographic">question</a> on Stats Overflow. 
</p>

<p>
I want to estimate the probability of a person aged 40-49 in Delaware
to be vaccinated, but I only have nationwide statistics on
vaccination levels by age, and a level of vaccination in Delaware, but
no age breakdown for that state.
</p>

<p>
I will need to make some independence assumptions, notably, that the
age distribution of vaccinations is the same in Delaware. See below
for another assumption I have to make to work with the provided data.
</p>

<p>
The method I use is to manually calculate the coefficients in a
logistic regression model. As you will see, what happens is that we
cannot add and subtract percentages directly, but we can add and
subtract logodds.
</p>
</div>
</div>

<div id="outline-container-org6a3af3a" class="outline-3">
<h3 id="org6a3af3a">Logistic regression model</h3>
<div class="outline-text-3" id="text-org6a3af3a">
<p>
To begin, we need two percentages from the <a href="https://covid.cdc.gov/covid-data-tracker/#vaccinations_vacc-total-admin-rate-total">official statistics</a>, the
nationwide (full) vaccination grade, and the percentage in Delaware.
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">us_vacc_p = .561
del_vacc_p = .566
</pre>
</div>

<pre class="example">
0.566
</pre>


<p>
I'm going to be using the following functions. The programming language
I'm using is Julia, but I'm using only two basic functions and
assignments so the code is going to be pretty much the same as in
Python or R. 
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">function logit(p)
     log(p / (1 - p))
end

function logistic(x)
    exp(x) / (exp(x) + 1)
end
</pre>
</div>

<p>
The <code>logit</code> function calculates the so called log odds of a probability. 
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">us_vacc_logodds = logit(us_vacc_p)
</pre>
</div>

<pre class="example">
0.24522149244752528
</pre>


<p>
The <code>logistic</code> function inverts this operation. A logistic regression
model for this looks like
</p>

<p>
\[
\text{logit}(p) = \text{base}
\]
</p>

<p>
for the general population, and
</p>

<p>
\[
\text{logit}(p) = \text{base} + \text{coefficient for Delaware}
\]
</p>

<p>
for persons living in Delaware, where \(p\) is the probability of that
person being vaccinated. Because the logistic function is the inverse
of the logit function, we can calculate \(p\), the probability we are
after, with the formula
</p>

<p>
\[
p = \text{logistic}\left(\text{base} + \text{coefficient for Delaware}\right)
\]
</p>

<p>
Now the trick is that we can manually calculate the coefficient for
Delaware using the following formula. 
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">del_vacc_coef = logit(del_vacc_p) - logit(us_vacc_p)
</pre>
</div>

<pre class="example">
0.020328051655252644
</pre>


<p>
To check this, let's use this model to calculate the vaccination
probability of the general us population,
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">logistic(us_vacc_logodds)
</pre>
</div>

<pre class="example">
0.561
</pre>


<p>
and for Delaware we use the coefficient as well, and we get
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">logistic(us_vacc_logodds + del_vacc_coef)
</pre>
</div>

<pre class="example">
0.566
</pre>


<p>
Now the next step is to calculate the coefficient for the age group,
and add that to our model as well. 
</p>
</div>
</div>

<div id="outline-container-orgd901c70" class="outline-3">
<h3 id="orgd901c70">Calculating the age coefficient for 40-49</h3>
<div class="outline-text-3" id="text-orgd901c70">
<p>
The official <a href="https://covid.cdc.gov/covid-data-tracker/#vaccination-demographic">statistics</a> aren't yet in the form we need them. On the
graphs, you can find that 14.1% of those vaccinated are in the age
group 40-49. What we want to know is how many in this age group are
vaccinated. A complication here is that only 91% of those vaccinated
have reported their age. We need another assumption here, namely that
this nonresponse is independent from age group. If we assume that, we
know that 14.1% of all vaccinated are in the age group 40-49.
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">vac_n = 186387228           # total number of vaccinated
age_vacc_n = .142 * vac_n   # in the age group 40-49
</pre>
</div>

<pre class="example">
26466986.376
</pre>


<p>
Also, we need the total number of people in the US in this age group,
which isn't listed directly either. From the graph, it's 12.2% of the
total population. The total population isn't listed either, but, 56.1%
of the population is vaccinated, so we can calculated the total
population from that.
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">us_n = vac_n / .561
</pre>
</div>

<pre class="example">
332241048.1283422
</pre>


<p>
So the percentage vaccinated in the age group 40-49 is
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">age_n = .122 * us_n
age_p = age_vacc_n / age_n
</pre>
</div>

<pre class="example">
0.6529672131147541
</pre>


<p>
Converting this to log odds, the calculation of the coefficient for the age
group 40-49 is the same as earlier for Delaware
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">age_vacc_coef = logit(age_p) - logit(us_vacc_p)
</pre>
</div>

<pre class="example">
0.38688616375890655
</pre>


<p>
In the final calculation I combine the age based coefficient to the
coefficient for Delaware. This is the step where I need the assumption
that the age distribution is the same in Delaware. 
</p>

<div class="org-src-container">
<pre class="src src-ess-julia">logistic(us_vacc_logodds + del_vacc_coef + age_vacc_coef)
</pre>
</div>

<pre class="example">
0.6575591337731559
</pre>


<p>
So with the listed assumptions I estimate the probability of a person
aged 40-49 living in Delaware to be vaccinated at 65.7%.
</p>

<p>
It is interesting to compare this to the original probabilities, with
65.3% of this age group being vaccinated in general, which is then
corrected by comparing the 56.6% Delaware population average to the
56.1% general us population average.
</p>

<p>
Thanks for reading! If you want to reach out, post an issue to the
<a href="https://github.com/Gijs-Koot/Gijs-Koot.github.io">Github repository of this website</a> or contact me on Twitter!
</p>
</div>
</div>
</div>
