---
layout: post
title:  "Swimming records cleanup and analysis"
date: 2018-1-16 10:30:00 +0200
categories: pandas swimming sports records
---
This is a tutorial in data cleanup using `pandas`. In one of my trainings, I asked the following questions. 


* Download the swimming data from https://en.wikipedia.org/wiki/List_of_world_records_in_swimming
* Combine the frames with the records and clean up the data
* Give a ranking of the swimming speed over different disciplines
* Save the clean data in a file called `swimming_records.feather`
* Give an estimate of how much time a turning point adds to swimming a distance
* Give an estimate of how much time a start adds to adds to swimming 

In this post, I try and answer these. 

---


```python
import pandas as pd

%pylab inline
```

    Populating the interactive namespace from numpy and matplotlib


### 1. Getting the data

These swimming records are in HTML tables, and luckily the `pd.read_html` function does work. 


```python
url = "https://en.wikipedia.org/wiki/List_of_world_records_in_swimming"

tables = pd.read_html(url, header = 0, encoding='utf-8')
tables[0].head(5)
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
      <th>Event</th>
      <th>Time</th>
      <th>Unnamed: 2</th>
      <th>Name</th>
      <th>Nationality</th>
      <th>Date</th>
      <th>Meet</th>
      <th>Location</th>
      <th>Ref</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01 ! 50 m freestyle</td>
      <td>20.91</td>
      <td>NaN</td>
      <td>Cielo, CésarCésar Cielo</td>
      <td>Brazil</td>
      <td>18 December 2009</td>
      <td>Brazilian Championships</td>
      <td>Brazil, São Paulo ! São Paulo, Brazil</td>
      <td>[9][10]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>02 ! 100 m freestyle</td>
      <td>46.91</td>
      <td>NaN</td>
      <td>Cielo, CésarCésar Cielo</td>
      <td>Brazil</td>
      <td>30 July 2009</td>
      <td>World Championships</td>
      <td>Italy, Rome ! Rome, Italy</td>
      <td>[11][12]</td>
    </tr>
    <tr>
      <th>2</th>
      <td>03 ! 200 m freestyle</td>
      <td>1:42.00</td>
      <td>NaN</td>
      <td>Biedermann, PaulPaul Biedermann</td>
      <td>Germany</td>
      <td>28 July 2009</td>
      <td>World Championships</td>
      <td>Italy, Rome ! Rome, Italy</td>
      <td>[13][14]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>04 ! 400 m freestyle</td>
      <td>3:40.07</td>
      <td>NaN</td>
      <td>Biedermann, PaulPaul Biedermann</td>
      <td>Germany</td>
      <td>26 July 2009</td>
      <td>World Championships</td>
      <td>Italy, Rome ! Rome, Italy</td>
      <td>[15][16]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>05 ! 800 m freestyle</td>
      <td>7:32.12</td>
      <td>NaN</td>
      <td>Zhang Lin</td>
      <td>China</td>
      <td>29 July 2009</td>
      <td>World Championships</td>
      <td>Italy, Rome ! Rome, Italy</td>
      <td>[17][18]</td>
    </tr>
  </tbody>
</table>
</div>



There are a few extra tables that we don't need. In addition, the tables refer to long course (50m bath) or short course. I use a `zip` to append that information and then combine all the records into a separate table. 


```python
category = "men", "women", "mixed", "men", "women", "mixed"
course = "long", "long", "long", "short", "short", "short"

record_tables = [t for t in tables if "Event" in t.columns]
len(record_tables)
```




    6




```python
ts = [t.assign(category = c, course = i) for t, c, i in zip(record_tables, category, course)]
raw = pd.concat(ts).reset_index(drop=True)
raw.sample(5)
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
      <th>Event</th>
      <th>Time</th>
      <th>Unnamed: 2</th>
      <th>Name</th>
      <th>Nationality</th>
      <th>Date</th>
      <th>Meet</th>
      <th>Location</th>
      <th>Ref</th>
      <th>category</th>
      <th>course</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>15</th>
      <td>16 ! 200 m individual medley</td>
      <td>1:54.00</td>
      <td>NaN</td>
      <td>Lochte, RyanRyan Lochte</td>
      <td>United States</td>
      <td>28 July 2011</td>
      <td>World Championships</td>
      <td>China, Shanghai ! Shanghai, China</td>
      <td>[34][35]</td>
      <td>men</td>
      <td>long</td>
    </tr>
    <tr>
      <th>2</th>
      <td>03 ! 200 m freestyle</td>
      <td>1:42.00</td>
      <td>NaN</td>
      <td>Biedermann, PaulPaul Biedermann</td>
      <td>Germany</td>
      <td>28 July 2009</td>
      <td>World Championships</td>
      <td>Italy, Rome ! Rome, Italy</td>
      <td>[13][14]</td>
      <td>men</td>
      <td>long</td>
    </tr>
    <tr>
      <th>49</th>
      <td>08 ! 100 m backstroke</td>
      <td>48.90</td>
      <td>NaN</td>
      <td>Kolesnikov, KlimentKliment Kolesnikov</td>
      <td>Russia</td>
      <td>22 December 2017</td>
      <td>Vladimir Salnikov Cup</td>
      <td>Russia, Saint Petersburg ! Saint Petersburg, R...</td>
      <td>[79]</td>
      <td>men</td>
      <td>short</td>
    </tr>
    <tr>
      <th>73</th>
      <td>08 ! 100 m backstroke</td>
      <td>55.03</td>
      <td>NaN</td>
      <td>Hosszú, KatinkaKatinka Hosszú</td>
      <td>Hungary</td>
      <td>4 December 2014</td>
      <td>World Championships</td>
      <td>Qatar, Doha ! Doha, Qatar</td>
      <td>[100]</td>
      <td>women</td>
      <td>short</td>
    </tr>
    <tr>
      <th>56</th>
      <td>15 ! 200 m butterfly</td>
      <td>1:48.56</td>
      <td>NaN</td>
      <td>le Clos, ChadChad le Clos</td>
      <td>South Africa</td>
      <td>5 November 2013</td>
      <td>World Cup</td>
      <td>Singapore, Singapore ! Singapore, Singapore</td>
      <td>[83]</td>
      <td>men</td>
      <td>short</td>
    </tr>
  </tbody>
</table>
</div>



First things first, I like to work with column names without spaces. There are two columns that are not useful to us, so I drop them immediately. 


```python
raw.shape
```




    (95, 11)




```python
raw.rename(columns = lambda x: x.lower().replace(' ', ''), inplace = True)
raw.drop(['ref', 'unnamed:2'], axis = 1, inplace = True, errors='ignore')
raw.head(2)
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
      <th>event</th>
      <th>time</th>
      <th>name</th>
      <th>nationality</th>
      <th>date</th>
      <th>meet</th>
      <th>location</th>
      <th>category</th>
      <th>course</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01 ! 50 m freestyle</td>
      <td>20.91</td>
      <td>Cielo, CésarCésar Cielo</td>
      <td>Brazil</td>
      <td>18 December 2009</td>
      <td>Brazilian Championships</td>
      <td>Brazil, São Paulo ! São Paulo, Brazil</td>
      <td>men</td>
      <td>long</td>
    </tr>
    <tr>
      <th>1</th>
      <td>02 ! 100 m freestyle</td>
      <td>46.91</td>
      <td>Cielo, CésarCésar Cielo</td>
      <td>Brazil</td>
      <td>30 July 2009</td>
      <td>World Championships</td>
      <td>Italy, Rome ! Rome, Italy</td>
      <td>men</td>
      <td>long</td>
    </tr>
  </tbody>
</table>
</div>



---

### 2. Parsing the data in the event and time columns 

The data has a lot of challenging parsing problems. In this post, I use regexes to solve most of those. There are non-breaking spaces, as you cannot see in the table, but it does show if you print separate values as below. There is also a weird `x` character, that you might mistake for an 'x'. I just copied it into the regex formula. 


```python
raw.event.values[0], raw.event.values[25], raw.event.values[17]
```




    ('01 ! 50\xa0m freestyle',
     '06 ! 1500\xa0m freestyle',
     '18 ! 4×100\xa0m freestyle relay')




```python
parsed_events = raw.event.str.replace(u'\xa0', ' ').str.extract('[\d\.]+ ! (?:(?P<team_size>4)×)?(?P<distance>\d{2,4}) m (?P<swimstyle>[a-z ]+)', expand = True)
parsed_events[parsed_events.swimstyle.isnull()]
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
      <th>team_size</th>
      <th>distance</th>
      <th>swimstyle</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>




```python
parsed_events["team_size"] = parsed_events.team_size.fillna(1).astype(int)
parsed_events.distance = parsed_events.distance.astype(int) * parsed_events.team_size

parsed_events.assign(original = raw.event).sample(5)
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
      <th>team_size</th>
      <th>distance</th>
      <th>swimstyle</th>
      <th>original</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>32</th>
      <td>1</td>
      <td>50</td>
      <td>butterfly</td>
      <td>13 ! 50 m butterfly</td>
    </tr>
    <tr>
      <th>60</th>
      <td>4</td>
      <td>200</td>
      <td>freestyle relay</td>
      <td>19.1 ! 4×50 m freestyle relay</td>
    </tr>
    <tr>
      <th>73</th>
      <td>1</td>
      <td>100</td>
      <td>backstroke</td>
      <td>08 ! 100 m backstroke</td>
    </tr>
    <tr>
      <th>23</th>
      <td>1</td>
      <td>400</td>
      <td>freestyle</td>
      <td>04 ! 400 m freestyle</td>
    </tr>
    <tr>
      <th>14</th>
      <td>1</td>
      <td>200</td>
      <td>butterfly</td>
      <td>15 ! 200 m butterfly</td>
    </tr>
  </tbody>
</table>
</div>



Next up are the times. It is possible to tackle these with `strftime`, but since I'm doing regexes already, let's use those again. 


```python
parsed_times = raw.time.str.extract("(?P<m>\d{1,2})?:?(?P<s>\d{2})\.(?P<ms>\d{2})", expand = True)
time_seconds = parsed_times.m.astype(float).fillna(0) * 60 + parsed_times.s.astype(float) + parsed_times.ms.astype(float) / 100
raw.assign(time_seconds = time_seconds)[["event", "time_seconds"]].sample(10)
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
      <th>event</th>
      <th>time_seconds</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>64</th>
      <td>22 ! 4×50 m medley relay</td>
      <td>90.44</td>
    </tr>
    <tr>
      <th>92</th>
      <td>23 ! 4×100 m medley relay</td>
      <td>225.20</td>
    </tr>
    <tr>
      <th>34</th>
      <td>15 ! 200 m butterfly</td>
      <td>121.81</td>
    </tr>
    <tr>
      <th>43</th>
      <td>02 ! 100 m freestyle</td>
      <td>44.94</td>
    </tr>
    <tr>
      <th>89</th>
      <td>21 ! 4×200 m freestyle relay</td>
      <td>452.85</td>
    </tr>
    <tr>
      <th>25</th>
      <td>06 ! 1500 m freestyle</td>
      <td>925.48</td>
    </tr>
    <tr>
      <th>20</th>
      <td>01 ! 50 m freestyle</td>
      <td>23.67</td>
    </tr>
    <tr>
      <th>18</th>
      <td>19 ! 4×200 m freestyle relay</td>
      <td>418.55</td>
    </tr>
    <tr>
      <th>50</th>
      <td>09 ! 200 m backstroke</td>
      <td>105.63</td>
    </tr>
    <tr>
      <th>72</th>
      <td>07 ! 50 m backstroke</td>
      <td>25.67</td>
    </tr>
  </tbody>
</table>
</div>



---

### 3. Splitting doubled name and location

The record holder names come out of the `html` in an interesting way. The `pd.read_html` function includes the title of the cell, which is the same name, in different order. Instead of splitting the strings on half their length plus one, I use a very explicit backref operator to make sure my assumptions on these data fields are correct. 


```python
raw.name.values[0], raw.name.values[10]
```




    ('Cielo, CésarCésar Cielo', 'Peaty, AdamAdam Peaty')




```python
## Two patterns. One works for most
## But names like Sun Yang are not repeated
## Maybe because it's a chinese character in the html that is ommitted by the parser?
parsed_names = raw.name.str.extract(r"(?P<last_name>[\w ]+), (?P<first_name>[\S ]+)\2 \1", expand = True)
parsed_names_simple = raw.name.str.extract(r"^(?P<last_name>[\w]+) (?P<first_name>[\w ]+)$", expand = True)

q = parsed_names.first_name.isnull() & parsed_names_simple.first_name.notnull()
parsed_names.loc[q] = parsed_names_simple.loc[q]

parsed_names.assign(original = raw.name).sample(10)
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
      <th>last_name</th>
      <th>first_name</th>
      <th>original</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>26</th>
      <td>Zhao</td>
      <td>Jing</td>
      <td>Zhao Jing</td>
    </tr>
    <tr>
      <th>45</th>
      <td>Agnel</td>
      <td>Yannick</td>
      <td>Agnel, YannickYannick Agnel</td>
    </tr>
    <tr>
      <th>36</th>
      <td>Hosszú</td>
      <td>Katinka</td>
      <td>Hosszú, KatinkaKatinka Hosszú</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Cielo</td>
      <td>César</td>
      <td>Cielo, CésarCésar Cielo</td>
    </tr>
    <tr>
      <th>69</th>
      <td>Belmonte García</td>
      <td>Mireia</td>
      <td>Belmonte García, MireiaMireia Belmonte García</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Sun</td>
      <td>Yang</td>
      <td>Sun Yang</td>
    </tr>
    <tr>
      <th>80</th>
      <td>Alshammar</td>
      <td>Therese</td>
      <td>Alshammar, ThereseTherese Alshammar</td>
    </tr>
    <tr>
      <th>50</th>
      <td>Larkin</td>
      <td>Mitch</td>
      <td>Larkin, MitchMitch Larkin</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Biedermann</td>
      <td>Paul</td>
      <td>Biedermann, PaulPaul Biedermann</td>
    </tr>
    <tr>
      <th>74</th>
      <td>Hosszú</td>
      <td>Katinka</td>
      <td>Hosszú, KatinkaKatinka Hosszú</td>
    </tr>
  </tbody>
</table>
</div>



These names look correct. For the teams, the medley records, I leave the names blank. Next up are the location fields. 


```python
raw.location.values[0], raw.location.values[17]
```




    ('Brazil, São Paulo ! São Paulo, Brazil', 'China, Beijing ! Beijing, China')




```python
parsed_locations = raw.location.str.extract(r'(?P<country>[\w ]+), (?P<city>[\w ]+) ! \2, \1', expand = True)
parsed_locations.assign(original = raw.location).sample(5)
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
      <th>country</th>
      <th>city</th>
      <th>original</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>66</th>
      <td>Germany</td>
      <td>Berlin</td>
      <td>Germany, Berlin ! Berlin, Germany</td>
    </tr>
    <tr>
      <th>42</th>
      <td>Qatar</td>
      <td>Doha</td>
      <td>Qatar, Doha ! Doha, Qatar</td>
    </tr>
    <tr>
      <th>74</th>
      <td>Qatar</td>
      <td>Doha</td>
      <td>Qatar, Doha ! Doha, Qatar</td>
    </tr>
    <tr>
      <th>48</th>
      <td>Qatar</td>
      <td>Doha</td>
      <td>Qatar, Doha ! Doha, Qatar</td>
    </tr>
    <tr>
      <th>37</th>
      <td>Brazil</td>
      <td>Rio de Janeiro</td>
      <td>Brazil, Rio de Janeiro ! Rio de Janeiro, Brazil</td>
    </tr>
  </tbody>
</table>
</div>




```python
## check whether the parsing succeeded for all the locations
parsed_locations[parsed_locations.country.isnull()]
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
      <th>country</th>
      <th>city</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



---

### 4. Combining the data into a clean set

We have all the separate parts of the dataset and assemble them into a `pd.DataFrame` called `events. 


```python
events = parsed_events.join(
    time_seconds.rename("time")
).join(
    pd.to_datetime(raw.date)
).join(parsed_locations).join(parsed_names).join(
    raw[["course", "category", "nationality", "meet"]]
)

events.sample(5)
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
      <th>team_size</th>
      <th>distance</th>
      <th>swimstyle</th>
      <th>time</th>
      <th>date</th>
      <th>country</th>
      <th>city</th>
      <th>last_name</th>
      <th>first_name</th>
      <th>course</th>
      <th>category</th>
      <th>nationality</th>
      <th>meet</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>86</th>
      <td>4</td>
      <td>200</td>
      <td>freestyle relay</td>
      <td>93.91</td>
      <td>2017-12-15</td>
      <td>Denmark</td>
      <td>Copenhagen</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>short</td>
      <td>women</td>
      <td>Netherlands</td>
      <td>European Championships</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1</td>
      <td>1500</td>
      <td>freestyle</td>
      <td>871.02</td>
      <td>2012-08-04</td>
      <td>United Kingdom</td>
      <td>London</td>
      <td>Sun</td>
      <td>Yang</td>
      <td>long</td>
      <td>men</td>
      <td>China</td>
      <td>Olympic Games</td>
    </tr>
    <tr>
      <th>57</th>
      <td>1</td>
      <td>100</td>
      <td>individual medley</td>
      <td>50.30</td>
      <td>2016-08-30</td>
      <td>Germany</td>
      <td>Berlin</td>
      <td>Morozov</td>
      <td>Vladimir</td>
      <td>short</td>
      <td>men</td>
      <td>Russia</td>
      <td>World Cup</td>
    </tr>
    <tr>
      <th>29</th>
      <td>1</td>
      <td>50</td>
      <td>breaststroke</td>
      <td>29.40</td>
      <td>2017-07-30</td>
      <td>Hungary</td>
      <td>Budapest</td>
      <td>King</td>
      <td>Lilly</td>
      <td>long</td>
      <td>women</td>
      <td>United States</td>
      <td>World Championships</td>
    </tr>
    <tr>
      <th>43</th>
      <td>1</td>
      <td>100</td>
      <td>freestyle</td>
      <td>44.94</td>
      <td>2008-12-13</td>
      <td>Croatia</td>
      <td>Rijeka</td>
      <td>Leveaux</td>
      <td>Amaury</td>
      <td>short</td>
      <td>men</td>
      <td>France</td>
      <td>European Championships</td>
    </tr>
  </tbody>
</table>
</div>




```python
events.dtypes
```




    team_size               int64
    distance                int64
    swimstyle              object
    time                  float64
    date           datetime64[ns]
    country                object
    city                   object
    last_name              object
    first_name             object
    course                 object
    category               object
    nationality            object
    meet                   object
    dtype: object



This looks fine. I'd like to use the `categorical` type in `pandas`, but it actually gives me some problems here, see https://github.com/pandas-dev/pandas/issues/19136 for example. Let's make some plots and the ranking of swimming speeds to check if this data looks allright. 


```python
import seaborn as sns

fig = plt.figure(figsize = (8, 6))
ax = fig.subplots(1)
pal = sns.color_palette()

for i, (st, frame) in enumerate(events.groupby(["swimstyle"])):
    frame.plot.scatter(x = 'time', y = 'distance', label = st, ax = ax, color = pal[i], s = 50, alpha = .4);
    
plt.title("Speed versus distance of swimming records")
plt.grid(True);
```


    
![png](/assets/images/swimming-records_27_0.png)
    



```python
import calendar
month_names = [calendar.month_name[i] for i in range(1, 13)]

events.date.dt.strftime("%B").value_counts().reindex(month_names).plot.bar(color = "steelblue")
plt.title("Number of records in swimming set in each month");
```


    
![png](/assets/images/swimming-records_28_0.png)
    


Interesting that most records are broken in December. My first hypothesis would be that this has to do with a recent tournament.

---

### 5. Ranking the disciplines on speed


```python
events["speed"] = events.distance / events.time
events.sort_values('speed', ascending = False).head()
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
      <th>team_size</th>
      <th>distance</th>
      <th>swimstyle</th>
      <th>time</th>
      <th>date</th>
      <th>country</th>
      <th>city</th>
      <th>last_name</th>
      <th>first_name</th>
      <th>course</th>
      <th>category</th>
      <th>nationality</th>
      <th>meet</th>
      <th>speed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>61</th>
      <td>4</td>
      <td>200</td>
      <td>freestyle relay</td>
      <td>80.77</td>
      <td>2008-12-14</td>
      <td>Croatia</td>
      <td>Rijeka</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>short</td>
      <td>men</td>
      <td>France</td>
      <td>European Championships</td>
      <td>2.476167</td>
    </tr>
    <tr>
      <th>42</th>
      <td>1</td>
      <td>50</td>
      <td>freestyle</td>
      <td>20.26</td>
      <td>2014-12-05</td>
      <td>Qatar</td>
      <td>Doha</td>
      <td>Manaudou</td>
      <td>Florent</td>
      <td>short</td>
      <td>men</td>
      <td>France</td>
      <td>World Championships</td>
      <td>2.467917</td>
    </tr>
    <tr>
      <th>60</th>
      <td>4</td>
      <td>200</td>
      <td>freestyle relay</td>
      <td>82.60</td>
      <td>2014-12-06</td>
      <td>Qatar</td>
      <td>Doha</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>short</td>
      <td>men</td>
      <td>Russia</td>
      <td>World Championships</td>
      <td>2.421308</td>
    </tr>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>50</td>
      <td>freestyle</td>
      <td>20.91</td>
      <td>2009-12-18</td>
      <td>Brazil</td>
      <td>São Paulo</td>
      <td>Cielo</td>
      <td>César</td>
      <td>long</td>
      <td>men</td>
      <td>Brazil</td>
      <td>Brazilian Championships</td>
      <td>2.391200</td>
    </tr>
    <tr>
      <th>54</th>
      <td>1</td>
      <td>50</td>
      <td>butterfly</td>
      <td>21.80</td>
      <td>2009-11-14</td>
      <td>Germany</td>
      <td>Berlin</td>
      <td>Deibler</td>
      <td>Steffen</td>
      <td>short</td>
      <td>men</td>
      <td>Germany</td>
      <td>World Cup</td>
      <td>2.293578</td>
    </tr>
  </tbody>
</table>
</div>




```python
events.sort_values('speed', ascending = False).tail()
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
      <th>team_size</th>
      <th>distance</th>
      <th>swimstyle</th>
      <th>time</th>
      <th>date</th>
      <th>country</th>
      <th>city</th>
      <th>last_name</th>
      <th>first_name</th>
      <th>course</th>
      <th>category</th>
      <th>nationality</th>
      <th>meet</th>
      <th>speed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>30</th>
      <td>1</td>
      <td>100</td>
      <td>breaststroke</td>
      <td>64.13</td>
      <td>2017-07-25</td>
      <td>Hungary</td>
      <td>Budapest</td>
      <td>King</td>
      <td>Lilly</td>
      <td>long</td>
      <td>women</td>
      <td>United States</td>
      <td>World Championships</td>
      <td>1.559333</td>
    </tr>
    <tr>
      <th>85</th>
      <td>1</td>
      <td>400</td>
      <td>individual medley</td>
      <td>258.94</td>
      <td>2017-08-12</td>
      <td>Netherlands</td>
      <td>Eindhoven</td>
      <td>Belmonte Garcia</td>
      <td>Mireia</td>
      <td>short</td>
      <td>women</td>
      <td>Spain</td>
      <td>World Cup</td>
      <td>1.544759</td>
    </tr>
    <tr>
      <th>36</th>
      <td>1</td>
      <td>400</td>
      <td>individual medley</td>
      <td>266.36</td>
      <td>2016-08-06</td>
      <td>Brazil</td>
      <td>Rio de Janeiro</td>
      <td>Hosszú</td>
      <td>Katinka</td>
      <td>long</td>
      <td>women</td>
      <td>Hungary</td>
      <td>Olympic Games</td>
      <td>1.501727</td>
    </tr>
    <tr>
      <th>79</th>
      <td>1</td>
      <td>200</td>
      <td>breaststroke</td>
      <td>134.57</td>
      <td>2009-12-18</td>
      <td>United Kingdom</td>
      <td>Manchester</td>
      <td>Soni</td>
      <td>Rebecca</td>
      <td>short</td>
      <td>women</td>
      <td>United States</td>
      <td>Duel in the Pool</td>
      <td>1.486215</td>
    </tr>
    <tr>
      <th>31</th>
      <td>1</td>
      <td>200</td>
      <td>breaststroke</td>
      <td>139.11</td>
      <td>2013-08-01</td>
      <td>Spain</td>
      <td>Barcelona</td>
      <td>Pedersen</td>
      <td>Rikke Møller</td>
      <td>long</td>
      <td>women</td>
      <td>Denmark</td>
      <td>World Championships</td>
      <td>1.437711</td>
    </tr>
  </tbody>
</table>
</div>



The fastest discipline is the 4 times 50 freestyle relay. That's interesting because that would mean that the split times on this have to be faster than the world record, at least for one. Another aspect to keep in mind is that some records are listed twice, I assume because of the records that were broken with the floating suits that came up some time ago, and were banned afterwards.  

The slowest discipline is the breaststroke, that makes sense. Apparently, there is no breaststroke 400m record. Also, from the table below, we can see quite clearly that short course is faster than long course. 


```python
events.loc[events.swimstyle == "breaststroke", ["distance", "swimstyle", "speed", "time", "category", "course"]].sort_values('speed')
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
      <th>distance</th>
      <th>swimstyle</th>
      <th>speed</th>
      <th>time</th>
      <th>category</th>
      <th>course</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>31</th>
      <td>200</td>
      <td>breaststroke</td>
      <td>1.437711</td>
      <td>139.11</td>
      <td>women</td>
      <td>long</td>
    </tr>
    <tr>
      <th>79</th>
      <td>200</td>
      <td>breaststroke</td>
      <td>1.486215</td>
      <td>134.57</td>
      <td>women</td>
      <td>short</td>
    </tr>
    <tr>
      <th>30</th>
      <td>100</td>
      <td>breaststroke</td>
      <td>1.559333</td>
      <td>64.13</td>
      <td>women</td>
      <td>long</td>
    </tr>
    <tr>
      <th>11</th>
      <td>200</td>
      <td>breaststroke</td>
      <td>1.578906</td>
      <td>126.67</td>
      <td>men</td>
      <td>long</td>
    </tr>
    <tr>
      <th>76</th>
      <td>100</td>
      <td>breaststroke</td>
      <td>1.603592</td>
      <td>62.36</td>
      <td>women</td>
      <td>short</td>
    </tr>
    <tr>
      <th>77</th>
      <td>100</td>
      <td>breaststroke</td>
      <td>1.603592</td>
      <td>62.36</td>
      <td>women</td>
      <td>short</td>
    </tr>
    <tr>
      <th>78</th>
      <td>100</td>
      <td>breaststroke</td>
      <td>1.603592</td>
      <td>62.36</td>
      <td>women</td>
      <td>short</td>
    </tr>
    <tr>
      <th>53</th>
      <td>200</td>
      <td>breaststroke</td>
      <td>1.660578</td>
      <td>120.44</td>
      <td>men</td>
      <td>short</td>
    </tr>
    <tr>
      <th>29</th>
      <td>50</td>
      <td>breaststroke</td>
      <td>1.700680</td>
      <td>29.40</td>
      <td>women</td>
      <td>long</td>
    </tr>
    <tr>
      <th>75</th>
      <td>50</td>
      <td>breaststroke</td>
      <td>1.745810</td>
      <td>28.64</td>
      <td>women</td>
      <td>short</td>
    </tr>
    <tr>
      <th>10</th>
      <td>100</td>
      <td>breaststroke</td>
      <td>1.750394</td>
      <td>57.13</td>
      <td>men</td>
      <td>long</td>
    </tr>
    <tr>
      <th>52</th>
      <td>100</td>
      <td>breaststroke</td>
      <td>1.798238</td>
      <td>55.61</td>
      <td>men</td>
      <td>short</td>
    </tr>
    <tr>
      <th>9</th>
      <td>50</td>
      <td>breaststroke</td>
      <td>1.926782</td>
      <td>25.95</td>
      <td>men</td>
      <td>long</td>
    </tr>
    <tr>
      <th>51</th>
      <td>50</td>
      <td>breaststroke</td>
      <td>1.980198</td>
      <td>25.25</td>
      <td>men</td>
      <td>short</td>
    </tr>
  </tbody>
</table>
</div>




```python
events.to_feather("./data/swimming-records.feather")
```

Now that we have the data in what looks like a clean format, it is time to turn to the two other questions. 

---

### 6.  Give an estimate of how much time a turning point adds to swimming a distance

For calculating the extra time a turn adds, I use a pivot table. The idea is that I can only really compare the same distances and swimming styles. 


```python
view = events.pivot_table(index=["distance", "swimstyle", "category"], columns='course', values='time').reset_index()
view.sample(5)
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
      <th>course</th>
      <th>distance</th>
      <th>swimstyle</th>
      <th>category</th>
      <th>long</th>
      <th>short</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>46</th>
      <td>800</td>
      <td>freestyle relay</td>
      <td>men</td>
      <td>418.55</td>
      <td>409.04</td>
    </tr>
    <tr>
      <th>37</th>
      <td>400</td>
      <td>freestyle relay</td>
      <td>mixed</td>
      <td>199.60</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>13</th>
      <td>100</td>
      <td>butterfly</td>
      <td>women</td>
      <td>55.48</td>
      <td>54.61</td>
    </tr>
    <tr>
      <th>32</th>
      <td>200</td>
      <td>medley relay</td>
      <td>mixed</td>
      <td>NaN</td>
      <td>97.17</td>
    </tr>
    <tr>
      <th>48</th>
      <td>1500</td>
      <td>freestyle</td>
      <td>men</td>
      <td>871.02</td>
      <td>848.06</td>
    </tr>
  </tbody>
</table>
</div>




```python
view["additional_turnpoints"] = ((view.distance / 25) - 1) - ((view.distance / 50) - 1)
view["additional_time_per_turn"] = (view.short - view.long) / (view.additional_turnpoints)

view = view[~view.swimstyle.str.contains('relay')].copy()
view.sample(5)
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
      <th>course</th>
      <th>distance</th>
      <th>swimstyle</th>
      <th>category</th>
      <th>long</th>
      <th>short</th>
      <th>additional_turnpoints</th>
      <th>additional_time_per_turn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>23</th>
      <td>200</td>
      <td>butterfly</td>
      <td>women</td>
      <td>121.81</td>
      <td>119.61</td>
      <td>4.0</td>
      <td>-0.5500</td>
    </tr>
    <tr>
      <th>10</th>
      <td>100</td>
      <td>breaststroke</td>
      <td>men</td>
      <td>57.13</td>
      <td>55.61</td>
      <td>2.0</td>
      <td>-0.7600</td>
    </tr>
    <tr>
      <th>40</th>
      <td>400</td>
      <td>individual medley</td>
      <td>women</td>
      <td>266.36</td>
      <td>258.94</td>
      <td>8.0</td>
      <td>-0.9275</td>
    </tr>
    <tr>
      <th>18</th>
      <td>200</td>
      <td>backstroke</td>
      <td>men</td>
      <td>111.92</td>
      <td>105.63</td>
      <td>4.0</td>
      <td>-1.5725</td>
    </tr>
    <tr>
      <th>34</th>
      <td>400</td>
      <td>freestyle</td>
      <td>men</td>
      <td>220.07</td>
      <td>212.25</td>
      <td>8.0</td>
      <td>-0.9775</td>
    </tr>
  </tbody>
</table>
</div>



Instead of averaging this, I will create a visualization that shows the differences in each discipline. 


```python
pal = sns.color_palette()

def plot_cat(category, ax):
    for i, (style, frame) in enumerate(view.groupby("swimstyle")):
        frame.plot.scatter(x = "additional_time_per_turn", y = "distance", ax = ax, label = style, c = pal[i]);
    
fig, axes = plt.subplots(1, 2, figsize = (10, 4))

for cat, ax in zip(["women", "men"], axes):
    plot_cat(cat, ax)
```


    
![png](/assets/images/swimming-records_39_0.png)
    


It's just a bit painful to fix this in `pandas` / `matplotlib`. I like to use `ggplot` for this, switch to `R`, but for this post I'll give `plotnine` a try.


```python
import plotnine as pn

fig = pn.ggplot(view[view.category != "mixed"].dropna()) + \
    pn.geom_jitter(
        pn.aes(x = "factor(distance)", y = "additional_time_per_turn", color = "swimstyle"), 
        width = .1, height = 0) + \
    pn.facet_wrap(facets = "category") + \
    pn.labs(
        x = "Distance", 
        y = "Average additional time for each turn (s)",
        title = "How long does it take to turn around in swimming?")
    
fig.draw();
```

    /home/gijsx/anaconda3/lib/python3.6/site-packages/statsmodels/compat/pandas.py:56: FutureWarning: The pandas.core.datetools module is deprecated and will be removed in a future version. Please use the pandas.tseries module instead.
      from pandas.core import datetools



    
![png](/assets/images/swimming-records_41_1.png)
    


`plotnine` works fine. I don't like the distance on the x axis. Below I've created one with speed, which is also not ideal. But we can see how long a turn takes. 


```python
fig = pn.ggplot(view[view.category != "mixed"].dropna().assign(long_speed = view.distance / view.long)) + \
    pn.geom_point(pn.aes(x = "long_speed", y = "additional_time_per_turn", color = "swimstyle")) + \
    pn.facet_wrap(facets = "category") + \
    pn.labs(
        x = "Record speed on long course (m/s)", 
        y = "Average additional time for each turn (s)",
        title = "How long does it take to turn around in swimming?")
    
fig.draw();
```


    
![png](/assets/images/swimming-records_43_0.png)
    


We can see that a turn doesn't really take time, it's actually quicker than swimming. The difference between long and short course seems larger for backstroke. The turn in the butterfly style isn't too quick, perhaps because it's a tricky technique, or because the butterfly is already quite quick? On longer distances, the advantage of the turns disappears a bit. 

I'll consider this question answered, allthough there is much more to be said. The most important critique that I can come up with here is that it's perhaps not the best idea to answer this question using records. These are weird cases, and with more data, old records or just data from many swimming tournaments, we could produce a much more reliable estimate. 

### 7. Give an estimate of how much time a start adds to adds to swimming 

Now onto the next question; how long does a start take? This is tricky because we cannot really isolate the starts from the data, since each record has exactly one start. You could say 100m equals 2 x 50m without the extra start, but the swimming speeds are also different. I think I'd need some physical model to estimate speed from this data, and then use that in the equation. 

Interesting. Hopefully I can do that some other time. For now, I'll just use the simplified idea. 


```python
view = pd.concat([events.assign(doubled = "real"), events.assign(time = events.time * 2, distance = events.distance * 2, doubled = "hypothetical")])
view = view[["distance", "swimstyle", "doubled", "category", "course", "time"]].copy()
view = view.pivot_table(index=["distance", "swimstyle", "category", "course"], values="time", columns="doubled").dropna().reset_index()
view["difference"] = view.real - view.hypothetical
view.sample(5)
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
      <th>doubled</th>
      <th>distance</th>
      <th>swimstyle</th>
      <th>category</th>
      <th>course</th>
      <th>hypothetical</th>
      <th>real</th>
      <th>difference</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>42</th>
      <td>400</td>
      <td>individual medley</td>
      <td>women</td>
      <td>long</td>
      <td>252.24</td>
      <td>266.36</td>
      <td>14.12</td>
    </tr>
    <tr>
      <th>51</th>
      <td>800</td>
      <td>freestyle relay</td>
      <td>men</td>
      <td>short</td>
      <td>366.60</td>
      <td>409.04</td>
      <td>42.44</td>
    </tr>
    <tr>
      <th>27</th>
      <td>200</td>
      <td>butterfly</td>
      <td>women</td>
      <td>short</td>
      <td>109.22</td>
      <td>119.61</td>
      <td>10.39</td>
    </tr>
    <tr>
      <th>24</th>
      <td>200</td>
      <td>butterfly</td>
      <td>men</td>
      <td>long</td>
      <td>99.64</td>
      <td>111.51</td>
      <td>11.87</td>
    </tr>
    <tr>
      <th>26</th>
      <td>200</td>
      <td>butterfly</td>
      <td>women</td>
      <td>long</td>
      <td>110.96</td>
      <td>121.81</td>
      <td>10.85</td>
    </tr>
  </tbody>
</table>
</div>




```python
q = (view.category != "mixed") & ~view.swimstyle.str.contains("relay")

fig = pn.ggplot(view[q].dropna()) + \
    pn.geom_jitter(
        pn.aes(x = "factor(distance)", y = "difference", color = "swimstyle", shape = "course"),
        width = .1, height = 0) + \
    pn.facet_wrap(facets = "category") + \
    pn.labs(
        x = "Distance", 
        y = "Difference (s)",
        title = "Time difference between record and twice that record on half the distance")
    
fig.draw();
```


    
![png](/assets/images/swimming-records_46_0.png)
    


Well, the start doesn't save more than a couple of seconds, but it's hard to say more. These difference are mainly fatigue of the swimmer. 

I do see some other interesting patterns. It seems the record for freestyle 400m, for men, on a long course, is not  as sharp as it could be. Also the male records on 100m butterfly are quite fast compared to the 200m records. 

### 8. Conclusion

The data is cleaned. We have an idea of how long a turn takes, or rather, how much time it saves. I haven't come up with an easy method to isolate the starting times. The clean data can be found on GitHub if you want to give this a try, or perhaps you want to have a look at one of these other open questions:

* Why are the records posted mainly in June, July, November and December?
* How does the time saved with a turn differ across swimmers, for example world records vs. professionals vs. amateurs?
* How can we make a model that predicts the next record to be set?
