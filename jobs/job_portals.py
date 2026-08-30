"""Module for handling job portal integrations"""
import logging
import urllib.parse
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Date-posted → portal param maps ──────────────────────────────────────────
# LinkedIn  f_TPR:  r86400=24h, r604800=week, r2592000=month
_DATE_LINKEDIN = {
    "Past 24 hours": "r86400",
    "Past week":     "r604800",
    "Past month":    "r2592000",
}
# Indeed    fromage: 1=24h, 7=week, 14=2wks, 30=month
_DATE_INDEED = {
    "Past 24 hours": "1",
    "Past week":     "7",
    "Past month":    "30",
}
# Naukri    jobAge: 1, 7, 30
_DATE_NAUKRI = {
    "Past 24 hours": "1",
    "Past week":     "7",
    "Past month":    "30",
}
# Foundit / Shine use similar "jobAge" params
_DATE_FOUNDIT = _DATE_NAUKRI

# ── Job-type → portal param maps ─────────────────────────────────────────────
# LinkedIn  f_JT: F=Full-time, P=Part-time, C=Contract, T=Temporary, I=Internship
_JTYPE_LINKEDIN = {
    "Full Time":  "F",
    "Part Time":  "P",
    "Contract":   "C",
    "Remote":     "F",   # use full-time + remote location flag
}
# Indeed    jt: fulltime, parttime, contract, internship
_JTYPE_INDEED = {
    "Full Time":  "fulltime",
    "Part Time":  "parttime",
    "Contract":   "contract",
    "Remote":     "fulltime",
}


class JobPortal:
    """Handles job portal URL generation for multi-portal search."""

    def __init__(self):
        self.portals = [
            {
                "name":  "LinkedIn",
                "icon":  "fab fa-linkedin",
                "color": "#0077b5",
            },
            {
                "name":  "Indeed",
                "icon":  "fas fa-search-dollar",
                "color": "#2164f3",
            },
            {
                "name":  "Naukri",
                "icon":  "fas fa-briefcase",
                "color": "#4a90e2",
            },
            {
                "name":  "Foundit",
                "icon":  "fas fa-globe",
                "color": "#ff6b6b",
            },
            {
                "name":  "Instahyre",
                "icon":  "fas fa-user-tie",
                "color": "#00bfa5",
            },
            {
                "name":  "Freshersworld",
                "icon":  "fas fa-graduation-cap",
                "color": "#28a745",
            },
        ]

    # ── helpers ───────────────────────────────────────────────────────────────
    def format_query(self, query: str) -> str:
        return query.replace(" ", "+")

    def format_location(self, location: str) -> str:
        return location.strip().lower().replace(" ", "-")

    def format_job_title(self, title: str) -> str:
        title = title.lower()
        title = title.replace("developer", "").replace("engineer", "").strip()
        return title.replace(" ", "-").strip("-")

    def format_experience(self, experience) -> tuple:
        """Return (exp_level_str, exp_min, exp_max, exp_type_str)."""
        if not experience or experience in ("all", ""):
            return "", "0", "0", "entry"
        try:
            exp_id = experience.get("id", "all") if isinstance(experience, dict) else experience
            if exp_id in ("all", ""):
                return "", "0", "0", "entry"

            # "10+" special case
            if "+" in exp_id:
                exp_min, exp_max = exp_id.replace("+", ""), "20"
            else:
                exp_min, exp_max = exp_id.split("-")

            exp_level = {
                "0-1": "0", "1-3": "1", "3-5": "2",
                "5-7": "3", "7-10": "4", "10+": "5",
            }.get(exp_id, "0")

            exp_type = "entry" if exp_min == "0" else "experienced"
            return exp_level, exp_min, exp_max, exp_type
        except Exception as exc:
            logger.warning("Error formatting experience: %s", exc)
            return "", "0", "0", "entry"

    # ── per-portal URL builders ───────────────────────────────────────────────
    def _linkedin_url(self, query, location, exp_level, date_posted, job_type):
        params = {"keywords": query, "location": location}
        if exp_level:
            # LinkedIn f_E: 1=Internship,2=Entry,3=Associate,4=Mid-Senior,5=Director
            linkedin_exp = {"0": "2", "1": "2", "2": "3", "3": "4", "4": "4", "5": "5"}
            params["f_E"] = linkedin_exp.get(exp_level, "")
        if date_posted and date_posted != "Any time":
            params["f_TPR"] = _DATE_LINKEDIN.get(date_posted, "")
        if job_type and job_type not in ("All Types", ""):
            params["f_JT"] = _JTYPE_LINKEDIN.get(job_type, "")
        if job_type == "Remote":
            params["f_WT"] = "2"   # LinkedIn remote work type
        return "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(
            {k: v for k, v in params.items() if v}
        )

    def _indeed_url(self, query, location, exp_level, date_posted, job_type):
        params = {"q": query, "l": location}
        if exp_level:
            explvl_map = {"0": "entry_level", "1": "entry_level", "2": "mid_level",
                          "3": "senior_level", "4": "senior_level", "5": "senior_level"}
            params["explvl"] = explvl_map.get(exp_level, "")
        if date_posted and date_posted != "Any time":
            params["fromage"] = _DATE_INDEED.get(date_posted, "")
        if job_type and job_type not in ("All Types", ""):
            params["jt"] = _JTYPE_INDEED.get(job_type, "")
        if job_type == "Remote":
            params["remotejob"] = "032b3046-06a3-4876-8dfd-474eb5e7ed11"
        return "https://www.indeed.com/jobs?" + urllib.parse.urlencode(
            {k: v for k, v in params.items() if v}
        )

    def _naukri_url(self, query, location, exp_level, date_posted, job_type):
        slug = self.format_query(query)
        loc  = self.format_location(location)
        url  = f"https://www.naukri.com/{slug}-jobs" + (f"-in-{loc}" if loc else "")
        params = {}
        if exp_level:
            params["experience"] = exp_level
        if date_posted and date_posted != "Any time":
            params["jobAge"] = _DATE_NAUKRI.get(date_posted, "")
        if job_type == "Remote":
            params["wfhType"] = "1"
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v})
        return f"{url}?{qs}" if qs else url

    def _foundit_url(self, query, location, exp_min, exp_max, date_posted, job_type):
        params = {
            "query":          f'"{query}"',
            "locations":      location,
            "experienceRanges": f"{exp_min}~{exp_max}",
        }
        if date_posted and date_posted != "Any time":
            params["jobAge"] = _DATE_FOUNDIT.get(date_posted, "")
        if job_type == "Remote":
            params["workType"] = "3"
        return "https://www.foundit.in/srp/results?" + urllib.parse.urlencode(
            {k: v for k, v in params.items() if v}
        )

    def _instahyre_url(self, query, location):
        title = self.format_job_title(query)
        loc   = self.format_location(location)
        return f"https://www.instahyre.com/{title}-jobs" + (f"-in-{loc}" if loc else "")

    def _freshersworld_url(self, query, location):
        title = self.format_job_title(query)
        loc   = self.format_location(location)
        return f"https://www.freshersworld.com/jobs/jobsearch/{title}-jobs" + (f"-in-{loc}" if loc else "")

    # ── public API ────────────────────────────────────────────────────────────
    def search_jobs(
        self,
        query: str,
        location: str = "",
        experience=None,
        date_posted: str = "Any time",
        job_type: str = "All Types",
    ) -> list:
        """Build pre-filtered search URLs across all portals.

        Args:
            query:       Job title / skill keywords.
            location:    City or region.
            experience:  Dict with 'id' key (e.g. {'id': '3-5', 'text': '3-5 years'})
                         OR plain string id (e.g. '3-5').
            date_posted: One of "Any time", "Past 24 hours", "Past week", "Past month".
            job_type:    One of "All Types", "Full Time", "Part Time", "Contract", "Remote".
        """
        results = []
        exp_level, exp_min, exp_max, exp_type = self.format_experience(experience)
        fmt_location = location.strip()

        for portal in self.portals:
            try:
                name = portal["name"]
                if name == "LinkedIn":
                    url = self._linkedin_url(query, fmt_location, exp_level, date_posted, job_type)
                elif name == "Indeed":
                    url = self._indeed_url(query, fmt_location, exp_level, date_posted, job_type)
                elif name == "Naukri":
                    url = self._naukri_url(query, fmt_location, exp_level, date_posted, job_type)
                elif name == "Foundit":
                    url = self._foundit_url(query, fmt_location, exp_min, exp_max, date_posted, job_type)
                elif name == "Instahyre":
                    url = self._instahyre_url(query, fmt_location)
                elif name == "Freshersworld":
                    url = self._freshersworld_url(query, fmt_location)
                else:
                    continue

                results.append({
                    "portal": name,
                    "icon":   portal["icon"],
                    "color":  portal["color"],
                    "title":  f"Search '{query}' jobs in {location}" if location else f"Search '{query}' jobs",
                    "url":    url,
                })
            except Exception as exc:
                logger.error("Error generating URL for %s: %s", portal.get("name"), exc)

        return results
