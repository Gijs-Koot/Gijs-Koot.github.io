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
introduction</a>.
</p>

<div class="org-src-container">
<pre class="src src-python"><span style="color: #b6a0ff;">import</span> rasterio
<span style="color: #b6a0ff;">import</span> matplotlib.pyplot <span style="color: #b6a0ff;">as</span> plt
<span style="color: #b6a0ff;">import</span> numpy <span style="color: #b6a0ff;">as</span> np

<span style="color: #b6a0ff;">with</span> rasterio.<span style="color: #f78fe7;">open</span><span style="color: #ffffff;">(</span><span style="color: #79a8ff;">"/tmp/sd9863_DSM_1M.tiff"</span><span style="color: #ffffff;">)</span> <span style="color: #b6a0ff;">as</span> <span style="color: #00d3d0;">dataset</span>:
   heights = dataset.read<span style="color: #ffffff;">(</span><span style="color: #00bcff;">1</span><span style="color: #ffffff;">)</span>

<span style="color: #00d3d0;">fn</span> = <span style="color: #79a8ff;">"images/heights.png"</span>

<span style="color: #a8a8a8;"># </span><span style="color: #a8a8a8;">replace nodata values with nan</span>
<span style="color: #00d3d0;">heights</span><span style="color: #ffffff;">[</span>np.where<span style="color: #ff62d4;">(</span>heights==dataset.nodata<span style="color: #ff62d4;">)</span><span style="color: #ffffff;">]</span> = np.nan

plt.imshow<span style="color: #ffffff;">(</span>heights<span style="color: #ffffff;">)</span>
plt.title<span style="color: #ffffff;">(</span><span style="color: #79a8ff;">"Example of a 1km x 1km raster"</span><span style="color: #ffffff;">)</span>
plt.tight_layout<span style="color: #ffffff;">()</span>
plt.savefig<span style="color: #ffffff;">(</span>fn<span style="color: #ffffff;">)</span>
fn
</pre>
</div>

<div id="org9973fc0" class="figure">
<p><img src="/assets/images/heights.png" alt="heights.png" />
</p>
</div>

<p>
Rastertiles, typically GeoTiff files, can become quite large in terms of memory
size. This grid above takes up around <code>4Mb as an uncompressed GeoTiff file, down
from 6.5Mb as a ~.asc</code> file, which is a simple text-based format. There are a
couple of interesting compression techniques like <a href="https://en.wikipedia.org/wiki/Deflate">DEFLATE</a> and <a href="https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Welch">LZW</a> that can bring
the size of the data down further.
</p>

<div class="org-src-container">
<pre class="src src-bash">gdal_translate /tmp/sd9863_DSM_1M.asc /tmp/sd9863_DSM_1M.tiff &gt; /dev/null
gdal_translate /tmp/sd9863_DSM_1M.asc /tmp/sd9863_DSM_1M_lzw.tiff -co <span style="color: #00d3d0;">COMPRESS</span>=LZW &gt; /dev/null
gdal_translate /tmp/sd9863_DSM_1M.asc /tmp/sd9863_DSM_1M_def.tiff -co <span style="color: #00d3d0;">COMPRESS</span>=DEFLATE &gt; /dev/null
gdal_translate /tmp/sd9863_DSM_1M.asc /tmp/sd9863_DSM_1M_def_pred.tiff -co <span style="color: #00d3d0;">COMPRESS</span>=DEFLATE -co <span style="color: #00d3d0;">PREDICTOR</span>=<span style="color: #00bcff;">2</span> &gt; /dev/null
ls -lha /tmp/sd*
</pre>
</div>

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-left">-rw-rw-r&#x2013; 1 gijs gijs 6</td>
<td class="org-left">5M mei  6 13:37 /tmp/sd9863<sub>DSM</sub><sub>1M.asc</sub></td>
</tr>

<tr>
<td class="org-left">-rw-rw-r&#x2013; 1 gijs gijs 1</td>
<td class="org-left">1M mei  6 16:45 /tmp/sd9863<sub>DSM</sub><sub>1M</sub><sub>def</sub><sub>pred.tiff</sub></td>
</tr>

<tr>
<td class="org-left">-rw-rw-r&#x2013; 1 gijs gijs 1</td>
<td class="org-left">5M mei  6 16:45 /tmp/sd9863<sub>DSM</sub><sub>1M</sub><sub>def.tiff</sub></td>
</tr>

<tr>
<td class="org-left">-rw-rw-r&#x2013; 1 gijs gijs 1</td>
<td class="org-left">8M mei  6 16:45 /tmp/sd9863<sub>DSM</sub><sub>1M</sub><sub>lzw.tiff</sub></td>
</tr>

<tr>
<td class="org-left">-rw-rw-r&#x2013; 1 gijs gijs 3</td>
<td class="org-left">9M mei  6 16:45 /tmp/sd9863<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>
</tbody>
</table>

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

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:55</td>
<td class="org-right">2903641</td>
<td class="org-left">sd9800<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:54</td>
<td class="org-right">2871755</td>
<td class="org-left">sd9801<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:54</td>
<td class="org-right">2938302</td>
<td class="org-left">sd9802<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:55</td>
<td class="org-right">2719476</td>
<td class="org-left">sd9803<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:55</td>
<td class="org-right">2643684</td>
<td class="org-left">sd9804<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:55</td>
<td class="org-right">2533681</td>
<td class="org-left">sd9805<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:55</td>
<td class="org-right">2715498</td>
<td class="org-left">sd9806<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:55</td>
<td class="org-right">2818095</td>
<td class="org-left">sd9807<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:55</td>
<td class="org-right">2755601</td>
<td class="org-left">sd9808<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>

<tr>
<td class="org-right">2022-04-29</td>
<td class="org-right">23:08:56</td>
<td class="org-right">468739</td>
<td class="org-left">sd9809<sub>DSM</sub><sub>1M.tiff</sub></td>
</tr>
</tbody>
</table>

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
<pre class="src src-python"><span style="color: #b6a0ff;">import</span> rasterio
<span style="color: #b6a0ff;">from</span> rasterio.windows <span style="color: #b6a0ff;">import</span> Window

<span style="color: #b6a0ff;">with</span> rasterio.<span style="color: #f78fe7;">open</span><span style="color: #ffffff;">(</span><span style="color: #79a8ff;">"s3://heights-tiles/tiles/sd9800_DSM_1M.tiff"</span><span style="color: #ffffff;">)</span> <span style="color: #b6a0ff;">as</span> <span style="color: #00d3d0;">raster</span>:
  dt = raster.read<span style="color: #ffffff;">(</span><span style="color: #00bcff;">1</span>, window=Window<span style="color: #ff62d4;">(</span><span style="color: #00bcff;">500</span>, <span style="color: #00bcff;">500</span>, <span style="color: #00bcff;">501</span>, <span style="color: #00bcff;">501</span><span style="color: #ff62d4;">)</span><span style="color: #ffffff;">)</span>
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash"><span style="color: #b6a0ff;">time</span> python src/read_raster_window.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash">real    <span style="color: #00bcff;">0m17,300s</span>
user    <span style="color: #00bcff;">0m3,026s</span>
sys     <span style="color: #00bcff;">0m1,038s</span>                                        
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
<pre class="src src-bash"><span style="color: #b6a0ff;">time</span> <span style="color: #00d3d0;">GDAL_DISABLE_READDIR_ON_OPEN</span>=YES python src/read_raster_window.py
</pre>
</div>

<div class="org-src-container">
<pre class="src src-bash">real    <span style="color: #00bcff;">0m1,230s</span>
user    <span style="color: #00bcff;">0m0,400s</span>
sys     <span style="color: #00bcff;">0m0,948s</span>
</pre>
</div>
</div>
</div>
