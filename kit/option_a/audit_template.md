# My audit

Replace every line below with your own words. Short sentences are fine.
If you copy a definition off a website, you have not done this part.

Where it says SCREENSHOT, paste the picture in underneath.

---

## Part 1: what am I actually looking at

Answer from the page in front of you, not from memory.

**What is the HTML doing here?**

**What is the CSS doing?**
(You will find out for certain in Experiment 3.)

**What is the JavaScript doing?**
(Which part of this page would not work at all if JavaScript were switched off?)

**Which parts of this page are frontend, and which are backend?**
(Careful. There is a trick in this one.)

**This page tries to use an AI model. Where does that work happen, and where
should it happen instead?**

---

## Part 2: the experiments

### Experiment 1. The page as the AI wrote it
Paste the draft page into the editor and press Run.

SCREENSHOT 1: the rendered page.

Three things you noticed just by looking:
1.
2.
3.

### Experiment 2. Make the result pane narrow
Drag the divider so the result pane is as narrow as you can make it, or open
the page on your phone.

SCREENSHOT 2: the page squeezed narrow.

What happened to the text, and why would that matter for someone opening your
link from a message?

### Experiment 3. Delete every line of CSS
In the editor, delete everything between `<style>` and `</style>`. Press Run.

SCREENSHOT 3: the page with no CSS at all.

Is the content still there? Is it still in a sensible order? Is it still
readable? Write one sentence on what that tells you about what HTML is for,
and one on what CSS is for.

(Reload the page to get the CSS back.)

### Experiment 4. Press the Send button
Fill in the contact form properly, with a name, an email and a message. Watch
the address bar at the top. Then press Send Message.

What happened to the form?

What happened to the address bar?

SCREENSHOT 4: the page straight after you pressed Send.

Now the important question. The form went blank. Nothing said it failed.
**What would the person who filled it in believe had happened?**

Nothing was sent. Nothing was saved. Nobody was told. Write one sentence on
why this is worse than having no contact form at all.

### Experiment 5. The two broken images
SCREENSHOT 5: close up on the broken image icons.

What were they supposed to be, and why is putting those particular images on
this page a problem even if they had loaded?

### Experiment 6. Fix the unreadable text
Find `.muted` in the CSS. Change `#c8c8c8` to `#555555`. Press Run.

SCREENSHOT 6: before and after, or just after.

How much work was that, and how long had that fault been sitting on a page
that looked finished?

### Experiment 7. The key
There is an API key written into this page.

**Do not screenshot it.** Write the line number here instead:

Line number:

Who can read that key once this page is on the internet?

The page sends it to an AI company's web address directly from the browser.
Why does that design make the leak unavoidable, rather than just careless?

---

## Part 3: the faults no tool could ever find

Everything above is something a program could be taught to spot.

This part is not. Read the words on the page and ask of each sentence:
**could this person be asked to prove it?**

List the claims you think were invented, and why each one is a problem.

| # | The claim on the page | Why it is a problem |
|---|-----------------------|---------------------|
| 1 |                       |                     |
| 2 |                       |                     |
| 3 |                       |                     |
| 4 |                       |                     |

---

## Part 4: my own page

Paste the starter page into the editor and replace every placeholder with
your own words.

Rules: short, true, yours, specific. Every sentence is one you could be asked
about in an interview.

SCREENSHOT 7: your finished page.

SCREENSHOT 8: your finished page with the result pane narrow.

---

## Part 5: the part that matters

**Nobody asked the AI for a PhD, twelve papers or two billion users. Why do
you think it produced them anyway?**

**That page was going to go out under somebody's name. What would you check
before publishing anything a model wrote for you?**

**One sentence, honestly: coding versus programming. Does this page change
your view either way, and why?**
