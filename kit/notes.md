# Option D – Development and Measurement Notes

## 1. Option B – Portfolio Development

I customised the original portfolio by replacing placeholder information with my own academic background, technical interests and project descriptions.

I added information about my MSc Applied Data Science with Advanced Practice at Teesside University and included three projects:

- NHS GP Appointments Pipeline
- Job Advert Decoder
- Payment Fraud Detection

I also improved the portfolio structure and presentation.

## 2. Option C – Backend Development

I used FastAPI to develop the backend.

The application includes:

- `/api/health` – checks the API configuration and whether personal notes are loaded.
- `/api/ask` – accepts questions and returns answers.
- `/api/projects` – returns project information from `projects.json`.

The frontend communicates with these endpoints using JavaScript.

The application initially supports demo mode, which finds the closest matching paragraph in the personal notes.

## 3. Option D – Real Model Integration

I integrated the Groq API using the model `openai/gpt-oss-120b`.

The API key is stored in the `GROQ_API_KEY` environment variable rather than in frontend code.

I updated the system prompt with explicit accuracy rules:

- Do not invent personal information.
- Do not invent qualifications, universities or employers.
- Do not invent experience, salaries or achievements.
- Do not confuse studying with graduating.
- Respond with exactly "I do not know." when the notes do not support an answer.

## 4. Demo Mode versus Real Model

I evaluated the application using the same eight questions in both demo mode and real-model mode to compare their responses.

### 4.1 Demo Mode

**Result: 6/8 correct (75%).**

The demo system used paragraph matching to find relevant information in my personal notes. Although it answered the four answerable questions correctly, it failed to refuse two unsupported questions.

For example, when asked which university I attended for my undergraduate degree, it returned information about my current MSc studies at Teesside University instead of refusing to answer.

### 4.2 Real Model

**Result: 8/8 correct (100%).**

The Groq model answered all four answerable questions correctly and refused all four unsupported questions by responding with "I do not know."

### 4.3 Comparison and Findings

The demo system sometimes returned related information even when the notes did not contain the answer. The real model followed the strengthened system instructions more consistently and avoided unsupported personal claims.

This comparison demonstrates that producing a relevant answer is not necessarily the same as producing an accurate answer.

## 5. Measurement History

The application was tested at different stages to evaluate its performance.

### 5.1 Initial Real-Model Measurement

**Result: 8/8 correct (100%).**

All eight questions were classified correctly during the initial real-model test.

### 5.2 Intermediate Measurement

**Result: 6/8 correct (75%).**

Two refusal responses were not recognised by the measurement script because their wording did not match the refusal phrases it was checking for. Manual testing confirmed that the two responses were refusals.

### 5.3 Final Real-Model Measurement

**Result: 8/8 correct (100%).**

I introduced more explicit refusal wording in the system prompt. The final measurement returned to 8/8.

## 6. Changes Made

I strengthened the system prompt to prevent unsupported personal claims and require an explicit refusal when information is unavailable.

I also improved the portfolio by adding a third project and checking that the frontend displayed all three projects correctly.

The HTML checker reported zero serious, important or tidy issues.

## 7. Reflection

This work demonstrated that a working AI application is not necessarily a reliable one.

The demo system sometimes returned related information instead of refusing unsupported questions. The real model performed better in this eight-question test after strengthening the instructions.

However, the result is based on a small set of questions and does not guarantee that the model will always be accurate.

A larger and more varied evaluation would be needed to assess reliability more confidently.

## 8. Live Deployment and Measurement

The portfolio was successfully deployed to Vercel on 24 November 2026.

The live application was configured with the Groq API key using Vercel environment variables.

The live `/api/health` endpoint confirmed the following:

- API working: true
- API key configured: true
- Personal notes loaded: true
- Mode: model

I ran the eight-question measurement against the live Vercel website.

**Final live measurement: 8/8 correct (100%).**

The results were:

- Answerable questions correctly answered: 4/4.
- Unsupported questions correctly refused: 4/4.

The initial live measurement was blocked by Vercel deployment protection and returned HTTP 401 errors. I disabled the protection and reran the measurement successfully.

The final result demonstrates that the live AI assistant answered questions supported by my notes and refused questions when the information was unavailable.