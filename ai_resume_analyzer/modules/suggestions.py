from __future__ import annotations

import re


def count_measurable_achievements(text: str) -> int:
    """Count signs of measurable impact such as percentages, revenue, users, or time saved."""

    patterns = [
        r"\b\d+%\b",
        r"\b\d+\+?\s?(users|clients|customers|projects|features|reports)\b",
        r"\$\s?\d+",
        r"\b\d+\+?\s?(hours|days|weeks|months|years)\b",
        r"\b\d+x\b",
    ]
    total = 0
    for pattern in patterns:
        total += len(re.findall(pattern, text, flags=re.IGNORECASE))
    return total


def generate_suggestions(
    resume_text: str,
    job_description: str,
    skill_match: dict,
    sections: dict,
    similarity: dict,
    ats_result: dict,
) -> list[dict]:
    """Generate practical, easy-to-understand suggestions based on the analysis results."""

    suggestions: list[dict] = []

    if skill_match["missing_skills"]:
        top_missing = ", ".join(skill_match["missing_skills"][:6])
        suggestions.append(
            {
                "priority": "High Priority",
                "title": "Add missing role keywords and skills",
                "details": (
                    f"The job description mentions skills that are not clearly visible in the resume, "
                    f"including {top_missing}. Add only the skills you genuinely have, and place them "
                    f"in your summary, skills section, project bullets, or experience bullets."
                ),
            }
        )

    if not sections["section_details"]["Summary / Objective"]["present"] or similarity["score"] < 60:
        suggestions.append(
            {
                "priority": "High Priority",
                "title": "Strengthen the summary for role alignment",
                "details": (
                    "Add a short professional summary near the top of the resume that mirrors the job "
                    "title, highlights your most relevant experience, and includes core keywords from "
                    "the target role."
                ),
            }
        )

    if not sections["section_details"]["Skills"]["present"]:
        suggestions.append(
            {
                "priority": "Medium Priority",
                "title": "Add a dedicated skills section",
                "details": (
                    "A clear skills section helps recruiters and ATS tools quickly identify your tools, "
                    "languages, frameworks, and soft skills. Group the skills into logical buckets if possible."
                ),
            }
        )

    if not sections["section_details"]["Projects"]["present"]:
        suggestions.append(
            {
                "priority": "Medium Priority",
                "title": "Show projects that prove relevant skills",
                "details": (
                    "Add 1 to 3 focused projects that match the role. Mention the tools used, the problem solved, "
                    "and the outcome. Projects are especially valuable for students and early-career candidates."
                ),
            }
        )

    if not sections["section_details"]["Certifications"]["present"]:
        suggestions.append(
            {
                "priority": "Low Priority",
                "title": "Add certifications if they support the role",
                "details": (
                    "Relevant certifications can strengthen credibility, especially for cloud, analytics, "
                    "or tool-heavy roles. Only include certifications that are completed or in progress."
                ),
            }
        )

    measurable_achievement_count = count_measurable_achievements(resume_text)
    if measurable_achievement_count < 3:
        suggestions.append(
            {
                "priority": "High Priority",
                "title": "Add measurable achievements to experience bullets",
                "details": (
                    "Your resume will feel stronger if more bullets include numbers such as percentages, time saved, "
                    "revenue impact, user growth, project count, or performance improvements."
                ),
            }
        )

    if ats_result["components"]["keyword_match"] < 55:
        suggestions.append(
            {
                "priority": "Medium Priority",
                "title": "Match the language used in the job description",
                "details": (
                    "Rewrite some bullets using the exact wording from the job description where it is truthful. "
                    "This improves keyword match and usually makes the resume feel better tailored."
                ),
            }
        )

    if not sections["section_details"]["Contact Information"]["present"]:
        suggestions.append(
            {
                "priority": "High Priority",
                "title": "Make contact information clearly visible",
                "details": (
                    "Ensure your email and phone number appear at the top of the resume. A LinkedIn URL and GitHub "
                    "link can also help for technical roles."
                ),
            }
        )

    if ats_result["overall_score"] >= 80 and not suggestions:
        suggestions.append(
            {
                "priority": "Low Priority",
                "title": "Keep tailoring for each application",
                "details": (
                    "The resume already aligns well. For best results, keep adjusting your summary, top skills, "
                    "and most recent bullets to match each role you apply for."
                ),
            }
        )

    return suggestions
