import os
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.get("/test")
def test():
    return jsonify({
        "message": "API is working",
        "env_vars": {
            "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
            "has_model": bool(os.getenv("OPENAI_MODEL")),
            "has_planning_url": bool(os.getenv("CABQ_PLANNING_URL")),
        }
    })

@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    
    if "account" in question.lower():
        return jsonify({
            "answer": "To create an ABQ-PLAN account, visit the online portal and click Register.",
            "links": [{"title": "ABQ-PLAN: Account Services", "url": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home"}]
        })
    
    return jsonify({
        "answer": "This is a test response. The API is working but needs configuration.",
        "links": []
    })

# Support /api/* paths when deployed under Vercel's /api routing
@app.get("/api/health")
def api_health():
    return health()

@app.get("/api/test")
def api_test():
    return test()

@app.post("/api/chat")
def api_chat():
    return chat()

# Expose app for Vercel Python runtime (WSGI)

