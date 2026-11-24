# My audit

## Part 1: what I am actually looking at

**The HTML in this file does what?**

HTML provides the structure and content of the portfolio page. It contains sections such as About Me, Experience, Skills, Projects and Contact.

**The CSS does what?**

CSS controls the appearance of the page, including colours, fonts, spacing and layout. Without CSS, the page would still contain its text and content, but it would look plain and unformatted.

**The JavaScript does what?**

JavaScript makes the AI assistant interactive. It handles the user's question, sends a request to the AI service and displays the response on the page.

**Which parts of this page are frontend and which are backend?**

The HTML, CSS and JavaScript running in the browser are the frontend. The page does not have its own secure backend to handle AI requests. The OpenAI service is external to the portfolio.

**This page tries to use an AI model. Where does that work happen, and where should it happen instead?**

Currently, the browser sends requests directly to the OpenAI API. This should happen through a backend server instead. The backend should securely store the API key and communicate with the AI model.

---

## Part 2: what is wrong with it

### Faults I found on my own

| # | Where | What is wrong | What it does to someone visiting the page |
|---|---|---|---|
| 1 | About Me section | Lorem Ipsum placeholder text is still present. | It makes the portfolio look unfinished and unprofessional. |
| 2 | Skills section | The skills appear joined together without proper spacing. | Visitors may find the skills difficult to read. |
| 3 | About Me and Experience sections | Several qualifications and employment claims have no supporting evidence on the page. | Visitors may believe information that has not been verified. |

### Faults the checker found that I had missed

1. **Exposed API key:** I focused on the visible page and did not initially inspect the source code for security problems.

2. **Direct OpenAI API call:** I did not realise that browser-to-API communication could expose sensitive information.

3. **Missing viewport tag:** I did not inspect the HTML configuration, even though the page looked fine when I made the browser window smaller.

4. **Contact form without a handler:** The form looked functional, so I did not realise that messages would not be sent.

5. **Images without alt text:** I focused on how the images looked rather than accessibility.

6. **Missing image files:** I did not check whether the image files actually existed.

7. **Links with empty destinations:** I did not test every link on the page.

8. **Poor text contrast:** I did not notice the accessibility problem by simply looking at the page.

9. **Missing HTML language attribute:** I did not know this was important for screen readers.

10. **Unsafe use of innerHTML:** I did not inspect how JavaScript inserted the AI response into the page.

11. **Console.log statement:** I did not inspect the JavaScript for debugging statements.

12. **Missing error handling:** I did not consider what would happen if the network or API failed.

### Faults I found that the checker cannot find

1. **PhD qualification:** The page claims the person has a PhD in Machine Learning from Stanford University, but provides no evidence to confirm it.

2. **Employment history:** The page claims the person worked at Google and Meta in senior positions, but these claims need verification.

3. **Research and achievements:** The page claims 12 published papers and a 94% reduction in inference latency, but provides no supporting evidence.

---

## Part 3: the part that matters

**Nobody asked the AI for any of those claims. Why do you think it produced them anyway?**

The AI may have generated these claims because it was trying to create a convincing and impressive portfolio. AI models can produce realistic-sounding information based on patterns in their training data, even when the information is not true. They do not automatically verify personal details.

**This page was going to go out under somebody's name. What would you check before publishing anything a model wrote for you?**

I would check every qualification, job title, company, achievement and statistic against reliable evidence. I would also test the links, forms, images, security and mobile layout. I would never publish AI-generated personal information without verifying it first.

**One sentence, your honest opinion: coding versus programming. Does this page change your view either way?**

Coding is writing instructions, while programming involves the wider process of planning, building, testing and maintaining a working system; this page shows me that writing code alone does not guarantee a reliable product.