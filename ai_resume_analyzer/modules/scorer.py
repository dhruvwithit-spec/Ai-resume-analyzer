from __future__ import annotations

from functools import lru_cache
from typing import Optional

from modules.matcher import keyword_overlap_score


@lru_cache(maxsize=1)
def load_similarity_model() -> Optional[object]:
    """
    Load the sentence-transformer model once.

    If loading fails, the app can still continue with a lexical fallback.
    """

    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def compute_semantic_similarity(resume_text: str, job_description: str) -> dict:
    """
    Compute similarity between the resume and job description.

    Preferred path:
        SentenceTransformer embeddings + cosine similarity

    Fallback:
        Token overlap between top keywords when the model is unavailable
    """

    model = load_similarity_model()

    if model is not None:
        try:
            from sentence_transformers import util

            embeddings = model.encode(
                [resume_text, job_description],
                convert_to_tensor=True,
                normalize_embeddings=True,
            )
            cosine_score = util.cos_sim(embeddings[0], embeddings[1]).item()
            cosine_score = max(0.0, min(1.0, cosine_score))
            return {
                "raw_score": cosine_score,
                "score": round(cosine_score * 100, 2),
                "method": "sentence_transformer",
                "method_label": "Sentence Transformers cosine similarity",
            }
        except Exception:
            pass

    from modules.preprocess import preprocess_text

    resume_keywords = preprocess_text(resume_text)["keywords"]
    job_keywords = preprocess_text(job_description)["keywords"]
    overlap_result = keyword_overlap_score(resume_keywords, job_keywords)
    fallback_score = overlap_result["score"] / 100

    return {
        "raw_score": fallback_score,
        "score": round(fallback_score * 100, 2),
        "method": "keyword_overlap",
        "method_label": "Keyword-overlap fallback",
    }


def calculate_ats_score(
    semantic_similarity: dict,
    skill_match: dict,
    sections: dict,
    resume_keywords: list[str],
    job_keywords: list[str],
) -> dict:
    """
    Calculate a transparent ATS-style score using four weighted components.

    Weighting:
        35% semantic similarity
        30% skill coverage
        20% section completeness
        15% keyword match
    """

    if skill_match["job_description_skills"]:
        skill_coverage = (
            len(skill_match["matched_skills"]) / len(skill_match["job_description_skills"])
        ) * 100
    else:
        # If the job description has no detected skills, we avoid punishing the resume too harshly.
        skill_coverage = 60.0 if skill_match["resume_skills"] else 0.0

    section_completeness = (
        sections["present_count"] / sections["total_sections"]
    ) * 100 if sections["total_sections"] else 0.0

    keyword_match = keyword_overlap_score(resume_keywords, job_keywords)["score"]
    semantic_score = semantic_similarity["score"]

    overall_score = (
        (semantic_score * 0.35)
        + (skill_coverage * 0.30)
        + (section_completeness * 0.20)
        + (keyword_match * 0.15)
    )

    overall_score = round(overall_score, 2)

    if overall_score >= 80:
        summary = "The resume aligns well with the target role and has strong ATS potential."
    elif overall_score >= 65:
        summary = "The resume has a good foundation, but some tailoring could improve its impact."
    elif overall_score >= 50:
        summary = "The resume shows partial alignment, but several improvements would help."
    else:
        summary = "The resume needs stronger tailoring to match the target role effectively."

    return {
        "overall_score": overall_score,
        "components": {
            "semantic_similarity": round(semantic_score, 2),
            "skill_coverage": round(skill_coverage, 2),
            "section_completeness": round(section_completeness, 2),
            "keyword_match": round(keyword_match, 2),
        },
        "summary": summary,
    }
