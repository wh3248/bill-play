import hf_hydrodata as hf
import requests
import io
import time
from tifffile import TiffFile
import rasterio
import json

def main():
    #url = "/vsicurl/https://hydrogen.princeton.edu/api/cog?email=wh3248@princeton.edu&pin=0000"
    url = "/hydrodata/temp/wh3248/cog/ma2025/wtd_mean_cog.tif"
    #url = "/hydrodata/national_obs/groundwater/data/ma_2025/wtd_mean_estimate_RF_additional_inputs_dummy_drop0LP_1s_CONUS2_m_v_20240813.tif"
    start_timer = time.time()
    start_timer = time.time()
    with rasterio.open(url) as src:
        print(src.crs)
        #print(str(src.profile))
#        print(src.profile)
        return
        factors = src.overviews(1)
        print("NUM FACTORS", len(factors))
        for factor in factors:
            print("Factor", factor)
        print("HEIGHT", src.height)
        print("WIDTH", src.width)
        print("PIXEL WIDTH", src.transform.a)
        print("PIXEL HEIGHT", abs(src.transform.e))
        return
        data = src.read(1, out_shape=(src.height//32, src.width// 32))
        print(data.shape)
        print(type(data))
main()

