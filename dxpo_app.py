import streamlit as st
import pandas as pd
import numpy as np
import anthropic
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="DXPO AI Magic Box",
    page_icon="🪄",
    layout="wide")

st.title("DXPO AI Magic Box")
st.subheader(
    "Dr. Jay Rajasekera | "
    "Tokyo International University")
st.markdown("---")

uploaded_file = st.file_uploader(
    "Upload your data file",
    type=["xlsx","xls","xlsm","csv"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        xl = pd.ExcelFile(uploaded_file)
        if len(xl.sheet_names) > 1:
            sheet = st.selectbox(
                "Select sheet:",
                xl.sheet_names)
        else:
            sheet = xl.sheet_names[0]
        df = pd.read_excel(
            uploaded_file,
            sheet_name=sheet)

    st.success(
        f"✅ Loaded: {uploaded_file.name}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{df.shape[0]:,}")
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Missing",
            df.isnull().sum().sum())

    with st.expander("👀 Preview Data"):
        st.dataframe(df.head(10),
            use_container_width=True)

    st.markdown("---")

    if st.button(
        "🚀 Generate DXPO Report",
        type="primary",
        use_container_width=True):

        with st.spinner(
            "🪄 Analyzing... Please wait..."):

            num_cols = df.select_dtypes(
                include=[np.number]
                ).columns.tolist()

            summary = f"""
Dataset: {df.shape[0]} rows,
{df.shape[1]} columns
Numeric columns: {len(num_cols)}
Columns: {", ".join(
    df.columns[:10].tolist())}
"""
            try:
                api_key = os.environ.get(
                    "ANTHROPIC_API_KEY", "")
                client = anthropic.Anthropic(
                    api_key=api_key)
                message = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=1500,
                    messages=[{
                        "role": "user",
                        "content": f"""
You are DXPO AI Magic Box by
Dr. Jay Rajasekera,
Tokyo International University.

Analyze this business data:
{summary}

Generate professional DXPO report:
1. EXECUTIVE SUMMARY
2. KEY PAIN POINTS
3. RECOMMENDED DX APPROACH
4. QUICK WINS (30 days)
5. STRATEGIC ROADMAP
"""
                    }])
                report = (
                    message.content[0].text)
            except Exception as e:
                report = f"Error: {e}"

            st.markdown("---")
            st.subheader("🪄 DXPO Report")
            st.markdown(report)

            st.download_button(
                "📥 Download Report",
                report,
                "DXPO_Report.txt",
                use_container_width=True)

            st.success("✅ Analysis complete!")
            st.balloons()

st.markdown("---")
st.caption(
    "DXPO AI Magic Box | "
    "Dr. Jay Rajasekera | "
    "Tokyo International University | "
    "Powered by Claude AI")
