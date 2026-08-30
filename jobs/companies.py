"""Company data and market insights for job search"""
from urllib.parse import urlencode, quote_plus

FEATURED_COMPANIES = {
    "tech": [
        {
            "name": "Google",
            "icon": "fab fa-google",
            "color": "#4285F4",
            "careers_url": "https://careers.google.com",
            "description": "Leading technology company known for search, cloud, and innovation",
            "categories": ["Software", "AI/ML", "Cloud", "Data Science"]
        },
        {
            "name": "Microsoft",
            "icon": "fab fa-microsoft",
            "color": "#00A4EF",
            "careers_url": "https://careers.microsoft.com",
            "description": "Global leader in software, cloud, and enterprise solutions",
            "categories": ["Software", "Cloud", "Gaming", "Enterprise"]
        },
        {
            "name": "Amazon",
            "icon": "fab fa-amazon",
            "color": "#FF9900",
            "careers_url": "https://www.amazon.jobs",
            "description": "E-commerce and cloud computing giant",
            "categories": ["Software", "Operations", "Cloud", "Retail"]
        },
        {
            "name": "Apple",
            "icon": "fab fa-apple",
            "color": "#555555",
            "careers_url": "https://www.apple.com/careers",
            "description": "Innovation leader in consumer technology",
            "categories": ["Software", "Hardware", "Design", "AI/ML"]
        },
        {
            "name": "Facebook",
            "icon": "fab fa-facebook",
            "color": "#1877F2",
            "careers_url": "https://www.metacareers.com/",
            "description": "Social media and technology company",
            "categories": ["Software", "Marketing", "Networking", "AI/ML"]
        },
        {
            "name": "Netflix",
            "icon": "fas fa-play-circle",
            "color": "#E50914",
            "careers_url": "https://explore.jobs.netflix.net/careers",
            "description": "Streaming media company",
            "categories": ["Software", "Marketing", "Design", "Service"],
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Netflix_2015_logo.svg/1920px-Netflix_2015_logo.svg.png",
            "website": "https://jobs.netflix.com/",
            "industry": "Entertainment & Technology"
        }
    ],
    "indian_tech": [
        {
            "name": "TCS",
            "icon": "fas fa-building",
            "color": "#0070C0",
            "careers_url": "https://www.tcs.com/careers",
            "description": "India's largest IT services company",
            "categories": ["IT Services", "Consulting", "Digital"]
        },
        {
            "name": "Infosys",
            "icon": "fas fa-building",
            "color": "#007CC3",
            "careers_url": "https://www.infosys.com/careers",
            "description": "Global leader in digital services and consulting",
            "categories": ["IT Services", "Consulting", "Digital"]
        },
        {
            "name": "Wipro",
            "icon": "fas fa-building",
            "color": "#341F65",
            "careers_url": "https://careers.wipro.com",
            "description": "Leading global information technology company",
            "categories": ["IT Services", "Consulting", "Digital"]
        },
        {
            "name": "HCL",
            "icon": "fas fa-building",
            "color": "#0075C9",
            "careers_url": "https://www.hcltech.com/careers",
            "description": "Global technology company",
            "categories": ["IT Services", "Engineering", "Digital"]
        }
    ],
    "global_corps": [
        {
            "name": "IBM",
            "icon": "fas fa-server",
            "color": "#1F70C1",
            "careers_url": "https://www.ibm.com/careers",
            "description": "Global leader in technology and consulting",
            "categories": ["Software", "Consulting", "AI/ML", "Cloud"],
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/IBM_logo.svg/1920px-IBM_logo.svg.png",
            "website": "https://www.ibm.com/careers/",
            "industry": "Technology & Consulting"
        },
        {
            "name": "Accenture",
            "icon": "fas fa-building",
            "color": "#A100FF",
            "careers_url": "https://www.accenture.com/careers",
            "description": "Global professional services company",
            "categories": ["Consulting", "Technology", "Digital"]
        },
        {
            "name": "Cognizant",
            "icon": "fas fa-building",
            "color": "#1299D8",
            "careers_url": "https://careers.cognizant.com",
            "description": "Leading professional services company",
            "categories": ["IT Services", "Consulting", "Digital"]
        }
    ]
}

JOB_MARKET_INSIGHTS = {
    "trending_skills": [
        {"name": "Artificial Intelligence", "growth": "+45%", "icon": "fas fa-brain"},
        {"name": "Cloud Computing", "growth": "+38%", "icon": "fas fa-cloud"},
        {"name": "Data Science", "growth": "+35%", "icon": "fas fa-chart-line"},
        {"name": "Cybersecurity", "growth": "+32%", "icon": "fas fa-shield-alt"},
        {"name": "DevOps", "growth": "+30%", "icon": "fas fa-code-branch"},
        {"name": "Machine Learning", "growth": "+28%", "icon": "fas fa-robot"},
        {"name": "Blockchain", "growth": "+25%", "icon": "fas fa-lock"},
        {"name": "Big Data", "growth": "+23%", "icon": "fas fa-database"},
        {"name": "Internet of Things", "growth": "+21%", "icon": "fas fa-wifi"}
    ],
    "top_locations": [
        {"name": "Bangalore", "jobs": "50,000+", "icon": "fas fa-city"},
        {"name": "Mumbai", "jobs": "35,000+", "icon": "fas fa-city"},
        {"name": "Delhi NCR", "jobs": "30,000+", "icon": "fas fa-city"},
        {"name": "Hyderabad", "jobs": "25,000+", "icon": "fas fa-city"},
        {"name": "Pune", "jobs": "20,000+", "icon": "fas fa-city"},
        {"name": "Chennai", "jobs": "15,000+", "icon": "fas fa-city"},
        {"name": "Noida", "jobs": "10,000+", "icon": "fas fa-city"},
        {"name": "Vadodara", "jobs": "7,000+", "icon": "fas fa-city"},
        {"name": "Ahmedabad", "jobs": "6,000+", "icon": "fas fa-city"},
        {"name": "Remote", "jobs": "3,000+", "icon": "fas fa-globe-americas"},
    ],
    "salary_insights": [
        {"role": "Machine Learning Engineer", "range": "10-35 LPA", "experience": "0-5 years"},
        {"role": "Big Data Engineer", "range": "8-30 LPA", "experience": "0-5 years"},
        {"role": "Software Engineer", "range": "5-25 LPA", "experience": "0-5 years"},
        {"role": "Data Scientist", "range": "8-30 LPA", "experience": "0-5 years"},
        {"role": "DevOps Engineer", "range": "6-28 LPA", "experience": "0-5 years"},
        {"role": "UI/UX Designer", "range": "5-25 LPA", "experience": "0-5 years"},
        {"role": "Full Stack Developer", "range": "8-30 LPA", "experience": "0-5 years"},
        {"role": "C++/C#/Python/Java Developer", "range": "6-26 LPA", "experience": "0-5 years"},
        {"role": "Django Developer", "range": "7-27 LPA", "experience": "0-5 years"},
        {"role": "Cloud Engineer", "range": "6-26 LPA", "experience": "0-5 years"},
        {"role": "Google Cloud/AWS/Azure Engineer", "range": "6-26 LPA", "experience": "0-5 years"},
        {"role": "Salesforce Engineer", "range": "6-26 LPA", "experience": "0-5 years"},
    ]
}

def get_featured_companies(category=None):
    """Get featured companies, optionally filtered by category"""
    if category and category in FEATURED_COMPANIES:
        return FEATURED_COMPANIES[category]
    return [company for companies in FEATURED_COMPANIES.values() for company in companies]

def get_market_insights():
    """Get job market insights"""
    return JOB_MARKET_INSIGHTS

# ─────────────────────────────────────────────────────────────────────────────
# Experience-level mappings  (our range string → each company's param value)
# ─────────────────────────────────────────────────────────────────────────────
_EXP_GOOGLE = {          # no native exp filter in URL; append to query
    "0-1": "entry level", "1-3": "junior", "3-5": "mid level",
    "5-7": "senior", "7-10": "senior", "10+": "principal staff",
}
_EXP_MICROSOFT = {       # &el=
    "0-1": "Entry+Level", "1-3": "Entry+Level", "3-5": "Mid-Level",
    "5-7": "Senior", "7-10": "Senior", "10+": "Senior",
}
_EXP_AMAZON = {          # &experience_level_key[]=
    "0-1": "entry_level", "1-3": "entry_level", "3-5": "mid_level",
    "5-7": "mid_level", "7-10": "senior", "10+": "senior",
}
_EXP_META = {            # &career_level=
    "0-1": "entry", "1-3": "entry", "3-5": "mid",
    "5-7": "senior", "7-10": "senior", "10+": "director",
}
_EXP_IBM = {             # &jobCategory= (appended to keyword)
    "0-1": "Entry Level", "1-3": "Entry Level", "3-5": "Mid Level",
    "5-7": "Senior", "7-10": "Senior", "10+": "Executive",
}
_EXP_COGNIZANT = {       # &experienceLevel=
    "0-1": "entry", "1-3": "junior", "3-5": "mid",
    "5-7": "senior", "7-10": "senior", "10+": "lead",
}

# ─────────────────────────────────────────────────────────────────────────────
# Date-posted mappings  (our label → each company's param value)
# ─────────────────────────────────────────────────────────────────────────────
_DATE_AMAZON = {
    "Past 24 hours": "last_24_hours", "Past week": "last_7_days",
    "Past month": "last_30_days",
}
_DATE_MICROSOFT = {      # &pg= is page; date uses &d=
    "Past 24 hours": "1", "Past week": "7", "Past month": "30",
}
_DATE_COGNIZANT = {
    "Past 24 hours": "1", "Past week": "7", "Past month": "30",
}
_DATE_WIPRO = {
    "Past 24 hours": "1", "Past week": "7", "Past month": "30",
}

# ─────────────────────────────────────────────────────────────────────────────
# Job-type mappings
# ─────────────────────────────────────────────────────────────────────────────
_JTYPE_AMAZON = {
    "Full Time": "Full+Time", "Part Time": "Part-Time",
    "Contract": "Temporary", "Remote": "Temporary",
}
_JTYPE_MICROSOFT = {
    "Full Time": "full_time", "Part Time": "part_time",
    "Contract": "contract", "Remote": "remote",
}


# ─────────────────────────────────────────────────────────────────────────────
# Per-company URL builders
# signature: (role, location, experience_id, date_posted, job_type) → URL str
# All params except role default to "" (meaning "do not filter").
# ─────────────────────────────────────────────────────────────────────────────
def _google_url(r, l, exp="", date="", jtype=""):
    params = {"q": r, "location": l}
    if exp and exp != "all":
        params["q"] = f"{r} {_EXP_GOOGLE.get(exp, '')}"
    return "https://careers.google.com/jobs/results/?" + urlencode(params)


def _microsoft_url(r, l, exp="", date="", jtype=""):
    params = {"q": r, "l": l}
    if exp and exp != "all":
        params["el"] = _EXP_MICROSOFT.get(exp, "")
    if date and date != "Any time":
        params["d"] = _DATE_MICROSOFT.get(date, "")
    if jtype and jtype != "All Types":
        params["et"] = _JTYPE_MICROSOFT.get(jtype, "")
    return "https://jobs.microsoft.com/en/search?" + urlencode({k: v for k, v in params.items() if v})


def _amazon_url(r, l, exp="", date="", jtype=""):
    params = {"base_query": r, "loc_query": l}
    if exp and exp != "all":
        params["experience_level_key[]"] = _EXP_AMAZON.get(exp, "")
    if date and date != "Any time":
        params["posted_date_filter"] = _DATE_AMAZON.get(date, "")
    if jtype and jtype not in ("All Types", ""):
        params["job_type[]"] = _JTYPE_AMAZON.get(jtype, "")
    return "https://www.amazon.jobs/en/search?" + urlencode({k: v for k, v in params.items() if v})


def _apple_url(r, l, exp="", date="", jtype=""):
    q = f"{r} {l}".strip()
    params = {"q": q}
    if jtype and jtype == "Remote":
        params["team"] = "Remote"
    return "https://jobs.apple.com/en-us/search?" + urlencode(params)


def _meta_url(r, l, exp="", date="", jtype=""):
    params = {"q": r, "offices[0]": l}
    if exp and exp != "all":
        params["career_level"] = _EXP_META.get(exp, "")
    return "https://www.metacareers.com/jobs?" + urlencode({k: v for k, v in params.items() if v})


def _netflix_url(r, l, exp="", date="", jtype=""):
    return "https://explore.jobs.netflix.net/careers?" + urlencode({"query": f"{r} {l}".strip()})


def _tcs_url(r, l, exp="", date="", jtype=""):
    params = {"search": r, "location": l}
    return "https://www.tcs.com/careers/tcs-careers-apply-now?" + urlencode(params)


def _infosys_url(r, l, exp="", date="", jtype=""):
    params = {"jobCategory": r, "location": l}
    return "https://career.infosys.com/joblist?" + urlencode(params)


def _wipro_url(r, l, exp="", date="", jtype=""):
    params = {"keyword": r, "location": l}
    if date and date != "Any time":
        params["postedDate"] = _DATE_WIPRO.get(date, "")
    if jtype == "Remote":
        params["workMode"] = "Remote"
    return "https://careers.wipro.com/careers-home/jobs?" + urlencode({k: v for k, v in params.items() if v})


def _hcl_url(r, l, exp="", date="", jtype=""):
    params = {"keyword": r, "location": l}
    if jtype == "Remote":
        params["workMode"] = "Remote"
    return "https://www.hcltech.com/careers/job-search?" + urlencode(params)


def _ibm_url(r, l, exp="", date="", jtype=""):
    keyword = r
    if exp and exp != "all":
        keyword = f"{_EXP_IBM.get(exp, '')} {r}".strip()
    params = {"field_keyword_08": keyword, "field_keyword_18": l}
    return "https://www.ibm.com/careers/search?" + urlencode({k: v for k, v in params.items() if v})


def _accenture_url(r, l, exp="", date="", jtype=""):
    params = {"jk": r, "l": l}
    if jtype == "Remote":
        params["workerType"] = "Remote"
    return "https://www.accenture.com/us-en/careers/jobsearch?" + urlencode({k: v for k, v in params.items() if v})


def _cognizant_url(r, l, exp="", date="", jtype=""):
    params = {"keywords": r, "location": l}
    if exp and exp != "all":
        params["experienceLevel"] = _EXP_COGNIZANT.get(exp, "")
    if date and date != "Any time":
        params["daysPosted"] = _DATE_COGNIZANT.get(date, "")
    return "https://careers.cognizant.com/global/en/search-results?" + urlencode({k: v for k, v in params.items() if v})


_CAREER_URL_BUILDERS = {
    "Google": _google_url,
    "Microsoft": _microsoft_url,
    "Amazon": _amazon_url,
    "Apple": _apple_url,
    "Facebook": _meta_url,
    "Netflix": _netflix_url,
    "TCS": _tcs_url,
    "Infosys": _infosys_url,
    "Wipro": _wipro_url,
    "HCL": _hcl_url,
    "IBM": _ibm_url,
    "Accenture": _accenture_url,
    "Cognizant": _cognizant_url,
}


def build_smart_career_url(
    company_name: str,
    role: str,
    location: str = "",
    experience: str = "",
    date_posted: str = "",
    job_type: str = "",
) -> str:
    """Return a pre-filtered career page URL for the given company and filters.

    Args:
        company_name: Exact name matching FEATURED_COMPANIES.
        role:         Job title / skill keyword.
        location:     City or region.
        experience:   One of the experience range IDs ("0-1", "1-3", "3-5", etc.) or "all".
        date_posted:  "Any time", "Past 24 hours", "Past week", "Past month".
        job_type:     "Full Time", "Part Time", "Contract", "Remote" or "All Types".

    Returns:
        A URL string (may be pre-filtered or the base careers URL as fallback).
    """
    role = role.strip()
    location = location.strip()

    builder = _CAREER_URL_BUILDERS.get(company_name)
    if builder and role:
        try:
            return builder(role, location, experience, date_posted, job_type)
        except Exception:
            pass  # fall through to base URL

    company = get_company_info(company_name)
    return company["careers_url"] if company else "#"


def get_company_info(company_name):
    """Get company information by name"""
    for companies in FEATURED_COMPANIES.values():
        for company in companies:
            if company["name"] == company_name:
                return company
    return None

def get_companies_by_industry(industry):
    """Get list of companies by industry"""
    companies = []
    for companies_list in FEATURED_COMPANIES.values():
        for company in companies_list:
            if "industry" in company and company["industry"] == industry:
                companies.append(company)
    return companies
