"""
The backend your page talks to.

It exists for one reason: the API key stays here, on the server, and never
reaches the browser. Compare this with the AI draft page in kit/audit, which
put the key straight into the JavaScript where anyone viewing the page can
read it.

Run it locally with:

    pip install -r requirements.txt
    uvicorn main:app --reload

then open http://127.0.0.1:8000

The file is called main.py and the app is called app because that is what
Vercel looks for. Renaming either one will stop it deploying.
"""

import json
import os
import re
import urllib.error
import urllib.request

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "static")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
MAX_QUESTION = 500

app = FastAPI(title="Ask me")


def load_notes():
    """
    Read static/about_me.md, dropping lines that start with ">".

    Those lines are instructions to whoever edits the file, not facts about
    them, so the assistant must not be able to quote them to a visitor.

    The file lives inside static/ on purpose. Vercel keeps mounted static
    directories in the function bundle, so the deployed backend can still
    read it. A file somewhere else may not survive the build.
    """
    path = os.path.join(SITE, "about_me.md")
    if not os.path.exists(path):
        return ""
    raw = open(path, encoding="utf-8").read()
    kept = [ln for ln in raw.splitlines() if not ln.lstrip().startswith(">")]
    return "\n".join(kept).strip()


def split_sections(notes):
    """Pair each '## heading' with the paragraphs underneath it."""
    sections, heading = [], ""
    for block in notes.split("\n\n"):
        text = " ".join(block.split())
        if not text:
            continue
        if text.startswith("##"):
            heading = text.lstrip("# ")
            continue
        if text.startswith("#"):
            heading = ""          # the file title is not a topic
            continue
        sections.append((heading, text))
    return sections


def demo_answer(question, notes):
    """
    No API key configured, so answer by finding the closest paragraph.

    Deliberately simple, and labelled, so nobody mistakes it for a model.
    It means the page works from the first minute, before anyone has a key.
    """
    stop = {"what", "how", "the", "and", "you", "your", "are", "for",
            "have", "has", "with", "that", "this", "can", "tell", "about",
            "did", "does", "any"}
    q = {w for w in re.findall(r"[a-z]+", question.lower())
         if len(w) > 2 and w not in stop}

    sections = split_sections(notes)
    best, score = None, 0
    for heading, text in sections:
        words = set(re.findall(r"[a-z]+", (heading + " " + text).lower()))
        hit = len(q & words)
        if hit > score:
            best, score = text, hit

    if not best or score == 0:
        # A dead end is a bad answer even when it is a true one. Say what the
        # notes do cover: the difference between "no" and "not that, but here
        # is what I have".
        topics = list(dict.fromkeys(h for h, _ in sections if h))
        if topics:
            return ("[demo mode] My notes do not cover that. They cover: "
                    + ", ".join(topics) + ".")
        return "[demo mode] My notes do not cover that."
    return "[demo mode] " + best


def call_model(question, notes, api_key):
    """Ask the real model. Raises RuntimeError with a readable message."""
    system = (
    "You answer questions about Abhinaya using ONLY the information "
    "provided in the notes below.\n\n"
    "STRICT ACCURACY RULES:\n"
    "1. Never invent or assume personal information.\n"
    "2. Never invent qualifications, universities or employers.\n"
    "3. Never invent years of experience, salaries or achievements.\n"
    "4. Do not confuse studying at a university with graduating.\n"
    "5. If the notes do not explicitly support an answer, "
    "respond with exactly: I do not know.\n"
    "6. Do not use general knowledge to fill gaps.\n"
    "7. Answer only with facts supported by the notes.\n\n"
    "Keep answers concise, within three sentences.\n\n"
    "NOTES:\n" + notes
    )
    payload = json.dumps({
        "model": MODEL, "temperature": 0, "max_tokens": 300,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": question}],
    }).encode("utf-8")
    req = urllib.request.Request(
    GROQ_URL,
    data=payload,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "AbhinayaPortfolio/1.0"
    }
)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as err:
        error_body = err.read().decode("utf-8", errors="replace")
        print("GROQ ERROR:", err.code, error_body)

        raise RuntimeError(
        f"Groq API returned {err.code}: {error_body}"
    )
        
    except urllib.error.URLError as err:
        raise RuntimeError(f"could not reach the model API: {err.reason}")
    except (KeyError, IndexError, ValueError):
        raise RuntimeError("the model replied in a shape I did not expect")


# ---- routes -------------------------------------------------------------
# These are declared BEFORE the static mount at the bottom of the file.
# On Vercel, a route declared before the mount wins over a file of the same
# name. Declared after, the file would win and the API would break.

@app.get("/api/health")
def health():
    """Open this first when something is wrong. It says what is loaded."""
    notes = load_notes()
    return {
        "ok": True,
        "key_configured": bool(os.environ.get("GROQ_API_KEY")),
        "notes_loaded": bool(notes),
        "notes_chars": len(notes),
        "mode": "model" if os.environ.get("GROQ_API_KEY") else "demo",
    }


@app.post("/api/ask")
async def ask(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "the body must be JSON"}, status_code=400)

    question = str(body.get("question", "")).strip()
    if not question:
        return JSONResponse({"error": "ask something"}, status_code=400)
    if len(question) > MAX_QUESTION:
        return JSONResponse(
            {"error": f"questions are limited to {MAX_QUESTION} characters"},
            status_code=413)

    notes = load_notes()
    if not notes:
        return JSONResponse(
            {"error": "static/about_me.md is missing, so there is nothing "
                      "to answer from"},
            status_code=503)

    key = os.environ.get("GROQ_API_KEY")
    try:
        answer = call_model(question, notes, key) if key \
            else demo_answer(question, notes)
    except RuntimeError as err:
        return JSONResponse({"error": str(err)}, status_code=502)

    return {"answer": answer, "mode": "model" if key else "demo"}

@app.get("/api/projects")
def projects():
    path = os.path.join(SITE, "projects.json")

    if not os.path.exists(path):
        return JSONResponse(
            {"error": "static/projects.json is missing"},
            status_code=503
        )

    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as err:
        return JSONResponse(
            {"error": f"projects.json is not valid JSON: {err}"},
            status_code=500
        )


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    """
    Anything we did not predict still gets a readable answer instead of a
    blank 500. If you add your own endpoint and it breaks, you will see this.
    """
    return JSONResponse(
        {"error": "something broke on the server",
         "where": str(request.url.path),
         "hint": "Check the terminal running uvicorn, or Runtime Logs on "
                 "Vercel. The real error is printed there."},
        status_code=500)


# The page itself. html=True makes "/" serve static/index.html.
# This mount is LAST on purpose. See the note above the routes.
app.mount("/", StaticFiles(directory=SITE, html=True), name="site")
