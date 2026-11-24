"""
Check a web page for the faults an AI assistant commonly leaves behind.

    python3 check_page.py path/to/index.html

No libraries to install. It reads the file as text, the way a reviewer would,
and reports what it finds with a severity so you know what to fix first.

It is not clever and it is not complete. It cannot tell you whether the words
on your page are TRUE, which is the single most important check and the one
only you can do.
"""

import os
import re
import sys

SEVERITY_ORDER = {"serious": 0, "important": 1, "tidy": 2}


def finding(sev, code, what, why, fix):
    return {"severity": sev, "code": code, "what": what, "why": why, "fix": fix}


# --------------------------------------------------------------------------
#  the checks
# --------------------------------------------------------------------------
SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9_\-]{20,}", "an OpenAI style key"),
    (r"gsk_[A-Za-z0-9]{20,}", "a Groq key"),
    (r"AIza[A-Za-z0-9_\-]{30,}", "a Google API key"),
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "an Anthropic key"),
    (r"ghp_[A-Za-z0-9]{30,}", "a GitHub token"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "a Slack token"),
]


def strip_comments(html):
    """
    Remove commentary before checks that look for code.

    Needed because a page that says, in a comment, "never call the model
    from the browser" would otherwise be reported for calling the model
    from the browser. Secrets are deliberately NOT stripped: a key in a
    comment is still a key in a committed file.
    """
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r"/\*.*?\*/", " ", html, flags=re.S)
    # // to end of line, but not the // in https://
    html = re.sub(r"(?<![:/])//[^\n]*", " ", html)
    return html


def is_fragment(html):
    """True if this is a snippet to paste in, not a whole page."""
    return not re.search(r"<html|<!doctype", html, re.I)


def check_secrets(html, path):
    out = []
    for pattern, label in SECRET_PATTERNS:
        for m in re.finditer(pattern, html):
            line = html[:m.start()].count("\n") + 1
            out.append(finding(
                "serious", "secret-in-page",
                f"line {line}: what looks like {label} is written into the page",
                "Anyone can read this. View source, or press F12. Automated "
                "scrapers find keys in public pages within minutes and spend "
                "them on your account.",
                "Delete it, revoke that key immediately, and move the call to "
                "a backend that holds the key server side."))
    return out


def check_browser_calls_model(html):
    hosts = ["api.openai.com", "api.anthropic.com", "api.groq.com",
             "generativelanguage.googleapis.com"]
    code = strip_comments(html)
    out = []
    for host in hosts:
        if host in code:
            out.append(finding(
                "serious", "browser-calls-model",
                f"the page calls {host} directly from the browser",
                "Any call a browser makes is visible to whoever is looking, "
                "and it needs a key in the page to work at all.",
                "Put a small backend between the page and the model. The page "
                "calls your backend, your backend holds the key."))
    return out


def check_mobile(html):
    out = []
    if not re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I):
        out.append(finding(
            "serious", "no-viewport",
            "there is no viewport meta tag",
            "Without it a phone renders the page at desktop width and shrinks "
            "it, so your text arrives unreadably small. Most people opening a "
            "link from a message are on a phone.",
            '<meta name="viewport" content="width=device-width, initial-scale=1">'))
    # (?<![-\w]) keeps this from matching the "width" inside max-width and
    # min-width, which are the correct things to use and must not be reported.
    for m in re.finditer(r"(?<![-\w])width\s*:\s*(\d{3,})px", html, re.I):
        size = int(m.group(1))
        if size >= 700:
            line = html[:m.start()].count("\n") + 1
            out.append(finding(
                "important", "fixed-width",
                f"line {line}: a fixed width of {size}px",
                f"A phone screen is around 390px wide. A fixed {size}px "
                "container forces sideways scrolling.",
                "Use max-width instead of width, so it can shrink."))
    return out


def _hex(value):
    """Turn a CSS colour into (r, g, b), or None if we cannot tell."""
    value = value.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3})", value)
    if m:
        return tuple(int(c * 2, 16) for c in m.group(1))
    m = re.fullmatch(r"#([0-9a-f]{6})", value)
    if m:
        return tuple(int(m.group(1)[i:i+2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+).*\)", value)
    if m:
        return tuple(int(m.group(i)) for i in (1, 2, 3))
    return {"white": (255, 255, 255), "black": (0, 0, 0)}.get(value)


def _relative_luminance(rgb):
    out = []
    for c in rgb:
        c = c / 255
        out.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


def contrast_ratio(fg, bg):
    """The real WCAG formula. 4.5 is the pass mark for normal text."""
    a, b = _relative_luminance(fg), _relative_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def gather_css(html, path):
    """
    Every stylesheet that applies to this page: the <style> blocks in it and
    any local file it links to.

    Reading the linked file matters. Most of a page's colours live there, and
    a checker that only reads the HTML would miss all of them.
    """
    sheets = [("the page", html)]
    folder = os.path.dirname(os.path.abspath(path))
    for m in re.finditer(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', html, re.I):
        href = re.search(r'href=["\']([^"\']+)["\']', m.group(0), re.I)
        if not href:
            continue
        target = href.group(1).split("?")[0]
        if target.startswith(("http://", "https://", "//")):
            continue
        full = os.path.join(folder, target)
        if os.path.exists(full):
            try:
                sheets.append((target, open(full, encoding="utf-8").read()))
            except OSError:
                pass
    return sheets


def css_variables(css):
    """Read the custom properties from the first :root block (light theme)."""
    m = re.search(r":root\s*\{([^{}]*)\}", css)
    if not m:
        return {}
    found = {}
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+)", m.group(1)):
        found[name] = value.strip()
    return found


def resolve_colour(value, variables, depth=0):
    """Follow var(--x) until it lands on something we can read."""
    if value is None or depth > 4:
        return None
    value = value.strip()
    m = re.match(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+))?\)", value)
    if m:
        target = variables.get(m.group(1))
        if target is None:
            target = m.group(2)
        return resolve_colour(target, variables, depth + 1)
    return _hex(value)


def check_contrast(html, path):
    """
    Work out what colour the text actually ends up, variables included, and
    measure it against whatever is behind it.

    This is the check that catches a pale accent colour, which is the easiest
    way to make a page unreadable while every other check still passes.
    """
    out = []
    sheets = gather_css(html, path)
    variables = {}
    for _, css in sheets:
        variables.update(css_variables(css))

    page_bg = None
    for _, css in sheets:
        for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            if "body" not in sel.split(",")[0]:
                continue
            bg = re.search(r"background(?:-color)?\s*:\s*([^;]+)", body)
            if bg:
                page_bg = resolve_colour(bg.group(1), variables) or page_bg
    page_bg = page_bg or (255, 255, 255)

    # Which selectors paint a background. Needed because ".hero p" is light
    # text sitting on ".hero", not on the page. Comparing it with the page
    # background would report readable text as unreadable, and a checker that
    # cries wolf on correct code is worse than no checker.
    backgrounds = {}
    for _, css in sheets:
        for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            bg = re.search(r"background(?:-color)?\s*:\s*([^;]+)", body)
            if not bg:
                continue
            colour = resolve_colour(bg.group(1), variables)
            if not colour:
                continue
            for one in sel.split(","):
                backgrounds[" ".join(one.split())] = colour

    def behind(selector):
        """The nearest ancestor selector that paints a background."""
        parts = selector.split()
        for cut in range(len(parts), 0, -1):
            found = backgrounds.get(" ".join(parts[:cut]))
            if found:
                return found
        return page_bg

    seen = set()
    for label, css in sheets:
        for raw_sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            sel = " ".join(raw_sel.split())[-60:]
            if sel.startswith(("@", ":root")):
                continue
            col = re.search(r"(?<![-\w])color\s*:\s*([^;]+)", body)
            if not col:
                continue
            fg = resolve_colour(col.group(1), variables)
            if not fg:
                continue
            own_bg = re.search(r"background(?:-color)?\s*:\s*([^;]+)", body)
            bg = resolve_colour(own_bg.group(1), variables) if own_bg else None
            bg = bg or behind(" ".join(raw_sel.split(",")[0].split()))
            ratio = contrast_ratio(fg, bg)
            if ratio >= 4.5:
                continue
            key = (sel, col.group(1).strip())
            if key in seen:
                continue
            seen.add(key)
            where = "in the page" if label == "the page" else f"in {label}"
            out.append(finding(
                "important", "low-contrast",
                f"{sel} sets text at a contrast of {ratio:.1f} to 1 ({where})",
                "Anything under 4.5 to 1 is hard to read, and for a lot of "
                "people impossible. A pale accent colour is the usual cause, "
                "and it makes every link on the page nearly invisible.",
                "Darken the colour until the ratio is at least 4.5 to 1. If it "
                "came from a variable, you only have to change it once."))
    return out


def check_accessibility(html):
    out = []
    if not re.search(r"<html[^>]+lang=", html, re.I):
        out.append(finding(
            "important", "no-lang",
            "the html tag has no lang attribute",
            "Screen readers use it to choose a pronunciation. Without it they "
            "guess, and often guess wrong.",
            '<html lang="en">'))
    for m in re.finditer(r"<img(?![^>]*\balt=)[^>]*>", html, re.I):
        line = html[:m.start()].count("\n") + 1
        out.append(finding(
            "important", "img-no-alt",
            f"line {line}: an image with no alt text",
            "Anyone using a screen reader is told nothing about this image. "
            "It is also what shows if the image fails to load.",
            'Add alt="...". If the image is purely decorative, use alt="".'))
    return out


def check_links(html, path):
    out = []
    folder = os.path.dirname(os.path.abspath(path))
    dead = len(re.findall(r'href=["\']#["\']', html))
    if dead:
        out.append(finding(
            "important", "dead-link",
            f"{dead} link(s) that go nowhere (href=\"#\")",
            "A visitor clicks and nothing happens. On a portfolio this reads "
            "as unfinished, which is worse than not having the link.",
            "Point it somewhere real, or remove the link and keep the text."))
    for m in re.finditer(r'(?:src|href)=["\']((?!https?:|//|#|mailto:)[^"\']+)["\']', html):
        target = m.group(1).split("?")[0].split("#")[0]
        if not target:
            continue
        if not os.path.exists(os.path.join(folder, target)):
            line = html[:m.start()].count("\n") + 1
            out.append(finding(
                "important", "missing-file",
                f"line {line}: refers to {target}, which is not there",
                "It works on nobody's machine, including yours, and shows as "
                "a broken image icon or a 404.",
                "Add the file, or remove the reference."))
    return out


def check_forms(html):
    """
    A form is fine if something receives it: an action, an onsubmit, or a
    script that listens for its submit event. The third one is how most
    JavaScript forms work, so missing it would report working code.
    """
    out = []
    code = strip_comments(html)
    listener = re.search(r"addEventListener\(\s*[\"']submit[\"']", code)
    for m in re.finditer(r"<form([^>]*)>", html, re.I):
        attrs = m.group(1)
        line = html[:m.start()].count("\n") + 1
        handled = "action=" in attrs.lower() or "onsubmit=" in attrs.lower()
        if not handled and listener:
            # If the form is named, make sure the script refers to that name.
            fid = re.search(r"""\bid=["']([^"']+)["']""", attrs)
            handled = fid.group(1) in code if fid else True
        if not handled:
            out.append(finding(
                "serious", "form-does-nothing",
                f"line {line}: a form with no action and no handler",
                "It looks like it works. Somebody types a message, presses "
                "send, and it goes nowhere. They think they contacted you.",
                "Point it at something that receives it, or replace the form "
                "with your email address, which is honest and works."))
    return out


def check_leftovers(html):
    out = []
    if re.search(r"lorem ipsum", html, re.I):
        line = html[:re.search(r"lorem ipsum", html, re.I).start()].count("\n") + 1
        out.append(finding(
            "important", "placeholder-text",
            f"line {line}: placeholder lorem ipsum text is still on the page",
            "It is the clearest possible signal that nobody read the page "
            "before publishing it.",
            "Replace it or delete that block."))
    for m in re.finditer(r"console\.log\s*\(", html):
        line = html[:m.start()].count("\n") + 1
        out.append(finding(
            "tidy", "console-log",
            f"line {line}: a console.log left in",
            "Harmless on its own, but it is where secrets and user input end "
            "up in public view. Check what this one prints.",
            "Remove it before publishing."))
    for m in re.finditer(r"\.innerHTML\s*=", html):
        line = html[:m.start()].count("\n") + 1
        out.append(finding(
            "important", "innerhtml",
            f"line {line}: innerHTML is used to insert content",
            "If that content comes from a model or a user, any HTML in it "
            "runs as part of your page.",
            "Use textContent instead, unless you genuinely need markup."))
    if re.search(r"<script", html, re.I) and "fetch(" in html and "catch" not in html:
        out.append(finding(
            "tidy", "no-error-handling",
            "a fetch call with no error handling anywhere on the page",
            "When the network fails, or the service is down, the visitor sees "
            "nothing at all happen.",
            "Wrap it in try and catch, and show the visitor a message."))
    return out


CHECKS = [
    ("secrets", lambda h, p: check_secrets(h, p)),
    ("model", lambda h, p: check_browser_calls_model(h)),
    ("mobile", lambda h, p: check_mobile(h)),
    ("accessibility", lambda h, p: check_accessibility(h)),
    ("contrast", lambda h, p: check_contrast(h, p)),
    ("links", lambda h, p: check_links(h, p)),
    ("forms", lambda h, p: check_forms(h)),
    ("leftovers", lambda h, p: check_leftovers(h)),
]


# Checks that only make sense on a whole page, not on a snippet you are
# about to paste into one.
PAGE_LEVEL = {"mobile", "accessibility", "contrast"}


def audit(path):
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    fragment = is_fragment(html)
    found = []
    for name, fn in CHECKS:
        if fragment and name in PAGE_LEVEL:
            continue
        found.extend(fn(html, path))
    found.sort(key=lambda f: SEVERITY_ORDER[f["severity"]])
    return found, fragment


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"No such file: {path}")
        sys.exit(1)

    found, fragment = audit(path)
    counts = {s: sum(1 for f in found if f["severity"] == s)
              for s in SEVERITY_ORDER}

    print("=" * 74)
    print(f"  {os.path.basename(path)}")
    print(f"  {counts['serious']} serious, {counts['important']} important, "
          f"{counts['tidy']} tidy")
    if fragment:
        print("  (a snippet, not a whole page, so page-wide checks are skipped)")
    print("=" * 74)

    for f in found:
        print()
        print(f"[{f['severity'].upper()}] {f['what']}")
        print(f"   why : {f['why']}")
        print(f"   fix : {f['fix']}")

    if not found:
        print()
        print("  Nothing found. Every check passed.")

    print()
    print("-" * 74)
    print("This tool cannot check whether anything on your page is TRUE.")
    print("Read every sentence about yourself and confirm you can back it up.")
    print("An AI assistant will invent qualifications, employers and numbers")
    print("without being asked, and they go out under your name.")
    print("-" * 74)
    return 0 if counts["serious"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
