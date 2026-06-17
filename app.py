"""
Smart Resume AI - Main Application
"""
# pyrefly: ignore [missing-import]
import streamlit as st

# Set page config at the very beginning
st.set_page_config(
    page_title="Smart Resume AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import json
import pandas as pd
import plotly.express as px
import traceback
from utils.resume_analyzer import ResumeAnalyzer
from utils.resume_builder import ResumeBuilder
from config.database import (
    get_database_connection, save_resume_data, save_analysis_data, 
    init_database, verify_admin, log_admin_action
)
from config.job_roles import JOB_ROLES
from config.courses import COURSES_BY_CATEGORY, RESUME_VIDEOS, INTERVIEW_VIDEOS, get_courses_for_role, get_category_for_role
from dashboard.dashboard import DashboardManager
import requests
from streamlit_lottie import st_lottie
import plotly.graph_objects as go
import base64
import io
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from feedback.feedback import FeedbackManager
from ui_components import (
    apply_modern_styles, hero_section, feature_card, about_section,
    page_header, render_analytics_section, render_activity_section,
    render_suggestions_section,
    groq_badge, verdict_banner, score_cards_row,
    strengths_weaknesses, section_feedback_grid, keyword_analysis,
    bullet_rewrites, ats_tips_card, course_card
)
from datetime import datetime
from jobs.job_search import render_job_search
from PIL import Image
from utils.groq_analyzer import (
    analyze_with_groq, rewrite_summary_with_groq,
    generate_cover_letter_opener, generate_interview_questions,
    is_groq_available
)

class ResumeApp:
    def __init__(self):
        """Initialize the application"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'personal_info': {
                    'full_name': '',
                    'email': '',
                    'phone': '',
                    'location': '',
                    'linkedin': '',
                    'portfolio': ''
                },
                'summary': '',
                'experiences': [],
                'education': [],
                'projects': [],
                'skills_categories': {
                    'technical': [],
                    'soft': [],
                    'languages': [],
                    'tools': []
                }
            }
        
        # Initialize navigation state
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
            
        # Initialize admin state
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False
        
        self.pages = {
            "🏠 HOME": self.render_home,
            "🔍 RESUME ANALYZER": self.render_analyzer,
            "📝 RESUME BUILDER": self.render_builder,
            "📊 DASHBOARD": self.render_dashboard,
            "🎯 JOB SEARCH": self.render_job_search,
            "💬 FEEDBACK": self.render_feedback_page,
            "ℹ️ ABOUT": self.render_about
        }
        
        # Initialize dashboard manager
        self.dashboard_manager = DashboardManager()
        
        self.analyzer = ResumeAnalyzer()
        self.builder = ResumeBuilder()
        self.job_roles = JOB_ROLES
        
        # Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'default_user'
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = None
        
        # Initialize database
        init_database()
        
        # Load external CSS
        with open('style/style.css', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
        # Load Google Fonts
        st.markdown("""
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        """, unsafe_allow_html=True)

    def load_lottie_url(self, url: str):
        """Load Lottie animation from URL"""
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    def apply_global_styles(self):
        st.markdown("""
        <style>
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #1a1a1a;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #45a049;
        }

        /* Global Styles */
        .main-header {
            background: linear-gradient(135deg, rgba(124,92,255,0.24), rgba(41,214,198,0.12));
            padding: 2rem;
            border-radius: 24px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 45px rgba(0,0,0,0.25);
            text-align: center;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: -20%;
            right: -10%;
            width: 240px;
            height: 240px;
            background: radial-gradient(circle, rgba(124,92,255,0.32) 0%, transparent 65%);
            pointer-events: none;
        }

        .main-header::after {
            content: '';
            position: absolute;
            bottom: -20%;
            left: 10%;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(41,214,198,0.24) 0%, transparent 70%);
            pointer-events: none;
        }

        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            position: relative;
            z-index: 2;
        }

        .main-header p {
            color: #c7d1e7;
            margin-top: 0.75rem;
            font-size: 1rem;
            position: relative;
            z-index: 2;
        }

        /* Template Card Styles */
        .template-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.8rem;
            padding: 1rem 0;
        }

        .template-card {
            background: rgba(16, 23, 42, 0.96);
            border-radius: 22px;
            padding: 2rem;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(12px);
            border: 1px solid rgba(124,92,255,0.12);
            transition: transform 0.35s ease, border-color 0.35s ease, box-shadow 0.35s ease;
        }

        .template-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 18px 35px rgba(124,92,255,0.16);
            border-color: rgba(41,214,198,0.25);
        }

        .template-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, transparent 0%, rgba(124,92,255,0.08) 55%);
            z-index: 1;
        }

        .template-icon {
            font-size: 3rem;
            color: #7c5cff;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
        }

        .template-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #f8fbff;
            margin-bottom: 1rem;
            position: relative;
            z-index: 2;
        }

        .template-description {
            color: #b8c2dd;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
            line-height: 1.75;
        }

        /* Feature List Styles */
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 1.5rem 0;
            position: relative;
            z-index: 2;
        }

        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            color: #d2d8ee;
            font-size: 0.96rem;
        }

        .feature-icon {
            color: #7c5cff;
            margin-right: 0.9rem;
            font-size: 1.1rem;
        }

        /* Skill Tags */
        .skill-tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .skill-tag {
            background: rgba(124,92,255,0.12);
            color: #b39dff;
            padding: 0.6rem 1.2rem;
            border-radius: 999px;
            border: 1px solid rgba(124,92,255,0.24);
            font-size: 0.9rem;
            transition: all 0.25s ease;
            cursor: pointer;
        }

        .skill-tag:hover {
            background: rgba(41,214,198,0.16);
            color: #f8fbff;
            transform: translateY(-2px);
            box-shadow: 0 8px 18px rgba(41,214,198,0.12);
        }

        /* Progress Circle */
        .progress-container {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 2rem auto;
        }

        .progress-circle {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }

        .progress-circle circle {
            fill: none;
            stroke-width: 8;
            stroke-linecap: round;
            stroke: #7c5cff;
            transform-origin: 50% 50%;
            transition: all 0.3s ease;
        }

        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            font-weight: 700;
            color: #f8fbff;
        }

        .progress-circle circle {
            fill: none;
            stroke-width: 8;
            stroke-linecap: round;
            stroke: #4CAF50;
            transform-origin: 50% 50%;
            transition: all 0.3s ease;
        }

        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            font-weight: 600;
            color: white;
        }

        /* Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-slide-in {
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .template-container {
                grid-template-columns: 1fr;
            }

            .main-header {
                padding: 1.5rem;
            }

            .main-header h1 {
                font-size: 2rem;
            }

            .template-card {
                padding: 1.5rem;
            }

            .action-button {
                padding: 0.8rem 1.6rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)

    def load_image(self, image_name):
        """Load image from assets directory"""
        import os
        # Search in project-relative paths
        search_paths = [
            os.path.join("assets", image_name),
            image_name,
        ]
        for image_path in search_paths:
            try:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                encoded = base64.b64encode(image_bytes).decode()
                return f"data:image/png;base64,{encoded}"
            except FileNotFoundError:
                continue
        print(f"Image not found: {image_name}")
        return None

    def export_to_excel(self):
        """Export resume data to Excel"""
        conn = get_database_connection()
        
        # Get resume data with analysis
        query = """
            SELECT 
                rd.name, rd.email, rd.phone, rd.linkedin, rd.github, rd.portfolio,
                rd.summary, rd.target_role, rd.target_category,
                rd.education, rd.experience, rd.projects, rd.skills,
                ra.ats_score, ra.keyword_match_score, ra.format_score, ra.section_score,
                ra.missing_skills, ra.recommendations,
                rd.created_at
            FROM resume_data rd
            LEFT JOIN resume_analysis ra ON rd.id = ra.resume_id
        """
        
        try:
            # Read data into DataFrame
            df = pd.read_sql_query(query, conn)
            
            # Create Excel writer object
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resume Data')
            
            return output.getvalue()
        except Exception as e:
            print(f"Error exporting to Excel: {str(e)}")
            return None
        finally:
            conn.close()

    def render_dashboard(self):
        """Render the dashboard page"""
        self.dashboard_manager.render_dashboard()

    def render_empty_state(self, icon, message):
        """Render an empty state with icon and message"""
        return f"""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <i class='{icon}' style='font-size: 2rem; margin-bottom: 1rem; color: #00bfa5;'></i>
                <p style='margin: 0;'>{message}</p>
            </div>
        """

    def analyze_resume(self, resume_text):
        """Analyze resume and store results"""
        analytics = self.analyzer.analyze_resume(resume_text)
        st.session_state.analytics_data = analytics
        return analytics

    def handle_resume_upload(self):
        """Handle resume upload and analysis"""
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx'])
        
        if uploaded_file is not None:
            try:
                # Extract text from resume
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)
                
                # Store resume data
                st.session_state.resume_data = {
                    'filename': uploaded_file.name,
                    'content': resume_text,
                    'upload_time': datetime.now().isoformat()
                }
                
                # Analyze resume
                analytics = self.analyze_resume(resume_text)
                
                return True
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
                return False
        return False

    def render_builder(self):
        st.title("Resume Builder 📝")
        st.write("Create your professional resume")
        
        # Template selection
        template_options = ["Modern", "Professional", "Minimal", "Creative"]
        selected_template = st.selectbox("Select Resume Template", template_options)
        st.success(f"🎨 Currently using: {selected_template} Template")

        # Personal Information
        st.subheader("Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            # Get existing values from session state
            existing_name = st.session_state.form_data['personal_info']['full_name']
            existing_email = st.session_state.form_data['personal_info']['email']
            existing_phone = st.session_state.form_data['personal_info']['phone']
            
            # Input fields with existing values
            full_name = st.text_input("Full Name", value=existing_name)
            email = st.text_input("Email", value=existing_email, key="email_input")
            phone = st.text_input("Phone", value=existing_phone)

            # Immediately update session state after email input
            if 'email_input' in st.session_state:
                st.session_state.form_data['personal_info']['email'] = st.session_state.email_input
        
        with col2:
            # Get existing values from session state
            existing_location = st.session_state.form_data['personal_info']['location']
            existing_linkedin = st.session_state.form_data['personal_info']['linkedin']
            existing_portfolio = st.session_state.form_data['personal_info']['portfolio']
            
            # Input fields with existing values
            location = st.text_input("Location", value=existing_location)
            linkedin = st.text_input("LinkedIn URL", value=existing_linkedin)
            portfolio = st.text_input("Portfolio Website", value=existing_portfolio)

        # Update personal info in session state
        st.session_state.form_data['personal_info'] = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'location': location,
            'linkedin': linkedin,
            'portfolio': portfolio
        }

        # Professional Summary
        st.subheader("Professional Summary")
        
        if is_groq_available():
            if st.button("✨ Generate Summary with Groq"):
                with st.spinner("Generating summary..."):
                    from utils.groq_analyzer import generate_summary_for_builder
                    new_summary = generate_summary_for_builder(
                        st.session_state.form_data.get('personal_info', {}),
                        st.session_state.form_data.get('experiences', []),
                        st.session_state.form_data.get('skills_categories', {})
                    )
                    if new_summary:
                        st.session_state.form_data['summary'] = new_summary
                        st.rerun()

        summary = st.text_area("Professional Summary", value=st.session_state.form_data.get('summary', ''), height=150,
                             help="Write a brief summary highlighting your key skills and experience")
        
        # Experience Section
        st.subheader("Work Experience")
        if 'experiences' not in st.session_state.form_data:
            st.session_state.form_data['experiences'] = []
            
        if st.button("Add Experience"):
            st.session_state.form_data['experiences'].append({
                'company': '',
                'position': '',
                'start_date': '',
                'end_date': '',
                'description': '',
                'responsibilities': [],
                'achievements': []
            })
        
        for idx, exp in enumerate(st.session_state.form_data['experiences']):
            with st.expander(f"Experience {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    exp['company'] = st.text_input("Company Name", key=f"company_{idx}", value=exp.get('company', ''))
                    exp['position'] = st.text_input("Position", key=f"position_{idx}", value=exp.get('position', ''))
                with col2:
                    exp['start_date'] = st.text_input("Start Date", key=f"start_date_{idx}", value=exp.get('start_date', ''))
                    exp['end_date'] = st.text_input("End Date", key=f"end_date_{idx}", value=exp.get('end_date', ''))
                
                exp['description'] = st.text_area("Role Overview", key=f"desc_{idx}", 
                                                value=exp.get('description', ''),
                                                help="Brief overview of your role and impact")
                
                # Responsibilities
                st.markdown("##### Key Responsibilities")
                
                if is_groq_available():
                    if st.button("✨ Generate Bullet Points with Groq", key=f"gen_exp_{idx}"):
                        with st.spinner("Generating bullet points..."):
                            from utils.groq_analyzer import generate_experience_bullets
                            bullets = generate_experience_bullets(
                                exp.get('position', ''),
                                exp.get('company', ''),
                                exp.get('description', '')
                            )
                            if bullets:
                                current_resp = '\n'.join(exp.get('responsibilities', []))
                                if current_resp:
                                    current_resp += '\n' + bullets
                                else:
                                    current_resp = bullets
                                exp['responsibilities'] = [r.replace('• ', '').strip() for r in current_resp.split('\n') if r.strip()]
                                st.rerun()

                resp_text = st.text_area("Enter responsibilities (one per line)", 
                                       key=f"resp_{idx}",
                                       value='\n'.join(exp.get('responsibilities', [])),
                                       height=100,
                                       help="List your main responsibilities, one per line")
                exp['responsibilities'] = [r.strip() for r in resp_text.split('\n') if r.strip()]
                
                # Achievements
                st.markdown("##### Key Achievements")
                achv_text = st.text_area("Enter achievements (one per line)", 
                                       key=f"achv_{idx}",
                                       value='\n'.join(exp.get('achievements', [])),
                                       height=100,
                                       help="List your notable achievements, one per line")
                exp['achievements'] = [a.strip() for a in achv_text.split('\n') if a.strip()]
                
                if st.button("Remove Experience", key=f"remove_exp_{idx}"):
                    st.session_state.form_data['experiences'].pop(idx)
                    st.rerun()
        
        # Projects Section
        st.subheader("Projects")
        if 'projects' not in st.session_state.form_data:
            st.session_state.form_data['projects'] = []
            
        if st.button("Add Project"):
            st.session_state.form_data['projects'].append({
                'name': '',
                'technologies': '',
                'description': '',
                'responsibilities': [],
                'achievements': [],
                'link': ''
            })
        
        for idx, proj in enumerate(st.session_state.form_data['projects']):
            with st.expander(f"Project {idx + 1}", expanded=True):
                proj['name'] = st.text_input("Project Name", key=f"proj_name_{idx}", value=proj.get('name', ''))
                proj['technologies'] = st.text_input("Technologies Used", key=f"proj_tech_{idx}", 
                                                   value=proj.get('technologies', ''),
                                                   help="List the main technologies, frameworks, and tools used")
                
                proj['description'] = st.text_area("Project Overview", key=f"proj_desc_{idx}", 
                                                 value=proj.get('description', ''),
                                                 help="Brief overview of the project and its goals")
                
                if is_groq_available():
                    if st.button("✨ Generate Description with Groq", key=f"gen_proj_{idx}"):
                        with st.spinner("Generating project details..."):
                            from utils.groq_analyzer import generate_project_description
                            details = generate_project_description(
                                proj.get('name', ''),
                                proj.get('technologies', ''),
                                proj.get('description', '')
                            )
                            if details:
                                proj['description'] = details
                                st.rerun()

                # Project Responsibilities
                st.markdown("##### Key Responsibilities")
                proj_resp_text = st.text_area("Enter responsibilities (one per line)", 
                                            key=f"proj_resp_{idx}",
                                            value='\n'.join(proj.get('responsibilities', [])),
                                            height=100,
                                            help="List your main responsibilities in the project")
                proj['responsibilities'] = [r.strip() for r in proj_resp_text.split('\n') if r.strip()]
                
                # Project Achievements
                st.markdown("##### Key Achievements")
                proj_achv_text = st.text_area("Enter achievements (one per line)", 
                                            key=f"proj_achv_{idx}",
                                            value='\n'.join(proj.get('achievements', [])),
                                            height=100,
                                            help="List the project's key achievements and your contributions")
                proj['achievements'] = [a.strip() for a in proj_achv_text.split('\n') if a.strip()]
                
                proj['link'] = st.text_input("Project Link (optional)", key=f"proj_link_{idx}", 
                                           value=proj.get('link', ''),
                                           help="Link to the project repository, demo, or documentation")
                
                if st.button("Remove Project", key=f"remove_proj_{idx}"):
                    st.session_state.form_data['projects'].pop(idx)
                    st.rerun()
        
        # Education Section
        st.subheader("Education")
        if 'education' not in st.session_state.form_data:
            st.session_state.form_data['education'] = []
            
        if st.button("Add Education"):
            st.session_state.form_data['education'].append({
                'school': '',
                'degree': '',
                'field': '',
                'graduation_date': '',
                'gpa': '',
                'achievements': []
            })
        
        for idx, edu in enumerate(st.session_state.form_data['education']):
            with st.expander(f"Education {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    edu['school'] = st.text_input("School/University", key=f"school_{idx}", value=edu.get('school', ''))
                    edu['degree'] = st.text_input("Degree", key=f"degree_{idx}", value=edu.get('degree', ''))
                with col2:
                    edu['field'] = st.text_input("Field of Study", key=f"field_{idx}", value=edu.get('field', ''))
                    edu['graduation_date'] = st.text_input("Graduation Date", key=f"grad_date_{idx}", 
                                                         value=edu.get('graduation_date', ''))
                
                edu['gpa'] = st.text_input("GPA (optional)", key=f"gpa_{idx}", value=edu.get('gpa', ''))
                
                # Educational Achievements
                st.markdown("##### Achievements & Activities")
                edu_achv_text = st.text_area("Enter achievements (one per line)", 
                                           key=f"edu_achv_{idx}",
                                           value='\n'.join(edu.get('achievements', [])),
                                           height=100,
                                           help="List academic achievements, relevant coursework, or activities")
                edu['achievements'] = [a.strip() for a in edu_achv_text.split('\n') if a.strip()]
                
                if st.button("Remove Education", key=f"remove_edu_{idx}"):
                    st.session_state.form_data['education'].pop(idx)
                    st.rerun()
        
        # Skills Section
        st.subheader("Skills")
        if 'skills_categories' not in st.session_state.form_data:
            st.session_state.form_data['skills_categories'] = {
                'technical': [],
                'soft': [],
                'languages': [],
                'tools': []
            }
        
        col1, col2 = st.columns(2)
        with col1:
            tech_skills = st.text_area("Technical Skills (one per line)", 
                                     value='\n'.join(st.session_state.form_data['skills_categories']['technical']),
                                     height=150,
                                     help="Programming languages, frameworks, databases, etc.")
            st.session_state.form_data['skills_categories']['technical'] = [s.strip() for s in tech_skills.split('\n') if s.strip()]
            
            soft_skills = st.text_area("Soft Skills (one per line)", 
                                     value='\n'.join(st.session_state.form_data['skills_categories']['soft']),
                                     height=150,
                                     help="Leadership, communication, problem-solving, etc.")
            st.session_state.form_data['skills_categories']['soft'] = [s.strip() for s in soft_skills.split('\n') if s.strip()]
        
        with col2:
            languages = st.text_area("Languages (one per line)", 
                                   value='\n'.join(st.session_state.form_data['skills_categories']['languages']),
                                   height=150,
                                   help="Programming or human languages with proficiency level")
            st.session_state.form_data['skills_categories']['languages'] = [l.strip() for l in languages.split('\n') if l.strip()]
            
            tools = st.text_area("Tools & Technologies (one per line)", 
                               value='\n'.join(st.session_state.form_data['skills_categories']['tools']),
                               height=150,
                               help="Development tools, software, platforms, etc.")
            st.session_state.form_data['skills_categories']['tools'] = [t.strip() for t in tools.split('\n') if t.strip()]
        
        # Update form data in session state
        st.session_state.form_data.update({
            'summary': summary
        })
        
        # Generate Resume button
        col_gen1, col_gen2 = st.columns(2)
        
        with col_gen2:
            if is_groq_available():
                if st.button("✉️ Generate Full Cover Letter with Groq"):
                    with st.spinner("Generating Cover Letter..."):
                        from utils.groq_analyzer import generate_full_cover_letter
                        cl = generate_full_cover_letter(
                            st.session_state.form_data.get('personal_info', {}),
                            st.session_state.form_data.get('experiences', []),
                            st.session_state.form_data.get('skills_categories', {})
                        )
                        if cl:
                            st.session_state.generated_cover_letter = cl

        if st.session_state.get('generated_cover_letter'):
            st.success("Cover Letter Generated!")
            st.download_button(
                label="Download Cover Letter 📥",
                data=st.session_state.generated_cover_letter,
                file_name="Cover_Letter.txt",
                mime="text/plain"
            )

        with col_gen1:
            if st.button("Generate Resume 📄", type="primary"):
                print("Validating form data...")
                print(f"Session state form data: {st.session_state.form_data}")
                print(f"Email input value: {st.session_state.get('email_input', '')}")
                
                # Get the current values from form
                current_name = st.session_state.form_data['personal_info']['full_name'].strip()
                current_email = st.session_state.email_input if 'email_input' in st.session_state else ''
                
                print(f"Current name: {current_name}")
                print(f"Current email: {current_email}")
                
                # Validate required fields
                if not current_name:
                    st.error("⚠️ Please enter your full name.")
                    return
                
                if not current_email:
                    st.error("⚠️ Please enter your email address.")
                    return
                    
                # Update email in form data one final time
                st.session_state.form_data['personal_info']['email'] = current_email
                
                try:
                    print("Preparing resume data...")
                    # Prepare resume data with current form values
                    resume_data = {
                        "personal_info": st.session_state.form_data['personal_info'],
                        "summary": st.session_state.form_data.get('summary', '').strip(),
                        "experience": st.session_state.form_data.get('experiences', []),
                        "education": st.session_state.form_data.get('education', []),
                        "projects": st.session_state.form_data.get('projects', []),
                        "skills": st.session_state.form_data.get('skills_categories', {
                            'technical': [],
                            'soft': [],
                            'languages': [],
                            'tools': []
                        }),
                        "template": selected_template
                    }
                    
                    print(f"Resume data prepared: {resume_data}")
                    
                    try:
                        # Generate resume
                        resume_buffer = self.builder.generate_resume(resume_data)
                        if resume_buffer:
                            try:
                                # Save resume data to database
                                save_resume_data(resume_data)
                                
                                # Offer the resume for download
                                st.success("✅ Resume generated successfully!")
                                st.download_button(
                                    label="Download Resume 📥",
                                    data=resume_buffer,
                                    file_name=f"{current_name.replace(' ', '_')}_resume.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                            except Exception as db_error:
                                print(f"Warning: Failed to save to database: {str(db_error)}")
                                # Still allow download even if database save fails
                                st.warning("⚠️ Resume generated but couldn't be saved to database")
                                st.download_button(
                                    label="Download Resume 📥",
                                    data=resume_buffer,
                                    file_name=f"{current_name.replace(' ', '_')}_resume.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                        else:
                            st.error("❌ Failed to generate resume. Please try again.")
                            print("Resume buffer was None")
                    except Exception as gen_error:
                        print(f"Error during resume generation: {str(gen_error)}")
                        print(f"Full traceback: {traceback.format_exc()}")
                        st.error(f"❌ Error generating resume: {str(gen_error)}")
                            
                except Exception as e:
                    print(f"Error preparing resume data: {str(e)}")
                    print(f"Full traceback: {traceback.format_exc()}")
                    st.error(f"❌ Error preparing resume data: {str(e)}")
    
    def render_about(self):
        """Render the about page"""
        # Apply modern styles
        from ui_components import apply_modern_styles
        import base64
        import os
        
        # Function to load image as base64
        def get_image_as_base64(file_path):
            try:
                with open(file_path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode()
                    return f"data:image/jpeg;base64,{encoded}"
            except:
                return None
        
        # Get image path and convert to base64
        image_path = os.path.join(os.path.dirname(__file__), "assets", "124852522.jpeg")
        image_base64 = get_image_as_base64(image_path)
        
        apply_modern_styles()
        
        # Add Font Awesome icons and custom CSS
        st.markdown("""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                .profile-section, .vision-section, .feature-card {
                    text-align: center;
                    padding: 2rem;
                    background: rgba(45, 45, 45, 0.9);
                    border-radius: 20px;
                    margin: 2rem auto;
                    max-width: 800px;
                }
                
                .profile-image {
                    width: 200px;
                    height: 200px;
                    border-radius: 50%;
                    margin: 0 auto 1.5rem;
                    display: block;
                    object-fit: cover;
                    border: 4px solid #4CAF50;
                }
                
                .profile-name {
                    font-size: 2.5rem;
                    color: white;
                    margin-bottom: 0.5rem;
                }
                
                .profile-title {
                    font-size: 1.2rem;
                    color: #4CAF50;
                    margin-bottom: 1.5rem;
                }
                
                .social-links {
                    display: flex;
                    justify-content: center;
                    gap: 1.5rem;
                    margin: 2rem 0;
                }
                
                .social-link {
                    font-size: 2rem;
                    color: #4CAF50;
                    transition: all 0.3s ease;
                    padding: 0.5rem;
                    border-radius: 50%;
                    background: rgba(76, 175, 80, 0.1);
                    width: 60px;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-decoration: none;
                }
                
                .social-link:hover {
                    transform: translateY(-5px);
                    background: #4CAF50;
                    color: white;
                    box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
                }
                
                .bio-text {
                    color: #ddd;
                    line-height: 1.8;
                    font-size: 1.1rem;
                    margin-top: 2rem;
                    text-align: left;
                }

                .vision-text {
                    color: #ddd;
                    line-height: 1.8;
                    font-size: 1.1rem;
                    font-style: italic;
                    margin: 1.5rem 0;
                    text-align: left;
                }

                .vision-icon {
                    font-size: 2.5rem;
                    color: #4CAF50;
                    margin-bottom: 1rem;
                }

                .vision-title {
                    font-size: 2rem;
                    color: white;
                    margin-bottom: 1rem;
                }

                .features-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 2rem;
                    margin: 2rem auto;
                    max-width: 1200px;
                }

                .feature-card {
                    padding: 2rem;
                    margin: 0;
                }

                .feature-icon {
                    font-size: 2.5rem;
                    color: #4CAF50;
                    margin-bottom: 1rem;
                }

                .feature-title {
                    font-size: 1.5rem;
                    color: white;
                    margin: 1rem 0;
                }

                .feature-description {
                    color: #ddd;
                    line-height: 1.6;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Hero Section
        st.markdown("""
            <div class="hero-section">
                <h1 class="hero-title">About Smart Resume AI</h1>
                <p class="hero-subtitle">A powerful AI-driven platform for optimizing your resume</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Profile Section
        st.markdown(f"""
            <div class="profile-section">
                <img src="{image_base64 if image_base64 else 'https://github.com/tabarakmukhtar.png'}" 
                     alt="Tabarak Mukhtar" 
                     class="profile-image"
                     onerror="this.onerror=null; this.src='https://github.com/tabarakmukhtar.png';">
                <h2 class="profile-name">Tabarak Mukhtar </h2>
                <p class="profile-title">Full Stack Developer & DevOps Enthusiast</p>
                <div class="social-links">
                    <a href="https://github.com/tabarakmukhtar" class="social-link" target="_blank">
                        <i class="fab fa-github"></i>
                    </a>
                    <a href="https://www.linkedin.com/in/tabarakmukhtar/" class="social-link" target="_blank">
                        <i class="fab fa-linkedin"></i>
                    </a>
                    <a href="mailto:tabarakmukhtar159@gmail.com" class="social-link" target="_blank">
                        <i class="fas fa-envelope"></i>
                    </a>
                </div>
                <p class="bio-text">
                    Hello! I'm a passionate Software Engineer with expertise Full stack Development & DevOps. 
                    I created Smart Resume AI to revolutionize how job seekers approach their career journey. 
                    With my background in both software development and AI, I've designed this platform to 
                    provide intelligent, data-driven insights for resume optimization.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Vision Section
        st.markdown("""
            <div class="vision-section">
                <i class="fas fa-lightbulb vision-icon"></i>
                <h2 class="vision-title">Our Vision</h2>
                <p class="vision-text">
                    "Smart Resume AI represents my vision of democratizing career advancement through technology. 
                    By combining cutting-edge AI with intuitive design, this platform empowers job seekers at 
                    every career stage to showcase their true potential and stand out in today's competitive job market."
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Features Section
        st.markdown("""
            <div class="features-grid">
                <div class="feature-card">
                    <i class="fas fa-robot feature-icon"></i>
                    <h3 class="feature-title">AI-Powered Analysis</h3>
                    <p class="feature-description">
                        Advanced AI algorithms provide detailed insights and suggestions to optimize your resume for maximum impact.
                    </p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-chart-line feature-icon"></i>
                    <h3 class="feature-title">Data-Driven Insights</h3>
                    <p class="feature-description">
                        Make informed decisions with our analytics-based recommendations and industry insights.
                    </p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-shield-alt feature-icon"></i>
                    <h3 class="feature-title">Privacy First</h3>
                    <p class="feature-description">
                        Your data security is our priority. We ensure your information is always protected and private.
                    </p>
                </div>
            </div>
            <div style="text-align: center; margin: 3rem 0;">
                <a href="?page=analyzer" class="cta-button">
                    Start Your Journey
                    <i class="fas fa-arrow-right" style="margin-left: 10px;"></i>
                </a>
            </div>
        """, unsafe_allow_html=True)
    
    def build_groq_only_analysis(self, resume_text, selected_role, selected_category, role_info, groq_result):
        """Build analysis structure from Groq result and basic extraction."""
        # Extract basic sections (no scoring)
        personal_info = self.analyzer.extract_personal_info(resume_text)
        education = self.analyzer.extract_education(resume_text)
        experience = self.analyzer.extract_experience(resume_text)
        projects = self.analyzer.extract_projects(resume_text)
        skills = self.analyzer.extract_skills(resume_text)
        summary = self.analyzer.extract_summary(resume_text)
        
        # Use Groq's scores and feedback as the main analysis
        return {
            **personal_info,  # name, email, phone, linkedin, github, portfolio
            'ats_score': groq_result.get('ai_overall_score', 0),
            'document_type': 'resume',
            'keyword_match': {
                'score': groq_result.get('keyword_match_percent', 0),
                'found_skills': groq_result.get('found_keywords', []),
                'missing_skills': groq_result.get('missing_keywords', [])
            },
            'section_score': 85,  # Groq handles this; we use a placeholder
            'format_score': 80,   # Groq handles formatting feedback
            'education': education,
            'experience': experience,
            'projects': projects,
            'skills': skills,
            'summary': summary,
            'suggestions': groq_result.get('ats_tips', []) or ['Groq analysis complete'],
            'contact_suggestions': [],
            'summary_suggestions': [],
            'skills_suggestions': [],
            'experience_suggestions': [],
            'education_suggestions': [],
            'format_suggestions': groq_result.get('recommended_additions', []),
            'groq_result': groq_result  # Keep full Groq response for UI
        }

    def render_analyzer(self):
        """Render the resume analyzer page"""
        apply_modern_styles()
        
        # Page Header
        page_header(
            "Resume Analyzer",
            "Get instant AI-powered feedback to optimize your resume"
        )

        # ── Groq status badge ──────────────────────────────────────────────
        groq_on = is_groq_available()
        groq_badge(groq_on)
        
        # ── REQUIRE GROQ FOR ANALYSIS ──────────────────────────────────────
        if not groq_on:
            st.error("🔑 AI Analysis Requires Groq API Key")
            st.warning("""
            To analyze resumes with AI, you need to:
            1. Get a free API key from [Groq Console](https://console.groq.com)
            2. Create a `.env` file in the project root with:
               ```
               GROQ_API_KEY=your_api_key_here
               ```
            3. Restart the app
            
            Groq provides fast, high-quality AI analysis powered by their LPU inference engine.
            """)
            return
        
        # Job Role Selection
        categories = list(self.job_roles.keys())
        selected_category = st.selectbox("Job Category", categories)
        
        roles = list(self.job_roles[selected_category].keys())
        selected_role = st.selectbox("Specific Role", roles)
        
        role_info = self.job_roles[selected_category][selected_role]
        
        # Display role information
        skills_html = " ".join(
            f'<span style="background:rgba(124,92,255,.12);color:#b39dff;border:1px solid rgba(124,92,255,.25);'
            f'border-radius:50px;padding:3px 12px;font-size:.78rem;font-weight:500;margin:3px;'
            f'display:inline-block;">{s}</span>'
            for s in role_info['required_skills']
        )
        st.markdown(f"""
        <div style="background:#161f38;border:1px solid rgba(255,255,255,.08);
                    border-radius:18px;padding:22px;margin:12px 0;">
          <div style="font-weight:700;color:#f8fbff;font-family:'Plus Jakarta Sans',sans-serif;
                      font-size:1rem;margin-bottom:8px;">{selected_role}</div>
          <p style="color:#98a8c6;font-size:.88rem;margin:0 0 14px;line-height:1.6;">
            {role_info['description']}
          </p>
          <div style="font-size:.75rem;color:#7b87a1;text-transform:uppercase;
                      letter-spacing:.5px;margin-bottom:8px;">Required Skills</div>
          <div style="line-height:2.2;">{skills_html}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # File Upload
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx'])
        
        st.markdown(
            self.render_empty_state(
            "fas fa-cloud-upload-alt",
            "Upload your resume for Groq AI analysis"
            ),
            unsafe_allow_html=True
        )
        if uploaded_file:
            with st.spinner("🤖 Groq is analyzing your resume..."):
                # ── Extract text ──────────────────────────────────────────
                text = ""
                try:
                    if uploaded_file.type == "application/pdf":
                        text = self.analyzer.extract_text_from_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        text = self.analyzer.extract_text_from_docx(uploaded_file)
                    else:
                        text = uploaded_file.getvalue().decode()
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    return

                if not text or len(text.strip()) < 50:
                    st.error("Resume text is too short or empty. Please upload a valid resume.")
                    return

                # ── Run Groq AI analysis (ONLY) ────────────────────────────
                groq = analyze_with_groq(text, selected_role, selected_category, role_info.get('required_skills', []))
                
                if not groq:
                    st.error("""
                    ⚠️ Groq analysis failed. Please check:
                    - Your API key is valid (in `.env` file as `GROQ_API_KEY`)
                    - Your Groq account has sufficient credits
                    - Your internet connection is working
                    - Try again in a few moments
                    """)
                    return

                # ── Build analysis from Groq result ────────────────────────
                analysis = self.build_groq_only_analysis(
                    text, selected_role, selected_category, role_info, groq
                )

                # ── Save to DB ─────────────────────────────────────────────
                resume_data = {
                    'personal_info': {
                        'name': analysis.get('name', ''), 'email': analysis.get('email', ''),
                        'phone': analysis.get('phone', ''), 'linkedin': analysis.get('linkedin', ''),
                        'github': analysis.get('github', ''), 'portfolio': analysis.get('portfolio', '')
                    },
                    'summary': analysis.get('summary', ''), 'target_role': selected_role,
                    'target_category': selected_category, 'education': analysis.get('education', []),
                    'experience': analysis.get('experience', []), 'projects': analysis.get('projects', []),
                    'skills': analysis.get('skills', []), 'template': ''
                }
                try:
                    resume_id = save_resume_data(resume_data)
                    save_analysis_data(resume_id, {
                        'resume_id': resume_id, 
                        'ats_score': analysis['ats_score'],
                        'keyword_match_score': analysis['keyword_match']['score'],
                        'format_score': 85,
                        'section_score': 85,
                        'missing_skills': ','.join(analysis['keyword_match']['missing_skills']),
                        'recommendations': ','.join(analysis['suggestions'][:5])  # Save top 5
                    })
                except Exception as e:
                    st.warning(f"Note: Could not save to database ({str(e)}), but analysis is complete.")

                # ═══════════════════════════════════════════════════════════
                # RESULTS UI — All powered by Groq AI
                # ═══════════════════════════════════════════════════════════

                # 1. AI Verdict Banner (Groq)
                verdict_banner(groq)
                st.markdown("<br>", unsafe_allow_html=True)

                # 2. Score Cards (Groq scores)
                ats   = groq.get('ai_overall_score', 0)
                kw    = int(groq.get('keyword_match_percent', 0))
                fmt   = 85
                sec   = 85
                score_cards_row(ats, kw, fmt, sec)
                st.markdown("<br>", unsafe_allow_html=True)

                # 3. Strengths & Weaknesses (Groq)
                if groq.get("strengths") or groq.get("weaknesses"):
                    strengths_weaknesses(
                        groq.get("strengths", []),
                        groq.get("weaknesses", [])
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                # 4. Section-by-Section Feedback (Groq)
                if groq.get("section_feedback"):
                    st.markdown("### 📋 Section-by-Section Feedback")
                    section_feedback_grid(groq["section_feedback"])
                    st.markdown("<br>", unsafe_allow_html=True)

                # 5. Keyword Gap Analysis (Groq)
                st.markdown("### 🎯 Keyword Analysis")
                found_kws = groq.get("found_keywords", [])
                miss_kws  = groq.get("missing_keywords", [])
                keyword_analysis(found_kws, miss_kws)
                st.markdown("<br>", unsafe_allow_html=True)

                # 6. Bullet Rewrites (Groq)
                if groq.get("bullet_rewrites"):
                    st.markdown("### ✍️ AI Bullet Point Rewrites")
                    bullet_rewrites(groq["bullet_rewrites"])
                    st.markdown("<br>", unsafe_allow_html=True)

                # 7. ATS Tips (Groq)
                if groq.get("ats_tips"):
                    ats_tips_card(groq["ats_tips"])

                # ── 8. Summary Rewrite (Groq) ────────────────────────────
                if analysis.get('summary'):
                    with st.expander("✨ Get AI-Rewritten Professional Summary"):
                        if st.button("🔄 Rewrite with Groq", key="rewrite_summary_btn"):
                            with st.spinner("Groq is rewriting your summary..."):
                                new_summary = rewrite_summary_with_groq(
                                    analysis['summary'], selected_role,
                                    role_info.get('required_skills', [])
                                )
                            if new_summary:
                                st.markdown("**Original:**")
                                st.info(analysis['summary'])
                                st.markdown("**✨ Groq Rewrite:**")
                                st.success(new_summary)
                                st.caption("Copy and paste this into your resume for better ATS performance.")
                            else:
                                st.warning("Could not generate rewrite. Try again.")

                # ── 9. Cover Letter Opener (Groq) ───────────────────────
                with st.expander("📨 Generate Cover Letter Opening (Groq)"):
                    if st.button("Generate Cover Letter Opener", key="cover_letter_btn"):
                        with st.spinner("Groq is writing your cover letter opener..."):
                            opener = generate_cover_letter_opener(text, selected_role, selected_category)
                        if opener:
                            st.success(opener)
                            st.caption("Use this as the opening paragraph of your cover letter.")
                        else:
                            st.warning("Could not generate opener. Try again.")

                # ── 10. Interview Questions (Groq) ───────────────────────
                with st.expander("🤖 Generate Interview Questions (Groq)"):
                    if st.button("Generate Interview Questions", key="interview_questions_btn"):
                        with st.spinner("Groq is generating tailored interview questions..."):
                            questions = generate_interview_questions(text, selected_role, selected_category)
                        if questions:
                            st.success("Here are some questions you should prepare for:")
                            st.markdown(questions)
                        else:
                            st.warning("Could not generate questions. Try again.")



        # Close the page container
        st.markdown('</div>', unsafe_allow_html=True)

    def render_job_search(self):
        """Render the job search page"""
        render_job_search()

    def render_feedback_page(self):
        """Render the feedback page"""
        st.markdown("""
            <style>
            .feedback-header {
                text-align: center;
                padding: 20px;
                background: linear-gradient(90deg, rgba(76, 175, 80, 0.1), rgba(33, 150, 243, 0.1));
                border-radius: 10px;
                margin-bottom: 30px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="feedback-header">
                <h1>📣 Your Voice Matters!</h1>
                <p>Help us improve Smart Resume AI with your valuable feedback</p>
            </div>
        """, unsafe_allow_html=True)

        # Initialize feedback manager
        feedback_manager = FeedbackManager()
        
        # Create tabs for form and statistics
        form_tab, stats_tab = st.tabs(["Share Feedback", "Feedback Overview"])
        
        with form_tab:
            feedback_manager.render_feedback_form()
            
        with stats_tab:
            feedback_manager.render_feedback_stats()

    def render_home(self):
        apply_modern_styles()
        
        # Hero Section
        hero_section(
            "Smart Resume AI",
            "Transform your career with AI-powered resume analysis and building. Get personalized insights and create professional resumes that stand out."
        )
        
        # Features Section
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        
        feature_card(
            "fas fa-robot",
            "AI-Powered Analysis",
            "Get instant feedback on your resume with advanced AI analysis that identifies strengths and areas for improvement."
        )
        
        feature_card(
            "fas fa-magic",
            "Smart Resume Builder",
            "Create professional resumes with our intelligent builder that suggests optimal content and formatting."
        )
        
        feature_card(
            "fas fa-chart-line",
            "Career Insights",
            "Access detailed analytics and personalized recommendations to enhance your career prospects."
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Call-to-Action with Streamlit navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Get Started", key="get_started_btn", 
                        help="Click to start analyzing your resume",
                        type="primary",
                        use_container_width=True):
                cleaned_name = "🔍 RESUME ANALYZER".lower().replace(" ", "_").replace("🔍", "").strip()
                st.session_state.page = cleaned_name
                st.rerun()

    def main(self):
        """Main application entry point"""
        self.apply_global_styles()

        # ── Floating sidebar toggle button ─────────────────────────────────
        st.markdown("""
        <style>
        /* Hide the default Streamlit sidebar collapse arrow */
        [data-testid="collapsedControl"] { display: none !important; }
        button[kind="header"]            { display: none !important; }

        /* Floating menu button */
        #sidebar-toggle-btn {
          position: fixed;
          top: 16px;
          left: 16px;
          z-index: 99999;
          width: 44px;
          height: 44px;
          border-radius: 12px;
          background: linear-gradient(135deg, #6c63ff, #5046e5);
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 16px rgba(108,99,255,0.45);
          transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
        }
        #sidebar-toggle-btn:hover {
          transform: scale(1.08);
          box-shadow: 0 8px 24px rgba(108,99,255,0.65);
        }
        #sidebar-toggle-btn svg {
          width: 20px; height: 20px;
          stroke: #fff; fill: none;
          stroke-width: 2; stroke-linecap: round;
          transition: all 0.25s ease;
        }
        /* Tooltip */
        #sidebar-toggle-btn::after {
          content: "Menu";
          position: absolute;
          left: 54px;
          top: 50%;
          transform: translateY(-50%);
          background: #1a2035;
          color: #f1f5f9;
          font-size: 12px;
          font-weight: 600;
          padding: 4px 10px;
          border-radius: 6px;
          white-space: nowrap;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.2s ease;
          font-family: 'Inter', sans-serif;
          border: 1px solid rgba(255,255,255,0.1);
        }
        #sidebar-toggle-btn:hover::after { opacity: 1; }
        </style>

        <button id="sidebar-toggle-btn" title="Toggle menu" onclick="toggleSidebar()">
          <svg viewBox="0 0 24 24">
            <line x1="3" y1="6"  x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>

        <script>
        function toggleSidebar() {
          // Find and click Streamlit's internal sidebar toggle
          const sidebarBtn = window.parent.document.querySelector(
            '[data-testid="collapsedControl"]'
          );
          if (sidebarBtn) {
            sidebarBtn.click();
            return;
          }
          // Fallback: toggle the sidebar section directly
          const sidebar = window.parent.document.querySelector(
            '[data-testid="stSidebar"]'
          );
          if (sidebar) {
            const isVisible = sidebar.style.display !== "none" &&
                              sidebar.offsetWidth > 0;
            sidebar.style.transition = "transform 0.3s ease";
            sidebar.style.transform  = isVisible
              ? "translateX(-110%)"
              : "translateX(0)";
          }
        }
        </script>
        """, unsafe_allow_html=True)
        
        # Admin login/logout in sidebar
        with st.sidebar:
            st_lottie(self.load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_xyadoh9h.json"), height=200, key="sidebar_animation")
            st.title("Smart Resume AI")
            st.markdown("---")
            
            # Navigation buttons
            for page_name in self.pages.keys():
                if st.button(page_name, use_container_width=True):
                    cleaned_name = page_name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").strip()
                    st.session_state.page = cleaned_name
                    st.rerun()

            # Add some space before admin login
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Admin Login/Logout section at bottom
            if st.session_state.get('is_admin', False):
                st.success(f"Logged in as: {st.session_state.get('current_admin_email')}")
                if st.button("Logout", key="logout_button"):
                    try:
                        log_admin_action(st.session_state.get('current_admin_email'), "logout")
                        st.session_state.is_admin = False
                        st.session_state.current_admin_email = None
                        st.success("Logged out successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during logout: {str(e)}")
            else:
                with st.expander("👤 Admin Login"):
                    admin_email_input = st.text_input("Email", key="admin_email_input")
                    admin_password = st.text_input("Password", type="password", key="admin_password_input")
                    if st.button("Login", key="login_button"):
                            try:
                                if verify_admin(admin_email_input, admin_password):
                                    st.session_state.is_admin = True
                                    st.session_state.current_admin_email = admin_email_input
                                    log_admin_action(admin_email_input, "login")
                                    st.success("Logged in successfully!")
                                    st.rerun()
                                else:
                                    st.error("Invalid credentials")
                            except Exception as e:
                                st.error(f"Error during login: {str(e)}")
        
        # Force home page on first load
        if 'initial_load' not in st.session_state:
            st.session_state.initial_load = True
            st.session_state.page = 'home'
            st.rerun()
        
        # Get current page and render it
        current_page = st.session_state.get('page', 'home')
        
        # Create a mapping of cleaned page names to original names
        page_mapping = {name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").strip(): name 
                       for name in self.pages.keys()}
        
        # Render the appropriate page
        if current_page in page_mapping:
            self.pages[page_mapping[current_page]]()
        else:
            # Default to home page if invalid page
            self.render_home()
    
if __name__ == "__main__":
    app = ResumeApp()
    app.main()
