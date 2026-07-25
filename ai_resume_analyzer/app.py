from __future__ import annotations

from datetime import datetime
from textwrap import dedent

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.matcher import compare_skill_sets
from modules.parser import extract_text_from_upload
from modules.preprocess import preprocess_text
from modules.scorer import calculate_ats_score, compute_semantic_similarity
from modules.section_detector import detect_sections
from modules.skill_extractor import extract_skills
from modules.suggestions import generate_suggestions


SAMPLE_JOB_DESCRIPTION = """We are looking for a Data Analyst with strong Python, SQL, Excel, Power BI, and communication skills.
The ideal candidate can build dashboards, clean messy data, analyze trends, and present business insights to stakeholders.
Experience with statistics, A/B testing, and cross-functional collaboration is a strong plus."""


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


def add_custom_styles() -> None:
    """Inject custom CSS so the Streamlit app feels more like a polished dashboard."""

    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(31, 122, 140, 0.10), transparent 28%),
                    radial-gradient(circle at top right, rgba(220, 166, 93, 0.08), transparent 25%),
                    linear-gradient(180deg, #f5f7f9 0%, #eef2f3 100%);
                color: #16323a;
                font-family: "Aptos", "Segoe UI", sans-serif;
            }

            .block-container {
                padding-top: 1.8rem;
                padding-bottom: 2.4rem;
                max-width: 1220px;
            }

            h1, h2, h3, h4 {
                font-family: "Georgia", "Times New Roman", serif;
                letter-spacing: -0.02em;
                color: #0f2f39;
            }

            .hero {
                background: linear-gradient(135deg, #16323a 0%, #1f5561 55%, #2b7a78 100%);
                padding: 2rem 2rem 1.6rem 2rem;
                border-radius: 26px;
                color: #f7fbfc;
                border: 1px solid rgba(255, 255, 255, 0.14);
                box-shadow: 0 24px 60px rgba(22, 50, 58, 0.22);
                margin-bottom: 1.4rem;
                overflow: hidden;
                position: relative;
            }

            .hero:before {
                content: "";
                position: absolute;
                width: 260px;
                height: 260px;
                right: -60px;
                top: -90px;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 50%;
            }

            .hero h1 {
                color: #ffffff;
                margin-bottom: 0.35rem;
                font-size: 2.3rem;
            }

            .hero p {
                color: rgba(255, 255, 255, 0.88);
                margin: 0;
                font-size: 1rem;
                max-width: 760px;
            }

            .glass-card {
                background: rgba(255, 255, 255, 0.84);
                border: 1px solid rgba(15, 47, 57, 0.08);
                box-shadow: 0 18px 45px rgba(38, 61, 69, 0.08);
                border-radius: 22px;
                padding: 1.15rem 1.15rem 0.9rem 1.15rem;
                backdrop-filter: blur(4px);
            }

            .metric-card {
                background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(247,249,250,0.94));
                border: 1px solid rgba(15, 47, 57, 0.08);
                border-radius: 20px;
                padding: 1rem 1rem 0.9rem 1rem;
                min-height: 134px;
                box-shadow: 0 14px 36px rgba(31, 53, 63, 0.08);
            }

            .metric-label {
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.78rem;
                color: #52727a;
                margin-bottom: 0.35rem;
                font-weight: 600;
            }

            .metric-value {
                font-size: 2rem;
                color: #123842;
                margin: 0;
                line-height: 1.1;
            }

            .metric-caption {
                margin-top: 0.35rem;
                color: #56727a;
                font-size: 0.92rem;
            }

            .section-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #123842;
                margin-bottom: 0.5rem;
            }

            .pill-wrap {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin-top: 0.35rem;
            }

            .skill-pill {
                display: inline-block;
                padding: 0.4rem 0.7rem;
                border-radius: 999px;
                font-size: 0.88rem;
                font-weight: 600;
                border: 1px solid transparent;
            }

            .pill-neutral {
                background: #edf4f6;
                color: #234954;
                border-color: #d6e4e8;
            }

            .pill-good {
                background: #e7f6ee;
                color: #18603a;
                border-color: #bfe0cd;
            }

            .pill-warn {
                background: #fff4e6;
                color: #8b4c14;
                border-color: #f0d0a8;
            }

            .pill-info {
                background: #e9f1fb;
                color: #184f7a;
                border-color: #bfd6ef;
            }

            .suggestion-card {
                background: #ffffff;
                border-left: 5px solid #2b7a78;
                border-radius: 18px;
                padding: 0.95rem 1rem;
                box-shadow: 0 12px 32px rgba(24, 48, 56, 0.08);
                margin-bottom: 0.8rem;
            }

            .suggestion-priority {
                display: inline-block;
                margin-bottom: 0.45rem;
                font-size: 0.78rem;
                font-weight: 700;
                color: #295965;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .helper-text {
                color: #5c747a;
                font-size: 0.94rem;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #143039 0%, #1b404a 100%);
            }

            [data-testid="stSidebar"] * {
                color: #f6fbfc !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>AI Resume Analyzer</h1>
            <p>
                Upload a resume, paste a job description, and get recruiter-friendly feedback:
                skills coverage, missing keywords, section checks, semantic alignment, ATS scoring,
                and practical improvement suggestions in one clean dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <p class="metric-value">{value}</p>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_pills(skills: list[str], pill_class: str) -> None:
    if not skills:
        st.markdown(
            "<p class='helper-text'>No items to show in this section yet.</p>",
            unsafe_allow_html=True,
        )
        return

    pills = "".join(
        f"<span class='skill-pill {pill_class}'>{skill}</span>" for skill in skills
    )
    st.markdown(f"<div class='pill-wrap'>{pills}</div>", unsafe_allow_html=True)


def score_caption(score: float) -> str:
    if score >= 80:
        return "Strong alignment"
    if score >= 65:
        return "Good foundation"
    if score >= 50:
        return "Needs tailoring"
    return "Needs major improvement"


def build_report(
    resume_text: str,
    job_description: str,
    skill_match: dict,
    sections: dict,
    similarity: dict,
    ats_result: dict,
    suggestions: list[dict],
) -> str:
    """Create a downloadable Markdown report."""

    found_sections = [
        name for name, details in sections["section_details"].items() if details["present"]
    ]
    missing_sections = [
        name for name, details in sections["section_details"].items() if not details["present"]
    ]

    report_lines = [
        "# AI Resume Analyzer Summary",
        "",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Scores",
        f"- ATS-style score: {ats_result['overall_score']}/100",
        f"- Semantic similarity: {similarity['score']}/100",
        f"- Skill coverage: {ats_result['components']['skill_coverage']}/100",
        f"- Section completeness: {ats_result['components']['section_completeness']}/100",
        f"- Keyword match: {ats_result['components']['keyword_match']}/100",
        "",
        "## Skills Comparison",
        f"- Resume skills found: {', '.join(skill_match['resume_skills']) or 'None'}",
        f"- Job description skills: {', '.join(skill_match['job_description_skills']) or 'None'}",
        f"- Matched skills: {', '.join(skill_match['matched_skills']) or 'None'}",
        f"- Missing skills: {', '.join(skill_match['missing_skills']) or 'None'}",
        "",
        "## Section Detection",
        f"- Found sections: {', '.join(found_sections) or 'None'}",
        f"- Missing sections: {', '.join(missing_sections) or 'None'}",
        "",
        "## Suggestions",
    ]

    for suggestion in suggestions:
        report_lines.append(
            f"- [{suggestion['priority'].upper()}] {suggestion['title']}: {suggestion['details']}"
        )

    report_lines.extend(
        [
            "",
            "## Resume Text Preview",
            resume_text[:2500] if resume_text else "No resume text extracted.",
            "",
            "## Job Description Preview",
            job_description[:1800] if job_description else "No job description provided.",
        ]
    )

    return "\n".join(report_lines)


def render_sidebar() -> None:
    st.sidebar.markdown("## How to use")
    st.sidebar.write("1. Upload a resume in PDF or DOCX format.")
    st.sidebar.write("2. Paste the target job description.")
    st.sidebar.write("3. Click **Analyze Resume** to generate the dashboard.")
    st.sidebar.write("4. Review skills, ATS score, section coverage, and suggestions.")

    st.sidebar.markdown("## What is scored?")
    st.sidebar.write("- Semantic similarity between resume and job description")
    st.sidebar.write("- Skill coverage for required keywords")
    st.sidebar.write("- Resume section completeness")
    st.sidebar.write("- Keyword overlap for ATS-style heuristics")

    st.sidebar.info(
        "First use of sentence-transformer similarity may download a small model. "
        "If that is unavailable, the app falls back to a local lexical similarity method."
    )


def main() -> None:
    add_custom_styles()
    render_sidebar()
    render_hero()

    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Input Workspace</div>
            <p class="helper-text">
                Use a real resume for the best results. The analyzer extracts text, compares it
                against the job description, estimates ATS alignment, and highlights gaps you can
                improve before applying.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1, 1.15], gap="large")

    with left_col:
        st.subheader("Upload Resume")
        uploaded_file = st.file_uploader(
            "Supported formats: PDF and DOCX",
            type=["pdf", "docx"],
            help="Upload a resume file to extract and analyze its text.",
        )
        st.caption("Tip: resumes with clear headings produce better section detection.")

    with right_col:
        st.subheader("Paste Job Description")
        job_description = st.text_area(
            "Paste the target role description here",
            height=240,
            placeholder=SAMPLE_JOB_DESCRIPTION,
        )
        st.caption("Include responsibilities, required skills, and nice-to-have qualifications.")

    analyze_clicked = st.button("Analyze Resume", type="primary", use_container_width=True)

    if not analyze_clicked:
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">What you will get</div>
                <p class="helper-text">
                    Extracted resume text, detected skills, matched and missing skills, semantic
                    similarity, ATS-style scoring, section detection, and practical suggestions.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if not uploaded_file:
        st.error("Please upload a PDF or DOCX resume before running the analysis.")
        return

    if not job_description.strip():
        st.error("Please paste a job description so the app can compare your resume against it.")
        return

    with st.spinner("Analyzing resume and job description..."):
        resume_text, parse_error = extract_text_from_upload(uploaded_file)

        if parse_error:
            st.error(parse_error)
            return

        if not resume_text.strip():
            st.error("The file was read successfully, but no readable resume text was extracted.")
            return

        resume_processed = preprocess_text(resume_text)
        job_processed = preprocess_text(job_description)

        resume_skill_result = extract_skills(
            resume_text, normalized_text=resume_processed["normalized_text"]
        )
        job_skill_result = extract_skills(
            job_description, normalized_text=job_processed["normalized_text"]
        )

        skill_match = compare_skill_sets(
            resume_skill_result["skills"], job_skill_result["skills"]
        )
        sections = detect_sections(resume_text)
        similarity = compute_semantic_similarity(resume_text, job_description)
        ats_result = calculate_ats_score(
            semantic_similarity=similarity,
            skill_match=skill_match,
            sections=sections,
            resume_keywords=resume_processed["keywords"],
            job_keywords=job_processed["keywords"],
        )
        suggestions = generate_suggestions(
            resume_text=resume_text,
            job_description=job_description,
            skill_match=skill_match,
            sections=sections,
            similarity=similarity,
            ats_result=ats_result,
        )

    report_content = build_report(
        resume_text=resume_text,
        job_description=job_description,
        skill_match=skill_match,
        sections=sections,
        similarity=similarity,
        ats_result=ats_result,
        suggestions=suggestions,
    )

    st.success("Analysis complete. Review the dashboard below.")

    metric_cols = st.columns(4, gap="medium")
    with metric_cols[0]:
        render_metric_card(
            "ATS Score",
            f"{ats_result['overall_score']:.0f}/100",
            score_caption(ats_result["overall_score"]),
        )
    with metric_cols[1]:
        render_metric_card(
            "Semantic Match",
            f"{similarity['score']:.0f}%",
            similarity["method_label"],
        )
    with metric_cols[2]:
        render_metric_card(
            "Skill Coverage",
            f"{ats_result['components']['skill_coverage']:.0f}%",
            f"{len(skill_match['matched_skills'])} matched of {max(len(skill_match['job_description_skills']), 1)}",
        )
    with metric_cols[3]:
        render_metric_card(
            "Sections Found",
            f"{sections['present_count']}/{sections['total_sections']}",
            f"{ats_result['components']['section_completeness']:.0f}% completeness",
        )

    overview_tab, skills_tab, sections_tab, suggestions_tab = st.tabs(
        ["Overview", "Skills Match", "Section Review", "Suggestions"]
    )

    with overview_tab:
        chart_col, summary_col = st.columns([1.1, 0.9], gap="large")

        with chart_col:
            component_df = pd.DataFrame(
                {
                    "Component": [
                        "Semantic Similarity",
                        "Skill Coverage",
                        "Section Completeness",
                        "Keyword Match",
                    ],
                    "Score": [
                        ats_result["components"]["semantic_similarity"],
                        ats_result["components"]["skill_coverage"],
                        ats_result["components"]["section_completeness"],
                        ats_result["components"]["keyword_match"],
                    ],
                }
            )

            component_chart = px.bar(
                component_df,
                x="Score",
                y="Component",
                orientation="h",
                color="Score",
                color_continuous_scale=["#dca65d", "#2b7a78"],
                range_x=[0, 100],
            )
            component_chart.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=20, b=10),
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Score",
                yaxis_title="",
            )
            st.plotly_chart(component_chart, use_container_width=True)

        with summary_col:
            st.markdown("### Analysis Summary")
            st.write(
                dedent(
                    f"""
                    - **Resume skills detected:** {len(skill_match['resume_skills'])}
                    - **Required job skills detected:** {len(skill_match['job_description_skills'])}
                    - **Matched skills:** {len(skill_match['matched_skills'])}
                    - **Missing skills:** {len(skill_match['missing_skills'])}
                    - **Similarity method:** {similarity['method_label']}
                    """
                )
            )
            st.progress(int(round(ats_result["overall_score"])))
            st.caption(ats_result["summary"])

        with st.expander("View Extracted Resume Text", expanded=False):
            st.text_area(
                "Extracted resume text",
                value=resume_text,
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )

    with skills_tab:
        skills_chart_col, skills_lists_col = st.columns([0.95, 1.05], gap="large")

        with skills_chart_col:
            coverage_df = pd.DataFrame(
                {
                    "Skill Bucket": ["Matched", "Missing", "Additional Resume Skills"],
                    "Count": [
                        len(skill_match["matched_skills"]),
                        len(skill_match["missing_skills"]),
                        len(skill_match["additional_resume_skills"]),
                    ],
                }
            )
            coverage_chart = px.bar(
                coverage_df,
                x="Skill Bucket",
                y="Count",
                color="Skill Bucket",
                color_discrete_map={
                    "Matched": "#2b7a78",
                    "Missing": "#dca65d",
                    "Additional Resume Skills": "#7aa4b4",
                },
            )
            coverage_chart.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=20, b=10),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(coverage_chart, use_container_width=True)

            if resume_skill_result["categories"]:
                category_df = pd.DataFrame(
                    {
                        "Category": list(resume_skill_result["categories"].keys()),
                        "Count": [len(items) for items in resume_skill_result["categories"].values()],
                    }
                ).sort_values("Count", ascending=False)
                st.markdown("### Resume Skill Categories")
                st.dataframe(category_df, use_container_width=True, hide_index=True)

        with skills_lists_col:
            st.markdown("### Skills Found in Resume")
            render_skill_pills(skill_match["resume_skills"], "pill-neutral")

            st.markdown("### Skills Required in Job Description")
            render_skill_pills(skill_match["job_description_skills"], "pill-info")

            st.markdown("### Matched Skills")
            render_skill_pills(skill_match["matched_skills"], "pill-good")

            st.markdown("### Missing Skills")
            render_skill_pills(skill_match["missing_skills"], "pill-warn")

    with sections_tab:
        section_rows = []
        for name, details in sections["section_details"].items():
            section_rows.append(
                {
                    "Section": name,
                    "Status": "Present" if details["present"] else "Missing",
                    "Confidence": f"{details['confidence'] * 100:.0f}%",
                    "Evidence": details["evidence"] or "No strong evidence found",
                }
            )

        section_df = pd.DataFrame(section_rows)
        status_df = pd.DataFrame(
            {
                "Section": section_df["Section"],
                "Score": [100 if status == "Present" else 0 for status in section_df["Status"]],
            }
        )
        status_chart = px.bar(
            status_df,
            x="Section",
            y="Score",
            color="Score",
            color_continuous_scale=["#dca65d", "#2b7a78"],
            range_y=[0, 100],
        )
        status_chart.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=20, b=10),
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis_title="Detected",
            xaxis_title="",
        )
        st.plotly_chart(status_chart, use_container_width=True)
        st.dataframe(section_df, use_container_width=True, hide_index=True)

    with suggestions_tab:
        st.markdown("### Actionable Recommendations")
        for suggestion in suggestions:
            st.markdown(
                f"""
                <div class="suggestion-card">
                    <div class="suggestion-priority">{suggestion['priority']}</div>
                    <div><strong>{suggestion['title']}</strong></div>
                    <div>{suggestion['details']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.download_button(
            label="Download Analysis Summary",
            data=report_content,
            file_name="resume_analysis_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
