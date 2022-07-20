import sys
import os
import time
import dask
from parflow.tools.io import read_pfb

def load_files(files_per_test, water_year, test_number):
    start_time = time.time()
    n = 0
    data_folder = f"/hydrodata/forcing/processed_data/CONUS1/NLDAS2/daily/WY{water_year}"
    for index,file_name in enumerate(os.listdir(data_folder)):
        if index >= (test_number -1) * files_per_test and index < (test_number + 0) * files_per_test:
            n = n + 1
            file_path = f"{data_folder}/{file_name}"
            read_pfb(file_path)
    duration = round(time.time() - start_time, 1)
    print(f"Loaded {n} PFB files in {duration} seconds for test #{test_number}.")

def load_files_parallel(files_per_test, water_year, test_number, n_threads):
    start_time = time.time()
    dask_results = []
    start_time = time.time()
    n = 0
    data_folder = f"/hydrodata/forcing/processed_data/CONUS1/NLDAS2/daily/WY{water_year}"
    for index,file_name in enumerate(os.listdir(data_folder)):
        if index >= (test_number -1) * files_per_test and index < (test_number + 0) * files_per_test:
            n = n + 1
            file_path = f"{data_folder}/{file_name}"
            dask_results.append(dask.delayed(read_pfb)(file_path))
            #read_pfb(file_path)
    dask.delayed(lambda x: x)(dask_results).compute(num_workers=n_threads)
    duration = round(time.time() - start_time, 1)
    print(f"Loaded {n} PFB files in parallel in {duration} seconds for test #{test_number} using {n_threads} threads.")

def main():
    if len(sys.argv) < 3:
        print()
        print("Usage: python hydrodata_test <year> <n>")
        print("   where <year> is between 2003 - 2006")
        print("     and <n> is a test number between 1-10")
        print("   for example, python hydrodata_test 2003 1")
        sys.exit(0)
    water_year = sys.argv[1]
    test_number = sys.argv[2]
    n_threads = sys.argv[3] if len(sys.argv) > 3 else False
    if n_threads:
        load_files_parallel(400, water_year, int(test_number), int(n_threads))
    else:
        load_files(400, water_year, int(test_number))

main()
