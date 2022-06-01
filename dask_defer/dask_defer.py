import time
import dask

def inc(x):
    time.sleep(1)
    return x + 1

def dec(x):
    time.sleep(1)
    return x - 1

def add(x, y):
    time.sleep(1)
    return x + 1

def sum(a):
    result = 0
    for i in range(0, len(a)):
        result = result + a[i]
    return result

def run_serial():
    start = time.time()
    x = inc(1)
    y = dec(2)
    z = add(x, y)
    duration = time.time() - start
    print(f"Run serial, Answer {z} in {duration} seconds.")

def run_parallel():
    start = time.time()
    p_inc = dask.delayed(inc)
    p_dec = dask.delayed(dec)
    p_add = dask.delayed(add)
    x = p_inc(1)
    y = p_dec(2)
    z = p_add(x, y)
    z = z.compute()
    duration = time.time() - start
    print(f"Ran parallel, Answer {z} in {duration} seconds.")

def run_serial_job():
    start = time.time()
    for i in range(0, 5):
        inc(1)
    duration = time.time() - start
    print(f"Ran serial job in {duration} seconds.")

def run_parallel_job():
    start = time.time()
    p_inc = dask.delayed(inc)
    p_sum = dask.delayed(sum)
    status = []
    for i in range(0,128):
        status.append(p_inc(0))
    result = p_sum(status)
    result = result.compute()
    duration = time.time() - start
    print(f"Ran parallel job {result} jobs in {duration} seconds.")

#run_serial()
#run_parallel()
#run_serial_job()
run_parallel_job()
