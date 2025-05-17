# Run the test to collect performance stats for a given configuration of the gunicorn server
# Run this again with different configurations of the gunicorn server running with different workers, thread, gevent

pytest -s test_webserver.py --scenario gridded-data --server gunicorn --days=10 --parallel 1,16,32 --grid_size 1024,102400
