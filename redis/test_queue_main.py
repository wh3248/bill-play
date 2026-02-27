import redis
import rq
import rq.job
import test_queue
import time

def main():
    try:
        redis_port = 6379
        redis_conn = redis.Redis(host="localhost", port=redis_port, db=0)
        large_tasks_queue = rq.Queue("large_tasks", connection=redis_conn, default_timeout=60*60)
        small_tasks_queue = rq.Queue("small_tasks", connection=redis_conn, default_timeout=60*60)
        bounds = [439, 2683, 440, 2684]
        options = {"dataset":"CW3E", "variable":"precipitation", "temporal_resolution": "hourly", "date_start": "1997-01-01", "date_end": "2000-01-01", "grid_bounds": bounds}
        job_id = test_queue.submit_job(large_tasks_queue, options)
        waited_time = 0
        for wait_time in [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1, 1, 1, 20, 30]:
            job = rq.job.Job.fetch(job_id, connection = redis_conn)
            status = job.get_status()
            if job.is_finished:
                print(job.return_value())
                break
            if job.is_failed:
                res = job.latest_result()
                print(str(res.exc_string))
                break
            time.sleep(wait_time)
            waited_time = waited_time + wait_time
        print(f"Waited time: {waited_time}")
    except Exception as e:
        print(e)
    print("Done")

if __name__ == "__main__":
    main()
