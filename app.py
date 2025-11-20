import streamlit as st
from typing import TypedDict, List
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
import os
os.environ["GROQ_API_KEY"]="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"


# ---------------------
# Define state
# ---------------------
class ProjectState(TypedDict):
    project: str
    summary: str
    tech_stack: str
    team: List[str]

llm = ChatGroq(model="openai/gpt-oss-120b")

students = [
    {"name": "Ananya", "visa": "OPT", "skills": ["React", "Node.js", "MongoDB"]},
    {"name": "Rahul", "visa": "STEM OPT", "skills": ["Python", "AWS", "Redshift"]},
    {"name": "Priya", "visa": "OPT", "skills": ["Flutter", "Firebase"]},
    {"name": "Vikram", "visa": "STEM OPT", "skills": ["React", "AWS"]},
]

# ---------------------
# Agent functions
# ---------------------
def project_analyzer(state: ProjectState):
    project = state["project"]
    prompt = f"Summarize this project and identify if it’s web, data, or mobile: {project}"
    summary = llm.invoke(prompt).content
    return {"summary": summary}

def tech_recommender(state: ProjectState):
    summary = state["summary"]
    prompt = f"Suggest a suitable tech stack for this project: {summary}. Keep it short."
    tech_stack = llm.invoke(prompt).content
    return {"tech_stack": tech_stack}

def student_allocator(state: ProjectState):
    tech = state["tech_stack"].lower()
    chosen = []
    for s in students:
        if any(skill.lower() in tech for skill in s["skills"]):
            chosen.append(f"{s['name']} ({s['visa']})")
        if len(chosen) == 2:
            break
    if not chosen:
        chosen = ["Generic OPT student", "Generic STEM OPT student"]
    return {"team": chosen}

# ---------------------
# Build LangGraph
# ---------------------
graph = StateGraph(ProjectState)
graph.add_node("analyzer", project_analyzer)
graph.add_node("recommender", tech_recommender)
graph.add_node("allocator", student_allocator)

graph.set_entry_point("analyzer")
graph.add_edge("analyzer", "recommender")
graph.add_edge("recommender", "allocator")

workflow = graph.compile()

# ---------------------
# Streamlit UI
# ---------------------
st.title("Project Analyzer & Student Allocator 🚀")

project_desc = st.text_area("Enter your project description:")

if st.button("Run Analysis"):
    if not project_desc.strip():
        st.error("Please enter a project description.")
    else:
        with st.spinner("Analyzing project..."):
            result = workflow.invoke({"project": project_desc})

        st.success("Analysis Complete!")

        st.subheader("📌 Summary")
        st.write(result["summary"])

        st.subheader("🛠 Recommended Tech Stack")
        st.write(result["tech_stack"])

        st.subheader("👥 Suggested Students")
        st.write(result["team"])
