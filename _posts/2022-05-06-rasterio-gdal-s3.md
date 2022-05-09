---
layout: post
title: Reading large tiles from S3 directly with `rasterio`
date: 2022-05-06
published: true
categories: AWS geo
---

<p>
At SpotR, we make heavy use of rasterdata containing gridded height measurements.
</p>

<p>
When working in <code>python</code>, the <a href="https://rasterio.readthedocs.io/en/latest/index.html"><code>rasterio</code></a> package is useful. This package is
essentially a more pythonic binding to the GDAl library, as explained in their <a href="https://rasterio.readthedocs.io/en/latest/intro.html">
introduction</a>. The file below was obtained from <a href="https://data.gov.uk/dataset/f0db0249-f17b-4036-9e65-309148c97ce4/national-lidar-programme">data.gov.uk</a> and shows a 1x1km
patch of height measurements in the UK. The resolution is 1000x1000 pixels,
every pixel represents the (maximum) height of 1x1m. The lighter dots along the
top of the image are houses, there are some ragged parts where there is no data.
In the middle there is a depression, could be a riverbed, and then at the bottom
the terrain is rising a little.
</p>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #4f97d7; font-weight: bold;">import</span> rasterio
<span style="color: #4f97d7; font-weight: bold;">import</span> matplotlib.pyplot <span style="color: #4f97d7; font-weight: bold;">as</span> plt
<span style="color: #4f97d7; font-weight: bold;">import</span> numpy <span style="color: #4f97d7; font-weight: bold;">as</span> np

<span style="color: #4f97d7; font-weight: bold;">with</span> rasterio.<span style="color: #4f97d7;">open</span><span style="color: #4f97d7;">(</span><span style="color: #2d9574;">"/tmp/sd9863_DSM_1M.tiff"</span><span style="color: #4f97d7;">)</span> <span style="color: #4f97d7; font-weight: bold;">as</span> <span style="color: #7590db;">dataset</span>:
   heights = dataset.read<span style="color: #4f97d7;">(</span><span style="color: #a45bad;">1</span><span style="color: #4f97d7;">)</span>

<span style="color: #7590db;">fn</span> = <span style="color: #2d9574;">"images/heights.png"</span>

<span style="color: #2aa1ae; background-color: #292e34;"># </span><span style="color: #2aa1ae; background-color: #292e34;">replace nodata values with nan</span>
<span style="color: #7590db;">heights</span><span style="color: #4f97d7;">[</span>np.where<span style="color: #bc6ec5;">(</span>heights==dataset.nodata<span style="color: #bc6ec5;">)</span><span style="color: #4f97d7;">]</span> = np.nan

plt.imshow<span style="color: #4f97d7;">(</span>heights<span style="color: #4f97d7;">)</span>
plt.title<span style="color: #4f97d7;">(</span><span style="color: #2d9574;">"Example of a 1km x 1km raster"</span><span style="color: #4f97d7;">)</span>
plt.tight_layout<span style="color: #4f97d7;">()</span>
plt.savefig<span style="color: #4f97d7;">(</span>fn<span style="color: #4f97d7;">)</span>
fn
</pre>
</div>

<div id="org18e4de7" class="figure">
<p><img src="/assets/images/heights.png" alt="heights.png" />
</p>
</div>

<p>
Rastertiles, typically GeoTiff files, can become quite large in terms of memory
size. This grid above takes up \~4Mb as an uncompressed GeoTiff file, down from
6.5Mb as a <code>.asc</code> file, which is a simple text-based format. There are a couple
of interesting compression techniques like <a href="https://en.wikipedia.org/wiki/Deflate">DEFLATE</a> and <a href="https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Welch">LZW</a> that can bring the
size of the data down further. It is possible to convert rasters with
<code>rasterio</code>, but the <code>gdal_translate</code> utility is the tool for the job.
</p>

<div class="org-src-container">
<pre class="src src-bash">gdal_translate /tmp/sd9863_DSM_1M.asc /tmp/sd9863_DSM_1M.tiff &gt; /dev/null
gdal_translate /tmp/sd9863_DSM_1M.asc /tmp/sd9863_DSM_1M_lzw.tiff -co <span style="color: #7590db;">COMPRESS</span>=LZW &gt; /dev/null
gdal_translate /tmp/sd9863_DSM_1M.asc /tmp/sd9863_DSM_1M_def.tiff -co <span style="color: #7590db;">COMPRESS</span>=DEFLATE &gt; /dev/null
gdal_translate /tmp/sd9863_DSM_1M.asc /tmp/sd9863_DSM_1M_def_pred.tiff -co <span style="color: #7590db;">COMPRESS</span>=DEFLATE -co <span style="color: #7590db;">PREDICTOR</span>=<span style="color: #a45bad;">2</span> &gt; /dev/null
ls -lha /tmp/sd*
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash">-rw-rw-r-- <span style="color: #a45bad;">1</span> gijs gijs <span style="color: #a45bad;">6,5M</span> jun <span style="color: #a45bad;">13</span>  <span style="color: #a45bad;">2018</span> /tmp/sd9863_DSM_1M.asc
-rw-rw-r-- <span style="color: #a45bad;">1</span> gijs gijs <span style="color: #a45bad;">1,1M</span> mei  <span style="color: #a45bad;">9</span> <span style="color: #a45bad;">09:11</span> /tmp/sd9863_DSM_1M_def_pred.tiff
-rw-rw-r-- <span style="color: #a45bad;">1</span> gijs gijs <span style="color: #a45bad;">1,5M</span> mei  <span style="color: #a45bad;">9</span> <span style="color: #a45bad;">09:11</span> /tmp/sd9863_DSM_1M_def.tiff
-rw-rw-r-- <span style="color: #a45bad;">1</span> gijs gijs <span style="color: #a45bad;">1,8M</span> mei  <span style="color: #a45bad;">9</span> <span style="color: #a45bad;">09:11</span> /tmp/sd9863_DSM_1M_lzw.tiff
-rw-rw-r-- <span style="color: #a45bad;">1</span> gijs gijs <span style="color: #a45bad;">3,9M</span> mei  <span style="color: #a45bad;">9</span> <span style="color: #a45bad;">09:11</span> /tmp/sd9863_DSM_1M.tiff
</pre>
</div>

<p>
Interestingly, all compression techniques available in <code>GDAL</code> are lossless.
There are JPEG based compression systems, but they can only be applied to 8bit
unsigned data, in other words, images, and these height measurements which are
organized as floating point numbers cannot be stored using JPEG compression. I
can definitely think of some usecases where some distortion of these
measurements is fine, as long as it's bounded somehow, but I haven't come across
examples of a lossy compression for rasters of floating points.
</p>

<div id="outline-container-org43128ac" class="outline-2">
<h2 id="org43128ac">Partial reads</h2>
<div class="outline-text-2" id="text-org43128ac">
<p>
Compression can save us almost an order of magnitude, but to store this data at
our scale, things still add up. I live in the Netherlands which has an area of
41,543 km<sup>2</sup>. That's 40k+ tiles at 1Mb+ each, 50Gb in total. Perfect to save on
cloud storage such as S3.
</p>

<div class="org-src-container">
<pre class="src src-bash">aws s3 ls s3://heights-tiles/tiles/sd980
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash"><span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:55</span>  <span style="color: #a45bad;">2903641</span>  sd9800_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:54</span>  <span style="color: #a45bad;">2871755</span>  sd9801_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:54</span>  <span style="color: #a45bad;">2938302</span>  sd9802_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:55</span>  <span style="color: #a45bad;">2719476</span>  sd9803_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:55</span>  <span style="color: #a45bad;">2643684</span>  sd9804_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:55</span>  <span style="color: #a45bad;">2533681</span>  sd9805_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:55</span>  <span style="color: #a45bad;">2715498</span>  sd9806_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:55</span>  <span style="color: #a45bad;">2818095</span>  sd9807_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:55</span>  <span style="color: #a45bad;">2755601</span>  sd9808_DSM_1M.tiff 
<span style="color: #a45bad;">2022-04-29</span>  <span style="color: #a45bad;">23:08:56</span>   <span style="color: #a45bad;">468739</span>  sd9809_DSM_1M.tiff 
</pre>
</div>

<p>
When doing a calculation, we're typically not interested in the whole of the
tile. For example, we only want to know the height of a single pixel in the
raster file. It is possible to avoid downloading the whole file, this operation
can be done using a partial read. This is possible because S3 allows
random-access reads, and GDAL supports reading over a network with
<a href="https://gdal.org/user/virtual_file_systems.html">virtual file systems</a>.
</p>

<p>
Depending on how large your tiles are, this can make a big difference. Let's
benchmark this.
</p>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #4f97d7; font-weight: bold;">import</span> rasterio
<span style="color: #4f97d7; font-weight: bold;">from</span> rasterio.windows <span style="color: #4f97d7; font-weight: bold;">import</span> Window

<span style="color: #4f97d7; font-weight: bold;">with</span> rasterio.<span style="color: #4f97d7;">open</span><span style="color: #4f97d7;">(</span><span style="color: #2d9574;">"s3://heights-tiles/tiles/sd9800_DSM_1M.tiff"</span><span style="color: #4f97d7;">)</span> <span style="color: #4f97d7; font-weight: bold;">as</span> <span style="color: #7590db;">raster</span>:
  dt = raster.read<span style="color: #4f97d7;">(</span><span style="color: #a45bad;">1</span>, window=Window<span style="color: #bc6ec5;">(</span><span style="color: #a45bad;">500</span>, <span style="color: #a45bad;">500</span>, <span style="color: #a45bad;">501</span>, <span style="color: #a45bad;">501</span><span style="color: #bc6ec5;">)</span><span style="color: #4f97d7;">)</span>
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash"><span style="color: #4f97d7; font-weight: bold;">time</span> python src/read_raster_window.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash">real    <span style="color: #a45bad;">0m17,300s</span>
user    <span style="color: #a45bad;">0m3,026s</span>
sys     <span style="color: #a45bad;">0m1,038s</span>                                        
</pre>
</div>

<p>
Wait a minute .. 17 seconds is still a long time. It turns out that <code>GDAL</code> will
scan the whole folder for other files before opening a file. This is interesting
behaviour that makes sense when geodata files are often accompanied by other
files that include information about transformation, possibly some indexes and
more. We can disable this behaviour by setting an environment value. 
</p>

<div class="org-src-container">
<pre class="src src-bash"><span style="color: #4f97d7; font-weight: bold;">time</span> <span style="color: #7590db;">GDAL_DISABLE_READDIR_ON_OPEN</span>=YES python src/read_raster_window.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash">real    <span style="color: #a45bad;">0m1,230s</span>
user    <span style="color: #a45bad;">0m0,400s</span>
sys     <span style="color: #a45bad;">0m0,948s</span>
</pre>
</div>
</div>
</div>
