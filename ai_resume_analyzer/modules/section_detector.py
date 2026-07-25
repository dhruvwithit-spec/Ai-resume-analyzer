from __future__ import annotations

import re

from modules.preprocess import clean_text


SECTION_PATTERNS = {
    "Summary / Objective": [r"professional summary", r"summary", r"objective", r"profile"],
    "Education": [r"education", r"academic background", r"qualifications"],
    "Skills": [r"skills", r"technical skills", r"core competencies"],
    "Experience": [r"experience", r"work experience", r"professional experience", r"employment"],
    "Projects": [r"projects", r"personal projects", r"academic projects"],
    "Certifications": [r"certifications", r"licenses", r"certificates"],
}


def _find_heading(patterns: list[str], lines: list[str]) -> str:
    """Return the first line that looks like the requested heading."""

    for line in lines:
        cleaned_line = line.strip().lower()
        for pattern in patterns:
            if re.fullmatch(rf".*{pattern}.*", cleaned_line):
                return line.strip()
    return ""


def _detect_contact_info(text: str) -> dict:
    """Check whether contact information is present near the top of the resume."""

    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone_match = re.search(r"(\+?\d[\d\-\s()]{8,}\d)", text)
    linkedin_match = re.search(r"(linkedin\.com/in/[A-Za-z0-9\-_/]+)", text, flags=re.IGNORECASE)
    github_match = re.search(r"(github\.com/[A-Za-z0-9\-_/]+)", text, flags=re.IGNORECASE)

    evidence_parts = []
    if email_match:
        evidence_parts.append("email detected")
    if phone_match:
        evidence_parts.append("phone detected")
    if linkedin_match:
        evidence_parts.append("LinkedIn detected")
    if github_match:
        evidence_parts.append("GitHub detected")

    return {
        "present": bool(email_match or phone_match),
        "confidence": 1.0 if (email_match and phone_match) else 0.75 if (email_match or phone_match) else 0.0,
        "evidence": ", ".join(evidence_parts),
    }


def detect_sections(text: str) -> dict:
    """Detect the presence of important resume sections using headings and light heuristics."""

    cleaned = clean_text(text)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

    section_details = {"Contact Information": _detect_contact_info(cleaned)}

    for section_name, patterns in SECTION_PATTERNS.items():
        evidence = _find_heading(patterns, lines)
        present = bool(evidence)
        confidence = 1.0 if present else 0.0

        # Small heuristics help when the resume does not use explicit headings.
        if not present and section_name == "Education":
            if re.search(r"\b(b\.tech|bachelor|master|university|college|gpa)\b", cleaned, flags=re.IGNORECASE):
                present = True
                confidence = 0.65
                evidence = "Education keywords detected"

        if not present and section_name == "Experience":
            if re.search(r"\b(intern|engineer|analyst|developer|manager|years)\b", cleaned, flags=re.IGNORECASE):
                present = True
                confidence = 0.6
                evidence = "Experience-related keywords detected"

        if not present and section_name == "Projects":
            if re.search(r"\b(project|built|developed|implemented)\b", cleaned, flags=re.IGNORECASE):
                present = True
                confidence = 0.55
                evidence = "Project-style action words detected"

        section_details[section_name] = {
            "present": present,
            "confidence": confidence,
            "evidence": evidence,
        }

    present_count = sum(1 for details in section_details.values() if details["present"])
    total_sections = len(section_details)
    missing_sections = [
        name for name, details in section_details.items() if not details["present"]
    ]

    return {
        "section_details": section_details,
        "present_count": present_count,
        "total_sections": total_sections,
        "missing_sections": missing_sections,
    }
