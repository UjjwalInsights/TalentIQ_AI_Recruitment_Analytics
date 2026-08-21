"""
TalentIQ Local LLM Client

Uses Ollama + Llama 3.2 3B locally.
No OpenAI API or paid API is required.
"""

from ollama import Client


# =============================================================
# CONFIGURATION
# =============================================================

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"


client = Client(
    host=OLLAMA_HOST
)


# =============================================================
# SYSTEM PROMPT
# =============================================================

SYSTEM_PROMPT = """
You are TalentIQ, an AI recruitment and hiring assistant.

Your job is to help recruiters understand candidates,
resumes, jobs, recruitment analytics, and candidate-job matches.

IMPORTANT RULES:

1. Use ONLY the context provided to you.
2. Never invent candidate skills, experience, education, metrics,
   job requirements, recruiter statistics, or hiring information.
3. Preserve exact numbers when they are provided.
4. If the context does not contain enough information, clearly say so.
5. Explain answers in concise professional language.
6. When discussing a candidate, distinguish strengths from missing skills.
7. Do not claim someone is qualified for something unless the supplied
   evidence supports it.
8. Do not change database values.
9. Avoid unnecessary filler.
10. Your answer should be useful to a recruiter or hiring manager.
"""


# =============================================================
# GENERATE GROUNDED ANSWER
# =============================================================

def generate_grounded_answer(
    question,
    context,
    answer_type="general"
):
    """
    Generate an answer using the local Ollama model.

    Parameters
    ----------
    question : str
        User's question.

    context : str
        Retrieved resume, SQL, or matching evidence.

    answer_type : str
        Type of TalentIQ answer.

    Returns
    -------
    str
        Grounded LLM-generated answer.
    """

    if not context:
        return (
            "I do not have enough retrieved information "
            "to answer that question."
        )

    user_prompt = f"""
QUESTION TYPE:
{answer_type}

USER QUESTION:
{question}

RETRIEVED TALENTIQ CONTEXT:
----------------------------
{context}
----------------------------

Answer the user's question using only the retrieved context.

Do not introduce facts that are not supported by the context.
"""

    try:

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            options={
                "temperature": 0.1,
                "num_predict": 350,
            },
        )

        return response.message.content.strip()

    except Exception as error:

        return (
            "Local LLM generation failed.\n"
            f"Reason: {error}\n\n"
            "Retrieved context:\n"
            f"{context}"
        )


# =============================================================
# CONNECTION TEST
# =============================================================

def test_llm():

    context = """
Candidate:
Priya Sharma

Experience:
4 years

Skills:
Python, SQL, PostgreSQL, Tableau, Pandas,
NumPy, Excel, Statistics.

Target Role:
Data Analyst
"""

    question = (
        "Summarize this candidate for a recruiter."
    )

    print("=" * 70)
    print("TALENTIQ LOCAL LLM TEST")
    print("=" * 70)

    print(
        generate_grounded_answer(
            question=question,
            context=context,
            answer_type="candidate_summary",
        )
    )


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":
    test_llm()