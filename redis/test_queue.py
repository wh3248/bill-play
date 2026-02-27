import datetime
import time

import hf_hydrodata as hf
def submit_job(large_tasks_queue, options):
    try:
        print(options)
        job = large_tasks_queue.enqueue(long_task, options)
        print("STATUS", job.get_status())
        return job.id
    except Exception as e:
        print(e)
        return None

def long_task(options):
    duration_start = time.time()
    try:
        data = hf.get_gridded_data(options)
        duration = time.time() -duration_start
        with open("redis_file.txt", "a+") as fp:
            now = datetime.datetime.now()
            fp.write(f"Ran job {now} with shape {data.shape} in {duration} seconds.\n")
        result = {"Shape": str(data.shape), "Duration": duration}
        print(result)
        return result
    except Exception as e:
        duration = time.time() -duration_start
        with open("redis_file.txt", "a+") as fp:
            now = datetime.datetime.now()
            fp.write(f"Job error {now} {str(e)} in {duration} seconds.\n")
        raise e
