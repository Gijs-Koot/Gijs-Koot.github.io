---
layout: post
title:  "Birth data cleanup"
date:   2017-12-30 10:30:00 +0200
categories: statistics births overdispersion cleanup
---

_Work in progress_

In this post I clean up some data on daily birth numbers in the Netherlands and Belgium. 

* http://statline.cbs.nl/Statweb/publication/?DM=SLNL&PA=70703ned&D1=0&D2=a&HDR=T&STB=G1&VW=D
* http://statbel.fgov.be/nl/statistieken/opendata/datasets/bevolking/


```python
import pandas as pd

%pylab inline
```

    Populating the interactive namespace from numpy and matplotlib


* Worden er meer baby's geboren als de economie aantrekt?
* Hoe sterk is de clustering?


```python
daily_ned = pd.read_csv("./data/Bevolkingsontwikkeli_171217121849.csv", encoding="latin-1", delimiter=";").reset_index()
daily_ned.columns = ["datum", "geboortes"]
daily_ned.geboortes = pd.to_numeric(daily_ned.geboortes, errors = "coerce")
daily_ned.head(7)
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>datum</th>
      <th>geboortes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Onderwerpen</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Onderwerpen</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Perioden</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Totaal 1995</td>
      <td>190513.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Totaal januari 1995</td>
      <td>16436.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Zondag 1 januari 1995</td>
      <td>368.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Maandag 2 januari 1995</td>
      <td>439.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
daily_ned = daily_ned[~daily_ned.datum.str.lower().str.contains("totaal")].dropna()
daily_ned.geboortes = daily_ned.geboortes.astype(int)

daily_ned.sample(10)
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>datum</th>
      <th>geboortes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2808</th>
      <td>Zondag 14 april 2002</td>
      <td>431</td>
    </tr>
    <tr>
      <th>7801</th>
      <td>2015 maandag 30 maart</td>
      <td>482</td>
    </tr>
    <tr>
      <th>6429</th>
      <td>2011 vrijdag 9 september</td>
      <td>522</td>
    </tr>
    <tr>
      <th>6321</th>
      <td>2011 zaterdag 28 mei</td>
      <td>407</td>
    </tr>
    <tr>
      <th>5844</th>
      <td>Zondag   28-2-2010</td>
      <td>378</td>
    </tr>
    <tr>
      <th>5933</th>
      <td>Dinsdag    25-5-2010</td>
      <td>509</td>
    </tr>
    <tr>
      <th>4120</th>
      <td>Maandag 12 september 2005</td>
      <td>567</td>
    </tr>
    <tr>
      <th>5299</th>
      <td>Zaterdag 4 oktober 2008</td>
      <td>447</td>
    </tr>
    <tr>
      <th>7416</th>
      <td>2014 maandag 31 maart</td>
      <td>497</td>
    </tr>
    <tr>
      <th>2115</th>
      <td>Woensdag 28 juni 2000</td>
      <td>573</td>
    </tr>
  </tbody>
</table>
</div>




```python
fmt_yd = daily_ned.datum.str.extract("(?P<year>\d{4}) [a-z]{6,10} (?P<day>\d{1,2}) (?P<month_named>[a-z]{3,11})", expand = True).dropna()
fmt_yd[fmt_yd.any(axis = 1)].sample(5)
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>day</th>
      <th>month_named</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>6489</th>
      <td>2011</td>
      <td>6</td>
      <td>november</td>
    </tr>
    <tr>
      <th>7901</th>
      <td>2015</td>
      <td>8</td>
      <td>juli</td>
    </tr>
    <tr>
      <th>7612</th>
      <td>2014</td>
      <td>13</td>
      <td>oktober</td>
    </tr>
    <tr>
      <th>6474</th>
      <td>2011</td>
      <td>23</td>
      <td>oktober</td>
    </tr>
    <tr>
      <th>6222</th>
      <td>2011</td>
      <td>21</td>
      <td>februari</td>
    </tr>
  </tbody>
</table>
</div>




```python
months = fmt_yd.month_named.dropna().unique()
```


```python
fmt_yd["month"] = fmt_yd.dropna().month_named.astype('category').cat.reorder_categories(months).cat.codes + 1
fmt_yd.sample(5)
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>day</th>
      <th>month_named</th>
      <th>month</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>6632</th>
      <td>2012</td>
      <td>17</td>
      <td>maart</td>
      <td>3</td>
    </tr>
    <tr>
      <th>7480</th>
      <td>2014</td>
      <td>3</td>
      <td>juni</td>
      <td>6</td>
    </tr>
    <tr>
      <th>6653</th>
      <td>2012</td>
      <td>6</td>
      <td>april</td>
      <td>4</td>
    </tr>
    <tr>
      <th>7168</th>
      <td>2013</td>
      <td>16</td>
      <td>augustus</td>
      <td>8</td>
    </tr>
    <tr>
      <th>6852</th>
      <td>2012</td>
      <td>16</td>
      <td>oktober</td>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>



In an undocumented feature that I found through [GitHub](https://github.com/nps/pandas/commit/cb7cdaa20ef5af421344819232ee289b93e22e7f), it is possible to combine columns of parts of dates into a datetime64-series. 


```python
yd_dates = pd.to_datetime(fmt_yd.drop('month_named', axis = 1))
yd_dates.sample(5)
```




    7636   2014-11-06
    7126   2013-07-05
    7123   2013-07-02
    7050   2013-04-20
    6521   2011-12-07
    dtype: datetime64[ns]




```python
fmt_m = daily_ned.datum.str.extract("(?P<day>\d{1,2}) (?P<month_named>[a-z]{3,11}) ?(?P<year>\d{4})", expand = True).dropna()
fmt_m["month"] = fmt_m.month_named.astype('category').cat.reorder_categories(months).cat.codes + 1
m_dates = pd.to_datetime(fmt_m.drop('month_named', axis = 1))

m_dates.sample(5)
```




    2641   2001-11-11
    860    1997-03-24
    3173   2003-03-26
    2510   2001-07-07
    3340   2003-09-03
    dtype: datetime64[ns]




```python
num_dates = pd.to_datetime(daily_ned.datum, format = "%d-%m-%Y", exact = False, errors = "coerce").dropna()
num_dates.sample(5)
```




    6077   2010-10-11
    6018   2010-08-15
    5872   2010-03-27
    5428   2009-01-30
    5931   2010-05-23
    Name: datum, dtype: datetime64[ns]




```python
daily_ned = daily_ned.assign(date = pd.concat([yd_dates, m_dates, num_dates]))
daily_ned.sample(5)
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>datum</th>
      <th>geboortes</th>
      <th>date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1003</th>
      <td>Zaterdag 9 augustus 1997</td>
      <td>479</td>
      <td>1997-08-09</td>
    </tr>
    <tr>
      <th>7406</th>
      <td>2014 vrijdag 21 maart</td>
      <td>558</td>
      <td>2014-03-21</td>
    </tr>
    <tr>
      <th>6625</th>
      <td>2012 zaterdag 10 maart</td>
      <td>391</td>
      <td>2012-03-10</td>
    </tr>
    <tr>
      <th>3789</th>
      <td>Woensdag 3 november 2004</td>
      <td>545</td>
      <td>2004-11-03</td>
    </tr>
    <tr>
      <th>1469</th>
      <td>Dinsdag 27 oktober 1998</td>
      <td>575</td>
      <td>1998-10-27</td>
    </tr>
  </tbody>
</table>
</div>




```python
daily_ned[daily_ned.date.isnull()]
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>datum</th>
      <th>geboortes</th>
      <th>date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5783</th>
      <td>Overig</td>
      <td>243</td>
      <td>NaT</td>
    </tr>
    <tr>
      <th>6553</th>
      <td>Overig</td>
      <td>171</td>
      <td>NaT</td>
    </tr>
    <tr>
      <th>6940</th>
      <td>Overig</td>
      <td>131</td>
      <td>NaT</td>
    </tr>
    <tr>
      <th>7314</th>
      <td>Overig</td>
      <td>144</td>
      <td>NaT</td>
    </tr>
    <tr>
      <th>7700</th>
      <td>Overig</td>
      <td>229</td>
      <td>NaT</td>
    </tr>
    <tr>
      <th>8086</th>
      <td>Overig</td>
      <td>121</td>
      <td>NaT</td>
    </tr>
  </tbody>
</table>
</div>




```python
daily_ned.dropna().date.dt.year.value_counts().sort_index().to_frame()
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1995</th>
      <td>365</td>
    </tr>
    <tr>
      <th>1996</th>
      <td>366</td>
    </tr>
    <tr>
      <th>1997</th>
      <td>365</td>
    </tr>
    <tr>
      <th>1998</th>
      <td>365</td>
    </tr>
    <tr>
      <th>1999</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2000</th>
      <td>366</td>
    </tr>
    <tr>
      <th>2001</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2002</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2003</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2004</th>
      <td>366</td>
    </tr>
    <tr>
      <th>2005</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2006</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2007</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2008</th>
      <td>366</td>
    </tr>
    <tr>
      <th>2009</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>366</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>365</td>
    </tr>
    <tr>
      <th>2015</th>
      <td>365</td>
    </tr>
  </tbody>
</table>
</div>



Looks good!


```python
daily_ned[daily_ned.date.dt.year == 2015].set_index('date').geboortes.plot()
```




    <matplotlib.axes._subplots.AxesSubplot at 0x7f5eb80aa588>




![png](/assets/images/birth-clustering_16_1.png)

