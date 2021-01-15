---
layout: post
title:  "Estimating matchup percentages in a hierarchical model with Stan"
date:   2019-02-25 10:30:00 +0200
published: true
categories: statistics mtg bayesian hierarchical game python
---
# Estimating matchup percentages in a hierarchical model with Stan

Following up on my previous post, I will be estimating winning percentages between decks in the game of Magic. First, I will give some motivation and the main part is a Bayesian hierarchical model written in [Stan](mc-stan.org), using its Python interface, `pystan`. First, let's load the data and the dependencies. 


```python
import pystan
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

%matplotlib inline
```


```python
mu = pd.read_csv("./data/matchups_clean.csv", index_col=0).rename(columns = dict(over="vs"))
all_decks = list(set(mu.deck.values.tolist() + mu.vs.values.tolist()))

# the categorical datatype is appropriate, and it helps in converting to stan's data format
mu.deck = pd.Categorical(mu.deck, categories=all_decks)
mu.vs = pd.Categorical(mu.vs, categories=all_decks)

np.random.seed(1)

mu.sample(10)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>deck</th>
      <th>vs</th>
      <th>won</th>
      <th>lost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>121</th>
      <td>Burn</td>
      <td>Infect</td>
      <td>3</td>
      <td>1</td>
    </tr>
    <tr>
      <th>51</th>
      <td>Burn</td>
      <td>Hardened Scales</td>
      <td>5</td>
      <td>6</td>
    </tr>
    <tr>
      <th>62</th>
      <td>Hardened Scales</td>
      <td>Izzet Phoenix</td>
      <td>9</td>
      <td>6</td>
    </tr>
    <tr>
      <th>59</th>
      <td>Izzet Phoenix</td>
      <td>Spirits</td>
      <td>20</td>
      <td>12</td>
    </tr>
    <tr>
      <th>120</th>
      <td>Green Tron</td>
      <td>Infect</td>
      <td>7</td>
      <td>8</td>
    </tr>
    <tr>
      <th>95</th>
      <td>Humans</td>
      <td>Jund</td>
      <td>4</td>
      <td>0</td>
    </tr>
    <tr>
      <th>98</th>
      <td>Hardened Scales</td>
      <td>Humans</td>
      <td>8</td>
      <td>3</td>
    </tr>
    <tr>
      <th>91</th>
      <td>Ironworks</td>
      <td>Jund</td>
      <td>6</td>
      <td>5</td>
    </tr>
    <tr>
      <th>118</th>
      <td>Infect</td>
      <td>Ironworks</td>
      <td>6</td>
      <td>2</td>
    </tr>
    <tr>
      <th>61</th>
      <td>Green Tron</td>
      <td>Izzet Phoenix</td>
      <td>10</td>
      <td>8</td>
    </tr>
  </tbody>
</table>
</div>



The data that I'll be using is collected from [this](https://www.channelfireball.com/articles/the-ghosts-of-portland-massive-modern-matchup-analysis/) post. In Magic, you are free to build your own deck of 60 cards that you bring to a tournament. Virtually all players select a deck that is a close variation of a well-known _archetype_. These archetypes work well against some other ones, and don't work well in other cases. This leads to a bit of a probabilistic rock-paper-scissors situation if you will. Usually there is not a single best deck, but if you expect some archetype to show up a lot, you want to chose a different archetype that matches up well against it. But the winning percentages are not a given. There is not a lot of data collection on this, and the creators of the game are actively avoiding publishing good information on the matchups, to keep it interesting. So I have to work with limited data, but make the most of it. Exactly where I want to be. In the table above, you can see some unclear matchups, and some matchups that look bad for one side. I have included the full table of all the data at the end of this post. As an example of an unbalanced matchup, the _Humans_ archetype won all of the four encounters against the _Jund_ archetype. It's logical to try and directly estimate the winning percentage from the outcomes above by dividing the number of won matches by matches played. This is also done in the referenced post where I collected the data from.  


```python
opp = mu.rename(columns = dict(deck="vs", vs="deck", lost="won", won="lost"))
symm = pd.concat([mu, opp], sort=False).set_index(['deck', 'vs'])
naive_perc = (symm.won / (symm.won + symm.lost)).unstack(1)
plt.figure(figsize=(10, 8))
sns.heatmap(naive_perc, annot=True, fmt=".0%", cmap=plt.get_cmap("bwr_r"));
```


    
![png](/assets/images/mtg-mup-stan_4_0.png)
    


This doesn't look good, and the problems that you see here are very common when you have little data. Or at least when your model has a lot of parameters relative to the data. 

There are parameters that you have no data on at all, and the parameters that you do have data on are exaggerated. No matchup is going to be 0% or 100%. I encounter this situation often at work, and it is common to say "we need more data" and simply move on to another project where [n is large enough](https://statmodeling.stat.columbia.edu/2005/07/31/n_is_never_larg/).  

But just from common sense, you could actually derive reasonable estimates for the missing matchups. For example, by saying, this deck is doing well against all other decks, so I'm going to guess it's 60%. Or, more advanced, the matchup versus Burn is similar to the matchup against Izzet Phoenix, so I'm going to go for something close to that matchup that I actually do have some data on. In the analysis that will follow, I will use a statistical model that implements this latter line of reasoning. The crucial twist that hierarchical models add is that they are actually simultaneously estimating the similarity of matchups, so I don't have to tell the model in advance that the _Burn_ matchup is a bit like the _Izzet Phoenix_ matchup. That makes sense, because that information is in the data as well, but still, I find it kind of amazing. 

Here is the model, with annotations if you want to understand more deeply what's going on. 


```python
%%time

model_code = '''
data {

    /*
    the data should contain one record per matchup, you might want to include both burn vs infect 
    as well as infect vs burn, which works fine, but it's interpreted by the model as twice the information
    /**/

    int N; // number of decks
    int M; // number of recorded matchups
    
    int deck[M]; // index of deck
    int vs[M];   // index of the opposite deck
    
    int won[M];  // number of times the first deck won
    int n[M];    // out of n recorded matches for this matchup
}

parameters {

  vector[N] A[N]; // N vectors of lenght N for all matchups. symmetry is handled later
  
  real deck_pow_sd; // all decks have a raw power level
  real deck_pow[N]; // and their prior is pooled
  
  real deck_var_mu; // all decks have a variance in power across matchups 
  real deck_var_sd; // this is also pooled
  vector[N] deck_var;
  
  corr_matrix[N] O; // this is the matrix that encodes information on similarity between matchups

}

model {
  
  // i use some unnecessary vars to simplify the coding
  int a;
  int b;
  real p;
  
  // the hierarchical priors for variance and power level
  deck_pow_sd ~ gamma(2, 2);
  deck_pow ~ normal(0, deck_pow_sd);
  
  deck_var_mu ~ normal(0, 1);
  deck_var_sd ~ gamma(2, 2);
  deck_var ~ normal(deck_var_mu, deck_var_sd);
  
  // the covariance matrix with a customary lkj 2 prior
  O ~ lkj_corr(2);
  for(i in 1:N)
      A[i] ~ multi_normal(exp(deck_var), O);
  
  
  // the matchups are the real information
  for(i in 1:M){
      
      a = deck[i];
      b = vs[i];
      
      // this next line handles the (anti-)symmetry in the matchup matrix
      // it works, but there might be a better way
      // the coefficients in a should be doubled for interpretation
      
      p = deck_pow[a] - deck_pow[b] + A[a, b] - A[b, a];
      
      // at the core, this is still a binomial model
      won[i] ~ binomial_logit(n[i], p);
      
  }

}

generated quantities {

  // for each sample, i calculate the resulting matchup table as well
  // the sampler is complaining that the diagonal is unused but it makes the coding a lot easier
  // so i'll just ignore that

  real mu[N, N];
  
  for(i in 1:N){
      mu[i, i] = 0;
      for(j in (i+1):N){
          mu[i, j] = deck_pow[i] - deck_pow[j] + A[i, j] * exp(deck_var[i]) - A[j, i] * exp(deck_var[j]);
          mu[j, i] = - mu[i, j];
      }
  }
  
  mu = inv_logit(mu);
  
}

'''

sm = pystan.StanModel(model_code=model_code)
```

    INFO:pystan:COMPILING THE C++ CODE FOR MODEL anon_model_a42892281e798b6f383b477edb0346a4 NOW.
    /home/gijs/anaconda3/lib/python3.6/site-packages/Cython/Compiler/Main.py:367: FutureWarning: Cython directive 'language_level' not set, using 2 for now (Py2). This will change in a later release! File: /tmp/tmp04z9516d/stanfit4anon_model_a42892281e798b6f383b477edb0346a4_3118027449987977750.pyx
      tree = Parsing.p_module(s, pxd, full_module_name)


    CPU times: user 1.44 s, sys: 152 ms, total: 1.59 s
    Wall time: 1min 26s


In human language, these are the parameters of this model, 

* Each deck has a basic power level
* Each deck has some variance between the matchups, some decks may perform matchup dependent, others could be more stable
* There is a relation between matchups, so decks that do well against a specific deck, also do well together against another specific deck

The priors that I chose are weak. I have first developed the model without using any data, to see how the prior predictive distributions are. The data that I loaded is already clean and the conversion to a format that `pystan` wants is easy. I'm more used to using `rstan`, the well-developed interface from `R`, but it doesn't change much. Stan does use one-based indexing. 


```python
%%time

data = {
    "N": len(all_decks),
    "M": mu.shape[0],
    "deck": mu.deck.cat.codes.values + 1,
    "vs": mu.vs.cat.codes.values + 1,
    "won": mu.won.values,
    "n": (mu.lost + mu.won).values
}

fit = sm.sampling(data=data, n_jobs=1)
```

    WARNING:pystan:n_eff / iter for parameter O[1,1] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[1,1] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[2,2] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[3,3] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[4,4] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[5,5] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[6,6] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[7,7] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[8,8] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[9,9] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[10,10] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[11,11] is nan!
    WARNING:pystan:n_eff / iter for parameter mu[12,12] is nan!
    WARNING:pystan:n_eff / iter below 0.001 indicates that the effective sample size has likely been overestimated
    WARNING:pystan:Rhat for parameter O[1,1] is nan!
    WARNING:pystan:Rhat for parameter mu[1,1] is nan!
    WARNING:pystan:Rhat for parameter mu[2,2] is nan!
    WARNING:pystan:Rhat for parameter mu[3,3] is nan!
    WARNING:pystan:Rhat for parameter mu[4,4] is nan!
    WARNING:pystan:Rhat for parameter mu[5,5] is nan!
    WARNING:pystan:Rhat for parameter mu[6,6] is nan!
    WARNING:pystan:Rhat for parameter mu[7,7] is nan!
    WARNING:pystan:Rhat for parameter mu[8,8] is nan!
    WARNING:pystan:Rhat for parameter mu[9,9] is nan!
    WARNING:pystan:Rhat for parameter mu[10,10] is nan!
    WARNING:pystan:Rhat for parameter mu[11,11] is nan!
    WARNING:pystan:Rhat for parameter mu[12,12] is nan!
    WARNING:pystan:Rhat above 1.1 or below 0.9 indicates that the chains very likely have not mixed
    WARNING:pystan:132 of 4000 iterations ended with a divergence (3.3%).
    WARNING:pystan:Try running with adapt_delta larger than 0.8 to remove the divergences.
    WARNING:pystan:2 of 4000 iterations saturated the maximum tree depth of 10 (0.05%)
    WARNING:pystan:Run again with max_treedepth larger than 10 to avoid saturation


    CPU times: user 3min 33s, sys: 726 ms, total: 3min 34s
    Wall time: 3min 33s


The sampling is fast enough. There is a lot of complaining on the diagonal entries in the matchup table, which are unused actually. So those warnings are expected, but I will ignore them. 

Below you find the new estimates for all the matchups. I'm not an expert at all on the game of Magic, but these estimates look good to me. I should really do some predictive checks, but that is a good topic for another post. 

Thanks to the Stan sampler, I can show uncertainty estimates for all parameters. These are the 80% credibility intervals. This is really where the Bayesian approach shines I think, allowing us to work with little data (relative to the complexity of the model), and dealing with the uncertainty all the way. Most of the matchups are still quite uncertain, reflecting the fact that we do, indeed, do not have a lot of data. 


```python
matchups = fit.extract()['mu']
mup = pd.DataFrame(np.median(matchups, axis=0), index=all_decks, columns=all_decks)
plt.figure(figsize=(12, 10))
lower = np.quantile(matchups, .1, axis=0).ravel().tolist()
upper = np.quantile(matchups, .9, axis=0).ravel().tolist()
annot = [f"{l:.0%} - {u:.0%}" for l, u in zip(lower, upper)]
annot = np.array(annot).reshape(len(all_decks), -1)
plt.figure(figsize=(18, 10))
sns.heatmap(mup, annot=annot, fmt="", cmap=plt.get_cmap("bwr_r"));
```


    <Figure size 864x720 with 0 Axes>



    
![png](/assets/images/mtg-mup-stan_10_1.png)
    


You can compare the naive estimation with the above below. All estimates are pulled towards 50%. In the left image, attention is drawn towards the extreme values, but then I find myself asking all the time, on how many matchups is this data based? On the right, the extreme cases are the ones we know from the data to be extreme. The effect of the correlation between matchups is not very big, with all matchups without any data estimated to be somewhere between 48% and 52%. Here, I have shown the median estimate instead of the interval. 


```python
fig, axes = plt.subplots(1, 2, figsize=(18, 6))
sns.heatmap(naive_perc, annot=True, fmt=".0%", cmap=plt.get_cmap("bwr_r"), ax=axes[0]);
sns.heatmap(mup, annot=True, fmt=".0%", cmap=plt.get_cmap("bwr_r"), ax=axes[1]);
```


    
![png](/assets/images/mtg-mup-stan_12_0.png)
    


To round up this post, some plots of the other parameters in the model. First of, the covariances between the matchups. 

* Deck's that perform well against Death's Shadow, also work well against Izzet Phoenix. Conversely, decks that perform poorly against one of these tend to do bad against both. 
* Negative correlations also show up, for example, decks that do well against Dredge perform poorly against Infect, and vice-versa. 

These are some interesting observations, but, for the moment, they are not that impactful for the final estimates of the matchups above. The uncertainty around these estimates (not shown) is big, also including opposite signs at 80% credibility. 


```python
cov = fit.extract()['O']
cov_med = np.median(cov, axis=0)
np.fill_diagonal(cov_med, np.nan)

cov_df = pd.DataFrame(cov_med, index=all_decks, columns=all_decks)

plt.figure(figsize=(10, 10))
sns.heatmap(cov_df, annot=True, fmt=".2f", cmap=plt.get_cmap("bwr_r"));
```


    
![png](/assets/images/mtg-mup-stan_14_0.png)
    


The power level are included in the model, but they are not a big factor. There is not really a best deck overall, allthough _Dredge_ and _Green Tron_ are doing well in this field. 


```python
deck_pow = pd.DataFrame(fit.extract()['deck_pow'], columns=all_decks)
order = deck_pow.median(axis="rows").sort_values(ascending=False)
deck_pow.reindex(order.index, axis="columns").boxplot(figsize=(15, 5))
plt.title("Estimated power levels including uncertainty");
```


    
![png](/assets/images/mtg-mup-stan_16_0.png)
    


The variances for all the decks are almost in the same order of the power levels. This is actually a bit suspicious. It may indicate some bad parametrization in the model, that should be investigated more. 


```python
deck_var = pd.DataFrame(np.exp(fit.extract()['deck_var']), columns=all_decks)
order = deck_var.median(axis="rows").sort_values()
deck_var.reindex(order.index, axis="columns").boxplot(figsize=(15, 5))
plt.ylim((0, 2))
plt.title("Estimated variance in matchups including uncertainty");
```


    
![png](/assets/images/mtg-mup-stan_18_0.png)
    


## Conclusion

I have shown you a model, for estimating matchup percentages accross decks with limited data. There's more work to do from here, as there always is. I think, from my limited knowledge of the game, that the model could be improved by including player strengths. This is a competitive game of course, so a matchup isn't decided by the decks alone. It could be interesting to look for some conclusions on the skill vs. luck ratio in this game, perhaps even for specific matchups. Sideboarding effects, for those that know the game, are also interesting, and to learn about those it would be helpful to have not just the outcome of the whole match, but also of the underlying games (a match consists of three separate games, after the first of which you are allowed to change your deck a bit to tune for the matchup). 

My previous post was about simulating metagames based on matchups percentages, so in a follow-up, I'd like to combine these analyses into a prediction on the metagame shifts. One of the archetypes, _Ironworks_, is now actually banned from the game and it would be interesting to see how that will affect those predictions as well. 

### Full dataset

This analysis is based on these data. They are gathered from asking people that were playing on two recent high-level tournaments. 


```python
mu
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>deck</th>
      <th>vs</th>
      <th>won</th>
      <th>lost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>111</th>
      <td>Burn</td>
      <td>Dredge</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>42</th>
      <td>Burn</td>
      <td>Green Tron</td>
      <td>7</td>
      <td>6</td>
    </tr>
    <tr>
      <th>51</th>
      <td>Burn</td>
      <td>Hardened Scales</td>
      <td>5</td>
      <td>6</td>
    </tr>
    <tr>
      <th>121</th>
      <td>Burn</td>
      <td>Infect</td>
      <td>3</td>
      <td>1</td>
    </tr>
    <tr>
      <th>87</th>
      <td>Burn</td>
      <td>Jund</td>
      <td>0</td>
      <td>7</td>
    </tr>
    <tr>
      <th>41</th>
      <td>Burn</td>
      <td>Spirits</td>
      <td>12</td>
      <td>10</td>
    </tr>
    <tr>
      <th>109</th>
      <td>Death's Shadow</td>
      <td>Dredge</td>
      <td>0</td>
      <td>5</td>
    </tr>
    <tr>
      <th>72</th>
      <td>Death's Shadow</td>
      <td>Green Tron</td>
      <td>4</td>
      <td>10</td>
    </tr>
    <tr>
      <th>123</th>
      <td>Death's Shadow</td>
      <td>Infect</td>
      <td>4</td>
      <td>0</td>
    </tr>
    <tr>
      <th>79</th>
      <td>Death's Shadow</td>
      <td>Ironworks</td>
      <td>2</td>
      <td>5</td>
    </tr>
    <tr>
      <th>70</th>
      <td>Death's Shadow</td>
      <td>Spirits</td>
      <td>10</td>
      <td>15</td>
    </tr>
    <tr>
      <th>102</th>
      <td>Death's Shadow</td>
      <td>W/U Control</td>
      <td>2</td>
      <td>6</td>
    </tr>
    <tr>
      <th>115</th>
      <td>Dredge</td>
      <td>Ironworks</td>
      <td>2</td>
      <td>6</td>
    </tr>
    <tr>
      <th>108</th>
      <td>Dredge</td>
      <td>Izzet Phoenix</td>
      <td>7</td>
      <td>0</td>
    </tr>
    <tr>
      <th>113</th>
      <td>Dredge</td>
      <td>Spirits</td>
      <td>10</td>
      <td>14</td>
    </tr>
    <tr>
      <th>52</th>
      <td>Green Tron</td>
      <td>Hardened Scales</td>
      <td>10</td>
      <td>9</td>
    </tr>
    <tr>
      <th>99</th>
      <td>Green Tron</td>
      <td>Humans</td>
      <td>10</td>
      <td>6</td>
    </tr>
    <tr>
      <th>120</th>
      <td>Green Tron</td>
      <td>Infect</td>
      <td>7</td>
      <td>8</td>
    </tr>
    <tr>
      <th>81</th>
      <td>Green Tron</td>
      <td>Ironworks</td>
      <td>8</td>
      <td>8</td>
    </tr>
    <tr>
      <th>61</th>
      <td>Green Tron</td>
      <td>Izzet Phoenix</td>
      <td>10</td>
      <td>8</td>
    </tr>
    <tr>
      <th>92</th>
      <td>Green Tron</td>
      <td>Jund</td>
      <td>8</td>
      <td>4</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Green Tron</td>
      <td>Spirits</td>
      <td>19</td>
      <td>18</td>
    </tr>
    <tr>
      <th>98</th>
      <td>Hardened Scales</td>
      <td>Humans</td>
      <td>8</td>
      <td>3</td>
    </tr>
    <tr>
      <th>78</th>
      <td>Hardened Scales</td>
      <td>Ironworks</td>
      <td>3</td>
      <td>8</td>
    </tr>
    <tr>
      <th>62</th>
      <td>Hardened Scales</td>
      <td>Izzet Phoenix</td>
      <td>9</td>
      <td>6</td>
    </tr>
    <tr>
      <th>93</th>
      <td>Hardened Scales</td>
      <td>Jund</td>
      <td>3</td>
      <td>1</td>
    </tr>
    <tr>
      <th>49</th>
      <td>Hardened Scales</td>
      <td>Spirits</td>
      <td>19</td>
      <td>12</td>
    </tr>
    <tr>
      <th>104</th>
      <td>Hardened Scales</td>
      <td>W/U Control</td>
      <td>2</td>
      <td>5</td>
    </tr>
    <tr>
      <th>116</th>
      <td>Humans</td>
      <td>Infect</td>
      <td>0</td>
      <td>4</td>
    </tr>
    <tr>
      <th>96</th>
      <td>Humans</td>
      <td>Izzet Phoenix</td>
      <td>8</td>
      <td>5</td>
    </tr>
    <tr>
      <th>95</th>
      <td>Humans</td>
      <td>Jund</td>
      <td>4</td>
      <td>0</td>
    </tr>
    <tr>
      <th>97</th>
      <td>Humans</td>
      <td>Spirits</td>
      <td>8</td>
      <td>10</td>
    </tr>
    <tr>
      <th>118</th>
      <td>Infect</td>
      <td>Ironworks</td>
      <td>6</td>
      <td>2</td>
    </tr>
    <tr>
      <th>122</th>
      <td>Infect</td>
      <td>Izzet Phoenix</td>
      <td>1</td>
      <td>9</td>
    </tr>
    <tr>
      <th>119</th>
      <td>Infect</td>
      <td>Spirits</td>
      <td>11</td>
      <td>9</td>
    </tr>
    <tr>
      <th>82</th>
      <td>Ironworks</td>
      <td>Izzet Phoenix</td>
      <td>4</td>
      <td>6</td>
    </tr>
    <tr>
      <th>91</th>
      <td>Ironworks</td>
      <td>Jund</td>
      <td>6</td>
      <td>5</td>
    </tr>
    <tr>
      <th>83</th>
      <td>Ironworks</td>
      <td>Spirits</td>
      <td>9</td>
      <td>15</td>
    </tr>
    <tr>
      <th>103</th>
      <td>Ironworks</td>
      <td>W/U Control</td>
      <td>1</td>
      <td>3</td>
    </tr>
    <tr>
      <th>90</th>
      <td>Izzet Phoenix</td>
      <td>Jund</td>
      <td>4</td>
      <td>7</td>
    </tr>
    <tr>
      <th>59</th>
      <td>Izzet Phoenix</td>
      <td>Spirits</td>
      <td>20</td>
      <td>12</td>
    </tr>
    <tr>
      <th>107</th>
      <td>Jund</td>
      <td>W/U Control</td>
      <td>3</td>
      <td>1</td>
    </tr>
    <tr>
      <th>105</th>
      <td>Spirits</td>
      <td>W/U Control</td>
      <td>12</td>
      <td>6</td>
    </tr>
  </tbody>
</table>
</div>


