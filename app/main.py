import logging
import time

from flask import Flask, request, jsonify
from app.fibonacci import fibonacci_cached

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("fibonacci_api")

app = Flask(__name__)

MAX_N = 100_000


@app.before_request
def start_timer():
    request._start_time = time.perf_counter()


@app.after_request
def log_request(response):
    elapsed_ms = (time.perf_counter() - request._start_time) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.route("/")
def index():
    return jsonify(
        service="Fibonacci Sequence API",
        endpoints={
            "GET /fibonacci?n=<int>": "Returns the nth Fibonacci number",
            "GET /health": "Health check",
        },
    )


@app.route("/health")
def health_check():
    return jsonify(status="ok")


@app.route("/fibonacci")
def get_fibonacci():
    """Return the nth Fibonacci number.
    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2) for n > 1.
    """
    n_raw = request.args.get("n")

    if n_raw is None:
        return jsonify(error="Missing required query parameter: n"), 422

    try:
        n = int(n_raw)
    except (ValueError, TypeError):
        return jsonify(error="n must be an integer."), 422

    if n < 0:
        return jsonify(error="n must be a non-negative integer."), 422

    if n > MAX_N:
        return jsonify(error=f"n must be <= {MAX_N} to avoid excessive computation."), 422

    result = fibonacci_cached(n)
    return jsonify(n=n, result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
