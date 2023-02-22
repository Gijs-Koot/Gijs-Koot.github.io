---
layout: post
title: Adjusting age group for local vaccination rate (2)
date: 2021-10-09
published: true
categories: julia statistics covid
---

<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>

<div id="outline-container-org7485290" class="outline-2">
<h2 id="org7485290">Adjusting percentages for local vaccination rate</h2>
<div class="outline-text-2" id="text-org7485290">
<p>
This is an answer to a <a href="https://stats.stackexchange.com/questions/546774/how-to-combine-state-level-covid-19-vaccination-rates-with-national-demographic">question</a> on Stats Overflow. 
</p>

<p>
I want to estimate the probability of a person aged 40-49 in Delaware
to be vaccinated, but I only have nationwide statistics on vaccination
levels by age, and a level of vaccination in Delaware, but no age
breakdown for that state. So the question is, how can we combine those
percentages, for the agegroup and Delaware, into a specific percentage
for that agegroup in Delaware?
</p>

<p>
I tried doing that in my
</p>
<a href="{{page.previous.url}}">previous</a>
<p>
post, but, I came up with a more straightforward method.
</p>

<p>
To begin, from the <a href="https://covid.cdc.gov/covid-data-tracker/#vaccinations_vacc-total-admin-rate-total">official statistics</a>, we get the percentage of
people vaccinated in Delaware, which is 56.6%. Let \(D\) be the total
population of Delaware. Then there are \(0.566 \cdot D\) vaccinated
persons in Delaware.
</p>

<p>
The number of people in the US in the age group 40-49 is 12.2%. But
they make up 14.2% percent of the people vaccinated. Let's assume
these percentages hold in Delaware as well.
</p>

<p>
Then the total number of people aged 40-49 living in Delaware is
\(0.122\cdot D\). And the number of people vaccinated aged between 40-49
is 14.2% of vaccinated subjects. So the final percentage is
</p>

<p>
\[
\frac{0.142 \cdot 0.566 \cdot D}{0.122 \cdot D} = \frac{.142 \cdot .566}{0.122} \approx 65.9\%
\]
</p>
</div>
</div>
