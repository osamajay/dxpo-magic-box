
import streamlit as st
import pandas as pd
import numpy as np
import anthropic
import os
import warnings
warnings.filterwarnings("ignore")

# Page config
st.set_page_config(
    page_title="DXPO AI Magic Box",
    page_icon="🪄",
    layout="wide"
)

# ── HEADER ──
st.title("🪄 DXPO AI Magic Box")
st.subheader(
    "Powered by Dr. Jay Rajasekera | "
    "Tokyo International University")
st.markdown("---")

# ── THREE STEPS ──
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Step 1**\n\n📂 Upload your data file")
with col2:
    st.info("**Step 2**\n\n🔍 Magic Box profiles it")
with col3:
    st.info("**Step 3**\n\n📊 Get your DXPO report!")

st.markdown("---")

# ── SITUATION ──
st.subheader("What describes your situation?")
situation = st.radio(
    "Select one:",
    ["1️⃣  I have NO data yet",
     "2️⃣  I have MESSY data",
     "3️⃣  I have CLEAN data ready!"],
    horizontal=True)

st.markdown("---")

# ── NO DATA ──
if "NO data" in situation:
    st.warning("### 📋 No Data? No Problem!")
    st.markdown("""
    To use DXPO Magic Box you need:
    - ✅ Process names in your company
    - ✅ Current cost per process
    - ✅ Time taken per process
    - ✅ Number of errors/complaints
    - ✅ Customer satisfaction score
    """)
    st.download_button(
        label="📥 Download Data Template",
        data="Process,Cost,Time,Errors,Satisfaction\nExample Process,1000,5,10,80",
        file_name="DXPO_Template.csv",
        mime="text/csv")

# ── MESSY OR CLEAN DATA ──
else:
    st.subheader("📂 Upload Your Data File")
    uploaded_file = st.file_uploader(
        "Choose Excel or CSV file",
        type=["xlsx","xls","xlsm","csv"])

    if uploaded_file is not None:
        # Load data
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success(
                f"✅ Loaded: {uploaded_file.name}")

            # ── DATA PROFILE ──
            st.markdown("---")
            st.subheader("🔍 Data Profile")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", f"{df.shape[0]:,}")
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                st.metric("Missing",
                    df.isnull().sum().sum())
            with col4:
                st.metric("Duplicates",
                    df.duplicated().sum())

            # Data preview
            st.subheader("👀 Data Preview")
            st.dataframe(df.head(10),
                use_container_width=True)

            # ── ANALYZE BUTTON ──
            st.markdown("---")
            if st.button(
                "🚀 ANALYZE WITH DXPO MAGIC BOX!!",
                type="primary",
                use_container_width=True):

                with st.spinner(
                    "🪄 Magic Box analyzing... "
                    "Please wait..."):

                    # Build analysis
                    num_cols = df.select_dtypes(
                        include=[np.number]
                        ).columns.tolist()

                    analysis = f"""
Dataset: {df.shape[0]} rows, {df.shape[1]} columns
Missing values: {df.isnull().sum().sum()}
Numeric columns: {len(num_cols)}
Column names: {", ".join(df.columns.tolist())}
"""
                    if len(num_cols) > 0:
                        desc = df[num_cols].describe()
                        analysis += f"""
Statistical Summary:
{desc.to_string()}
"""

                    # Call Claude
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
You are the DXPO AI Magic Box by
Dr. Jay Rajasekera,
Tokyo International University.

DXPO = Digital Transformation-driven
Process Optimization

Analyze this business data and provide
a professional DXPO report:

{analysis}

Structure your report as:

1. KEY FINDINGS (top 3 insights)
2. PROCESSES NEEDING DX
3. HIGHEST IMPACT OPPORTUNITY
4. RECOMMENDED DX APPROACH
5. QUICK WINS (next 30 days)
6. STRATEGIC ACTIONS (6 months)

Be concise and board-level professional!
"""
                            }])

                        report = message.content[0].text

                    except Exception as e:
                        report = f"""
## DXPO Analysis Report

**Dataset:** {df.shape[0]} rows, 
{df.shape[1]} columns

**Key Observations:**
- {len(num_cols)} numeric columns found
- Missing values: {df.isnull().sum().sum()}
- Ready for DXPO analysis!

*Connect API key for full AI recommendations*
"""

                    # Show report
                    st.markdown("---")
                    st.subheader(
                        "🪄 DXPO Magic Box Report")
                    st.markdown(report)

                    # Download
                    st.download_button(
                        label="📥 Download Report",
                        data=report,
                        file_name="DXPO_Report.txt",
                        mime="text/plain",
                        use_container_width=True)

                    st.success(
                        "✅ Analysis complete!")
                    st.balloons()

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ── FOOTER ──
st.markdown("---")
st.caption(
    "🪄 DXPO AI Magic Box | "
    "Dr. Jay Rajasekera | "
    "Tokyo International University | "
    "Powered by Claude AI")
