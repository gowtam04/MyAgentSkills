# fly.toml Configuration Reference

This is a comprehensive reference for all fly.toml configuration sections. Use it when generating or reviewing fly.toml files for users.

## Table of Contents
1. [Top-level options](#top-level-options)
2. [Build configuration](#build)
3. [Environment variables](#env)
4. [HTTP service](#http_service)
5. [Services (non-HTTP)](#services)
6. [Health checks](#health-checks)
7. [VM sizing](#vm)
8. [Mounts (volumes)](#mounts)
9. [Deploy settings](#deploy)
10. [Processes (multi-process apps)](#processes)
11. [Metrics](#metrics)
12. [Statics](#statics)
13. [Restart policy](#restart)

---

## Top-level Options

```toml
app = 'my-app-name'            # App name on Fly.io
primary_region = 'ord'          # Region for new machines + PRIMARY_REGION env var
kill_signal = 'SIGTERM'         # Signal sent on shutdown (default: SIGINT)
kill_timeout = 30               # Seconds to wait after kill_signal before force kill (default: 5, max: 300)
console_command = '/bin/bash'   # Command for `fly console`
swap_size_mb = 512              # Swap space in MB (optional)
```

## Build

```toml
[build]
  dockerfile = "Dockerfile"           # Path to Dockerfile (default: auto-detected)
  ignorefile = ".dockerignore"        # Path to ignore file
  # OR use a pre-built image:
  image = "registry.example.com/app:latest"

  [build.args]
    NODE_ENV = "production"           # Build-time arguments (non-secret)

  [build.settings]
    # Builder-specific settings (for buildpacks)
```

For build-time secrets (private npm tokens, etc.), use Docker's `--mount=type=secret` in the Dockerfile and pass them via `fly deploy --build-secret ID=value`.

## Env

Non-secret environment variables. These are visible in fly.toml — don't put credentials here.

```toml
[env]
  PORT = "8080"
  NODE_ENV = "production"
  LOG_LEVEL = "info"
  # PRIMARY_REGION is set automatically by Fly
```

## HTTP Service

The primary way to expose a web application.

```toml
[http_service]
  internal_port = 8080            # Port your app listens on inside the container
  force_https = true              # Redirect HTTP to HTTPS
  auto_stop_machines = 'stop'     # 'stop', 'suspend', or 'off'
  auto_start_machines = true      # Restart stopped machines on incoming requests
  min_machines_running = 1        # Minimum warm machines (0 = full scale-to-zero)
  processes = ['app']             # Which process group serves HTTP (if using multi-process)

  [http_service.concurrency]
    type = "requests"             # "requests" or "connections"
    hard_limit = 250              # Max concurrent; new requests get 503
    soft_limit = 200              # Autoscaler target per machine

  [http_service.http_options]
    compress = true               # Enable gzip/br compression at the proxy
    h2_backend = false            # Use HTTP/2 to reach your app (default: HTTP/1.1)

  [http_service.tls_options]
    alpn = ["h2", "http/1.1"]     # TLS ALPN protocols
    default_self_signed = false   # Use self-signed cert if no valid cert exists

  # Machine-level health check for HTTP
  [[http_service.checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "5s"
    method = "GET"
    path = "/health"
    # Optional:
    protocol = "http"             # "http" or "https"
    tls_skip_verify = false
    tls_server_name = ""
    [http_service.checks.headers]
      X-Custom-Header = "value"

  # Machine checks (run during deploy only, for canary testing)
  [[http_service.machine_checks]]
    image = "curlimages/curl"
    entrypoint = ["/bin/sh", "-c"]
    command = ["curl -f http://$FLY_TEST_MACHINE_IP:8080/health"]
    kill_timeout = "5s"
    kill_signal = "SIGTERM"
```

### auto_stop_machines explained
- `'stop'`: Machine stops completely when idle. Cold start on next request (typically 1-3 seconds).
- `'suspend'`: Machine is suspended to disk. Faster resume than stop (~300ms), but still bills for the volume.
- `'off'`: Machine never auto-stops. Always running, always billed. Use for WebSocket servers, workers, etc.

## Services (non-HTTP)

For TCP/UDP services that aren't standard HTTP:

```toml
[[services]]
  internal_port = 5432
  protocol = "tcp"                # "tcp" or "udp"
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 0
  processes = ['db']

  [[services.ports]]
    port = 5432
    handlers = ["tls"]            # "tls", "http", "proxy_proto"

  [[services.tcp_checks]]
    interval = "15s"
    timeout = "2s"
    grace_period = "10s"
```

## Health Checks

### Top-level checks (observability only — don't affect routing)
```toml
[[checks]]
  name = "db_connection"
  port = 8080
  type = "http"                   # "http" or "tcp"
  interval = "15s"
  timeout = "5s"
  grace_period = "10s"
  method = "GET"
  path = "/checks/db"
```

### Service-level checks (affect traffic routing)
Defined under `[http_service]` or `[[services]]` — see sections above.

### Machine checks (deploy-time validation)
Defined under `[[http_service.machine_checks]]` — see HTTP service section above. These run a throwaway machine during deploy to validate the new version before rolling it out.

## VM

```toml
[[vm]]
  memory = '1gb'                  # Memory: '256mb', '512mb', '1gb', '2gb', etc.
  cpu_kind = 'shared'             # 'shared' or 'performance'
  cpus = 1                        # Number of CPUs
  # processes = ['app']           # Assign specific VM size per process group

# Different VM sizes for different process groups:
[[vm]]
  memory = '2gb'
  cpu_kind = 'performance'
  cpus = 2
  processes = ['worker']
```

GPU options (for ML workloads):
```toml
[[vm]]
  memory = '16gb'
  cpu_kind = 'performance'
  cpus = 4
  gpu_kind = 'l40s'              # Options: 'a100-pcie-40gb', 'a100-sxm4-80gb', 'l40s', 'a10'
```

## Mounts

```toml
[mounts]
  source = "data"                 # Volume name
  destination = "/data"           # Mount path inside container
  initial_size = "10gb"           # Size for auto-created volumes on first deploy
  snapshot_retention = 5          # Number of snapshots to keep
  # processes = ['app']           # Which process group gets the mount
```

Remember: volumes are region-specific. One volume per machine at a time.

## Deploy

```toml
[deploy]
  release_command = "python manage.py migrate"   # Run before new machines start
  strategy = "rolling"            # "rolling", "canary", "bluegreen", "immediate"
  max_unavailable = 0.33          # Fraction of machines that can be down during rolling deploy
  wait_timeout = "5m"             # How long to wait for machines to become healthy
```

### Deployment strategies explained
- **rolling** (default): Updates machines one at a time. Safe, minimal resource overhead. Some requests may hit old and new versions simultaneously.
- **canary**: Deploys one machine first, verifies health, then proceeds with rolling. Good for catching bad deploys early.
- **bluegreen**: Boots a full set of new machines alongside old ones, then switches traffic atomically. Zero-downtime with instant rollback, but uses 2x resources during deploy.
- **immediate**: Stops all machines and starts new ones. Fast but causes downtime. Only for apps where brief downtime is acceptable.

## Processes

For apps with multiple process types (e.g., web server + background worker):

```toml
[processes]
  app = "node dist/server.js"
  worker = "node dist/worker.js"
```

Then assign HTTP service, VM sizing, and mounts per process group using the `processes` field in each section.

## Metrics

Expose Prometheus metrics for Fly's built-in Grafana:

```toml
[metrics]
  port = 9091
  path = "/metrics"
  # processes = ['app']
```

## Statics

Serve static files directly from Fly Proxy without hitting your app:

```toml
[[statics]]
  guest_path = "/app/public"      # Path inside the container
  url_prefix = "/static/"         # URL prefix to serve from
```

## Restart

```toml
[restart]
  policy = "always"               # "always", "never", "on-failure"
  max_retries = 3                 # Max restart attempts (for "on-failure")
```
