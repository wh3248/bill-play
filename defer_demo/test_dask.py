import dask
import time

def first_task(arg):
    print("First task")
    time.sleep(1)
    return None



def scenario_task(first, scenario_id):
    print(scenario_id)
    time.sleep(2)
    return None

def run_job():
    dask_first = dask.delayed(first_task)("abc")
    result_list = []
    result_list.append(dask.delayed(scenario_task)(dask_first, "one"))
    result_list.append(dask.delayed(scenario_task)(dask_first, "two"))
    combine = dask.delayed(lambda x:x)(result_list)
    combine.compute(scheduler="multiprocessing")

if __name__ == "__main__":
    run_job()
