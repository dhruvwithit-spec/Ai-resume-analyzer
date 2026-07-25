from __future__ import annotations


def compare_skill_sets(resume_skills: list[str], job_description_skills: list[str]) -> dict:
    """Compare resume skills against the skills found in the job description."""

    resume_set = set(resume_skills)
    job_set = set(job_description_skills)

    matched_skills = sorted(resume_set & job_set)
    missing_skills = sorted(job_set - resume_set)
    additional_resume_skills = sorted(resume_set - job_set)

    return {
        "resume_skills": sorted(resume_set),
        "job_description_skills": sorted(job_set),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_resume_skills": additional_resume_skills,
    }


def keyword_overlap_score(resume_keywords: list[str], job_keywords: list[str]) -> dict:
    """Estimate keyword alignment using simple overlap between important tokens."""

    resume_set = set(resume_keywords)
    job_set = set(job_keywords)

    if not job_set:
        return {"score": 0.0, "matched_keywords": []}

    overlap = sorted(resume_set & job_set)
    score = (len(overlap) / len(job_set)) * 100
    return {"score": round(score, 2), "matched_keywords": overlap}
