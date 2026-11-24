"""
Measure your own assistant (Option D).

The question is not "does it work". The question is: when it does not know
something, does it say so, or does it make something up?

Write your questions in questions.json. Mark each one answerable true or
false. Answerable false means the answer is NOT in static/about_me.md, so the
only correct behaviour is to say it does not know.

One thing to understand before you argue with the score. This measures your
notes AND the model together, not the model alone. If you add a fact to your
notes, the question it answers becomes answerable, and you must change that
flag to true. A truthful "I have not worked there" is a correct answer, not a
refusal, and the tool cannot tell the two apart. That judgement is yours.

Run it with the server running:

    python3 measure.py
    python3 measure.py --url https://your-site.vercel.app

It prints a table and one number. Put that number on your page.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

# Phrases that mean "I do not know". Add your own if your model says it
# differently. Be honest here: widening this list to make your score look
# better is cheating at a test you set yourself.
REFUSALS = [
    "do not cover", "does not cover", "do not know", "don't know",
    "not know", "no information", "not mentioned", "not in my notes",
    "cannot answer", "can't answer", "unable to answer", "not sure",
]


def looks_like_refusal(answer):
    low = answer.lower()
    return any(p in low for p in REFUSALS)


def ask(url, question, timeout=60):
    payload = json.dumps({"question": question}).encode("utf-8")
    req = urllib.request.Request(
        url.rstrip("/") + "/api/ask", data=payload,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")).get("answer", "")
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")
        return f"[HTTP {err.code}] {body[:120]}"
    except urllib.error.URLError as err:
        print(f"\nCould not reach {url}")
        print(f"Reason: {err.reason}")
        print("Is the server running? Try: uvicorn main:app --reload")
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--questions", default=os.path.join(HERE, "questions.json"))
    args = ap.parse_args()

    if not os.path.exists(args.questions):
        print(f"No questions file at {args.questions}")
        sys.exit(1)
    items = json.load(open(args.questions, encoding="utf-8"))

    print(f"\nAsking {len(items)} questions of {args.url}\n")
    print(f"  {'#':<3} {'should':<10} {'did':<10} {'ok':<4} question")
    print("  " + "-" * 72)

    right = 0
    invented = []
    for i, item in enumerate(items, 1):
        q, answerable = item["question"], item["answerable"]
        answer = ask(args.url, q)
        refused = looks_like_refusal(answer)
        # Correct = answered when it could, refused when it could not.
        ok = (not refused) if answerable else refused
        right += ok
        if answerable is False and not refused:
            invented.append((q, answer))
        print(f"  {i:<3} {'answer' if answerable else 'refuse':<10} "
              f"{'refused' if refused else 'answered':<10} "
              f"{'yes' if ok else 'NO':<4} {q[:44]}")

    total = len(items)
    print("\n  " + "-" * 72)
    print(f"  {right} of {total} correct ({100*right//total}%)\n")

    if invented:
        print(f"  It answered {len(invented)} question(s) you marked as not")
        print("  answerable from your notes. Here is the first one:\n")
        q, a = invented[0]
        print(f"    Q: {q}")
        print(f"    A: {a[:220]}\n")
        print("  Read that answer and decide which of these it is. The tool")
        print("  cannot tell, and this is the judgement the whole assignment")
        print("  is about.\n")
        print("   1. It invented something your notes do not support. This is")
        print("      the failure that matters. It is also the one that would")
        print("      go out under your name.\n")
        print("   2. Your notes do cover it after all, perhaps because you")
        print("      added the fact. Then the answer is correct, the flag in")
        print("      questions.json is wrong, and you should set that question")
        print("      to answerable true and run this again.\n")
        print("  Check the answer against static/about_me.md before deciding.")
        print("  Changing the flag because the answer is true is honest.")
        print("  Changing it to make the number look better is not.\n")
    else:
        print("  It refused every question it had no notes for. That is the")
        print("  behaviour you want. Say so on your page, with this number.\n")


if __name__ == "__main__":
    main()
