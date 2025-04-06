import streamlit as st
import docx
import matplotlib.pyplot as plt

# Resume file parsing function
def parse_resume(file):
    resume_text = ""
    doc = docx.Document(file)
    for paragraph in doc.paragraphs:
        resume_text += paragraph.text + "\n"
    return resume_text

# Extract resume information
def extract_resume_info(resume_text):
    sections = {
        "Education": [],
        "Work Experience": [],
        "Research Experience": [],
        "Skills & Interests": []
    }
    lines = resume_text.split("\n")
    current_section = None
    for line in lines:
        line = line.strip()
        if "EDUCATION" in line.upper():
            current_section = "Education"
        elif "PROFESSIONAL EXPERIENCES" in line.upper() or "WORK EXPERIENCE" in line.upper():
            current_section = "Work Experience"
        elif "RESEARCH EXPERIENCES" in line.upper() or "RESEARCH EXPERIENCE" in line.upper():
            current_section = "Research Experience"
        elif "SKILLS & INTERESTS" in line.upper() or "SKILLS" in line.upper():
            current_section = "Skills & Interests"
        elif current_section and line:
            sections[current_section].append(line)
    return sections

# Display content on the website
st.title("Resume Analysis and Display")

uploaded_file = st.file_uploader("Please upload your resume (Word document)", type=["docx"])
if uploaded_file:
    try:
        resume_text = parse_resume(uploaded_file)
        resume_data = extract_resume_info(resume_text)

        # Display raw text for debugging
        with st.expander("View Raw Text"):
            st.text(resume_text)

        # Two-column layout
        col1, col2 = st.columns(2, gap="large")

        # Education section
        with col1:
            st.header("🎓 **Education**")
            if resume_data["Education"]:
                for edu in resume_data["Education"]:
                    if edu.strip():
                        if ":" in edu:
                            title, details = edu.split(":", 1)
                            st.markdown(f"- **{title.strip()}**: {details.strip()}")
                        else:
                            st.markdown(f"- {edu}")
            else:
                st.write("No education information detected")

        # Work Experience section
        with col1:
            st.header("💼 **Work Experience**")
            if resume_data["Work Experience"]:
                for exp in resume_data["Work Experience"]:
                    if exp.strip():
                        if ":" in exp:
                            title, details = exp.split(":", 1)
                            st.markdown(f"- **{title.strip()}**: {details.strip()}")
                        else:
                            st.markdown(f"- {exp}")
            else:
                st.write("No work experience detected")

        # Research Experience section
        with col2:
            st.header("🔬 **Research Experience**")
            if resume_data["Research Experience"]:
                for research in resume_data["Research Experience"]:
                    if research.strip():
                        if ":" in research:
                            title, details = research.split(":", 1)
                            st.markdown(f"- **{title.strip()}**: {details.strip()}")
                        else:
                            st.markdown(f"- {research}")
            else:
                st.write("No research experience detected")

        # Skills and Interests section
        with col2:
            st.header("🧠 **Skills & Interests**")
            if resume_data["Skills & Interests"]:
                for skill in resume_data["Skills & Interests"]:
                    if skill.strip():
                        st.markdown(f"- {skill}")
            else:
                st.write("No skills & interests detected")

        st.markdown("---")

        # Improved layout and spacing
        st.markdown("""
        <style>
        .stMarkdown h2 {margin-top: 2rem;}
        .stMarkdown ul {margin-bottom: 1rem;}
        .stMarkdown li {margin-bottom: 0.5rem;}
        </style>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error parsing resume: {str(e)}") 