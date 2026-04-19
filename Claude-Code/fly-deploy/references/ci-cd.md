# CI/CD for Fly.io Deployments

This reference covers setting up automated deployments to Fly.io from CI/CD systems.

## GitHub Actions (Recommended)

### Step 1: Generate a deploy token

```bash
fly tokens create deploy --app <app-name>
```

This creates a scoped token that can only deploy this specific app. For org-wide tokens, use `fly tokens create org`.

### Step 2: Add the token to GitHub

In your GitHub repo: Settings → Secrets and variables → Actions → New repository secret.
- Name: `FLY_API_TOKEN`
- Value: paste the deploy token

### Step 3: Create the workflow file

Create `.github/workflows/fly.yml`:

```yaml
name: Fly Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    name: Deploy app
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

That's the minimal setup. Every push to `main` triggers a deploy.

### Variations

**Deploy only when specific files change:**
```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'Dockerfile'
      - 'fly.toml'
```

**Run tests before deploying:**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**Staging + Production pipeline:**
```yaml
on:
  push:
    branches: [main, staging]

jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only --app my-app-staging
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN_STAGING }}

  deploy-production:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only --app my-app --strategy canary
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN_PRODUCTION }}
```

**Deploy with a specific flyctl version:**
```yaml
- uses: superfly/flyctl-actions/setup-flyctl@master
  with:
    version: 0.3.50
```

## Review Apps (PR Previews)

Fly.io supports ephemeral review apps that spin up for each PR and destroy when the PR is closed.

```yaml
name: Review App

on:
  pull_request:
    types: [opened, synchronize, reopened, closed]

jobs:
  deploy-preview:
    if: github.event.action != 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Create or deploy review app
        run: |
          APP_NAME="pr-${{ github.event.pull_request.number }}-my-app"
          flyctl apps create $APP_NAME --org personal || true
          flyctl deploy --remote-only --app $APP_NAME
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      - name: Comment PR with URL
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `Preview deployed: https://pr-${{ github.event.pull_request.number }}-my-app.fly.dev`
            })

  cleanup:
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl apps destroy pr-${{ github.event.pull_request.number }}-my-app --yes
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

## Other CI Systems

### GitLab CI

```yaml
deploy:
  image: alpine:latest
  stage: deploy
  before_script:
    - apk add --no-cache curl
    - curl -L https://fly.io/install.sh | sh
    - export PATH="$HOME/.fly/bin:$PATH"
  script:
    - flyctl deploy --remote-only
  only:
    - main
  variables:
    FLY_API_TOKEN: $FLY_API_TOKEN
```

### Generic CI (any system with Docker/curl)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"

# Deploy (FLY_API_TOKEN must be set as env var)
flyctl deploy --remote-only
```

## Deploy Tokens vs Auth Tokens

- **Deploy tokens** (`fly tokens create deploy`): Scoped to a single app. Can only deploy, not create/destroy apps or manage secrets. Best for CI/CD.
- **Org tokens** (`fly tokens create org`): Broader access within an organization. Needed for review apps or multi-app workflows.
- **Personal tokens** (`fly tokens create`): Full access to your account. Avoid using these in CI.

Always use the most restrictive token that works for your use case.
