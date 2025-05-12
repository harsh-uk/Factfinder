import os

import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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
        response = requests.get(f"{API_HOST}/summarize/{entity}", timeout=60)
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


def display_financial_dashboard(financial_data: dict):
    if not financial_data:
        st.info("No financial data available for visualization.")
        return

    years = sorted(financial_data.keys(), reverse=True)
    current_year = str(datetime.now().year)
    current_month = datetime.now().month
    completed_quarters = ["Q1", "Q2", "Q3", "Q4"]
    if current_year in years:
        if current_month <= 3:
            completed_quarters = ["Q1"]
        elif current_month <= 6:
            completed_quarters = ["Q1", "Q2"]
        elif current_month <= 9:
            completed_quarters = ["Q1", "Q2", "Q3"]

    selected_year = st.selectbox("Select Year", years, index=0)
    available_quarters = sorted(financial_data[selected_year].keys())
    if selected_year == current_year:
        available_quarters = [q for q in available_quarters if q in completed_quarters]

    selected_quarter = st.selectbox("Select Quarter", available_quarters, index=len(available_quarters)-1)

    current = financial_data[selected_year][selected_quarter]
    prev_quarter_index = available_quarters.index(selected_quarter) - 1
    previous = financial_data[selected_year][available_quarters[prev_quarter_index]] if prev_quarter_index >= 0 else None

    st.subheader(f"📊 {selected_quarter} {selected_year} Financials")
    df = pd.DataFrame([
        {"Metric": "Revenue", "Value": current.get("revenue", 0)},
        {"Metric": "Profit", "Value": current.get("profit", 0)}
    ])
    fig = px.bar(df, x="Metric", y="Value", title="Quarterly Metrics", text="Value")
    st.plotly_chart(fig, use_container_width=True)

    if previous:
        st.markdown("### 🔁 Comparison with Previous Quarter")
        comp_df = pd.DataFrame([
            {"Metric": "Revenue", "Previous": previous.get("revenue", 0), "Current": current.get("revenue", 0)},
            {"Metric": "Profit", "Previous": previous.get("profit", 0), "Current": current.get("profit", 0)}
        ])
        comp_df["Change (%)"] = ((comp_df["Current"] - comp_df["Previous"]) / comp_df["Previous"].replace(0, 1)) * 100
        st.dataframe(comp_df.style.format({"Previous": ".2f", "Current": ".2f", "Change (%)": "{:+.2f}%"}))

    st.markdown("### 🔮 Prediction (Linear Extrapolation)")
    q_index = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    past_data = [
        (q_index[q], data["revenue"], data["profit"])
        for q, data in financial_data[selected_year].items()
        if data["revenue"] and data["profit"]
    ]
    if len(past_data) >= 2:
        q_nums, revs, profits = zip(*past_data)
        rev_trend = (revs[-1] - revs[0]) / (q_nums[-1] - q_nums[0]) if q_nums[-1] != q_nums[0] else 0
        prof_trend = (profits[-1] - profits[0]) / (q_nums[-1] - q_nums[0]) if q_nums[-1] != q_nums[0] else 0
        next_q = max(q_nums) + 1
        if next_q <= 4:
            st.info(f"Prediction for Q{next_q} {selected_year}:\n- Revenue: {revs[-1] + rev_trend:.2f}\n- Profit: {profits[-1] + prof_trend:.2f}")
    else:
        st.warning("Not enough data for prediction.")


if st.session_state.summary_data:
    display_tabs(st.session_state.summary_data)

    if "financial_data" in st.session_state.summary_data:
        display_financial_dashboard(st.session_state.summary_data["financial_data"])
