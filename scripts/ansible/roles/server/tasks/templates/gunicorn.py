import multiprocessing

cores = multiprocessing.cpu_count()

# host & port
bind = ["0.0.0.0:{{ gunicorn_port }}"]

# app
wsgi_app = "main:app"

# worker type
worker_class = "uvicorn.workers.UvicornWorker"

# logs
accesslog = "-"

# misc
proc_name = "crm-pilates-api"
graceful_timeout = 120
timeout = 120
keepalive = 5
max_requests = 100

# workers calc
# workers_per_core = 1.0
# workers = int(workers_per_core * cores)
workers = 1
worker_tmp_dir = "/tmp"
