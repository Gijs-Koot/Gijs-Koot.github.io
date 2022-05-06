import rasterio
from rasterio.windows import Window

with rasterio.open("s3://heights-tiles/tiles/sd9800_DSM_1M.tiff") as raster:
  dt = raster.read(1, window=Window(500, 500, 501, 501))
