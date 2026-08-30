import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_database_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect('resume_data.db')
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Create resume_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        linkedin TEXT,
        github TEXT,
        portfolio TEXT,
        summary TEXT,
        target_role TEXT,
        target_category TEXT,
        education TEXT,
        experience TEXT,
        projects TEXT,
        skills TEXT,
        template TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create resume_skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        skill_name TEXT NOT NULL,
        skill_category TEXT NOT NULL,
        proficiency_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resume_data (id)
    )
    ''')
    
    # Create resume_analysis table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        ats_score REAL,
        keyword_match_score REAL,
        format_score REAL,
        section_score REAL,
        missing_skills TEXT,
        recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resume_data (id)
    )
    ''')
    
    # Create admin_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_email TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create admin table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_resume_data(data):
    """Save resume data to database.
    List fields are stored as JSON strings for reliable round-trip parsing.
    """
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        personal_info = data.get('personal_info', {})

        cursor.execute('''
        INSERT INTO resume_data (
            name, email, phone, linkedin, github, portfolio,
            summary, target_role, target_category, education,
            experience, projects, skills, template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            personal_info.get('full_name') or personal_info.get('name', ''),
            personal_info.get('email', ''),
            personal_info.get('phone', ''),
            personal_info.get('linkedin', ''),
            personal_info.get('github', ''),
            personal_info.get('portfolio', ''),
            data.get('summary', ''),
            data.get('target_role', ''),
            data.get('target_category', ''),
            json.dumps(data.get('education', [])),
            json.dumps(data.get('experience', [])),
            json.dumps(data.get('projects', [])),
            json.dumps(data.get('skills', [])),
            data.get('template', '')
        ))

        conn.commit()
        return cursor.lastrowid
    except Exception as exc:
        logger.error("Error saving resume data: %s", exc)
        conn.rollback()
        return None
    finally:
        conn.close()

def save_analysis_data(resume_id, analysis):
    """Save resume analysis data."""
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO resume_analysis (
            resume_id, ats_score, keyword_match_score,
            format_score, section_score, missing_skills,
            recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id,
            float(analysis.get('ats_score', 0)),
            float(analysis.get('keyword_match_score', 0)),
            float(analysis.get('format_score', 0)),
            float(analysis.get('section_score', 0)),
            analysis.get('missing_skills', ''),
            analysis.get('recommendations', '')
        ))

        conn.commit()
    except Exception as exc:
        logger.error("Error saving analysis data: %s", exc)
        conn.rollback()
    finally:
        conn.close()

def get_resume_stats():
    """Get statistics about resumes."""
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT COUNT(*) FROM resume_data')
        total_resumes = cursor.fetchone()[0]

        cursor.execute('SELECT AVG(ats_score) FROM resume_analysis')
        avg_ats_score = cursor.fetchone()[0] or 0

        cursor.execute('''
        SELECT name, target_role, created_at
        FROM resume_data
        ORDER BY created_at DESC
        LIMIT 5
        ''')
        recent_activity = cursor.fetchall()

        return {
            'total_resumes': total_resumes,
            'avg_ats_score': round(avg_ats_score, 2),
            'recent_activity': recent_activity
        }
    except Exception as exc:
        logger.error("Error getting resume stats: %s", exc)
        return None
    finally:
        conn.close()

def log_admin_action(admin_email, action):
    """Log admin login/logout actions."""
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO admin_logs (admin_email, action)
        VALUES (?, ?)
        ''', (admin_email, action))
        conn.commit()
    except Exception as exc:
        logger.error("Error logging admin action: %s", exc)
    finally:
        conn.close()

def get_admin_logs():
    """Get all admin login/logout logs."""
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT admin_email, action, timestamp
        FROM admin_logs
        ORDER BY timestamp DESC
        ''')
        return cursor.fetchall()
    except Exception as exc:
        logger.error("Error getting admin logs: %s", exc)
        return []
    finally:
        conn.close()

def get_all_resume_data():
    """Get all resume data for admin dashboard."""
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        SELECT
            r.id,
            r.name,
            r.email,
            r.phone,
            r.linkedin,
            r.github,
            r.portfolio,
            r.target_role,
            r.target_category,
            r.created_at,
            a.ats_score,
            a.keyword_match_score,
            a.format_score,
            a.section_score
        FROM resume_data r
        LEFT JOIN resume_analysis a ON r.id = a.resume_id
        ORDER BY r.created_at DESC
        ''')
        return cursor.fetchall()
    except Exception as exc:
        logger.error("Error getting resume data: %s", exc)
        return []
    finally:
        conn.close()

def _hash_password(password: str) -> str:
    """Return a bcrypt hash of the given password."""
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _check_password(password: str, hashed: str) -> bool:
    """Verify a plain password against a stored bcrypt hash."""
    import bcrypt
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def verify_admin(email: str, password: str) -> bool:
    """Verify admin credentials using bcrypt comparison."""
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT password FROM admin WHERE email = ?', (email,))
        row = cursor.fetchone()
        if not row:
            return False
        stored_hash = row[0]
        # Support both legacy plain-text (length < 60) and bcrypt hashes
        if stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$"):
            return _check_password(password, stored_hash)
        # Legacy plain-text: accept but warn
        if stored_hash == password:
            logger.warning(
                "Admin '%s' is using a plain-text password. "
                "Call add_admin() to reset with a hashed password.", email
            )
            return True
        return False
    except Exception as exc:
        logger.error("Error verifying admin: %s", exc)
        return False
    finally:
        conn.close()


def add_admin(email: str, password: str) -> bool:
    """Add (or update) an admin with a bcrypt-hashed password."""
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        hashed = _hash_password(password)
        cursor.execute(
            'INSERT OR REPLACE INTO admin (email, password) VALUES (?, ?)',
            (email, hashed)
        )
        conn.commit()
        return True
    except Exception as exc:
        logger.error("Error adding admin: %s", exc)
        return False
    finally:
        conn.close()
