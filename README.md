# Fibonacci Sequence API

A production-ready REST API that computes and returns the *n*th number in the Fibonacci sequence, built with **Python 3.12** and **Flask**.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Reference](#api-reference)
3. [Running Tests](#running-tests)
4. [Project Structure](#project-structure)
5. [Design Decisions](#design-decisions)
6. [Production Deployment](#production-deployment)
7. [AI Usage Disclosure](#ai-usage-disclosure)

---

## Quick Start

### Prerequisites

- Python 3.11+ **or** Docker

### Option A – Run locally

```bash
# Clone the repository
git clone https://github.com/XinLu0/Fibonacci_Sequence_API.git
cd Fibonacci_Sequence_API

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start the server
flask --app app.main run --port 8000 --reload
```

The API is now available at **http://localhost:8000**.

### Option B – Run with Docker

```bash
docker compose up --build
```

Or without Compose:

```bash
docker build -t fibonacci-api .
docker run -p 8000:8000 fibonacci-api
```

---

## API Reference

### `GET /fibonacci?n={n}`

Returns the *n*th Fibonacci number.

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `n` | int | yes | 0 ≤ n ≤ 100 000 | Index into the Fibonacci sequence |

**Example requests:**

```bash
curl "http://localhost:8000/fibonacci?n=2"
# {"n": 2, "result": 1}

curl "http://localhost:8000/fibonacci?n=10"
# {"n": 10, "result": 55}
```

**Error responses:**

| Status | Condition |
|--------|-----------|
| 422 | Missing `n`, non-integer, negative, or exceeds 100 000 |

### `GET /health`

Liveness / readiness probe.

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### Interactive docs

You can explore the API using tools like **curl**, **Postman**, or **HTTPie**.

---

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Tests cover:
- **Unit tests** – correctness of the Fibonacci computation for known values, edge cases (n=0, n=1), negative input, and large values.
- **Integration tests** – every API endpoint, including validation errors, boundary conditions, and response format.

---

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── fibonacci.py        # Pure Fibonacci computation logic
│   └── main.py             # Flask application & endpoints
├── tests/
│   ├── __init__.py
│   ├── test_fibonacci.py   # Unit tests for computation
│   └── test_api.py         # API integration tests
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD pipeline
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Flask** | Lightweight, well-documented, large ecosystem of extensions, easy to learn and deploy with Gunicorn. |
| **Iterative algorithm** | O(n) time, O(1) space. No recursion depth limits. Reliable for n up to 100 000. |
| **LRU cache** | Wraps the iterative function so repeated queries for the same `n` return instantly. Bounded at 1 024 entries to cap memory. |
| **Upper bound on n** | Prevents a single request from monopolising the CPU. 100 000 is generous but still computes in well under a second. |
| **Separation of concerns** | `fibonacci.py` is a pure module with no web dependencies — easy to unit-test and reuse. `main.py` handles HTTP concerns only. |

---

## Production Deployment

### Containerization

The included **Dockerfile** produces a minimal image based on `python:3.12-slim`. It:

- Runs as a **non-root user** (`appuser`) for security.
- Sets `PYTHONUNBUFFERED=1` so logs appear immediately.
- Includes a **HEALTHCHECK** directive used by Docker and orchestrators.

Build and push to a registry:

```bash
docker build -t ghcr.io/<org>/fibonacci-api:1.0.0 .
docker push ghcr.io/<org>/fibonacci-api:1.0.0
```

### CI/CD

The repository ships a **GitHub Actions** workflow (`.github/workflows/ci.yml`) that:

1. Runs the test suite on Python 3.11 and 3.12.
2. On merge to `main`, builds the Docker image and performs a smoke test (health check + sample request).

To extend this for full CD, add a step that pushes the image to a container registry and triggers a rolling deployment (e.g., via `kubectl set image` or an ArgoCD sync).

### Monitoring & Logging

- **Structured request logs** – Every request is logged with method, path, status code, and latency (middleware in `main.py`). In production, switch to JSON logging (e.g., `python-json-logger`) for easy ingestion by ELK.
- **Health endpoint** – `GET /health` is designed for Kubernetes `livenessProbe` / `readinessProbe` or load-balancer health checks.
- **Metrics** – For deeper observability, emit metrics via **StatsD** (`statsd` Python client) or **Telegraf** (with its StatsD input plugin). Both are lightweight, language-agnostic, and pair well with backends like Graphite or InfluxDB for dashboards and alerting.
- **Tracing** – OpenTelemetry can be added for distributed tracing if this service becomes part of a larger system.

### Scaling

| Strategy | Detail |
|----------|--------|
| **Horizontal scaling** | The API is stateless — deploy multiple replicas behind a load balancer (e.g., Kubernetes `Deployment` with an `HPA` based on CPU or request rate). |
| **Gunicorn workers** | For a single host, run `gunicorn app.main:app --workers 4` to utilise multiple CPU cores. |
| **Caching layer** | For very high traffic, place a reverse-proxy cache (Nginx, Varnish) or CDN in front of the API. Fibonacci responses are deterministic and highly cacheable (`Cache-Control: public, max-age=86400`). |
| **Rate limiting** | Protect against abuse with a rate limiter (e.g., `slowapi` or API-gateway level limits). |

### Kubernetes example (abbreviated)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fibonacci-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fibonacci-api
  template:
    spec:
      containers:
        - name: api
          image: ghcr.io/<org>/fibonacci-api:1.0.0
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fibonacci-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fibonacci-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## AI Usage

AI-assisted tools were used during this project, but the final implementation decisions, validation, and modifications were done manually.

### Where I used AI

I used AI to help with:
- Brainstorming the API structure.
- Generating an initial draft of boilerplate code.
- Suggesting edge cases and unit test scenarios.
- Reviewing the README for clarity.
- Drafting production deployment considerations such as Docker, CI/CD, logging, monitoring, and scaling.

### How I used it

I treated AI as a development assistant rather than a source of truth. I asked it for suggestions, compared the output against the project requirements, and only accepted parts that I understood and could explain.

### What I accepted vs modified

Accepted:
- Basic API route structure.
- Some README wording.
- Suggested test cases for common Fibonacci inputs.

Modified:
- Input validation logic.
- Error responses for missing, negative, or non-integer values.
- Fibonacci implementation to use an iterative approach instead of recursion.
- Production deployment notes to match how I would realistically deploy the service.

### How I validated correctness

I validated the implementation by:
- Running the API locally.
- Testing known Fibonacci values such as:
  - `F(0) = 0`
  - `F(1) = 1`
  - `F(2) = 1`
  - `F(10) = 55`
- Running automated tests for valid and invalid inputs.
- Reviewing the code manually for readability and edge cases.

### What AI got wrong or incomplete

The AI-generated suggestions were useful but incomplete in several areas:
- It initially suggested a recursive Fibonacci implementation, which is inefficient for larger values of `n`.
- It did not fully handle invalid inputs such as missing, negative, or non-integer values.
- The first README draft was too generic and needed to be adjusted to explain actual implementation and deployment choices.
- The production deployment section needed more practical detail around containerization, CI/CD, logging, monitoring, and scaling.
- The CI workflow built the Docker image but never pushed it to a registry — the image was discarded when the ephemeral runner was destroyed.
- The CI and CD pipelines both built the Docker image independently, wasting time and risking deploying a different image than the one that was tested.
- The Docker image tag used `github.repository_owner` which preserves the original GitHub username casing (e.g., "XinLu0"), causing `docker build` to fail because Docker tags must be lowercase.
- The `GITHUB_TOKEN` lacked `packages: write` permission, so `docker push` to GHCR was denied with "installation not allowed to Create organization package".

