import os
import time
import hmac
import hashlib
import logging
import requests
from flask import Flask, request, jsonify, abort

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_OWNER = os.getenv("REPO_OWNER", "Harshitha-2003-4")
REPO_NAME = os.getenv("REPO_NAME", "flask-gif-app")
WORKFLOW_FILE = os.getenv("WORKFLOW_FILE", "ci.cd.yml")  # filename or workflow id
BRANCH = os.getenv("BRANCH", "docker-flask-version")

if not SLACK_SIGNING_SECRET or not GITHUB_TOKEN:
    logging.warning("Make sure SLACK_SIGNING_SECRET and GITHUB_TOKEN are set in env")

def verify_slack_request(req):
    timestamp = req.headers.get("X-Slack-Request-Timestamp", "")
    slack_sig = req.headers.get("X-Slack-Signature", "")
    if not timestamp or not slack_sig:
        return False
    # prevent replay attacks (allow 5 minutes)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        logging.warning("Slack request timestamp out of range")
        return False
    body = req.get_data(as_text=True)
    basestring = f"v0:{timestamp}:{body}"
    my_sig = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode("utf-8"),
        basestring.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(my_sig, slack_sig)

@app.route("/slack/slash", methods=["POST"])
def slack_slash():
    if not verify_slack_request(request):
        logging.warning("Slack signature verification failed")
        return abort(400, "invalid request signature")

    form = request.form
    command = form.get("command")
    text = form.get("text", "").strip()
    user_name = form.get("user_name") or form.get("user_id")
    response_url = form.get("response_url")

    # parse optional env from slash text (e.g. "/run prod")
    env = "dev"
    if text:
        env = text.split()[0]

    # immediate user-friendly response to Slack
    starter_msg = {
        "response_type": "ephemeral",
        "text": f"Hey {user_name}, attempting to trigger CI/CD for `{BRANCH}` (env={env})..."
    }
    # You may return this immediately; we'll still attempt dispatch synchronously.
    # Returning quickly ensures Slack doesn't time out.
    # We'll call GitHub and then send an update to the response_url.
    # Return the immediate message now and continue. (Slack expects a 200)
    try:
        # Trigger GitHub workflow_dispatch
        api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"
        payload = {
            "ref": BRANCH,
            "inputs": {
                "env": env,
                "actor": user_name or "unknown"
            }
        }
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GITHUB_TOKEN}"
        }
        r = requests.post(api_url, json=payload, headers=headers, timeout=10)
        if r.status_code in (204, 201):
            result_text = f"✅ Workflow dispatch sent for `{BRANCH}` (env={env}). Check Actions tab."
        else:
            result_text = f"❌ Failed to dispatch workflow. GitHub returned {r.status_code}: {r.text}"
            logging.error("GitHub response: %s %s", r.status_code, r.text)
    except Exception as e:
        result_text = f"❌ Exception while calling GitHub: {e}"
        logging.exception("GitHub call failed")

    # send a follow-up message to the response_url so user sees final status
    try:
        if response_url:
            requests.post(response_url, json={
                "response_type": "ephemeral",
                "text": result_text
            }, timeout=5)
    except Exception:
        logging.exception("Failed to post to response_url")

    return jsonify(starter_msg)

@app.route("/health", methods=["GET"])
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
