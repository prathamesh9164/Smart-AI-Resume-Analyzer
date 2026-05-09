"""
ui_components.py  ·  Premium UI building blocks for Smart Resume AI
Design language: deep-space dark + electric indigo/teal accents
"""
import streamlit as st


# ── Helpers ──────────────────────────────────────────────────────────────────

def apply_modern_styles():
    """No-op: styles are loaded from style/style.css in app.py __init__."""
    pass


# ── Page Structures ───────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = ""):
    """Render a premium gradient page header."""
    sub_html = f'<p class="header-subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div class="page-header animate-fade-up">
      <h1 class="header-title">{title}</h1>
      {sub_html}
    </div>""", unsafe_allow_html=True)


def hero_section(title: str, subtitle: str = ""):
    """Render a large centered hero section with glow effects."""
    sub_html = f'<div class="header-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="page-header hero-header animate-fade-up">
      <h1 class="header-title">{title}</h1>
      {sub_html}
    </div>""", unsafe_allow_html=True)


# ── Cards ─────────────────────────────────────────────────────────────────────

def feature_card(icon: str, title: str, description: str):
    """Render a modern feature card with icon box, hover lift."""
    st.markdown(f"""
    <div class="card feature-card animate-fade-up">
      <div class="feature-icon">
        <i class="{icon}"></i>
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>""", unsafe_allow_html=True)


def stat_card(label: str, value: str, icon: str = "fas fa-chart-bar",
              color: str = "#6c63ff"):
    """Render a compact statistics card."""
    st.markdown(f"""
    <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                border-radius:14px;padding:22px;text-align:center;
                border-top:3px solid {color};transition:all .25s ease;">
      <div style="font-size:1.6rem;color:{color};margin-bottom:8px;">
        <i class="{icon}"></i>
      </div>
      <div style="font-size:1.9rem;font-weight:800;color:#f1f5f9;
                  font-family:'Plus Jakarta Sans',sans-serif;">{value}</div>
      <div style="font-size:.78rem;color:#64748b;margin-top:4px;
                  text-transform:uppercase;letter-spacing:.6px;">{label}</div>
    </div>""", unsafe_allow_html=True)


def info_card(content: str, border_color: str = "#6c63ff"):
    """Render a simple bordered info card."""
    st.markdown(f"""
    <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                border-left:4px solid {border_color};border-radius:14px;
                padding:20px;margin:8px 0;">
      {content}
    </div>""", unsafe_allow_html=True)


def groq_badge(active: bool = True):
    """Render the Groq AI status badge."""
    if active:
        st.markdown("""
        <div class="glow-badge animate-fade-up" style="margin-bottom:20px;display:inline-flex;">
          <span style="width:9px;height:9px;border-radius:50%;background:#6c63ff;
                       box-shadow:0 0 10px #6c63ff;display:inline-block;
                       animation:pulse-glow 2s infinite;"></span>
          <span>Groq AI &mdash; AI Analysis Active</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:inline-flex;align-items:center;gap:8px;
                    background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.3);
                    border-radius:50px;padding:7px 18px;margin-bottom:16px;font-size:.82rem;">
          <span style="color:#f59e0b;">⚠️ Groq unavailable —
            add <code>GROQ_API_KEY</code> to <code>.env</code>
            for AI analysis</span>
        </div>""", unsafe_allow_html=True)


# ── Score Display ─────────────────────────────────────────────────────────────

def score_ring(score: int, label: str = "AI Score"):
    """Render an SVG circular score ring."""
    radius = 46
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1 - score / 100)
    color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
    st.markdown(f"""
    <div style="text-align:center;">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="{radius}" fill="none"
                stroke="rgba(255,255,255,0.07)" stroke-width="8"/>
        <circle cx="60" cy="60" r="{radius}" fill="none"
                stroke="{color}" stroke-width="8"
                stroke-linecap="round"
                stroke-dasharray="{circumference:.1f}"
                stroke-dashoffset="{offset:.1f}"
                transform="rotate(-90 60 60)"
                style="transition:stroke-dashoffset 1s ease;"/>
        <text x="60" y="55" text-anchor="middle"
              font-family="Plus Jakarta Sans,sans-serif"
              font-size="22" font-weight="800" fill="{color}">{score}</text>
        <text x="60" y="72" text-anchor="middle"
              font-family="Inter,sans-serif"
              font-size="9" fill="#64748b">{label}</text>
      </svg>
    </div>""", unsafe_allow_html=True)


def verdict_banner(gem: dict):
    """Render the full Groq verdict banner."""
    verdict = gem.get("ai_verdict", "Good")
    score   = gem.get("ai_overall_score", 0)
    summary = gem.get("ai_summary", "")
    likelihood = gem.get("interview_likelihood", "—")

    vc = {"Excellent":"#22c55e","Strong":"#00d4aa","Good":"#6c63ff",
          "Needs Work":"#f59e0b","Major Revision":"#ef4444"}.get(verdict,"#6c63ff")

    radius = 46
    circ   = 2 * 3.14159 * radius
    offset = circ * (1 - score / 100)

    lh_color = {"Very High":"#22c55e","High":"#6c63ff",
                "Medium":"#f59e0b","Low":"#ef4444"}.get(likelihood,"#94a3b8")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0e1220,#141929);
                border:1px solid {vc}44;border-radius:20px;
                padding:28px 32px;margin:16px 0;
                box-shadow:0 8px 32px {vc}22;position:relative;overflow:hidden;">
      <!-- glow blob -->
      <div style="position:absolute;top:-40%;right:-10%;width:320px;height:320px;
                  background:radial-gradient(circle,{vc}18 0%,transparent 65%);
                  pointer-events:none;"></div>
      <div style="display:flex;align-items:center;gap:28px;flex-wrap:wrap;position:relative;">
        <!-- score ring -->
        <div style="text-align:center;min-width:120px;">
          <svg width="120" height="120" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="{radius}" fill="none"
                    stroke="rgba(255,255,255,0.07)" stroke-width="8"/>
            <circle cx="60" cy="60" r="{radius}" fill="none"
                    stroke="{vc}" stroke-width="8" stroke-linecap="round"
                    stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"
                    transform="rotate(-90 60 60)"/>
            <text x="60" y="55" text-anchor="middle"
                  font-family="Plus Jakarta Sans,sans-serif"
                  font-size="24" font-weight="800" fill="{vc}">{score}</text>
            <text x="60" y="72" text-anchor="middle"
                  font-family="Inter,sans-serif" font-size="9" fill="#64748b">AI SCORE</text>
          </svg>
          <div style="margin-top:6px;">
            <span style="background:{vc};color:#000;font-weight:700;font-size:.72rem;
                         border-radius:50px;padding:3px 12px;display:inline-block;
                         letter-spacing:.5px;">{verdict.upper()}</span>
          </div>
        </div>
        <!-- text -->
        <div style="flex:1;min-width:220px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
            <div style="width:8px;height:8px;border-radius:50%;background:#6c63ff;
                        box-shadow:0 0 8px #6c63ff;"></div>
            <span style="color:#8b83ff;font-weight:600;font-size:.85rem;
                         letter-spacing:.3px;">GROQ AI ANALYSIS</span>
          </div>
          <p style="color:#e2e8f0;margin:0 0 14px;line-height:1.7;font-size:.95rem;">
            {summary}
          </p>
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="color:#64748b;font-size:.82rem;">Interview Likelihood:</span>
            <span style="color:{lh_color};font-weight:700;font-size:.85rem;">
              {likelihood}
            </span>
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


def score_cards_row(ats: int, kw: int, fmt: int, sec: int):
    """Render 4-column score metric cards."""
    def color(s):
        return "#22c55e" if s >= 75 else "#f59e0b" if s >= 50 else "#ef4444"

    cols = st.columns(4)
    for col, label, val in zip(cols,
        ["ATS Score","Keyword Match","Format Score","Section Score"],
        [ats, kw, fmt, sec]):
        col.markdown(f"""
        <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px;padding:20px;text-align:center;
                    border-top:3px solid {color(val)};margin-bottom:4px;">
          <div style="font-size:2rem;font-weight:800;color:{color(val)};
                      font-family:'Plus Jakarta Sans',sans-serif;">{val}%</div>
          <div style="color:#64748b;font-size:.75rem;text-transform:uppercase;
                      letter-spacing:.5px;margin-top:4px;">{label}</div>
        </div>""", unsafe_allow_html=True)


def strengths_weaknesses(strengths: list, weaknesses: list):
    """Render side-by-side strength/weakness panels."""
    c1, c2 = st.columns(2)
    with c1:
        items = "".join(
            f"<div style='display:flex;gap:10px;margin-bottom:10px;'>"
            f"<span style='color:#22c55e;margin-top:2px;'>✓</span>"
            f"<span style='color:#cbd5e1;font-size:.9rem;'>{s}</span></div>"
            for s in strengths
        )
        st.markdown(f"""
        <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                    border-left:3px solid #22c55e;border-radius:14px;padding:22px;">
          <div style="font-weight:700;color:#22c55e;margin-bottom:16px;
                      font-family:'Plus Jakarta Sans',sans-serif;">
            💪 Strengths
          </div>
          {items}
        </div>""", unsafe_allow_html=True)
    with c2:
        items = "".join(
            f"<div style='display:flex;gap:10px;margin-bottom:10px;'>"
            f"<span style='color:#f59e0b;margin-top:2px;'>!</span>"
            f"<span style='color:#cbd5e1;font-size:.9rem;'>{w}</span></div>"
            for w in weaknesses
        )
        st.markdown(f"""
        <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                    border-left:3px solid #ef4444;border-radius:14px;padding:22px;">
          <div style="font-weight:700;color:#ef4444;margin-bottom:16px;
                      font-family:'Plus Jakarta Sans',sans-serif;">
            🔧 Areas to Improve
          </div>
          {items}
        </div>""", unsafe_allow_html=True)


def section_feedback_grid(section_feedback: dict):
    """Render a 2-col grid of section feedback cards."""
    icons = {"contact":"📞","summary":"📝","experience":"💼",
             "skills":"🛠️","education":"🎓","projects":"🚀"}
    items = list(section_feedback.items())
    cols = st.columns(2)
    for i, (section, feedback) in enumerate(items):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="section-fb-card">
              <div style="font-weight:700;color:#8b83ff;margin-bottom:8px;
                          font-size:.88rem;text-transform:uppercase;letter-spacing:.4px;">
                {icons.get(section,'📄')} {section.title()}
              </div>
              <p style="color:#94a3b8;margin:0;font-size:.88rem;line-height:1.6;">
                {feedback}
              </p>
            </div>""", unsafe_allow_html=True)


def keyword_analysis(found: list, missing: list):
    """Render keyword gap analysis with tag pills."""
    c1, c2 = st.columns(2)
    with c1:
        tags = " ".join(f'<span class="kw-tag-found">✓ {k}</span>' for k in found) \
               or '<span style="color:#64748b;font-size:.85rem;">None detected</span>'
        st.markdown(f"""
        <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px;padding:20px;">
          <div style="font-weight:700;color:#22c55e;margin-bottom:12px;font-size:.9rem;">
            ✓ Found Keywords
          </div>
          <div style="line-height:2;">{tags}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        tags = " ".join(f'<span class="kw-tag-miss">✗ {k}</span>' for k in missing) \
               or '<span style="color:#22c55e;font-size:.85rem;">🎉 All keywords matched!</span>'
        st.markdown(f"""
        <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px;padding:20px;">
          <div style="font-weight:700;color:#ef4444;margin-bottom:12px;font-size:.9rem;">
            ✗ Missing Keywords
          </div>
          <div style="line-height:2;">{tags}</div>
        </div>""", unsafe_allow_html=True)


def bullet_rewrites(rewrites: list):
    """Render before/after bullet point rewrite cards."""
    st.markdown("""
    <div style="font-size:.82rem;color:#64748b;margin-bottom:16px;
                display:flex;align-items:center;gap:8px;">
      <span style="color:#6c63ff;">✦</span>
      Groq identified weak bullets and rewrote them with stronger impact language.
    </div>""", unsafe_allow_html=True)

    for bw in rewrites:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="rewrite-original">
              <div style="color:#ef4444;font-size:.7rem;font-weight:700;
                          letter-spacing:.6px;margin-bottom:8px;">ORIGINAL</div>
              <div style="color:#94a3b8;font-size:.88rem;line-height:1.5;">
                {bw.get('original','')}
              </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="rewrite-improved">
              <div style="color:#22c55e;font-size:.7rem;font-weight:700;
                          letter-spacing:.6px;margin-bottom:8px;">✨ IMPROVED</div>
              <div style="color:#e2e8f0;font-size:.88rem;line-height:1.5;">
                {bw.get('improved','')}
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


def ats_tips_card(tips: list):
    """Render ATS optimization tips box."""
    items = "".join(
        f"<div style='display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;'>"
        f"<span style='color:#6c63ff;font-size:1rem;margin-top:1px;flex-shrink:0;'>💡</span>"
        f"<span style='color:#94a3b8;font-size:.88rem;line-height:1.5;'>{t}</span></div>"
        for t in tips
    )
    st.markdown(f"""
    <div style="background:#1a2035;border:1px solid rgba(108,99,255,0.2);
                border-radius:14px;padding:22px;margin:16px 0;">
      <div style="font-weight:700;color:#8b83ff;margin-bottom:16px;
                  font-family:'Plus Jakarta Sans',sans-serif;">
        🤖 ATS Optimization Tips from Groq
      </div>
      {items}
    </div>""", unsafe_allow_html=True)


def course_card(name: str, url: str):
    """Render a single course recommendation card."""
    st.markdown(f"""
    <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                border-radius:12px;padding:16px;margin-bottom:10px;
                transition:all .25s ease;">
      <div style="font-weight:600;color:#e2e8f0;font-size:.88rem;
                  margin-bottom:8px;">{name}</div>
      <a href="{url}" target="_blank"
         style="color:#8b83ff;font-size:.8rem;text-decoration:none;
                display:inline-flex;align-items:center;gap:4px;">
        View Course <span style="font-size:.7rem;">→</span>
      </a>
    </div>""", unsafe_allow_html=True)


# ── Legacy compatibility stubs ────────────────────────────────────────────────

def about_section(title="", description="", team_members=None, content="",
                  image_path=None, social_links=None):
    """Legacy stub — renders a simple about block."""
    st.markdown(f"""
    <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                border-radius:20px;padding:32px;margin:16px 0;">
      <h2 style="color:#f1f5f9;margin:0 0 12px;">{title}</h2>
      <p style="color:#94a3b8;line-height:1.7;">{description or content}</p>
    </div>""", unsafe_allow_html=True)


def render_analytics_section(resume_uploaded=False, metrics=None):
    """Render 3 analytics stat cards."""
    metrics = metrics or {"views": 0, "downloads": 0, "score": "N/A"}
    c1, c2, c3 = st.columns(3)
    with c1:
        stat_card("Resume Views", str(metrics["views"]), "fas fa-eye", "#6c63ff")
    with c2:
        stat_card("Downloads", str(metrics["downloads"]), "fas fa-download", "#00d4aa")
    with c3:
        stat_card("Profile Score", str(metrics["score"]), "fas fa-chart-line", "#f59e0b")


def render_activity_section(resume_uploaded=False):
    """Render recent activity panel."""
    body = """
    <div style="color:#94a3b8;">
      <p style="margin:.6rem 0;font-size:.9rem;">• Resume uploaded and analyzed</p>
      <p style="margin:.6rem 0;font-size:.9rem;">• Generated optimization suggestions</p>
      <p style="margin:.6rem 0;font-size:.9rem;">• Updated profile score</p>
    </div>""" if resume_uploaded else """
    <div style="text-align:center;padding:2rem;color:#64748b;">
      <div style="font-size:2rem;color:#6c63ff;margin-bottom:12px;">📤</div>
      <p style="margin:0;font-size:.9rem;">Upload your resume to see activity</p>
    </div>"""
    st.markdown(f"""
    <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                border-radius:16px;padding:24px;">
      <div style="font-weight:700;color:#f1f5f9;margin-bottom:16px;
                  font-family:'Plus Jakarta Sans',sans-serif;">
        <i class="fas fa-history" style="color:#6c63ff;margin-right:8px;"></i>Recent Activity
      </div>
      {body}
    </div>""", unsafe_allow_html=True)


def render_suggestions_section(resume_uploaded=False):
    """Render suggestions panel."""
    body = """
    <div style="color:#94a3b8;">
      <p style="margin:.6rem 0;font-size:.9rem;">• Add more quantifiable achievements</p>
      <p style="margin:.6rem 0;font-size:.9rem;">• Include relevant keywords</p>
      <p style="margin:.6rem 0;font-size:.9rem;">• Optimize formatting</p>
    </div>""" if resume_uploaded else """
    <div style="text-align:center;padding:2rem;color:#64748b;">
      <div style="font-size:2rem;color:#6c63ff;margin-bottom:12px;">📄</div>
      <p style="margin:0;font-size:.9rem;">Upload your resume to get suggestions</p>
    </div>"""
    st.markdown(f"""
    <div style="background:#1a2035;border:1px solid rgba(255,255,255,0.07);
                border-radius:16px;padding:24px;">
      <div style="font-weight:700;color:#f1f5f9;margin-bottom:16px;
                  font-family:'Plus Jakarta Sans',sans-serif;">
        <i class="fas fa-lightbulb" style="color:#6c63ff;margin-right:8px;"></i>Suggestions
      </div>
      {body}
    </div>""", unsafe_allow_html=True)
