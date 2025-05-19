# Run the test to collect performance stats for a given configuration of the gunicorn server
# Run this again with different configurations of the gunicorn server running with different workers, thread, gevent

pytest -s test_webserver.py --scenario sleep --server gunicorn --sleep_time 1,10,30 --parallel 1,8,16,32,64 
