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


```python
import pandas as pd

%pylab inline
```

    Populating the interactive namespace from numpy and matplotlib


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
      <th>26</th>
      <td>07 ! 50 m backstroke</td>
      <td>27.06</td>
      <td>NaN</td>
      <td>Zhao Jing</td>
      <td>China</td>
      <td>30 July 2009</td>
      <td>World Championships</td>
      <td>Italy, Rome ! Rome, Italy</td>
      <td>[51][52]</td>
      <td>women</td>
      <td>long</td>
    </tr>
    <tr>
      <th>59</th>
      <td>18 ! 400 m individual medley</td>
      <td>3:55.50</td>
      <td>NaN</td>
      <td>Lochte, RyanRyan Lochte</td>
      <td>United States</td>
      <td>16 December 2010</td>
      <td>World Championships</td>
      <td>United Arab Emirates, Dubai ! Dubai, United Ar...</td>
      <td>[86]</td>
      <td>men</td>
      <td>short</td>
    </tr>
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
      <th>42</th>
      <td>01 ! 50 m freestyle</td>
      <td>20.26</td>
      <td>NaN</td>
      <td>Manaudou, FlorentFlorent Manaudou</td>
      <td>France</td>
      <td>5 December 2014</td>
      <td>World Championships</td>
      <td>Qatar, Doha ! Doha, Qatar</td>
      <td>[69]</td>
      <td>men</td>
      <td>short</td>
    </tr>
    <tr>
      <th>90</th>
      <td>22.1 ! 4×50 m medley relay</td>
      <td>1:43.27</td>
      <td>NaN</td>
      <td>(26.12) Alexandra Margaret de Loof  (28.78) Li...</td>
      <td>United States</td>
      <td>7 December 2016</td>
      <td>World Championships</td>
      <td>Canada, Windsor ! Windsor, Canada</td>
      <td>[116]</td>
      <td>women</td>
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
      <th>44</th>
      <td>1</td>
      <td>200</td>
      <td>freestyle</td>
      <td>03 ! 200 m freestyle</td>
    </tr>
    <tr>
      <th>9</th>
      <td>1</td>
      <td>50</td>
      <td>breaststroke</td>
      <td>10 ! 50 m breaststroke</td>
    </tr>
    <tr>
      <th>55</th>
      <td>1</td>
      <td>100</td>
      <td>butterfly</td>
      <td>14 ! 100 m butterfly</td>
    </tr>
    <tr>
      <th>24</th>
      <td>1</td>
      <td>800</td>
      <td>freestyle</td>
      <td>05 ! 800 m freestyle</td>
    </tr>
    <tr>
      <th>49</th>
      <td>1</td>
      <td>100</td>
      <td>backstroke</td>
      <td>08 ! 100 m backstroke</td>
    </tr>
  </tbody>
</table>
</div>



Next up are the times. It is possible to tackle these with `strftime` of some sort, but since the format is flexible, and I'm doing regexes already, let's use those again. 


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
      <th>11</th>
      <td>12 ! 200 m breaststroke</td>
      <td>126.67</td>
    </tr>
    <tr>
      <th>8</th>
      <td>09 ! 200 m backstroke</td>
      <td>111.92</td>
    </tr>
    <tr>
      <th>14</th>
      <td>15 ! 200 m butterfly</td>
      <td>111.51</td>
    </tr>
    <tr>
      <th>10</th>
      <td>11 ! 100 m breaststroke</td>
      <td>57.13</td>
    </tr>
    <tr>
      <th>89</th>
      <td>21 ! 4×200 m freestyle relay</td>
      <td>452.85</td>
    </tr>
    <tr>
      <th>84</th>
      <td>17 ! 200 m individual medley</td>
      <td>121.86</td>
    </tr>
    <tr>
      <th>33</th>
      <td>14 ! 100 m butterfly</td>
      <td>55.48</td>
    </tr>
    <tr>
      <th>81</th>
      <td>14 ! 100 m butterfly</td>
      <td>54.61</td>
    </tr>
    <tr>
      <th>76</th>
      <td>11.1 ! 100 m breaststroke</td>
      <td>62.36</td>
    </tr>
    <tr>
      <th>82</th>
      <td>15 ! 200 m butterfly</td>
      <td>119.61</td>
    </tr>
  </tbody>
</table>
</div>



## Splitting doubled name and location

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
      <th>72</th>
      <td>Medeiros</td>
      <td>Etiene</td>
      <td>Medeiros, EtieneEtiene Medeiros</td>
    </tr>
    <tr>
      <th>59</th>
      <td>Lochte</td>
      <td>Ryan</td>
      <td>Lochte, RyanRyan Lochte</td>
    </tr>
    <tr>
      <th>46</th>
      <td>Hackett</td>
      <td>Grant</td>
      <td>Hackett, GrantGrant Hackett</td>
    </tr>
    <tr>
      <th>77</th>
      <td>Atkinson</td>
      <td>Alia</td>
      <td>Atkinson, AliaAlia Atkinson</td>
    </tr>
    <tr>
      <th>89</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>(1:54.73) Inge Dekker  (1:51.22) Femke Heemske...</td>
    </tr>
    <tr>
      <th>29</th>
      <td>King</td>
      <td>Lilly</td>
      <td>King, LillyLilly King</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Ledecky</td>
      <td>Katie</td>
      <td>Ledecky, KatieKatie Ledecky</td>
    </tr>
    <tr>
      <th>31</th>
      <td>Pedersen</td>
      <td>Rikke Møller</td>
      <td>Pedersen, Rikke MøllerRikke Møller Pedersen</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Phelps</td>
      <td>Michael</td>
      <td>Phelps, MichaelMichael Phelps</td>
    </tr>
    <tr>
      <th>56</th>
      <td>le Clos</td>
      <td>Chad</td>
      <td>le Clos, ChadChad le Clos</td>
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
      <th>46</th>
      <td>Australia</td>
      <td>Melbourne</td>
      <td>Australia, Melbourne ! Melbourne, Australia</td>
    </tr>
    <tr>
      <th>52</th>
      <td>Germany</td>
      <td>Berlin</td>
      <td>Germany, Berlin ! Berlin, Germany</td>
    </tr>
    <tr>
      <th>86</th>
      <td>Denmark</td>
      <td>Copenhagen</td>
      <td>Denmark, Copenhagen ! Copenhagen, Denmark</td>
    </tr>
    <tr>
      <th>72</th>
      <td>Qatar</td>
      <td>Doha</td>
      <td>Qatar, Doha ! Doha, Qatar</td>
    </tr>
    <tr>
      <th>55</th>
      <td>Canada</td>
      <td>Windsor</td>
      <td>Canada, Windsor ! Windsor, Canada</td>
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



We have all the separate parts of the dataset and assemble them into a `pd.DataFrame` called `events. 


```python
events = parsed_events.join(
    time_seconds.rename("time")
).join(
    pd.to_datetime(raw.date)
).join(parsed_locations).join(parsed_names).join(
    raw[["course", "category", "nationality", "meet"]]
)

view = events.sample(10)
view
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
      <th>20</th>
      <td>1</td>
      <td>50</td>
      <td>freestyle</td>
      <td>23.67</td>
      <td>2017-07-29</td>
      <td>Hungary</td>
      <td>Budapest</td>
      <td>Sjöström</td>
      <td>Sarah</td>
      <td>long</td>
      <td>women</td>
      <td>Sweden</td>
      <td>World Championships</td>
    </tr>
    <tr>
      <th>11</th>
      <td>1</td>
      <td>200</td>
      <td>breaststroke</td>
      <td>126.67</td>
      <td>2017-01-29</td>
      <td>Japan</td>
      <td>Tokyo</td>
      <td>Watanabe</td>
      <td>Ippei</td>
      <td>long</td>
      <td>men</td>
      <td>Japan</td>
      <td>Kosuke Kitajima Cup</td>
    </tr>
    <tr>
      <th>56</th>
      <td>1</td>
      <td>200</td>
      <td>butterfly</td>
      <td>108.56</td>
      <td>2013-11-05</td>
      <td>Singapore</td>
      <td>Singapore</td>
      <td>le Clos</td>
      <td>Chad</td>
      <td>short</td>
      <td>men</td>
      <td>South Africa</td>
      <td>World Cup</td>
    </tr>
    <tr>
      <th>68</th>
      <td>1</td>
      <td>200</td>
      <td>freestyle</td>
      <td>110.43</td>
      <td>2017-08-12</td>
      <td>Netherlands</td>
      <td>Eindhoven</td>
      <td>Sjöström</td>
      <td>Sarah</td>
      <td>short</td>
      <td>women</td>
      <td>Sweden</td>
      <td>World Cup</td>
    </tr>
    <tr>
      <th>90</th>
      <td>4</td>
      <td>200</td>
      <td>medley relay</td>
      <td>103.27</td>
      <td>2016-12-07</td>
      <td>Canada</td>
      <td>Windsor</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>short</td>
      <td>women</td>
      <td>United States</td>
      <td>World Championships</td>
    </tr>
    <tr>
      <th>13</th>
      <td>1</td>
      <td>100</td>
      <td>butterfly</td>
      <td>49.82</td>
      <td>2009-08-01</td>
      <td>Italy</td>
      <td>Rome</td>
      <td>Phelps</td>
      <td>Michael</td>
      <td>long</td>
      <td>men</td>
      <td>United States</td>
      <td>World Championships</td>
    </tr>
    <tr>
      <th>63</th>
      <td>4</td>
      <td>800</td>
      <td>freestyle relay</td>
      <td>409.04</td>
      <td>2010-12-16</td>
      <td>United Arab Emirates</td>
      <td>Dubai</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>short</td>
      <td>men</td>
      <td>Russia</td>
      <td>World Championships</td>
    </tr>
    <tr>
      <th>51</th>
      <td>1</td>
      <td>50</td>
      <td>breaststroke</td>
      <td>25.25</td>
      <td>2009-11-14</td>
      <td>Germany</td>
      <td>Berlin</td>
      <td>van der Burgh</td>
      <td>Cameron</td>
      <td>short</td>
      <td>men</td>
      <td>South Africa</td>
      <td>World Cup</td>
    </tr>
    <tr>
      <th>87</th>
      <td>4</td>
      <td>200</td>
      <td>freestyle relay</td>
      <td>93.25</td>
      <td>2009-12-11</td>
      <td>Turkey</td>
      <td>Istanbul</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>short</td>
      <td>women</td>
      <td>Netherlands</td>
      <td>European Championships</td>
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

## Part 2: Analysis

* Give an estimate of how much time a turning point adds to swimming a distance
* Give an estimate of how much time a start adds to adds to swimming 

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
      <th>16</th>
      <td>100</td>
      <td>individual medley</td>
      <td>men</td>
      <td>NaN</td>
      <td>50.30</td>
    </tr>
    <tr>
      <th>29</th>
      <td>200</td>
      <td>individual medley</td>
      <td>men</td>
      <td>114.00</td>
      <td>109.63</td>
    </tr>
    <tr>
      <th>44</th>
      <td>800</td>
      <td>freestyle</td>
      <td>men</td>
      <td>452.12</td>
      <td>443.42</td>
    </tr>
    <tr>
      <th>28</th>
      <td>200</td>
      <td>freestyle relay</td>
      <td>women</td>
      <td>NaN</td>
      <td>93.58</td>
    </tr>
    <tr>
      <th>13</th>
      <td>100</td>
      <td>butterfly</td>
      <td>women</td>
      <td>55.48</td>
      <td>54.61</td>
    </tr>
  </tbody>
</table>
</div>




```python
view["additional_turnpoints"] = ((view.distance / 25) - 1) - ((view.distance / 50) - 1)
view["additional_time_per_turn"] = (view.short - view.long) / (view.additional_turnpoints)
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
      <th>1</th>
      <td>50</td>
      <td>backstroke</td>
      <td>women</td>
      <td>27.06</td>
      <td>25.67</td>
      <td>1.0</td>
      <td>-1.390</td>
    </tr>
    <tr>
      <th>9</th>
      <td>100</td>
      <td>backstroke</td>
      <td>women</td>
      <td>58.10</td>
      <td>55.03</td>
      <td>2.0</td>
      <td>-1.535</td>
    </tr>
    <tr>
      <th>4</th>
      <td>50</td>
      <td>butterfly</td>
      <td>men</td>
      <td>22.43</td>
      <td>21.80</td>
      <td>1.0</td>
      <td>-0.630</td>
    </tr>
    <tr>
      <th>10</th>
      <td>100</td>
      <td>breaststroke</td>
      <td>men</td>
      <td>57.13</td>
      <td>55.61</td>
      <td>2.0</td>
      <td>-0.760</td>
    </tr>
    <tr>
      <th>30</th>
      <td>200</td>
      <td>individual medley</td>
      <td>women</td>
      <td>126.12</td>
      <td>121.86</td>
      <td>4.0</td>
      <td>-1.065</td>
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
    pn.geom_point(pn.aes(x = "distance", y = "additional_time_per_turn", color = "swimstyle")) + \
    pn.facet_wrap(facets = "category") + \
    pn.labs(
        x = "Distance", 
        y = "Average additional time for each turn (s)",
        title = "How long does it take to turn around in swimming?")
    
fig.draw();
```


![png](/assets/images/swimming-records_41_0.png)


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

Now onto the next question; how long does a start take? This is kind of tricky because we cannot really isolate the starts from the data, since each record has exactly one start. You could say 100m equals 2 x 50m without the extra start, but the swimming speeds are also different. I think I'd need some physical model to estimate speed from this data, and then use that in the equation. 

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
      <th>33</th>
      <td>200</td>
      <td>individual medley</td>
      <td>women</td>
      <td>short</td>
      <td>113.02</td>
      <td>121.86</td>
      <td>8.84</td>
    </tr>
    <tr>
      <th>3</th>
      <td>100</td>
      <td>backstroke</td>
      <td>women</td>
      <td>short</td>
      <td>51.34</td>
      <td>55.03</td>
      <td>3.69</td>
    </tr>
    <tr>
      <th>49</th>
      <td>800</td>
      <td>freestyle</td>
      <td>women</td>
      <td>short</td>
      <td>469.04</td>
      <td>479.34</td>
      <td>10.30</td>
    </tr>
    <tr>
      <th>45</th>
      <td>400</td>
      <td>medley relay</td>
      <td>women</td>
      <td>short</td>
      <td>205.96</td>
      <td>225.20</td>
      <td>19.24</td>
    </tr>
    <tr>
      <th>41</th>
      <td>400</td>
      <td>individual medley</td>
      <td>men</td>
      <td>short</td>
      <td>219.26</td>
      <td>235.50</td>
      <td>16.24</td>
    </tr>
  </tbody>
</table>
</div>




```python
q = (view.category != "mixed") & ~view.swimstyle.str.contains("relay")

fig = pn.ggplot(view[q].dropna()) + \
    pn.geom_point(pn.aes(x = "factor(distance)", y = "difference", color = "swimstyle", shape = "course")) + \
    pn.facet_wrap(facets = "category") + \
    pn.labs(
        x = "Distance", 
        y = "Difference (s)",
        title = "Time difference between record and twice that record on half the distance")
    
fig.draw();
```


![png](/assets/images/swimming-records_46_0.png)


Well, the start doesn't save more than a couple of seconds, but it's hard to say more. This difference is for a large part fatigue of the swimmer.
