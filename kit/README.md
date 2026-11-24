# Week 3 kit

Everything here is yours to use.

## Doing Option A? You only need one folder

Open `option_a/` and read the README in there. Option A happens entirely in
your browser, in an online editor. There is nothing to install, no terminal,
and you can ignore everything else in this kit.

The rest of this file is for Options B, C and D.

```
kit/
  option_a/                   Option A lives entirely in here
    README.md                 start here if you are doing Option A
    1_COPY_THIS_ai_draft_page.txt
    2_COPY_THIS_starter_page.txt
    audit_template.md         the Option A write-up, built around screenshots

  audit/
    portfolio_ai_draft.html   the page you audit. Everyone starts here.
  tools/
    check_page.py             checks a page for faults. Needs Python, nothing else.
  starter/
    static/                   the page itself. Options A and B deploy this folder.
      index.html
      styles.css
      about_me.md             what the assistant may say about you (C and D)
    main.py                   the backend (C and D)
    requirements.txt
    ask_snippet.html          paste into index.html (C and D)
```

## Running the checker

You need Python. No libraries, no pip install, no internet.

```
python3 tools/check_page.py audit/portfolio_ai_draft.html
```

On Windows use `python` instead of `python3`.

Point it at your own page the same way:

```
python3 tools/check_page.py starter/static/index.html
```

It prints findings as serious, important or tidy, and explains each one.
A page with no findings prints nothing but a clean bill.

It cannot tell you whether anything on your page is true. Only you can.

## Looking at a page before you deploy it

Double click `starter/static/index.html` and it opens in your browser. That is
the whole of Option A and B. You do not need a server.

To check it on a phone without owning one, open your browser's developer tools
and click the small phone icon in the panel that appears.

    Windows or Linux    F12
    Mac                 Cmd + Option + I
    Any                 right click the page, then Inspect

## Running the backend (Options C and D only)

```
cd starter
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000

It works with no API key. It answers from `static/about_me.md` by finding the
closest paragraph, and labels every answer `[demo mode]` so you can see which
mode you are in. Open http://127.0.0.1:8000/api/health if anything looks wrong.

## Adding a real model (Option D only)

Get a free key from console.groq.com. No payment card.

Then set it in your terminal, in the same window you run uvicorn in:

macOS or Linux
```
export GROQ_API_KEY=your_key_here
uvicorn main:app --reload
```

Windows, Command Prompt
```
set GROQ_API_KEY=your_key_here
uvicorn main:app --reload
```

Windows, PowerShell
```
$env:GROQ_API_KEY="your_key_here"
uvicorn main:app --reload
```

`/api/health` will now say `"mode": "model"`. The answers stop saying
`[demo mode]`.

There is deliberately no `.env` file in this kit. A key you type into a file
is a key you can commit by accident. A key you type into your terminal
disappears when you close it.

On Vercel the key goes in Project Settings, Environment Variables. It never
goes in a file you upload.

## The one rule about keys

Never paste a key into the group chat, not even when asking for help, and not
even a key you are about to delete. Blur it in screenshots. If you think a key
has been seen by anyone, delete it at console.groq.com and make a new one.
That takes about ten seconds and costs nothing.
