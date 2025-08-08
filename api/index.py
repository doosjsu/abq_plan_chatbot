import os
import re
import logging
from typing import Dict, List, Tuple

from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests

try:
    # New OpenAI SDK (>=1.0)
    from openai import OpenAI
    _openai_client = OpenAI()

    def generate_completion(model: str, messages: List[Dict[str, str]]) -> str:
        resp = _openai_client.chat.completions.create(model=model, messages=messages)
        return (resp.choices[0].message.content or "").strip()
except Exception:  # pragma: no cover
    # Legacy SDK fallback
    import openai as _openai_legacy

    def generate_completion(model: str, messages: List[Dict[str, str]]) -> str:
        _openai_legacy.api_key = os.getenv("OPENAI_API_KEY")
        resp = _openai_legacy.ChatCompletion.create(model=model, messages=messages)
        return (resp["choices"][0]["message"]["content"] or "").strip()


app = Flask(__name__)

# Simple per-instance cache to avoid scraping on every request
_corpus_cache: str | None = None


def get_service_links() -> Dict[str, str]:
    return {
        "permit": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "license": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "application": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "account": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "create account": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "new account": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "register": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "login": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "sign in": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "status": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "check status": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "application status": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "permit status": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "contact": "https://www.cabq.gov/planning/contact",
        "location": "https://www.cabq.gov/planning/contact",
        "located": "https://www.cabq.gov/planning/contact",
        "address": "https://www.cabq.gov/planning/contact",
        "where": "https://www.cabq.gov/planning/contact",
        "phone": "https://www.cabq.gov/planning/contact",
        "bill": "https://www.cabq.gov/311/pay-a-bill",
        "payment": "https://www.cabq.gov/311/pay-a-bill",
        "pay": "https://www.cabq.gov/311/pay-a-bill",
        "planning": "https://www.cabq.gov/planning",
        "division": "https://www.cabq.gov/planning/contact",
        "divisions": "https://www.cabq.gov/planning/contact",
        "building": "https://www.cabq.gov/planning/contact",
        "code": "https://www.cabq.gov/planning/contact",
        "development": "https://www.cabq.gov/planning/contact",
        "urban": "https://www.cabq.gov/planning/contact",
        "agis": "https://www.cabq.gov/planning/contact",
        "business": "https://www.cabq.gov/planning/contact",
        "311": "https://www.cabq.gov/311",
        "help": "https://www.cabq.gov/311",
        "assistance": "https://www.cabq.gov/311",
        "support": "https://www.cabq.gov/311",
        "violation": "https://www.cabq.gov/planning/report-a-violation",
        "complaint": "https://www.cabq.gov/planning/report-a-violation",
        "report": "https://www.cabq.gov/planning/report-a-violation",
    }


def scrape_cabq_pages(urls: List[str]) -> str:
    combined_text = ""
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ")
            combined_text += f"\n\n--- Content from {url} ---\n\n" + page_text
        except Exception as error:
            logging.warning("Could not scrape %s: %s", url, str(error))
    return combined_text


def get_corpus_text() -> str:
    global _corpus_cache
    if _corpus_cache:
        return _corpus_cache

    planning_url = os.getenv("CABQ_PLANNING_URL")
    if not planning_url:
        raise RuntimeError("CABQ_PLANNING_URL not found in environment variables.")

    # Keep it lightweight to avoid timeouts
    urls_to_scrape = [
        planning_url,
        "https://www.cabq.gov/planning/contact",
        "https://www.cabq.gov/311/pay-a-bill",
    ]
    _corpus_cache = scrape_cabq_pages(urls_to_scrape)
    return _corpus_cache


def split_text(text: str, chunk_size: int = 1200, chunk_overlap: int = 150) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - chunk_overlap
        if start < 0:
            start = 0
    return chunks


_STOPWORDS = set(
    "the a an and or but if then else for to of in on at by with from is are was were be being been it this that these those as".split()
)


def rank_chunks(question: str, chunks: List[str], top_k: int = 6) -> List[Tuple[int, int]]:
    q_terms = [t for t in re.findall(r"[a-zA-Z0-9']+", question.lower()) if t not in _STOPWORDS]
    scored: List[Tuple[int, int]] = []
    for idx, ch in enumerate(chunks):
        text_lower = ch.lower()
        score = sum(text_lower.count(term) for term in q_terms)
        scored.append((idx, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def derive_direct_links(user_message: str, answer_text: str) -> List[Dict[str, str]]:
    links_map = get_service_links()
    result: Dict[str, str] = {}
    lower_user = user_message.lower()
    lower_answer = answer_text.lower()

    for keyword, url in links_map.items():
        if keyword in lower_user or keyword in lower_answer:
            result[url] = keyword

    # If answer references visiting the planning site, include it
    website_phrases = [
        "visit the planning department",
        "visit the website",
        "planning department's website",
        "planning website",
    ]
    if any(p in lower_answer for p in website_phrases):
        result["https://www.cabq.gov/planning"] = "planning"

    violation_phrases = [
        "report a violation",
        "file a complaint",
        "violation",
        "complaint",
    ]
    if any(p in lower_answer for p in violation_phrases) and "website" in lower_answer:
        result["https://www.cabq.gov/planning/report-a-violation"] = "violation"

    # Convert to list with titles
    titled: List[Dict[str, str]] = []
    for url, keyword in result.items():
        if keyword in ["permit", "license", "application"]:
            titled.append({"title": "ABQ-PLAN: Apply Online", "url": url})
        elif keyword in [
            "account",
            "create account",
            "new account",
            "register",
            "login",
            "sign in",
        ]:
            titled.append({"title": "ABQ-PLAN: Account Services", "url": url})
        elif keyword in ["status", "check status", "application status", "permit status"]:
            titled.append({"title": "ABQ-PLAN: Check Status", "url": url})
        elif keyword in [
            "contact",
            "location",
            "located",
            "address",
            "where",
            "phone",
        ]:
            titled.append({"title": "Contact Information: View Details", "url": url})
        elif keyword in ["bill", "payment", "pay"]:
            titled.append({"title": "Bill Payment: Pay Online", "url": url})
        elif keyword == "planning":
            titled.append({"title": "Planning Department: Main Page", "url": url})
        elif keyword in [
            "division",
            "divisions",
            "building",
            "code",
            "development",
            "urban",
            "agis",
            "business",
        ]:
            titled.append({"title": "Contact Information: View Details", "url": url})
        elif keyword in ["311", "help", "assistance", "support"]:
            titled.append({"title": "311 Services: Get Help", "url": url})
        elif keyword in ["violation", "complaint", "report"]:
            titled.append({"title": "Violation Reporting: File a Complaint", "url": url})
    return titled


def sanitize_answer(answer_text: str) -> str:
    personal_info_phrases = [
        "alan varela",
        "james aranda",
        "jeremy keiser",
        "director",
        "deputy director",
        "deputy directors",
        "[email protected]",
        "email at",
        "via email",
    ]
    lower_answer = answer_text.lower()
    if any(p in lower_answer for p in personal_info_phrases):
        if "violation" in lower_answer or "complaint" in lower_answer:
            return (
                "To file a complaint for a permit violation, you can contact the "
                "Planning Department at 505-924-3860 or dial 311 (505-768-2000). "
                "They will connect you with the appropriate staff member to handle your complaint."
            )
        return (
            "For this inquiry, please contact the Planning Department at 505-924-3860 "
            "or dial 311 (505-768-2000). They will connect you with the appropriate staff member to assist you."
        )
    return answer_text


def quick_answer_for_keywords(user_message: str) -> Tuple[str, List[Dict[str, str]]] | None:
    msg = user_message.lower()
    links = derive_direct_links(user_message, "")

    def with_links(title_filter: str) -> List[Dict[str, str]]:
        if not links:
            return []
        return [l for l in links if title_filter.lower() in l["title"].lower()]

    if any(k in msg for k in ["create account", "new account", "register", "sign up", "signup", "account setup", "make an account"]):
        answer = (
            "To create an ABQ-PLAN account: \n"
            "1) Go to the ABQ-PLAN online portal.\n"
            "2) Click Register or Create Account.\n"
            "3) Enter your contact information and verify your email.\n"
            "4) Sign in and follow prompts to start applications or check status."
        )
        acct_links = with_links("Account Services") or links
        return answer, acct_links

    if any(k in msg for k in ["sign in", "login", "log in"]):
        answer = (
            "You can sign in to ABQ-PLAN from the online portal. If you don't have an account yet, choose Register."
        )
        acct_links = with_links("Account Services") or links
        return answer, acct_links

    if any(k in msg for k in ["apply", "permit", "license", "application"]):
        answer = (
            "You can apply online through ABQ-PLAN. After signing in, select the appropriate application and follow the steps."
        )
        apply_links = with_links("Apply Online") or links
        return answer, apply_links

    if any(k in msg for k in ["status", "check status"]):
        answer = "You can check your application or permit status after signing in to ABQ-PLAN."
        status_links = with_links("Check Status") or links
        return answer, status_links

    return None


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Missing 'question'"}), 400

    model_name = os.getenv("OPENAI_MODEL")
    if not model_name:
        # Provide a graceful fallback so the UI doesn't just show an error
        qa = quick_answer_for_keywords(question)
        if qa is not None:
            ans, links = qa
            ans = sanitize_answer(ans)
            return jsonify({"answer": ans, "links": links}), 200
        return jsonify({
            "answer": (
                "I don't have specific information about that topic in my current knowledge base. "
                "For this question, I recommend contacting 311 at 505-768-2000 or dialing 311 from any phone. "
                "They can connect you with the appropriate department or provide the most current information."
            )
        }), 200
    if model_name == "gpt-4o-nano":
        model_name = "gpt-3.5-turbo"

    try:
        corpus = get_corpus_text()
    except Exception as error:
        logging.exception("Corpus initialization failed: %s", str(error))
        qa = quick_answer_for_keywords(question)
        if qa is not None:
            ans, links = qa
            ans = sanitize_answer(ans)
            return jsonify({"answer": ans, "links": links}), 200
        return jsonify({
            "answer": (
                "I ran into an initialization issue. Please contact 311 at 505-768-2000 "
                "if you need immediate assistance."
            )
        }), 200

    chunks = split_text(corpus)
    top_idx_scores = rank_chunks(question, chunks, top_k=6)
    selected_context = "\n\n".join(chunks[i] for i, _ in top_idx_scores)

    system_prompt = (
        "You are the ABQ Planning Assistant. Answer using the provided context. "
        "If the answer is not in the context, say you don't have that information and suggest contacting 311 (505-768-2000)."
    )
    user_prompt = (
        f"Question: {question}\n\n" 
        f"Context:\n{selected_context}\n\nProvide a concise and helpful answer."
    )

    try:
        answer = generate_completion(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as error:
        logging.exception("OpenAI error: %s", str(error))
        qa = quick_answer_for_keywords(question)
        if qa is not None:
            ans, links = qa
            ans = sanitize_answer(ans)
            return jsonify({"answer": ans, "links": links}), 200
        return jsonify({
            "answer": (
                "I ran into an issue processing that question. Please contact 311 at 505-768-2000 "
                "if you need immediate assistance."
            )
        }), 200

    # Apply policy sanitization and helpful fallback
    answer_lower = answer.lower()
    unhelpful_phrases = [
        "i don't know",
        "i don't have",
        "no information",
        "cannot find",
        "unable to",
        "not available",
    ]
    if any(p in answer_lower for p in unhelpful_phrases):
        answer = (
            "I don't have specific information about that topic in my current knowledge base. "
            "For this question, I recommend contacting 311 at 505-768-2000 or dialing 311 from any phone. "
            "They can connect you with the appropriate department or provide the most current information."
        )

    answer = sanitize_answer(answer)
    links = derive_direct_links(question, answer)

    return jsonify({"answer": answer, "links": links}), 200


# Support /api/* paths when deployed under Vercel's /api routing
@app.get("/api/health")
def api_health():
    return health()


@app.post("/api/chat")
def api_chat():
    return chat()


# Expose app for Vercel Python runtime (WSGI)
# The variable name 'app' is important for the runtime to detect

