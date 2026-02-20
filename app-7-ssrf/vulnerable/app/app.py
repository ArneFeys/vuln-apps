import os
import requests
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/fetch", methods=["POST"])
def fetch_url():
    """Vulnerable endpoint: fetches any URL the user provides without validation."""
    url = request.form.get("url", "")
    if not url:
        return render_template("index.html", error="Please provide a URL.")

    try:
        # VULNERABLE: No validation on the URL — allows SSRF to internal services,
        # cloud metadata endpoints (e.g. http://169.254.169.254/), localhost, etc.
        resp = requests.get(url, timeout=5)
        return render_template(
            "index.html",
            url=url,
            status=resp.status_code,
            body=resp.text[:5000],
        )
    except Exception as e:
        return render_template("index.html", url=url, error=str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
