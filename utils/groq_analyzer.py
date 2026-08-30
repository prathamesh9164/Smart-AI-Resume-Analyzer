"""
Groq AI-powered Resume Analyzer
Uses the OpenAI-compatible Groq API endpoint via the OpenAI Python client.
"""
import os
import json
import re
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_GROQ_AVAILABLE = False
_client = None
# Read model from env; default to a known-good Groq model
_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")


def _init_groq():
    """Lazy-init Groq client, returns True if successful."""
    global _GROQ_AVAILABLE, _client
    if _client is not None:
        return _GROQ_AVAILABLE

    # Only use GROQ_API_KEY — do NOT fall back to unrelated Google/other keys
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("your_"):
        _GROQ_AVAILABLE = False
        return False

    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=api_key, base_url=base_url)
        _GROQ_AVAILABLE = True
        logger.info("Groq client initialised with model: %s", _MODEL)
        return True
    except Exception as exc:
        logger.error("Failed to initialise Groq client: %s", exc)
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

_BUILDER_SUMMARY_PROMPT = """You are an expert resume writer. Generate a powerful professional summary (3-4 sentences) for the candidate.

CANDIDATE INFO:
Name: {name}
Experience: {experiences}
Skills: {skills}
Target Role: {role}

Return ONLY the summary text, nothing else. Make it ATS-optimized, highlighting key strengths and achievements."""

_EXPERIENCE_BULLETS_PROMPT = """You are an expert resume writer. The candidate worked as {job_title} at {company}.
Context/Details provided by candidate: {context}

Generate 3-4 strong, action-oriented resume bullet points highlighting responsibilities and achievements. Use metrics where appropriate (or placeholders). 
Return ONLY the bullet points, each on a new line starting with a bullet character (•). Do not include any other text."""

_PROJECT_DESC_PROMPT = """You are an expert resume writer. The candidate worked on a project named "{project_name}" using these technologies: {tech_stack}.
Additional Context: {context}

Generate a concise 2-sentence project description followed by 2-3 bullet points of key achievements or features. 
Return ONLY the description and bullet points. Bullet points should start with (•). Do not include any other text."""

_FULL_COVER_LETTER_PROMPT = """You are an expert career coach. Write a complete, professional, 3-paragraph cover letter for the candidate applying for the role of {role}.

CANDIDATE DETAILS:
Name: {name}
Experience: {experiences}
Skills: {skills}

Return ONLY the cover letter text, properly formatted. Do not include placeholder addresses at the top, just start with a professional greeting."""

_JD_MATCH_PROMPT = """You are a world-class ATS system and senior technical recruiter with 20+ years of experience evaluating candidates against job descriptions.

You are given a candidate's resume and a job description. Your task is to perform a deep, precise match analysis.

RESUME TEXT:
\"\"\"{resume_text}\"\"\"

JOB DESCRIPTION:
\"\"\"{jd_text}\"\"\"

Perform a thorough comparison and return a valid JSON object with EXACTLY this structure (raw JSON only, no markdown fences, no extra text):
{{
  "jd_role_title": "<inferred job title from JD>",
  "jd_company": "<inferred company name from JD, or 'Not specified'>",
  "overall_match_score": <integer 0-100, holistic match percentage>,
  "match_verdict": "<Perfect Fit|Strong Match|Good Match|Partial Match|Weak Match>",
  "match_summary": "<2-3 sentence executive summary of how well this resume fits the JD>",
  "skill_match": {{
    "matched_skills": ["<skill from JD that resume has>", ...],
    "missing_critical_skills": ["<required skill from JD NOT in resume>", ...],
    "missing_nice_to_have": ["<preferred/bonus skill from JD NOT in resume>", ...],
    "bonus_skills": ["<skill candidate has that goes beyond JD requirements>", ...]
  }},
  "experience_match": {{
    "score": <integer 0-100>,
    "feedback": "<1-2 sentences on how candidate experience aligns with JD requirements>"
  }},
  "education_match": {{
    "score": <integer 0-100>,
    "feedback": "<1 sentence on education alignment>"
  }},
  "section_gaps": {{
    "summary": "<specific advice to tailor the summary for THIS JD>",
    "experience": "<specific advice to reframe experience bullets for THIS JD>",
    "skills": "<specific skills to add or reorganize for THIS JD>",
    "projects": "<project advice tailored to THIS JD>"
  }},
  "tailored_bullet_rewrites": [
    {{"original": "<existing bullet from resume>", "improved": "<rewritten bullet using JD language and keywords>"}},
    {{"original": "<another bullet>", "improved": "<JD-tailored rewrite>"}}
  ],
  "jd_keywords_to_add": ["<exact keyword/phrase from JD to add to resume>", ...],
  "application_recommendation": "<Strong Apply|Apply|Apply with Modifications|Significant Rework Needed|Not Recommended>",
  "top_3_action_items": ["<most impactful change #1>", "<most impactful change #2>", "<most impactful change #3>"]
}}"""


def _create_response(prompt: str, temperature: float, max_output_tokens: int):
    """Send a prompt to Groq and return (text, None) on success, (None, error_str) on failure."""
    if not _init_groq():
        return None, "Groq client not initialised. Check GROQ_API_KEY in .env"
    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_output_tokens
        )
        return response.choices[0].message.content, None
    except Exception as exc:
        logger.error("Groq API call failed: %s", exc)
        return None, str(exc)


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
    raw, err = _create_response(prompt, 0.3, 2048)
    if not raw:
        return None
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                return json.loads(m.group())
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
    text, _ = _create_response(prompt, 0.5, 256)
    return text


def generate_cover_letter_opener(resume_text: str, role: str, category: str):
    """Generate a cover letter opening paragraph using Groq."""
    if not _init_groq():
        return None

    prompt = _COVER_LETTER_PROMPT.format(
        role=role,
        category=category,
        resume_text=resume_text[:3000]
    )
    text, _ = _create_response(prompt, 0.6, 200)
    return text


def generate_interview_questions(resume_text: str, role: str, category: str):
    """Generate role-specific mock interview questions using Groq."""
    if not _init_groq():
        return None

    prompt = _INTERVIEW_QUESTIONS_PROMPT.format(
        role=role,
        category=category,
        resume_text=resume_text[:3000]
    )
    text, _ = _create_response(prompt, 0.6, 500)
    return text


def generate_summary_for_builder(personal_info: dict, experiences: list, skills: dict, role: str = "General"):
    """Generate a professional summary for the resume builder."""
    if not _init_groq():
        return None

    exp_str = ", ".join([f"{e.get('position', '')} at {e.get('company', '')}" for e in experiences if e.get('position')])
    skills_str = ", ".join(skills.get('technical', []) + skills.get('soft', []))

    prompt = _BUILDER_SUMMARY_PROMPT.format(
        name=personal_info.get('full_name', 'Candidate'),
        experiences=exp_str or "Entry Level",
        skills=skills_str or "General Skills",
        role=role
    )
    text, _ = _create_response(prompt, 0.6, 300)
    return text


def generate_experience_bullets(job_title: str, company: str, context: str):
    """Generate bullet points for an experience entry."""
    if not _init_groq():
        return None

    prompt = _EXPERIENCE_BULLETS_PROMPT.format(
        job_title=job_title or "Employee",
        company=company or "Company",
        context=context or "General responsibilities"
    )
    text, _ = _create_response(prompt, 0.7, 400)
    return text


def generate_project_description(project_name: str, tech_stack: str, context: str):
    """Generate description and bullets for a project entry."""
    if not _init_groq():
        return None

    prompt = _PROJECT_DESC_PROMPT.format(
        project_name=project_name or "Project",
        tech_stack=tech_stack or "Various technologies",
        context=context or "General project"
    )
    text, _ = _create_response(prompt, 0.7, 400)
    return text


def generate_full_cover_letter(personal_info: dict, experiences: list, skills: dict, role: str = "Target Role"):
    """Generate a full cover letter."""
    if not _init_groq():
        return None

    exp_str = ", ".join([f"{e.get('position', '')} at {e.get('company', '')}" for e in experiences if e.get('position')])
    skills_str = ", ".join(skills.get('technical', []) + skills.get('soft', []))

    prompt = _FULL_COVER_LETTER_PROMPT.format(
        name=personal_info.get('full_name', 'Candidate'),
        experiences=exp_str or "Entry Level",
        skills=skills_str or "General Skills",
        role=role
    )
    text, _ = _create_response(prompt, 0.7, 800)
    return text



def match_resume_to_jd(resume_text: str, jd_text: str):
    """Deep JD-vs-resume match analysis using Groq.
    Returns (result_dict, None) on success, (None, error_str) on failure.
    """
    if not _init_groq():
        return None, "Groq client not initialised. Check GROQ_API_KEY in .env"

    if not jd_text or len(jd_text.strip()) < 50:
        return None, "Job description is too short (minimum 50 characters)."

    prompt = _JD_MATCH_PROMPT.format(
        resume_text=resume_text[:6000],
        jd_text=jd_text[:4000]
    )
    # 4096 tokens — the JSON output is large; 2048 caused mid-response truncation
    raw, api_err = _create_response(prompt, 0.2, 4096)
    if not raw:
        return None, api_err or "Groq API returned an empty response."

    clean = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE).strip()
    try:
        return json.loads(clean), None
    except json.JSONDecodeError:
        try:
            m = re.search(r'\{.*\}', clean, re.DOTALL)
            if m:
                return json.loads(m.group()), None
        except Exception:
            pass
        logger.error("JD match JSON parse failed. Raw reply (first 500 chars): %s", raw[:500])
        return None, f"Groq replied but the JSON was malformed. Model used: {_MODEL}. First 200 chars of reply: {raw[:200]}"


def is_groq_available() -> bool:
    """Check if Groq is configured and ready."""
    return _init_groq()
