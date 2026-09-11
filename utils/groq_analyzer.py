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
_MODEL_OPTIONS = tuple(dict.fromkeys(
    model.strip()
    for model in os.getenv(
        "GROQ_MODELS",
        f"{_MODEL},llama-3.3-70b-versatile,llama-3.1-8b-instant,"
        "meta-llama/llama-4-scout-17b-16e-instruct"
    ).split(",")
    if model.strip()
))


def get_groq_models() -> tuple:
    """Return model IDs available to the UI, preserving environment order."""
    return _MODEL_OPTIONS


def get_default_groq_model() -> str:
    """Return the deployment-configured model used when no model is selected."""
    return _MODEL


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

_STRUCTURED_RESUME_PROMPT = """You are a precise resume parsing system. Extract only information explicitly present in the resume below.

RESUME TEXT:
\"\"\"{resume_text}\"\"\"

Return valid JSON only, with exactly this structure. Use empty strings or empty arrays when a value is not present. Never invent employers, dates, achievements, skills, contact details, or education.
{{
    "personal_info": {{
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "portfolio": ""
    }},
    "summary": "",
    "education": [
        {{"institution": "", "degree": "", "field": "", "start_date": "", "end_date": "", "details": ""}}
    ],
    "experience": [
        {{"company": "", "title": "", "location": "", "start_date": "", "end_date": "", "description": "", "achievements": []}}
    ],
    "skills": [],
    "projects": [
        {{"name": "", "description": "", "technologies": [], "url": ""}}
    ]
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

_INTERVIEW_QUESTIONS_PROMPT = """You are an expert senior technical recruiter and hiring manager at a top company. 

Based on the candidate's resume and target role of **{role}** in the **{category}** domain, generate a COMPREHENSIVE MASTER BANK of 15 to 20 highly relevant, realistic, and challenging interview questions.

RESUME TEXT:
\"\"\"{resume_text}\"\"\"

Organize the questions into the following categories using clean Markdown formatting:

### 🛠️ 1. Technical & Tool Deep Dives (5-6 Questions)
(Questions targeting the programming languages, frameworks, tools, and technical skills listed on their resume)

### 🚀 2. Project & Work Experience Deep Dives (4-5 Questions)
(Questions asking about specific accomplishments, architectural choices, metrics, and technical challenges from their work experience/projects)

### 🎯 3. Role-Specific & Situational Questions (3-4 Questions)
(Scenario-based questions tailored specifically for a {role})

### 🤝 4. Behavioral & STAR Method Questions (3-4 Questions)
(Questions evaluating soft skills, conflict resolution, teamwork, failure recovery, and problem-solving)

For EACH question, provide:
- **Question**: Clear and specific question text.
- 💡 **Interviewer Insight & Prep Tip**: What hiring managers evaluate and key talking points to include in a winning response.

Return a complete, detailed Markdown guide. Do not truncate."""

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


def _create_response(
    prompt: str,
    temperature: float,
    max_output_tokens: int,
    model: str = None,
):
    """Send a prompt to Groq and return (text, None) on success, (None, error_str) on failure."""
    if not _init_groq():
        return None, "Groq client not initialised. Check GROQ_API_KEY in .env"
    try:
        response = _client.chat.completions.create(
            model=model or _MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_output_tokens
        )
        return response.choices[0].message.content, None
    except Exception as exc:
        logger.error("Groq API call failed: %s", exc)
        return None, str(exc)


def _parse_json_response(raw: str):
    """Parse raw model output that may be wrapped in a Markdown code fence."""
    if not raw:
        return None
    clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE).strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None


def parse_resume_with_groq(resume_text: str, model: str = None):
    """Extract a normalized structured resume profile, or return None on failure."""
    if not _init_groq() or not resume_text or len(resume_text.strip()) < 50:
        return None

    prompt = _STRUCTURED_RESUME_PROMPT.format(resume_text=resume_text[:10000])
    raw, _ = _create_response(prompt, 0.0, 2500, model=model)
    parsed = _parse_json_response(raw)
    if not isinstance(parsed, dict):
        logger.warning("Groq structured resume extraction returned invalid JSON")
        return None

    personal_info = parsed.get("personal_info")
    if not isinstance(personal_info, dict):
        personal_info = {}

    def clean_string(value):
        return value.strip() if isinstance(value, str) else ""

    def clean_list(value):
        if not isinstance(value, list):
            return []
        return [clean_string(item) for item in value if isinstance(item, str) and item.strip()]

    def clean_records(value, fields):
        if not isinstance(value, list):
            return []
        records = []
        for item in value:
            if not isinstance(item, dict):
                continue
            record = {
                field: clean_list(item.get(field))
                if field in ("achievements", "technologies")
                else clean_string(item.get(field))
                for field in fields
            }
            if any(record.values()):
                records.append(record)
        return records

    return {
        "personal_info": {
            field: clean_string(personal_info.get(field))
            for field in ("name", "email", "phone", "location", "linkedin", "github", "portfolio")
        },
        "summary": clean_string(parsed.get("summary")),
        "education": clean_records(
            parsed.get("education"),
            ("institution", "degree", "field", "start_date", "end_date", "details"),
        ),
        "experience": clean_records(
            parsed.get("experience"),
            ("company", "title", "location", "start_date", "end_date", "description", "achievements"),
        ),
        "skills": clean_list(parsed.get("skills")),
        "projects": clean_records(
            parsed.get("projects"), ("name", "description", "technologies", "url")
        ),
    }


def analyze_with_groq(
    resume_text: str,
    role: str,
    category: str,
    required_skills: list,
    model: str = None,
):
    """Run full Groq analysis on a resume."""
    if not _init_groq():
        return None

    prompt = _ANALYSIS_PROMPT.format(
        role=role,
        category=category,
        resume_text=resume_text[:8000],
        required_skills=", ".join(required_skills)
    )
    raw, err = _create_response(prompt, 0.3, 2048, model=model)
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


def rewrite_summary_with_groq(
    summary: str, role: str, required_skills: list, model: str = None
):
    """Ask Groq to rewrite a professional summary. Returns new text or None."""
    if not _init_groq() or not summary or len(summary.strip()) < 20:
        return None

    prompt = _SUMMARY_REWRITE_PROMPT.format(
        role=role,
        summary=summary[:1000],
        required_skills=", ".join(required_skills[:10])
    )
    text, _ = _create_response(prompt, 0.5, 256, model=model)
    return text


def generate_cover_letter_opener(
    resume_text: str, role: str, category: str, model: str = None
):
    """Generate a cover letter opening paragraph using Groq."""
    if not _init_groq():
        return None

    prompt = _COVER_LETTER_PROMPT.format(
        role=role,
        category=category,
        resume_text=resume_text[:3000]
    )
    text, _ = _create_response(prompt, 0.6, 200, model=model)
    return text


def generate_interview_questions(
    resume_text: str, role: str, category: str, model: str = None
):
    """Generate role-specific mock interview question bank using Groq."""
    if not _init_groq():
        return None

    prompt = _INTERVIEW_QUESTIONS_PROMPT.format(
        role=role,
        category=category,
        resume_text=resume_text[:4000]
    )
    text, _ = _create_response(prompt, 0.6, 2500, model=model)
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



def match_resume_to_jd(resume_text: str, jd_text: str, model: str = None):
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
    raw, api_err = _create_response(prompt, 0.2, 4096, model=model)
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
        return None, f"Groq replied but the JSON was malformed. Model used: {model or _MODEL}. First 200 chars of reply: {raw[:200]}"


def is_groq_available() -> bool:
    """Check if Groq is configured and ready."""
    return _init_groq()


def stream_chat_with_resume_context(
    messages: list,
    resume_text: str = "",
    role: str = "",
    category: str = "",
    analysis_info: dict = None,
    jd_text: str = "",
    model: str = None,
):
    """
    Stream chunks of response text from Groq for a conversational chat with resume memory/RAG.
    `messages` should be a list of dicts: [{'role': 'user'|'assistant', 'content': '...'}]
    """
    if not _init_groq():
        yield "⚠️ Groq client is not initialised. Please check `GROQ_API_KEY` in `.env`."
        return

    system_content = (
        "You are an expert AI Resume Coach, Senior Hiring Manager, and Career Mentor with 15+ years of experience.\n"
        "Your goal is to help the candidate elevate their resume, optimize for ATS filters, prepare for interviews, "
        "and land their dream job offer.\n\n"
    )

    if resume_text and len(resume_text.strip()) > 30:
        system_content += "=== ACTIVE RESUME CONTEXT (RAG MEMORY) ===\n"
        if role:
            system_content += f"Target Role: {role}\n"
        if category:
            system_content += f"Target Category: {category}\n"
        
        if analysis_info and isinstance(analysis_info, dict):
            ats = analysis_info.get("ai_overall_score") or analysis_info.get("overall_match_score") or analysis_info.get("ats_score")
            if ats:
                system_content += f"Latest ATS/Match Score: {ats}/100\n"
            
            verdict = analysis_info.get("ai_verdict") or analysis_info.get("match_verdict")
            if verdict:
                system_content += f"Analysis Verdict: {verdict}\n"
            
            summary = analysis_info.get("ai_summary") or analysis_info.get("match_summary")
            if summary:
                system_content += f"Analysis Summary: {summary}\n"
            
            strengths = analysis_info.get("strengths")
            if strengths:
                system_content += f"Identified Strengths: {', '.join(strengths[:5])}\n"
            
            weaknesses = analysis_info.get("weaknesses")
            if weaknesses:
                system_content += f"Areas for Improvement: {', '.join(weaknesses[:5])}\n"
            
            missing = analysis_info.get("missing_keywords")
            if missing:
                system_content += f"Missing Keywords: {', '.join(missing[:8])}\n"
        
        if jd_text:
            system_content += f"\nTARGET JOB DESCRIPTION (JD):\n\"\"\"{jd_text[:3000]}\"\"\"\n"

        system_content += f"\nFULL CANDIDATE RESUME TEXT:\n\"\"\"{resume_text[:6000]}\"\"\"\n"
        system_content += "========================================\n\n"
        system_content += (
            "INSTRUCTIONS FOR RESPONDING:\n"
            "- Refer directly to specific achievements, roles, tools, and sections from the candidate's resume.\n"
            "- When asked to rewrite bullets or sections, provide concrete, high-impact rewrites with quantifiable metrics where possible.\n"
            "- Be concise, encouraging, professional, and actionable.\n"
            "- Use clean Markdown formatting (bold key points, bullet lists, code blocks for text rewrites).\n"
        )
    else:
        system_content += (
            "NOTE: No resume context is currently uploaded. Provide general expert resume & career advice, "
            "and encourage the user to upload their resume in the Context panel above for tailored assistance."
        )

    api_messages = [{"role": "system", "content": system_content}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        response = _client.chat.completions.create(
            model=model or _MODEL,
            messages=api_messages,
            temperature=0.6,
            max_tokens=1500,
            stream=True
        )
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as exc:
        logger.error("Groq chat streaming failed: %s", exc)
        yield f"⚠️ Error communicating with Groq: {str(exc)}"


def chat_with_resume_context(
    messages: list,
    resume_text: str = "",
    role: str = "",
    category: str = "",
    analysis_info: dict = None,
    jd_text: str = "",
    model: str = None,
) -> str:
    """Non-streaming helper function returning complete chat response string."""
    chunks = list(stream_chat_with_resume_context(
        messages, resume_text, role, category, analysis_info, jd_text, model
    ))
    return "".join(chunks)

