---
name: fly-deploy
description: >
  Configure and deploy Docker-based applications to Fly.io. Use this skill whenever the user mentions fly.io, flyctl, fly deploy, fly launch, fly.toml, Fly Machines, or wants to deploy a containerized application to Fly.io's platform. Also trigger when the user asks about multi-region deployments on Fly, Fly.io secrets management, custom domains with Fly, Fly.io autoscaling, Fly Machines API, Fly volumes, or CI/CD pipelines targeting Fly.io (e.g. GitHub Actions with flyctl). Even if the user just says "deploy this to fly" or "set up fly for my app", use this skill. Covers the full lifecycle including project init, Dockerfile review, fly.toml generation, secrets, volumes, databases, custom domains, SSL certificates, multi-region scaling, Machines API, deployment strategies, health checks, and CI/CD automation.
---

# Fly.io Deployment Skill

This skill helps configure and deploy Docker-based applications to Fly.io. It covers the full deployment lifecycle — from initial project setup through production-grade multi-region deployments.

## Core Principle: Ask First, Then Configure

Every deployment is different. Before generating any configuration or running any commands, interview the user to understand their specific requirements. Don't assume defaults — ask.

## Step 1: Gather Requirements

Before writing any config, ask the user about their deployment. Collect answers to as many of these as are relevant:

### Essential Questions
1. **What's the app?** — What language/framework, what does it do, does it already have a Dockerfile?
2. **What region(s)?** — Where should it run? Single region or multi-region? (Fly has 30+ regions; common ones: `ord` Chicago, `iad` Virginia, `lhr` London, `nrt` Tokyo, `sin` Singapore, `syd` Sydney)
3. **What size?** — CPU/memory requirements? (`shared-cpu-1x` with 256MB is the smallest; `performance` CPUs available for heavier workloads; GPU options exist for ML)
4. **Does it need a database?** — Fly Postgres, SQLite on a volume, Redis, or external?
5. **Does it need persistent storage?** — Volumes for data that must survive restarts?
6. **Any secrets/env vars?** — API keys, database URLs, credentials?

### Advanced Questions (ask if the user seems to need them)
7. **Custom domain?** — Do they have a domain they want to point at this app?
8. **Deployment strategy?** — Rolling (default), canary, bluegreen, or immediate?
9. **Autoscaling?** — Should machines auto-stop when idle and auto-start on traffic? Min machines?
10. **CI/CD?** — Do they want automatic deploys from GitHub or another CI system?
11. **Multiple process groups?** — Web server + background workers, for example?
12. **Health checks?** — Custom health check endpoints?

Adapt your questions to what the user has already told you. If they've described their app in detail, skip questions you can infer answers to and confirm your assumptions.

**Do not generate fly.toml, Dockerfiles, or run any `fly` commands until you've gathered enough context.** It's much better to ask two or three clarifying questions upfront than to produce a config that doesn't match the user's needs. When you do generate config, explain your choices so the user can push back.

## Step 2: Review or Create the Dockerfile

Fly.io deploys Docker images. If the user already has a Dockerfile, review it. If not, help them create one.

### Dockerfile Best Practices for Fly.io
- Use multi-stage builds to keep images small — a builder stage for compiling and a slim runtime stage
- The app should listen on `0.0.0.0`, not `127.0.0.1` or `localhost` — Fly's proxy needs to reach it
- Expose the port the app listens on (typically 8080 or 3000, configurable in fly.toml via `internal_port`)
- Handle `SIGTERM` gracefully for zero-downtime deploys — Fly sends `SIGINT` by default, configurable via `kill_signal`
- If the app needs build-time secrets (e.g., private npm tokens), use Docker build secrets or Fly's `[build.args]`, not environment variables baked into the image

### Common Dockerfile patterns

**Node.js (multi-stage)**
```dockerfile
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Python (multi-stage)**
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

**Go**
```dockerfile
FROM golang:1.22 AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o server .

FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
```

Adapt these to the user's specific framework. Don't just copy-paste — tailor to their stack.

## Step 3: Generate fly.toml

The `fly.toml` file is the heart of a Fly deployment. Generate it based on the user's answers from Step 1.

Read `references/fly-toml-reference.md` for the full configuration reference with all available sections and options. Below is the high-level structure:

```toml
app = 'my-app-name'
primary_region = 'ord'

[build]
  # Usually auto-detected from Dockerfile; specify if needed
  # dockerfile = "Dockerfile"

[env]
  # Non-secret environment variables
  PORT = "8080"
  NODE_ENV = "production"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 1

  [http_service.concurrency]
    type = "requests"
    hard_limit = 250
    soft_limit = 200

  [[http_service.checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "5s"
    method = "GET"
    path = "/health"

[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1
```

### Key decisions to discuss with the user

**auto_stop_machines**: Set to `'stop'` to save money (machines stop when idle and restart on traffic). Set to `'off'` if the app needs to stay running (e.g., WebSocket servers, cron jobs). There's also `'suspend'` which is faster to resume than stop.

**min_machines_running**: How many machines should always be warm? 0 means full scale-to-zero. 1 means at least one is always ready (eliminates cold-start latency). 2 for redundancy.

**Deployment strategy**: The default `rolling` is safe for most apps. Use `canary` to test a single machine before rolling out. Use `bluegreen` for zero-downtime with full rollback capability (but uses 2x resources during deploy).

## Step 4: Set Up Infrastructure

Based on what the user needs, set up supporting infrastructure.

### Secrets
Secrets are encrypted and injected as environment variables at runtime. They never appear in logs or fly.toml.

```bash
# Set secrets (triggers a redeploy by default)
fly secrets set DATABASE_URL="postgres://..." API_KEY="sk-..."

# Stage secrets without immediate redeploy
fly secrets set --stage DATABASE_URL="postgres://..."
fly secrets deploy  # deploy all staged secrets at once

# List secrets (shows names and digests, never values)
fly secrets list

# Import from a file
cat .env | fly secrets import
```

Tell the user: never put sensitive values in `[env]` in fly.toml — those are visible in plaintext. Use `fly secrets set` instead.

### Volumes (Persistent Storage)
Volumes are region-specific NVMe storage. One volume attaches to one machine at a time.

```bash
# Create a volume
fly volumes create data --region ord --size 10  # 10 GB

# List volumes
fly volumes list
```

In fly.toml:
```toml
[mounts]
  source = "data"
  destination = "/data"
```

Important caveats to mention to the user:
- Volumes are pinned to a region — a machine in `ord` can't use a volume in `lhr`
- If you need multi-region with volumes, you need volumes in each region
- Volumes survive machine restarts but are not replicated — recommend snapshots for backup
- For multi-region databases, consider Fly Postgres or LiteFS instead of raw volumes

### Databases

**Fly Postgres** (managed):
```bash
fly postgres create --name my-db --region ord
fly postgres attach my-db  # attaches to current app, sets DATABASE_URL secret
```

**SQLite on a volume**: Great for small apps. Mount a volume and point your app's SQLite at the mount path. Consider using LiteFS for read replicas across regions.

### IP Addresses
```bash
# Allocate public IPs (needed for custom domains)
fly ips allocate-v4
fly ips allocate-v6

# List IPs
fly ips list
```

## Step 5: Custom Domains & SSL

If the user wants a custom domain, walk them through this process:

1. **Allocate IPs** if not already done (see above)
2. **Add the certificate**:
   ```bash
   fly certs add example.com
   fly certs add www.example.com  # if they want www too
   ```
3. **Configure DNS** at their domain registrar:
   - A record → the IPv4 address from `fly ips list`
   - AAAA record → the IPv6 address from `fly ips list`
   - For `www`: CNAME → `<app-name>.fly.dev`
4. **Verify**: Fly auto-provisions Let's Encrypt certificates once DNS is verified
   ```bash
   fly certs check example.com
   fly certs list
   ```

For wildcard certificates (`*.example.com`), the DNS-01 challenge is required — Fly will show the CNAME record needed for `_acme-challenge`.

Read `references/fly-toml-reference.md` for TLS-specific configuration options if the user needs custom certificate uploads or specific TLS settings.

## Step 6: Multi-Region Deployment

If the user wants multi-region, help them think through the tradeoffs:

**Stateless apps** (API servers, web frontends): Easy — just add machines in more regions.
```bash
# Clone a machine into a new region
fly machine clone --region lhr
fly machine clone --region nrt

# Or scale with fly scale
fly scale count 2 --region ord
fly scale count 1 --region lhr
```

**Stateful apps** (databases): Harder. Options include Fly Postgres with read replicas, LiteFS for SQLite replication, or using a primary-region pattern where writes go to one region and reads are served locally.

Key fly.toml settings for multi-region:
```toml
primary_region = 'ord'  # write region

[http_service]
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 1
```

The `PRIMARY_REGION` environment variable is automatically set on every machine, so app code can use it to determine whether to handle writes locally or forward them.

## Step 7: Deploy

```bash
# First deployment (creates app + initial config)
fly launch --no-deploy    # configure without deploying
fly deploy                # deploy when ready

# Subsequent deployments
fly deploy

# Deployment with specific strategy
fly deploy --strategy canary
fly deploy --strategy bluegreen

# Monitor deployment
fly status
fly logs
```

### Health Checks Matter
Fly won't route traffic to a machine until it passes health checks. If the user's app doesn't have a `/health` endpoint, help them add one. A basic health check should return 200 OK when the app is ready to serve.

### Release Commands
For running migrations before deploy:
```toml
[deploy]
  release_command = "python manage.py migrate"
  # or: "npx prisma migrate deploy"
  # or: "bundle exec rails db:migrate"
```

Release commands run in a temporary machine before the new version goes live. If they fail, the deploy is aborted.

## Step 8: CI/CD (if requested)

Read `references/ci-cd.md` for detailed GitHub Actions setup and other CI/CD patterns.

Quick setup:
1. Generate a deploy token: `fly tokens create deploy`
2. Add it as `FLY_API_TOKEN` secret in GitHub repo settings
3. Create `.github/workflows/fly.yml` — see the reference file for the template

## Step 9: Machines API (Advanced)

If the user needs fine-grained control over machines beyond what `fly deploy` provides, read `references/machines-api.md` for the REST API reference, including creating machines, managing leases, executing commands, and building custom orchestration.

## Troubleshooting Checklist

When a deployment fails or an app isn't working, check these in order:

1. **`fly logs`** — Almost always the first thing to check
2. **`fly status`** — Are machines running? What state are they in?
3. **`fly checks list`** — Are health checks passing?
4. **Port mismatch** — Does `internal_port` in fly.toml match what the app actually listens on?
5. **Binding address** — Is the app listening on `0.0.0.0`, not `127.0.0.1`?
6. **Memory** — Is the app OOM-killed? Check `fly logs` for `OOM` and consider increasing `memory` in `[[vm]]`
7. **Secrets** — Are all required env vars set? `fly secrets list` to check names
8. **DNS** — For custom domains: `fly certs check <hostname>` to verify
9. **Volumes** — If using volumes, is the mount path correct? Is the volume in the same region as the machine?

## Important Notes

- Always confirm with the user before running any `fly` commands — especially destructive ones like `fly apps destroy` or `fly secrets unset`
- Fly.io bills for running machines, volumes, and bandwidth. Mention cost implications when recommending configurations (e.g., `auto_stop_machines = 'stop'` saves money; `performance` CPUs cost more than `shared`)
- The `fly.toml` file should be committed to version control, but secrets should never be
- When in doubt, link the user to the relevant Fly.io docs page for the most current information
