from __future__ import annotations

import csv
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from modules.preprocess import clean_text


SKILLS_PATH = Path(__file__).resolve().parents[1] / "data" / "skills.csv"


@lru_cache(maxsize=1)
def load_skills_dataset() -> list[dict]:
    """Load the local skill dataset from CSV."""

    skill_rows: list[dict] = []

    with SKILLS_PATH.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            aliases = [item.strip().lower() for item in row["aliases"].split("|") if item.strip()]
            canonical_skill = row["skill"].strip()
            all_terms = {canonical_skill.lower(), *aliases}
            skill_rows.append(
                {
                    "skill": canonical_skill,
                    "category": row["category"].strip(),
                    "terms": sorted(all_terms, key=len, reverse=True),
                }
            )

    return skill_rows


def phrase_in_text(phrase: str, normalized_text: str) -> bool:
    """
    Match skill phrases using a safe regex boundary.

    This avoids partial matches such as `sql` inside `mysql`.
    """

    escaped = re.escape(phrase)
    escaped = escaped.replace(r"\ ", r"\s+")
    pattern = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
    return re.search(pattern, normalized_text, flags=re.IGNORECASE) is not None


def extract_skills(text: str, normalized_text: str | None = None) -> dict:
    """
    Detect skills from a text input using the local skills dataset.

    The result is intentionally simple so it is easy to explain in an interview.
    """

    searchable_text = normalized_text or f" {clean_text(text).lower()} "
    matched_skills: list[str] = []
    categories = defaultdict(list)

    for row in load_skills_dataset():
        found = any(phrase_in_text(term, searchable_text) for term in row["terms"])
        if found:
            matched_skills.append(row["skill"])
            categories[row["category"]].append(row["skill"])

    matched_skills = sorted(set(matched_skills))
    sorted_categories = {
        category: sorted(set(items)) for category, items in sorted(categories.items())
    }

    return {
        "skills": matched_skills,
        "categories": sorted_categories,
        "count": len(matched_skills),
    }
