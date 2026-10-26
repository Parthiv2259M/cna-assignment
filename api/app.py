import os
from flask import Flask, jsonify
import redis

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
OPTIONS = ["Docker", "Kubernetes", "Terraform"]

@app.route("/api/vote/<option>", methods=["POST"])
def vote(option):
    if option not in OPTIONS:
        return jsonify(error="invalid option"), 400
    r.incr(f"votes:{option}")
    return jsonify(ok=True)

@app.route("/api/results")
def results():
    return jsonify({o: int(r.get(f"votes:{o}") or 0) for o in OPTIONS})

@app.route("/api/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)