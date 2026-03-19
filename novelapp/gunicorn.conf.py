import multiprocessing

# Server socket
bind = "0.0.0.0:6080"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
loglevel = "info"
accesslog = "-"   # stdout
errorlog = "-"    # stdout

# Process naming
proc_name = "novel-it"

# Limits
limit_request_line = 4094
limit_request_fields = 100
