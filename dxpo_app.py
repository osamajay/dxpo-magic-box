
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import anthropic
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="DXPO AI Magic Box",
    page_icon="🪄",
    layout="wide"
)

# ── HEADER ──
st.title("DXPO AI Magic Box")
st.subheader(
    "Powered by Dr. Jay Rajasekera | "
    "Tokyo International University")
st.markdown("---")

# ── THREE STEPS ──
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Step 1**\n\n📂 Upload your data")
with col2:
    st.info("**Step 2**\n\n📊 Review analytics")
with col3:
    st.info("**Step 3**\n\n🪄 Get DXPO report!")
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
        data="Process,Cost,Time,Errors,"
             "Satisfaction\n"
             "Example Process,1000,5,10,80",
        file_name="DXPO_Template.csv",
        mime="text/csv")

# ── MESSY OR CLEAN DATA ──
else:
    st.subheader("📂 Upload Your Data File")
    uploaded_file = st.file_uploader(
        "Choose Excel or CSV file",
        type=["xlsx","xls","xlsm","csv"])

    if uploaded_file is not None:
        try:
            # ── SHEET SELECTOR ──
            if not uploaded_file.name.endswith(
                    ".csv"):
                xl = pd.ExcelFile(uploaded_file)
                sheet_names = xl.sheet_names
                if len(sheet_names) > 1:
                    st.info(
                        f"Found {len(sheet_names)}"
                        f" sheets in your file!")
                    selected_sheet = st.selectbox(
                        "Select sheet to analyze:",
                        sheet_names)
                else:
                    selected_sheet = sheet_names[0]

                df = pd.read_excel(
                    uploaded_file,
                    sheet_name=selected_sheet)
                st.success(
                    f"✅ Loaded sheet: "
                    f"'{selected_sheet}' from "
                    f"{uploaded_file.name}")
            else:
                df = pd.read_csv(uploaded_file)
                st.success(
                    f"✅ Loaded: {uploaded_file.name}")

            # ── DATA CLEANING (Option 2) ──
            if "MESSY" in situation:
                st.markdown("---")
                st.subheader("🔧 Data Cleaning Agent")

                missing = df.isnull().sum().sum()
                dupes = df.duplicated().sum()

                col1, col2, col3, col4 = (
                    st.columns(4))
                with col1:
                    st.metric("Rows",
                        f"{df.shape[0]:,}")
                with col2:
                    st.metric("Columns",
                        df.shape[1])
                with col3:
                    st.metric("Missing Values",
                        missing)
                with col4:
                    st.metric("Duplicates", dupes)

                if missing > 0 or dupes > 0:
                    st.warning(
                        f"Found {missing} missing "
                        f"values and {dupes} "
                        f"duplicate rows!")
                    if st.button(
                            "🔧 Auto-Fix Issues"):
                        num_cols = df.select_dtypes(
                            include=[np.number]
                            ).columns
                        df[num_cols] = df[
                            num_cols].fillna(0)
                        df = df.fillna("Unknown")
                        df = df.drop_duplicates()
                        st.success(
                            "✅ Data cleaned!")
                else:
                    st.success(
                        "✅ No issues found!")

            # ── DATA PROFILE ──
            st.markdown("---")
            st.subheader("🔍 Data Profile")

            num_cols = df.select_dtypes(
                include=[np.number]).columns.tolist()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows",
                    f"{df.shape[0]:,}")
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                st.metric("Missing",
                    df.isnull().sum().sum())
            with col4:
                st.metric("Numeric Cols",
                    len(num_cols))

            with st.expander("👀 Preview Data"):
                st.dataframe(df.head(10),
                    use_container_width=True)

            # ── ANALYTICS TABS ──
            if len(num_cols) > 0:
                st.markdown("---")
                st.subheader("📊 Automatic Analytics")

                tab1, tab2, tab3, tab4 = st.tabs([
                    "📈 Distributions",
                    "🔗 Correlations",
                    "📊 Summary Stats",
                    "🏆 Top Values"])

                with tab1:
                    st.write(
                        "**Distribution of "
                        "Numeric Columns**")
                    n_cols = min(len(num_cols), 4)
                    fig, axes = plt.subplots(
                        1, n_cols,
                        figsize=(5*n_cols, 4))
                    if n_cols == 1:
                        axes = [axes]
                    for i, col in enumerate(
                            num_cols[:n_cols]):
                        axes[i].hist(
                            df[col].dropna(),
                            bins=20,
                            color="#1B3A6B",
                            edgecolor="white")
                        axes[i].set_title(
                            col[:20], fontsize=10)
                        axes[i].set_facecolor(
                            "#FAFAFA")
                        axes[i].spines[
                            "top"].set_visible(False)
                        axes[i].spines[
                            "right"].set_visible(False)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()

                with tab2:
                    if len(num_cols) >= 2:
                        st.write(
                            "**Correlation Heatmap**")
                        corr = df[num_cols].corr()
                        fig, ax = plt.subplots(
                            figsize=(8, 6))
                        im = ax.imshow(
                            corr.values,
                            cmap="RdYlGn",
                            vmin=-1, vmax=1)
                        plt.colorbar(im, ax=ax)
                        ax.set_xticks(
                            range(len(num_cols)))
                        ax.set_yticks(
                            range(len(num_cols)))
                        ax.set_xticklabels(
                            [c[:10] for c in
                             num_cols],
                            rotation=45,
                            fontsize=8)
                        ax.set_yticklabels(
                            [c[:10] for c in
                             num_cols],
                            fontsize=8)
                        for i in range(
                                len(num_cols)):
                            for j in range(
                                    len(num_cols)):
                                ax.text(
                                    j, i,
                                    f"{corr.iloc[i,j]:.2f}",
                                    ha="center",
                                    va="center",
                                    fontsize=7,
                                    fontweight="bold")
                        ax.set_title(
                            "Correlation Heatmap",
                            fontsize=12,
                            fontweight="bold")
                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.info(
                            "Need 2+ numeric columns"
                            " for correlation!")

                with tab3:
                    st.write(
                        "**Summary Statistics**")
                    st.dataframe(
                        df[num_cols].describe(
                            ).round(2),
                        use_container_width=True)

                with tab4:
                    st.write(
                        "**Top Values Explorer**")
                    selected = st.selectbox(
                        "Select column:",
                        num_cols)
                    top_n = st.slider(
                        "Show top N:", 5, 20, 10)
                    top_vals = df.nlargest(
                        top_n, selected)
                    fig, ax = plt.subplots(
                        figsize=(8, 4))
                    ax.barh(
                        range(len(top_vals)),
                        top_vals[selected],
                        color="#1B3A6B")
                    ax.set_yticks(
                        range(len(top_vals)))
                    ax.set_yticklabels(
                        [str(i) for i in
                         top_vals.index],
                        fontsize=8)
                    ax.set_title(
                        f"Top {top_n}: {selected}",
                        fontweight="bold")
                    ax.spines[
                        "top"].set_visible(False)
                    ax.spines[
                        "right"].set_visible(False)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()

            else:
                st.warning(
                    "No numeric columns found "
                    "in this sheet. "
                    "Try selecting a different "
                    "sheet or check your data!")

            # ── GENERATE REPORT ──
            st.markdown("---")
            if st.button(
                "🚀 GENERATE DXPO REPORT!!",
                type="primary",
                use_container_width=True):

                with st.spinner(
                    "🪄 Magic Box analyzing..."
                    " Please wait..."):

                    num_cols = df.select_dtypes(
                        include=[np.number]
                        ).columns.tolist()

                    analysis = f"""
Dataset: {df.shape[0]} rows,
         {df.shape[1]} columns
Missing values: {df.isnull().sum().sum()}
Numeric columns: {len(num_cols)}
All columns: {", ".join(df.columns.tolist())}
"""
                    if len(num_cols) > 0:
                        desc = df[
                            num_cols].describe()
                        analysis += f"""
Statistical Summary:
{desc.to_string()}
"""
                        if len(num_cols) >= 2:
                            corr = df[
                                num_cols].corr()
                            high_corr = []
                            for i in range(
                                    len(num_cols)):
                                for j in range(
                                        i+1,
                                        len(num_cols)):
                                    r = corr.iloc[
                                        i, j]
                                    if abs(r) > 0.5:
                                        high_corr.append(
                                            f"{num_cols[i]}"
                                            f" & {num_cols[j]}"
                                            f": r={r:.2f}")
                            if high_corr:
                                analysis += (
                                    "\nStrong "
                                    "correlations: " +
                                    ", ".join(
                                        high_corr))

                    try:
                        api_key = os.environ.get(
                            "ANTHROPIC_API_KEY",
                            "")
                        client = (
                            anthropic.Anthropic(
                                api_key=api_key))

                        message = (
                            client.messages.create(
                                model=(
                                    "claude-opus-4-5"),
                                max_tokens=2000,
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
                                }]))

                        report = message.content[
                            0].text

                    except Exception as e:
                        report = f"""
## DXPO Analysis Report

**Dataset:** {df.shape[0]} rows,
{df.shape[1]} columns

**Observations:**
- {len(num_cols)} numeric columns
- Missing: {df.isnull().sum().sum()}

*Connect API key for full AI report*
"""

                    st.markdown("---")
                    st.subheader(
                        "🪄 DXPO Magic Box Report")
                    st.markdown(report)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download Report",
                            data=report,
                            file_name=(
                                "DXPO_Report.txt"),
                            mime="text/plain",
                            use_container_width=True)
                    with col2:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label=(
                                "📥 Download Clean Data"),
                            data=csv,
                            file_name=(
                                "cleaned_data.csv"),
                            mime="text/csv",
                            use_container_width=True)

                    st.success("✅ Analysis complete!")
                    st.balloons()

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ── FOOTER ──
st.markdown("---")
st.caption(
    "DXPO AI Magic Box | "
    "Dr. Jay Rajasekera | "
    "Tokyo International University | "
    "Powered by Claude AI")
