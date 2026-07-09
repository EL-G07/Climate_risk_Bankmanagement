"""
proxy_server.py

Render (and most single-port PaaS hosts) exposes exactly ONE public port per
web service. app_risk.ipynb and prediction.ipynb run as two independent Dash
servers on internal ports 8050 and 8051 (see run_app.py) - this proxy is what
makes both of them reachable from that one public port.

Routing:
  /risk-calc/*  -> http://127.0.0.1:8051  (prediction.ipynb, Risk Calculator)
  everything else -> http://127.0.0.1:8050  (app_risk.ipynb, Main Dashboard + Map)
"""
import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

DASHBOARD_URL = "http://127.0.0.1:8050"
RISK_CALC_URL = "http://127.0.0.1:8051"

EXCLUDED_RESPONSE_HEADERS = {"content-encoding", "content-length", "transfer-encoding", "connection"}


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
def proxy(path):
    if path.startswith("risk-calc"):
        target = f"{RISK_CALC_URL}/{path}"
    else:
        target = f"{DASHBOARD_URL}/{path}"

    forward_headers = {k: v for k, v in request.headers if k.lower() != "host"}

    upstream = requests.request(
        method=request.method,
        url=target,
        headers=forward_headers,
        data=request.get_data(),
        params=request.args,
        cookies=request.cookies,
        allow_redirects=False,
        stream=True,
        timeout=30,
    )

    response_headers = [
        (k, v) for k, v in upstream.raw.headers.items() if k.lower() not in EXCLUDED_RESPONSE_HEADERS
    ]
    return Response(upstream.content, upstream.status_code, response_headers)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
