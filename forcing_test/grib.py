import pygrib
import hf_hydrodata as hf

path = "/hydrodata/maxwell_group/powell/data/common/NLDAS/2005/20050101/2005010100.nldasforce-a.grb"
print(path)
grbs = pygrib.open(path)
print("Opened file")
n = 0
min_x = 10000000
max_x = 0
min_y = 10000000
max_y = 0
n_points = 0
for grb in grbs:
    lats, lons = grb.latlons()
    print(lats.shape)
    for i in range(0, lats.shape[0]):
        for j in range(0, lats.shape[1]):
            lat = lats[i,j]
            lon = lons[i,j]
            x,y = hf.to_meters("conus1", lat, lon)
            if i == 0 and j == 0:
                print(lat, lon, x, y)
            if x >= 0 and x <= 4442000 and y >= 0 and y <= 3256000:
                n_points = n_points + 1
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    print(f"XY Range [{min_x}, {min_y}, {max_x}, {max_y}]")
    print(f"Num points in conus2 {n_points}")
    if n < 0:
        for k in grb.keys():
            print(k)
    print(n, grb.level, grb.parameterName, grb.parameterUnits, grb.typeOfLevel, grb.eps)
    n = n + 1
