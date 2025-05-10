import os
import requests
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Entity Summarizer")

# Initialize session state variables
if 'summary_data' not in st.session_state:
    st.session_state.summary_data = None
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = None
if 'entity_name' not in st.session_state:
    st.session_state.entity_name = ""

@st.cache_data(ttl=3600, show_spinner=False)
def get_entity_summary(entity: str):
    try:
        response = requests.get(
            f"http://127.0.0.1:8000/summarize/{entity}",
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def display_summary(data):
    st.subheader("🔎 Company Summary")
    st.markdown(data.get("summary", "No summary found."), unsafe_allow_html=True)

    if data.get("official_news"):
        st.subheader("📎 Official News")
        for item in data["official_news"]:
            st.markdown(f"- [{item['title']}]({item['link']})")

    if data.get("official_documents"):
        st.subheader("📂 Documents by Year")
        docs_by_year = {}
        for doc in data["official_documents"]:
            year = doc.get("year", "Unknown")
            docs_by_year.setdefault(year, []).append(doc)

        years = sorted(docs_by_year.keys(), reverse=True)
        selected_year = st.selectbox(
            "Select a year",
            years,
            index=years.index(st.session_state.selected_year) if st.session_state.selected_year in years else 0,
            key='year_select'
        )

        # Update selected year in session state
        st.session_state.selected_year = selected_year

        for doc in docs_by_year[selected_year]:
            st.markdown(f"- [{doc['title']}]({doc['link']})")

    pdf_path = data.get("pdf", "")
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 Download Summary PDF",
                data=f.read(),
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )
    else:
        st.warning("PDF report not available")

# Main form
with st.form("summary_form"):
    entity = st.text_input("Enter company/entity name", value=st.session_state.entity_name)
    submit_button = st.form_submit_button("Summarize Entity")

if submit_button:
    if not entity.strip():
        st.warning("Please enter a valid company/entity name.")
    else:
        st.session_state.entity_name = entity
        with st.spinner("Summarizing..."):
            data = get_entity_summary(entity.strip())

            if data and "error" not in data:
                st.session_state.summary_data = data
                # Set default year to most recent
                if data.get("official_documents"):
                    docs_by_year = {}
                    for doc in data["official_documents"]:
                        year = doc.get("year", "Unknown")
                        docs_by_year.setdefault(year, []).append(doc)
                    st.session_state.selected_year = sorted(docs_by_year.keys(), reverse=True)[0]

                st.rerun()
            elif data and "error" in data:
                st.error(data["error"])
            else:
                st.error("Failed to summarize entity. Please try again.")

# Display results if available
if st.session_state.summary_data:
    display_summary(st.session_state.summary_data)