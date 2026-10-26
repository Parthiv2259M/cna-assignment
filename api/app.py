import os
import json
import socket
import time

import redis
from flask import Flask, jsonify

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

POD = socket.gethostname()
OPTIONS = ["Docker", "Kubernetes", "Terraform", "GitHub Actions", "Trivy", "Prometheus"]


@app.route("/api/vote/<option>", methods=["POST"])
def vote(option):
    if option not in OPTIONS:
        return jsonify(error="invalid option"), 400
    r.incr(f"votes:{option}")
    r.lpush("activity", json.dumps({"option": option, "pod": POD, "ts": int(time.time())}))
    r.ltrim("activity", 0, 9)
    return jsonify(ok=True, pod=POD)


@app.route("/api/results")
def results():
    counts = {o: int(r.get(f"votes:{o}") or 0) for o in OPTIONS}
    total = sum(counts.values())
    items = [
        {"name": o, "votes": v, "percent": round(v * 100 / total, 1) if total else 0}
        for o, v in counts.items()
    ]
    leader = max(items, key=lambda i: i["votes"])["name"] if total else None
    return jsonify(options=items, total=total, leader=leader, pod=POD)


@app.route("/api/activity")
def activity():
    return jsonify([json.loads(x) for x in r.lrange("activity", 0, 9)])


@app.route("/api/reset", methods=["POST"])
def reset():
    for o in OPTIONS:
        r.delete(f"votes:{o}")
    r.delete("activity")
    return jsonify(ok=True)


@app.route("/api/health")
def health():
    try:
        r.ping()
        return jsonify(status="ok", redis="up", pod=POD)
    except redis.RedisError:
        return jsonify(status="degraded", redis="down", pod=POD), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)