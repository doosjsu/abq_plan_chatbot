import os
import logging
from typing import Dict, List

from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


app = Flask(__name__)


# Globals initialized on cold start. These are safe to cache for the
# lifetime of the serverless instance, but will not persist across instances.
global_vectorstore = None
global_llm = None


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
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ")
            combined_text += f"\n\n--- Content from {url} ---\n\n" + page_text
        except Exception as error:
            logging.warning("Could not scrape %s: %s", url, str(error))
    return combined_text


def build_knowledge_and_models():
    """Build the vectorstore and LLM once per cold start."""
    logging.info("Initializing knowledge base and LLM for serverless instance...")

    planning_url = os.getenv("CABQ_PLANNING_URL")
    if not planning_url:
        raise RuntimeError(
            "CABQ_PLANNING_URL not found in environment variables."
        )

    urls_to_scrape = [
        planning_url,
        "https://www.cabq.gov/planning/department-contact-information",
        "https://www.cabq.gov/planning/contact",
        "https://www.cabq.gov/planning",
        "https://www.cabq.gov/planning/about-the-planning-department",
        "https://www.cabq.gov/311/pay-a-bill",
    ]
    text = scrape_cabq_pages(urls_to_scrape)

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.create_documents([text])

    embeddings = OpenAIEmbeddings()
    # Use /tmp to avoid write restrictions; ephemeral per instance
    vectorstore = Chroma.from_documents(
        docs,
        embeddings,
        collection_name="cabq_planning",
        persist_directory="/tmp/chroma",
    )

    model_name = os.getenv("OPENAI_MODEL")
    if not model_name:
        raise RuntimeError(
            "OPENAI_MODEL not found in environment variables."
        )
    if model_name == "gpt-4o-nano":
        model_name = "gpt-3.5-turbo"

    llm = ChatOpenAI(model=model_name)
    return vectorstore, llm


def ensure_initialized():
    global global_vectorstore, global_llm
    if global_vectorstore is None or global_llm is None:
        global_vectorstore, global_llm = build_knowledge_and_models()


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


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/chat")
def chat():
    ensure_initialized()

    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Missing 'question'"}), 400

    # Create a per-request memory to avoid cross-user leakage
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    chain = ConversationalRetrievalChain.from_llm(
        llm=global_llm,
        retriever=global_vectorstore.as_retriever(),
        memory=memory,
        return_source_documents=False,
        chain_type="stuff",
        max_tokens_limit=4000,
        rephrase_question=True,
    )

    try:
        result = chain({"question": question})
        answer = str(result.get("answer", "")).strip()
    except Exception as error:
        logging.exception("Error generating answer: %s", str(error))
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


# Expose app for Vercel Python runtime (WSGI)
# The variable name 'app' is important for the runtime to detect

