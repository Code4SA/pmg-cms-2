web: newrelic-admin run-program gunicorn --workers 1 --worker-class gevent --timeout 30 --max-requests 3000 --max-requests-jitter 100 --pid gunicorn.pid --log-file - --access-logfile - pmg:app
