\# Option D – Development and Measurement Notes



\## 1. Option B – Portfolio development



I customised the original portfolio by replacing placeholder information with my own academic background, technical interests and project descriptions.



I added information about my MSc Applied Data Science with Advanced Practice at Teesside University and included three projects:



\- NHS GP Appointments Pipeline

\- Job Advert Decoder

\- Payment Fraud Detection



I also improved the portfolio structure and presentation.



\## 2. Option C – Backend development



I used FastAPI to develop the backend.



The application includes:



\- `/api/health` – checks the API configuration and whether personal notes are loaded.

\- `/api/ask` – accepts questions and returns answers.

\- `/api/projects` – returns project information from projects.json.



The frontend communicates with these endpoints using JavaScript.



The application initially supports demo mode, which finds the closest matching paragraph in the personal notes.



\## 3. Option D – Real model integration



I integrated the Groq API using the model `openai/gpt-oss-120b`.



The API key is stored in the `GROQ\_API\_KEY` environment variable rather than in frontend code.



I updated the system prompt with explicit accuracy rules:



\- Do not invent personal information.

\- Do not invent qualifications, universities or employers.

\- Do not invent experience, salaries or achievements.

\- Do not confuse studying with graduating.

\- Respond with exactly "I do not know." when the notes do not support an answer.



\## 4. Demo mode versus real model



I tested the same eight questions in both modes.



\### Demo mode



Result: 6/8 correct (75%).



The demo system correctly answered the four answerable questions but failed to refuse two unsupported questions.



For example, when asked about the undergraduate university, it returned information about my current MSc studies at Teesside University.



This demonstrated a limitation of paragraph matching.



\### Real model



Result: 8/8 correct (100%).



The Groq model answered all four answerable questions and refused all four unsupported questions.



The refusal instruction made the model's behaviour more consistent with the requirements.



\## 5. Measurement history



| Test | Result | Explanation |

|---|---|---|

| Initial real-model measurement | 8/8 (100%) | All questions classified correctly. |

| Intermediate measurement | 6/8 (75%) | Two refusal responses were not recognised by the measurement script. |

| Final real-model measurement | 8/8 (100%) | Explicit refusal wording was introduced. |



The intermediate result was caused by a refusal-phrase recognition mismatch. Manual testing confirmed that the two responses were refusals.



The final result returned to 8/8.



\## 6. Changes made



I strengthened the system prompt to prevent unsupported personal claims and require an explicit refusal when information is unavailable.



I also improved the portfolio by adding a third project and checking that the frontend displayed all three projects correctly.



The HTML checker reported zero serious, important or tidy issues.



\## 7. Reflection



This work demonstrated that a working AI application is not necessarily a reliable one.



The demo system sometimes returned related information instead of refusing unsupported questions. The real model performed better in this eight-question test after strengthening the instructions.



However, the result is based on a small set of questions and does not guarantee that the model will always be accurate.



A larger and more varied evaluation would be needed to assess reliability more confidently.



\## 8. Deployment measurement



Live Vercel deployment and live measurement are still pending.

