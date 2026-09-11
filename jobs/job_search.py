import streamlit as st
from typing import List, Dict
from .job_portals import JobPortal
from .suggestions import (
    JOB_SUGGESTIONS, 
    LOCATION_SUGGESTIONS, 
    EXPERIENCE_RANGES,
    SALARY_RANGES,
    JOB_TYPES
)
from .companies import get_featured_companies, get_market_insights, build_smart_career_url

def filter_suggestions(query: str, suggestions: List[Dict]) -> List[Dict]:
    """Filter suggestions based on user input"""
    if not query:
        return []
    return [
        s for s in suggestions 
        if query.lower() in s["text"].lower()
    ][:5]

def get_filter_options():
    """Get filter options for job search"""
    return {
        "experience_levels": [
            {"id": "all", "text": "All Levels"},
            {"id": "0-1", "text": "0-1 years"},
            {"id": "1-3", "text": "1-3 years"},
            {"id": "3-5", "text": "3-5 years"},
            {"id": "5-7", "text": "5-7 years"},
            {"id": "7-10", "text": "7-10 years"},
            {"id": "10+", "text": "10+ years"}
        ],
        "salary_ranges": [
            {"id": "all", "text": "All Ranges"},
            {"id": "0-3", "text": "0-3 LPA"},
            {"id": "3-6", "text": "3-6 LPA"},
            {"id": "6-10", "text": "6-10 LPA"},
            {"id": "10-15", "text": "10-15 LPA"},
            {"id": "15+", "text": "15+ LPA"}
        ],
        "job_types": [
            {"id": "all", "text": "All Types"},
            {"id": "full-time", "text": "Full Time"},
            {"id": "part-time", "text": "Part Time"},
            {"id": "contract", "text": "Contract"},
            {"id": "remote", "text": "Remote"}
        ]
    }

def render_company_section(
    job_query: str = "",
    location: str = "",
    experience: str = "",
    date_posted: str = "",
    job_type: str = "",
):
    """Render a ranked company radar with pre-filtered career links."""
    st.markdown("""
        <style>
        .radar-card { background: rgba(255,255,255,.05); border: 1px solid rgba(0,191,165,.16);
            border-radius: 14px; padding: 1rem; min-height: 205px; }
        .radar-card h3 { margin: 0; font-size: 1.05rem; }
        .radar-meta { color: #94a3b8; font-size: .8rem; line-height: 1.5; }
        .radar-signal { color: #00e0b0; font-weight: 700; font-size: .78rem; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🛰️ Company Radar")
    if job_query:
        st.caption(
            f"Prioritized employers for **{job_query}**. Each launch opens the company's own careers search with your filters applied."
        )
    else:
        st.caption("Enter a role above to rank employers by fit and generate targeted career searches.")

    query_terms = {term.lower() for term in job_query.replace("/", " ").split() if len(term) > 2}
    ranked_companies = []
    for company in get_featured_companies():
        category_terms = {
            term.lower() for category in company["categories"]
            for term in category.replace("/", " ").split() if len(term) > 2
        }
        matched_terms = sorted(query_terms & category_terms)
        score = len(matched_terms)
        ranked_companies.append((score, matched_terms, company))

    ranked_companies.sort(key=lambda item: (-item[0], item[2]["name"]))
    visible_companies = ranked_companies[:6]
    applied_filters = sum(bool(value and value not in ("all", "Any time", "All Types"))
                          for value in (location, experience, date_posted, job_type))
    if job_query:
        st.success(f"{len(visible_companies)} employer searches ready · {applied_filters} additional filter(s) applied")

    columns = st.columns(3)
    for column, (score, matched_terms, company) in zip(columns * 2, visible_companies):
        smart_url = build_smart_career_url(
            company["name"], job_query, location, experience, date_posted, job_type
        )
        signal = "Strong role fit" if score >= 2 else "Relevant employer" if score == 1 else "Explore employer"
        match_text = ", ".join(matched_terms) if matched_terms else "Broad technology hiring"
        with column:
            st.markdown(f"""
                <div class="radar-card">
                    <h3><i class="{company['icon']}" style="color:{company['color']}"></i>
                    &nbsp;{company['name']}</h3>
                    <p class="radar-signal">{signal}</p>
                    <p class="radar-meta">{company['description']}</p>
                    <p class="radar-meta"><strong>Why it appears:</strong> {match_text}</p>
                </div>
            """, unsafe_allow_html=True)
            st.link_button(f"Open {company['name']} search ↗", smart_url, use_container_width=True)

def render_market_insights():
    """Render job market insights section"""
    insights = get_market_insights()
    
    st.markdown("""
        <style>
        /* ── Horizontal scroll strip for trending / location cards ── */
        .scroll-strip {
            display: flex;
            flex-direction: row;
            gap: 1rem;
            overflow-x: auto;
            padding: 0.75rem 0.25rem 1rem;
            scrollbar-width: thin;
            scrollbar-color: #00bfa5 transparent;
            -webkit-overflow-scrolling: touch;
        }
        .scroll-strip::-webkit-scrollbar {
            height: 5px;
        }
        .scroll-strip::-webkit-scrollbar-track {
            background: transparent;
        }
        .scroll-strip::-webkit-scrollbar-thumb {
            background: #00bfa5;
            border-radius: 99px;
        }
        .insight-card {
            flex: 0 0 160px;           /* fixed width, won't shrink */
            background: rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 1.1rem 0.9rem;
            text-align: center;
            transition: transform 0.25s ease, background 0.25s ease;
            border: 1px solid rgba(0,191,165,0.12);
        }
        .insight-card:hover {
            transform: translateY(-5px);
            background: rgba(0, 191, 165, 0.09);
            border-color: rgba(0,191,165,0.35);
        }
        .insight-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: #00bfa5;
        }
        .insight-card h4 {
            font-size: 0.88rem;
            margin: 0.3rem 0;
            color: #e2e8f0;
            line-height: 1.4;
        }
        .growth-text {
            color: #00e676;
            font-weight: 700;
            font-size: 0.95rem;
            margin: 0;
        }
        .salary-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            border-left: 4px solid #00bfa5;
        }
        .salary-card:hover {
            transform: translateX(10px);
            background: rgba(255, 255, 255, 0.08);
        }
        .salary-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        .role-icon {
            font-size: 1.5rem;
            margin-right: 1rem;
            color: #00bfa5;
        }
        .salary-details {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.5rem;
        }
        .salary-tag {
            background: rgba(0, 191, 165, 0.1);
            color: #00bfa5;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        .experience-tag {
            background: rgba(255, 255, 255, 0.1);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        .role-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin: 0;
        }
        .salary-range {
            font-size: 1.1rem;
            color: #00bfa5;
            font-weight: bold;
        }
        .role-icons {
            font-family: "Font Awesome 5 Free";
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 Job Market Insights")
    
    tabs = st.tabs(["Trending Skills", "Top Locations", "Salary Insights"])
    
    with tabs[0]:
        # Build all cards in ONE markdown call so they share the flex container
        cards_html = "".join(f"""
            <div class="insight-card">
                <i class="{skill['icon']} insight-icon"></i>
                <h4>{skill['name']}</h4>
                <p class="growth-text">{skill['growth']}</p>
            </div>"""
            for skill in insights["trending_skills"]
        )
        st.markdown(f'<div class="scroll-strip">{cards_html}</div>', unsafe_allow_html=True)
    
    with tabs[1]:
        locs_html = "".join(f"""
            <div class="insight-card">
                <i class="{loc['icon']} insight-icon"></i>
                <h4>{loc['name']}</h4>
                <p style="margin:0;font-size:0.8rem;color:#94a3b8;">{loc['jobs']} jobs</p>
            </div>"""
            for loc in insights["top_locations"]
        )
        st.markdown(f'<div class="scroll-strip">{locs_html}</div>', unsafe_allow_html=True)
    
    with tabs[2]:
        # Role-specific icons
        role_icons = {
            "Software Engineer": "fas fa-code",
            "Data Scientist": "fas fa-brain",
            "Product Manager": "fas fa-tasks",
            "DevOps Engineer": "fas fa-server",
            "UI/UX Designer": "fas fa-paint-brush"
        }
        
        for insight in insights["salary_insights"]:
            role = insight['role']
            icon = role_icons.get(role, "fas fa-briefcase")
            
            st.markdown(f"""
                <div class="salary-card">
                    <div class="salary-header">
                        <i class="{icon} role-icon"></i>
                        <div>
                            <h3 class="role-title">{role}</h3>
                            <div class="salary-details">
                                <span class="salary-tag">₹ {insight['range']}</span>
                                <span class="experience-tag">
                                    <i class="fas fa-history"></i> {insight['experience']}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

def render_job_search():
    """Render job search page with enhanced features"""
    st.title("🔍 Smart Job Search")
    st.markdown("Find Your Dream Job Across Multiple Platforms")

    # Market Insights Section (Above Search)
    render_market_insights()

    # Job Search Section
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)

        # ── Initialise session-state search values ──────────────────────────
        if "js_job_query" not in st.session_state:
            st.session_state.js_job_query = ""
        if "js_location" not in st.session_state:
            st.session_state.js_location = ""
        if "js_experience" not in st.session_state:
            st.session_state.js_experience = "all"
        if "js_date_posted" not in st.session_state:
            st.session_state.js_date_posted = "Any time"
        if "js_job_type" not in st.session_state:
            st.session_state.js_job_type = "All Types"
        if "js_results" not in st.session_state:
            st.session_state.js_results = []

        # Search inputs
        col1, col2 = st.columns([2, 1])

        with col1:
            raw_job_query = st.text_input(
                "Job Title / Skills",
                value=st.session_state.js_job_query,
                placeholder="e.g. Software Engineer, Data Scientist",
                key="js_job_input"
            )
            job_query = raw_job_query  # working value for this render

            if raw_job_query and len(raw_job_query) >= 2:
                filtered_jobs = [
                    s["text"] for s in JOB_SUGGESTIONS
                    if raw_job_query.lower() in s["text"].lower()
                ]
                if filtered_jobs:
                    selected = st.selectbox(
                        "Select Job Title", filtered_jobs, key="js_job_select"
                    )
                    job_query = selected  # use the autocomplete pick

        with col2:
            raw_location = st.text_input(
                "Location",
                value=st.session_state.js_location,
                placeholder="e.g. Bangalore, Mumbai",
                key="js_loc_input"
            )
            location = raw_location

            if raw_location and len(raw_location) >= 2:
                filtered_locations = [
                    s["text"] for s in LOCATION_SUGGESTIONS
                    if raw_location.lower() in s["text"].lower()
                ]
                if filtered_locations:
                    selected_loc = st.selectbox(
                        "Select Location", filtered_locations, key="js_loc_select"
                    )
                    location = selected_loc

        # Advanced Filters
        with st.expander("🎯 Advanced Filters"):
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            filter_cols = st.columns(4)

            with filter_cols[0]:
                exp_options = get_filter_options()["experience_levels"]
                exp_idx = next(
                    (i for i, o in enumerate(exp_options)
                     if o["id"] == st.session_state.js_experience), 0
                )
                experience = st.selectbox(
                    "Experience Level",
                    options=exp_options,
                    index=exp_idx,
                    format_func=lambda x: x["text"],
                    key="js_exp_select"
                )
            with filter_cols[1]:
                date_options = ["Any time", "Past 24 hours", "Past week", "Past month"]
                date_idx = date_options.index(st.session_state.js_date_posted) \
                    if st.session_state.js_date_posted in date_options else 0
                date_posted = st.selectbox(
                    "Date Posted",
                    options=date_options,
                    index=date_idx,
                    key="js_date_select"
                )
            with filter_cols[2]:
                salary_range = st.selectbox(
                    "Salary Range",
                    options=get_filter_options()["salary_ranges"],
                    format_func=lambda x: x["text"],
                    key="js_salary_select"
                )
                st.caption("Salary is a planning preference; portal links use the filters supported by each job board.")
            with filter_cols[3]:
                jtype_options = ["All Types", "Full Time", "Part Time", "Contract", "Remote"]
                jtype_idx = jtype_options.index(st.session_state.js_job_type) \
                    if st.session_state.js_job_type in jtype_options else 0
                job_type = st.selectbox(
                    "Job Type",
                    options=jtype_options,
                    index=jtype_idx,
                    key="js_jtype_select"
                )
            st.markdown('</div>', unsafe_allow_html=True)

        # Search button — persist values into session_state on click
        if st.button("SEARCH JOBS", type="primary"):
            # Persist all filters so company cards stay pre-filtered after reruns
            st.session_state.js_job_query  = job_query
            st.session_state.js_location   = location
            st.session_state.js_experience = experience["id"] if isinstance(experience, dict) else experience
            st.session_state.js_date_posted = date_posted
            st.session_state.js_job_type   = job_type

            if job_query:
                job_portal = JobPortal()
                results = job_portal.search_jobs(
                    job_query,
                    location=location,
                    experience=experience,
                    date_posted=date_posted,
                    job_type=job_type,
                )
                st.session_state.js_results = results
            else:
                st.session_state.js_results = []
                st.warning("Please enter a job title or skills to search.")

        st.markdown('</div>', unsafe_allow_html=True)

    # URL generation is local; these links open the live job boards in a new tab.
    search_results = st.session_state.get("js_results", [])
    if search_results:
        st.markdown("### 🎯 Search Launch Center")
        st.caption(
            f"{len(search_results)} job-board searches generated successfully. "
            "The live listings load on the selected portal after you open a link."
        )
        result_columns = st.columns(3)
        for column, result in zip(result_columns * 2, search_results):
            with column:
                st.markdown(f"""
                    <div class="radar-card" style="min-height:125px;">
                        <h3><i class="{result['icon']}" style="color:{result['color']}"></i>
                        &nbsp;{result['portal']}</h3>
                        <p class="radar-meta">{result['title']}</p>
                        <p class="radar-signal">Portal URL ready · filters applied where supported</p>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button(f"Open {result['portal']} ↗", result["url"], use_container_width=True)

    # ── Company cards always use persisted session_state values ────────────
    render_company_section(
        job_query=st.session_state.get("js_job_query", ""),
        location=st.session_state.get("js_location", ""),
        experience=st.session_state.get("js_experience", ""),
        date_posted=st.session_state.get("js_date_posted", ""),
        job_type=st.session_state.get("js_job_type", ""),
    )

# Removed render_job_search() call to prevent automatic rendering
