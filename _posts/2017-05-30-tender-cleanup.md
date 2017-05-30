---
layout: post
title:  "Cleaning up tender data"
date:   2017-05-30 22:30:00 +0200
categories: hackathon tender dataset
---

_Work in progress_

For the [Accountability hack](https://accountabilityhack.nl/) I am cleaning up data regarding tenders in the Netherlands. These are published on https://www.tenderned.nl/over-tenderned/datasets-aanbestedingen, and this data is in some rough shape. This is a notebook that cleans it up. I will also include a script that does it.   

First, I extract the relevant links to datasets from the page.


```python
from bs4 import BeautifulSoup
import requests

url = "https://www.tenderned.nl/over-tenderned/datasets-aanbestedingen"

soup  = BeautifulSoup(requests.get(url).content, "html.parser")

links = [link for link in [a.attrs["href"] for a in soup.find_all("a")] if "Dataset" in link]
links
```




    ['https://www.tenderned.nl/sites/default/files//Dataset_TenderNed_2016_Q1_Q2.xlsx',
     'https://www.tenderned.nl/sites/default/files//Dataset_TenderNed_2016_Q3_Q4_0.xlsx',
     'https://www.tenderned.nl/sites/default/files//Dataset_TenderNed_2015.xlsx',
     'https://www.tenderned.nl/sites/default/files//Dataset_TenderNed_2014.xlsx',
     'https://www.tenderned.nl/sites/default/files//Dataset_TenderNed_2013.xlsx',
     'https://www.tenderned.nl/sites/default/files//Dataset_TenderNed_2012.xlsx',
     'https://www.tenderned.nl/sites/default/files//Dataset_TenderNed_2010_2011.xlsx']



It's useful to have a list of shorter names as well. I use pandas to read all the excel files as `pd.DataFrame`.


```python
import re
import pandas as pd

# i'll need this later
pd.options.display.max_columns = 100
pd.options.display.max_rows = 100

names = [re.match(r'.*TenderNed_(.*)\.xlsx', link).groups()[0] for link in links]
frames = [pd.read_excel(link) for link in links]

names
```




    ['2016_Q1_Q2', '2016_Q3_Q4_0', '2015', '2014', '2013', '2012', '2010_2011']



The colums are not the same among all of the frames, so let's create a heatmap to see what's missing where.


```python
import seaborn.apionly as sns
from functools import reduce

%pylab inline
```

    Populating the interactive namespace from numpy and matplotlib



```python
all_columns = set(reduce(lambda x, y: x + y, [list(df.columns) for df in frames]))

missing = pd.DataFrame(index=all_columns)

for name, frame in zip(names, frames):

    missing.loc[frame.columns, name] = 1

plt.figure(figsize = (8, 18))
sns.heatmap(missing)
```




    <matplotlib.axes._subplots.AxesSubplot at 0x7f067dfa07f0>




![png](2017-05-30-tender-cleanup_files/2017-05-30-tender-cleanup_7_1.png)


Allright. I don't like the ugly column names, with spaces, and some even have a question mark at the end. WTF? Unfortunately, there is no functionality like `janitor::clean_names` in `R` available in python (anyone?), so I'll hack my own for now.


```python
import string

def sanitize(name):

    t = "".join([c if c in string.ascii_lowercase + string.digits else "_" for c in name.lower()])
    return re.sub(r"_+", "_", t).lstrip("_").rstrip("_")

sanitize(df.columns[-3])
```




    'betreft_uitbesteding'



Now I'll merge the frames, except the one with the different column names, into one, while also sanitizing each frame and adding a reference to the source.


```python
def transform(df, name, link):

    return df.rename(columns=sanitize).assign(
        name = name,
        link = link
    )

clean_frames = [transform(df, name, link) for df, name, link in zip(frames, names, links) if not "2016_Q3" in name]

tenders = pd.concat(clean_frames)
tenders.head()
```


```python
tenders.shape
```




    (58289, 70)



The first thing I always do in a dataset is checking the id's, and if they're actually unique. Terrible datasets have duplicated id's, many of them, and have all kinds of redundant data. This one, as mentioned earlier, is terrible. Let's count the duplicates and null values in each column to see if we can make something of that.


```python
def count_dupes(col):
    return pd.Series({
        "duplications": col.duplicated().sum(),
        "unique_values": len(col.unique()),
        "na": col.isnull().sum(),
        "na + duplications": (col.duplicated() | col.isnull()).sum()
    })

tenders.apply(count_dupes, axis = 0).T.sort_values("duplications")
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>duplications</th>
      <th>na</th>
      <th>na + duplications</th>
      <th>unique_values</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>id_publicatie</th>
      <td>14994</td>
      <td>0</td>
      <td>14994</td>
      <td>43295</td>
    </tr>
    <tr>
      <th>tenderned_kenmerk</th>
      <td>33137</td>
      <td>0</td>
      <td>33137</td>
      <td>25152</td>
    </tr>
    <tr>
      <th>aanbesteding_id</th>
      <td>33137</td>
      <td>0</td>
      <td>33137</td>
      <td>25152</td>
    </tr>
    <tr>
      <th>korte_beschrijving_aanbesteding</th>
      <td>35803</td>
      <td>51</td>
      <td>35804</td>
      <td>22486</td>
    </tr>
    <tr>
      <th>naam_aanbesteding</th>
      <td>36222</td>
      <td>0</td>
      <td>36222</td>
      <td>22067</td>
    </tr>
    <tr>
      <th>referentienummer</th>
      <td>41271</td>
      <td>13614</td>
      <td>41272</td>
      <td>17018</td>
    </tr>
    <tr>
      <th>trefwoorden</th>
      <td>48636</td>
      <td>10465</td>
      <td>48637</td>
      <td>9653</td>
    </tr>
    <tr>
      <th>naam_gegunde_ondernemer</th>
      <td>50474</td>
      <td>29203</td>
      <td>50475</td>
      <td>7815</td>
    </tr>
    <tr>
      <th>id_s_publicatie</th>
      <td>50999</td>
      <td>29203</td>
      <td>51000</td>
      <td>7290</td>
    </tr>
    <tr>
      <th>gegunde_ondernemer_postcode</th>
      <td>51968</td>
      <td>29432</td>
      <td>51969</td>
      <td>6321</td>
    </tr>
    <tr>
      <th>gegunde_ondernemer_postadres</th>
      <td>52265</td>
      <td>29562</td>
      <td>52266</td>
      <td>6024</td>
    </tr>
    <tr>
      <th>tsender</th>
      <td>54348</td>
      <td>46585</td>
      <td>58275</td>
      <td>15</td>
    </tr>
    <tr>
      <th>id_perceel</th>
      <td>54988</td>
      <td>44227</td>
      <td>54989</td>
      <td>3301</td>
    </tr>
    <tr>
      <th>hoofd_cpv_definitie</th>
      <td>55112</td>
      <td>2</td>
      <td>55113</td>
      <td>3177</td>
    </tr>
    <tr>
      <th>definitieve_waarde</th>
      <td>55833</td>
      <td>49122</td>
      <td>55834</td>
      <td>2456</td>
    </tr>
    <tr>
      <th>ad_officiele_benaming</th>
      <td>55865</td>
      <td>0</td>
      <td>55865</td>
      <td>2424</td>
    </tr>
    <tr>
      <th>ad_vestigingsadres</th>
      <td>55991</td>
      <td>0</td>
      <td>55991</td>
      <td>2298</td>
    </tr>
    <tr>
      <th>naam_perceel</th>
      <td>56153</td>
      <td>47206</td>
      <td>56154</td>
      <td>2136</td>
    </tr>
    <tr>
      <th>ad_postcode</th>
      <td>56421</td>
      <td>0</td>
      <td>56421</td>
      <td>1868</td>
    </tr>
    <tr>
      <th>gegunde_ondernemer_internetadres</th>
      <td>56489</td>
      <td>49173</td>
      <td>56490</td>
      <td>1800</td>
    </tr>
    <tr>
      <th>gegunde_ondernemer_plaats</th>
      <td>56643</td>
      <td>29428</td>
      <td>56644</td>
      <td>1646</td>
    </tr>
    <tr>
      <th>plaats_opening_kluis</th>
      <td>56667</td>
      <td>47743</td>
      <td>56668</td>
      <td>1622</td>
    </tr>
    <tr>
      <th>internetadres_aanbestedende_dienst</th>
      <td>56744</td>
      <td>14790</td>
      <td>56745</td>
      <td>1545</td>
    </tr>
    <tr>
      <th>nationale_identificatie_aansluitnummer</th>
      <td>56751</td>
      <td>0</td>
      <td>56751</td>
      <td>1538</td>
    </tr>
    <tr>
      <th>sluitingsdatum_aanbesteding</th>
      <td>56763</td>
      <td>9469</td>
      <td>56764</td>
      <td>1526</td>
    </tr>
    <tr>
      <th>publicatiedatum</th>
      <td>56814</td>
      <td>0</td>
      <td>56814</td>
      <td>1475</td>
    </tr>
    <tr>
      <th>termijn_verkrijgen_documenten</th>
      <td>56883</td>
      <td>26792</td>
      <td>56884</td>
      <td>1406</td>
    </tr>
    <tr>
      <th>datum_gunning</th>
      <td>57036</td>
      <td>29203</td>
      <td>57037</td>
      <td>1253</td>
    </tr>
    <tr>
      <th>voltooiing_opdracht</th>
      <td>57069</td>
      <td>38171</td>
      <td>57070</td>
      <td>1220</td>
    </tr>
    <tr>
      <th>aanvang_opdracht</th>
      <td>57241</td>
      <td>37764</td>
      <td>57242</td>
      <td>1048</td>
    </tr>
    <tr>
      <th>verzending_uitnodigingen</th>
      <td>57306</td>
      <td>52169</td>
      <td>57307</td>
      <td>983</td>
    </tr>
    <tr>
      <th>sluitingsdatum_aanmelding</th>
      <td>57319</td>
      <td>51497</td>
      <td>57320</td>
      <td>970</td>
    </tr>
    <tr>
      <th>ad_plaats</th>
      <td>57608</td>
      <td>0</td>
      <td>57608</td>
      <td>681</td>
    </tr>
    <tr>
      <th>personen_aanwezig_opening_kluis</th>
      <td>57747</td>
      <td>2</td>
      <td>57748</td>
      <td>542</td>
    </tr>
    <tr>
      <th>geraamde_waarde</th>
      <td>57813</td>
      <td>54252</td>
      <td>57814</td>
      <td>476</td>
    </tr>
    <tr>
      <th>nutscode</th>
      <td>57864</td>
      <td>358</td>
      <td>57865</td>
      <td>425</td>
    </tr>
    <tr>
      <th>korte_omschrijving_uitbesteding</th>
      <td>58060</td>
      <td>57069</td>
      <td>58061</td>
      <td>229</td>
    </tr>
    <tr>
      <th>laagste_waarde_ingediende_offertes</th>
      <td>58062</td>
      <td>57609</td>
      <td>58063</td>
      <td>227</td>
    </tr>
    <tr>
      <th>hoogste_waarde_ingediende_offertes</th>
      <td>58064</td>
      <td>57609</td>
      <td>58065</td>
      <td>225</td>
    </tr>
    <tr>
      <th>tweede_adresregel</th>
      <td>58089</td>
      <td>55860</td>
      <td>58090</td>
      <td>200</td>
    </tr>
    <tr>
      <th>hoofd_sub_cpv_1</th>
      <td>58148</td>
      <td>57542</td>
      <td>58149</td>
      <td>141</td>
    </tr>
    <tr>
      <th>opdracht_categorie</th>
      <td>58158</td>
      <td>13726</td>
      <td>58159</td>
      <td>131</td>
    </tr>
    <tr>
      <th>hoofd_sub_cpv_2</th>
      <td>58220</td>
      <td>58060</td>
      <td>58221</td>
      <td>69</td>
    </tr>
    <tr>
      <th>aantal_inschrijvingen</th>
      <td>58222</td>
      <td>29203</td>
      <td>58223</td>
      <td>67</td>
    </tr>
    <tr>
      <th>geraamde_waarde_heeft_betrekking_op_een_periode_van</th>
      <td>58240</td>
      <td>55008</td>
      <td>58241</td>
      <td>49</td>
    </tr>
    <tr>
      <th>aantal_elektronisch_ingediende_inschrijvingen</th>
      <td>58241</td>
      <td>29203</td>
      <td>58242</td>
      <td>48</td>
    </tr>
    <tr>
      <th>gegunde_ondernemer_land</th>
      <td>58260</td>
      <td>29217</td>
      <td>58261</td>
      <td>29</td>
    </tr>
    <tr>
      <th>hoofdactiviteit</th>
      <td>58270</td>
      <td>4616</td>
      <td>58271</td>
      <td>19</td>
    </tr>
    <tr>
      <th>publicatie_soort</th>
      <td>58273</td>
      <td>0</td>
      <td>58273</td>
      <td>16</td>
    </tr>
    <tr>
      <th>waarde_van_de_uitbesteding</th>
      <td>58278</td>
      <td>57908</td>
      <td>58279</td>
      <td>11</td>
    </tr>
    <tr>
      <th>ad_land</th>
      <td>58279</td>
      <td>0</td>
      <td>58279</td>
      <td>10</td>
    </tr>
    <tr>
      <th>aard_van_de_opdracht</th>
      <td>58281</td>
      <td>0</td>
      <td>58281</td>
      <td>8</td>
    </tr>
    <tr>
      <th>soort_aanbestedende_dienst</th>
      <td>58281</td>
      <td>3962</td>
      <td>58282</td>
      <td>8</td>
    </tr>
    <tr>
      <th>procedure</th>
      <td>58281</td>
      <td>545</td>
      <td>58282</td>
      <td>8</td>
    </tr>
    <tr>
      <th>juridisch_kader</th>
      <td>58282</td>
      <td>0</td>
      <td>58282</td>
      <td>7</td>
    </tr>
    <tr>
      <th>btw_percentage_bij_geraamde_waarde</th>
      <td>58283</td>
      <td>57882</td>
      <td>58284</td>
      <td>6</td>
    </tr>
    <tr>
      <th>name</th>
      <td>58283</td>
      <td>0</td>
      <td>58283</td>
      <td>6</td>
    </tr>
    <tr>
      <th>link</th>
      <td>58283</td>
      <td>0</td>
      <td>58283</td>
      <td>6</td>
    </tr>
    <tr>
      <th>btw_percentage_bij_definitieve_waarde</th>
      <td>58284</td>
      <td>57749</td>
      <td>58285</td>
      <td>5</td>
    </tr>
    <tr>
      <th>geraamde_waarde_incl_btw</th>
      <td>58286</td>
      <td>32724</td>
      <td>58287</td>
      <td>3</td>
    </tr>
    <tr>
      <th>voorbehouden_voor_beroepsgroep</th>
      <td>58286</td>
      <td>58190</td>
      <td>58287</td>
      <td>3</td>
    </tr>
    <tr>
      <th>type_opdracht</th>
      <td>58286</td>
      <td>0</td>
      <td>58286</td>
      <td>3</td>
    </tr>
    <tr>
      <th>definitieve_waarde_incl_btw</th>
      <td>58286</td>
      <td>32699</td>
      <td>58287</td>
      <td>3</td>
    </tr>
    <tr>
      <th>betreft_uitbesteding</th>
      <td>58286</td>
      <td>29203</td>
      <td>58287</td>
      <td>3</td>
    </tr>
    <tr>
      <th>digitaal</th>
      <td>58287</td>
      <td>0</td>
      <td>58287</td>
      <td>2</td>
    </tr>
    <tr>
      <th>nationaal_of_europees</th>
      <td>58287</td>
      <td>0</td>
      <td>58287</td>
      <td>2</td>
    </tr>
    <tr>
      <th>tegen_betaling_documenten_verkrijgen</th>
      <td>58287</td>
      <td>0</td>
      <td>58287</td>
      <td>2</td>
    </tr>
    <tr>
      <th>geimporteerd</th>
      <td>58287</td>
      <td>0</td>
      <td>58287</td>
      <td>2</td>
    </tr>
    <tr>
      <th>inlichtingen_elektronische_veiling</th>
      <td>58287</td>
      <td>0</td>
      <td>58287</td>
      <td>2</td>
    </tr>
    <tr>
      <th>gpa</th>
      <td>58287</td>
      <td>0</td>
      <td>58287</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>
