"""
Groq AI-powered Resume Analyzer
Uses the OpenAI-compatible Groq API endpoint via the OpenAI Python client.
"""
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

_GROQ_AVAILABLE = False
_client = None
_MODEL = "openai/gpt-oss-20b"


def _init_groq():
    """Lazy-init Groq client, returns True if successful."""
    global _GROQ_AVAILABLE, _client
    if _client is not None:
        return _GROQ_AVAILABLE

    api_key = os.getenv("GROQ_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key.startswith("your_"):
        _GROQ_AVAILABLE = False
        return False

    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=api_key, base_url=base_url)
        _GROQ_AVAILABLE = True
        return True
    except Exception:
        _GROQ_AVAILABLE = False
        return False


def _extract_response_text(response):
    if not response:
        return ""
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text
    if hasattr(response, "output") and response.output:
        try:
            output = response.output
            if isinstance(output, list) and output:
                first = output[0]
                if isinstance(first, dict) and "content" in first:
                    content = first["content"]
                    if isinstance(content, list):
                        return "".join(
                            item.get("text", "") if isinstance(item, dict) else str(item)
                            for item in content
                        )
                    return str(content)
        except Exception:
            pass
    return str(response)


_ANALYSIS_PROMPT = """You are an expert resume coach and ATS specialist with 15+ years of experience.

Analyze the following resume for the role of **{role}** in the **{category}** domain.

RESUME TEXT:
\"\"\"{resume_text}\"\"\"

TARGET ROLE REQUIRED SKILLS: {required_skills}

Return a valid JSON object with EXACTLY this structure (raw JSON only, no markdown fences):
{{
  "ai_overall_score": <integer 0-100>,
  "ai_verdict": "<Excellent|Strong|Good|Needs Work|Major Revision>",
  "ai_summary": "<2-3 sentence professional coach assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
  "missing_keywords": ["<kw1>", "<kw2>", "<kw3>", "<kw4>", "<kw5>"],
  "found_keywords": ["<kw1>", "<kw2>", "<kw3>"],
  "section_feedback": {{
    "contact": "<specific feedback>",
    "summary": "<specific feedback>",
    "experience": "<specific feedback>",
    "skills": "<specific feedback>",
    "education": "<specific feedback>",
    "projects": "<specific feedback>"
  }},
  "ats_tips": ["<tip1>", "<tip2>", "<tip3>"],
  "bullet_rewrites": [
    {{"original": "<bullet from resume>", "improved": "<stronger rewrite>"}},
    {{"original": "<another bullet>", "improved": "<improved version>"}}
  ],
  "recommended_additions": ["<item1>", "<item2>", "<item3>"],
  "interview_likelihood": "<Low|Medium|High|Very High>",
  "keyword_match_percent": <integer 0-100>
}}"""

_SUMMARY_REWRITE_PROMPT = """You are an expert resume writer. Rewrite the following professional summary to be more impactful, keyword-rich, and tailored for the role of {role}.

CURRENT SUMMARY: {summary}
TARGET ROLE: {role}
REQUIRED SKILLS: {required_skills}

Return ONLY the rewritten summary (2-3 sentences, no JSON, no extra text). Make it powerful, specific, and ATS-optimized."""

_COVER_LETTER_PROMPT = """You are a professional career coach. Write a concise, compelling cover letter opening paragraph (3-4 sentences) for a candidate applying to the role of {role}.

RESUME HIGHLIGHTS:
{resume_text}

Return ONLY the opening paragraph, nothing else. Make it genuine and impactful."""

_INTERVIEW_QUESTIONS_PROMPT = """You are an expert technical recruiter and hiring manager. Based on the candidate's resume and the target role of {role} in the {category} domain, generate 8 highly relevant interview questions (a mix of behavioral and technical).

RESUME HIGHLIGHTS:
{resume_text}

Return ONLY a numbered list of the questions, nothing else. Make them realistic and challenging."""


def _create_response(prompt: str, temperature: float, max_output_tokens: int):
    if not _init_groq():
        return None
    try:
        response = _client.responses.create(
            model=_MODEL,
            input=prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )
        return _extract_response_text(response)
    except Exception:
        return None


def analyze_with_groq(resume_text: str, role: str, category: str, required_skills: list):
    """Run full Groq analysis on a resume."""
    if not _init_groq():
        return None

    prompt = _ANALYSIS_PROMPT.format(
        role=role,
        category=category,
        resume_text=resume_text[:8000],
        required_skills=", ".join(required_skills)
    )
    raw = _create_response(prompt, 0.3, 2048)
    if not raw:
        return None
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return None


def rewrite_summary_with_groq(summary: str, role: str, required_skills: list):
    """Ask Groq to rewrite a professional summary. Returns new text or None."""
    if not _init_groq() or not summary or len(summary.strip()) < 20:
        return None

    prompt = _SUMMARY_REWRITE_PROMPT.format(
        role=role,
        summary=summary[:1000],
        required_skills=", ".join(required_skills[:10])
    )
    return _create_response(prompt, 0.5, 256)


def generate_cover_letter_opener(resume_text: str, role: str, category: str):
    """Generate a cover letter opening paragraph using Groq."""
    if not _init_groq():
        return None

    prompt = _COVER_LETTER_PROMPT.format(
        role=role,
        category=category,
        resume_text=resume_text[:3000]
    )
    return _create_response(prompt, 0.6, 200)


def generate_interview_questions(resume_text: str, role: str, category: str):
    """Generate role-specific mock interview questions using Groq."""
    if not _init_groq():
        return None

    prompt = _INTERVIEW_QUESTIONS_PROMPT.format(
        role=role,
        category=category,
        resume_text=resume_text[:3000]
    )
    return _create_response(prompt, 0.6, 500)


def is_groq_available() -> bool:
    """Check if Groq is configured and ready."""
    return _init_groq()
