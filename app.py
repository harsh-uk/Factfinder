import os

import requests
import streamlit as st

API_HOST = os.getenv("API_HOST", "http://127.0.0.1:8000")

st.set_page_config(layout="wide")
st.title("📊 Entity Summarizer")

if 'summary_data' not in st.session_state:
    st.session_state.summary_data = None
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = None
if 'entity_name' not in st.session_state:
    st.session_state.entity_name = ""


@st.cache_data(ttl=3600, show_spinner=False)
def get_entity_summary(entity: str):
    try:
        response = requests.get(f"{API_HOST}/summarize/{entity}", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None


def display_tabs(data):
    tabs = st.tabs(["📄 Summary", "📂 Documents"])

    with tabs[0]:
        st.subheader("🔎 Company Summary")
        st.markdown(data.get("summary", "No summary found."), unsafe_allow_html=True)

        if data.get("official_news"):
            st.subheader("📎 Official News")
            for item in data["official_news"]:
                st.markdown(f"- [{item['title']}]({item['link']})")

    with tabs[1]:
        if data.get("official_documents"):
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
            st.session_state.selected_year = selected_year

            for doc in docs_by_year[selected_year]:
                st.markdown(f"- [{doc['title']}]({doc['link']})")
        else:
            st.info("No documents found.")

    # Download button
    entity_safe = st.session_state.entity_name.replace(" ", "_")
    pdf_download_url = f"{API_HOST}/download/{entity_safe}"
    try:
        response = requests.get(pdf_download_url)
        response.raise_for_status()
        st.download_button(
            "📄 Download Summary PDF",
            data=response.content,
            file_name=f"{entity_safe}_summary.pdf",
            mime="application/pdf"
        )
    except requests.exceptions.RequestException:
        st.warning("PDF download failed. Try again after summarization.")


# Main form
with st.form("summary_form"):
    entity = st.text_input("Enter company/entity name", value=st.session_state.entity_name)
    submit_button = st.form_submit_button("Summarize Entity")

if submit_button:
    if not entity.strip():
        st.warning("Please enter a valid company/entity name.")
    else:
        st.session_state.entity_name = entity.strip()
        with st.spinner("Summarizing..."):
            data = get_entity_summary(entity.strip())

            if data and "error" not in data:
                st.session_state.summary_data = data
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

if st.session_state.summary_data:
    display_tabs(st.session_state.summary_data)
