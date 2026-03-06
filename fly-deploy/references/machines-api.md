# Fly Machines API Reference

The Machines API gives fine-grained control over Fly Machines — the Firecracker microVMs that run your app. Use this when `fly deploy` isn't flexible enough: custom orchestration, dynamic scaling, ephemeral workers, or infrastructure automation.

## When to Use the Machines API vs fly deploy

Use **fly deploy** when:
- Standard web app deployment
- Rolling/canary/bluegreen strategies are sufficient
- You want Fly Launch to manage machine lifecycle

Use the **Machines API** when:
- Building custom orchestration or deployment tooling
- Spawning ephemeral worker machines on demand
- Fine-grained control over individual machines
- Dynamic scaling based on custom logic
- Running one-off tasks or batch jobs

## Authentication

```bash
# Set up environment variables
export FLY_API_HOSTNAME="https://api.machines.dev"
export FLY_API_TOKEN=$(fly tokens deploy)

# For machine-to-machine within Fly's private network:
export FLY_API_HOSTNAME="http://_api.internal:4280"
```

All requests require the token in the Authorization header:
```
Authorization: Bearer <FLY_API_TOKEN>
```

## Core Endpoints

### Apps

```bash
# List apps in an org
curl -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps?org_slug=personal"

# Create an app
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$FLY_API_HOSTNAME/v1/apps" \
  -d '{"app_name": "my-app", "org_slug": "personal"}'
```

### Machines

```bash
# List machines for an app
curl -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines"

# Create a machine
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines" \
  -d '{
    "name": "worker-1",
    "region": "ord",
    "config": {
      "image": "my-app:latest",
      "guest": {
        "cpu_kind": "shared",
        "cpus": 1,
        "memory_mb": 256
      },
      "env": {
        "ROLE": "worker"
      },
      "services": [],
      "auto_destroy": true
    }
  }'

# Start a stopped machine
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines/<machine-id>/start"

# Stop a machine
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines/<machine-id>/stop"

# Delete a machine
curl -X DELETE -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines/<machine-id>?force=true"

# Execute a command in a running machine
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines/<machine-id>/exec" \
  -d '{"cmd": ["echo", "hello"]}'

# Wait for a machine to reach a specific state
curl -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines/<machine-id>/wait?state=started&timeout=30"
```

### Machine Configuration Object

The `config` object in machine creation/update supports:

```json
{
  "image": "registry.fly.io/my-app:deployment-xxxxx",
  "guest": {
    "cpu_kind": "shared",
    "cpus": 1,
    "memory_mb": 256,
    "gpu_kind": "l40s",
    "gpus": 1
  },
  "env": {
    "KEY": "value"
  },
  "services": [
    {
      "protocol": "tcp",
      "internal_port": 8080,
      "ports": [
        {
          "port": 443,
          "handlers": ["tls", "http"]
        }
      ],
      "checks": [
        {
          "type": "http",
          "port": 8080,
          "method": "GET",
          "path": "/health",
          "interval": "10s",
          "timeout": "2s"
        }
      ],
      "concurrency": {
        "type": "requests",
        "hard_limit": 250,
        "soft_limit": 200
      },
      "autostart": true,
      "autostop": "stop",
      "min_machines_running": 1
    }
  ],
  "mounts": [
    {
      "volume": "vol_xxxx",
      "path": "/data"
    }
  ],
  "restart": {
    "policy": "on-failure",
    "max_retries": 3
  },
  "auto_destroy": false,
  "dns": {},
  "processes": [],
  "metadata": {
    "managed_by": "my-tool"
  }
}
```

### Volumes

```bash
# List volumes
curl -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/volumes"

# Create a volume
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/volumes" \
  -d '{
    "name": "data",
    "region": "ord",
    "size_gb": 10
  }'

# Extend a volume
curl -X PUT -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/volumes/<volume-id>/extend" \
  -d '{"size_gb": 20}'

# Create a snapshot
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/volumes/<volume-id>/snapshots"
```

### Certificates

```bash
# List certificates
curl -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/certificates"

# Add a certificate (ACME/Let's Encrypt)
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/certificates/acme" \
  -d '{"hostname": "example.com"}'

# Upload a custom certificate
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/certificates/custom" \
  -d '{
    "hostname": "example.com",
    "fullchain": "-----BEGIN CERTIFICATE-----\n...",
    "private_key": "-----BEGIN PRIVATE KEY-----\n..."
  }'
```

### Machine Leases

Leases provide distributed coordination — a machine with an active lease can only be modified by the lease holder.

```bash
# Acquire a lease
curl -X POST -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines/<machine-id>/lease" \
  -d '{"ttl": 30}'

# Release a lease
curl -X DELETE -H "Authorization: Bearer $FLY_API_TOKEN" \
  "$FLY_API_HOSTNAME/v1/apps/my-app/machines/<machine-id>/lease" \
  -H "fly-machine-lease-nonce: <nonce-from-acquire>"
```

## Rate Limits

The Machines API has per-action, per-machine rate limits. If you're doing bulk operations, add small delays between requests. The API returns standard HTTP 429 responses when rate limited.

## Common Patterns

### Ephemeral Worker
Spawn a machine, run a task, and let it self-destruct:
```json
{
  "config": {
    "image": "my-app:latest",
    "auto_destroy": true,
    "restart": {"policy": "never"},
    "env": {"TASK_ID": "abc123"}
  }
}
```

### Scheduled Scaling
Use a cron job or external scheduler to scale machines up/down based on demand patterns:
- Morning: create additional machines in high-traffic regions
- Night: stop machines in low-traffic regions
- Use machine metadata to track which machines were auto-scaled

### Canary with Machines API
1. Create one new machine with the updated image
2. Wait for health checks to pass
3. Monitor for errors in logs
4. If healthy, update remaining machines one by one
5. If unhealthy, destroy the canary and abort
