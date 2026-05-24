import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import anthropic
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="DXPO AI Magic Box",
    page_icon="🪄",
    layout="wide")

# Header
st.title("🪄 DXPO AI Magic Box")
st.subheader(
    "Dr. Jay Rajasekera | "
    "Tokyo International University")
st.caption(
    "Digital Transformation-driven "
    "Process Optimization")
st.markdown("---")

# ── STEP 1: FILE UPLOAD ──
st.subheader("📂 Step 1 — Upload Your Data")
uploaded_file = st.file_uploader(
    "Upload Excel or CSV file",
    type=["xlsx","xls","xlsm","csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.success(
                f"✅ Loaded: {uploaded_file.name}")
        else:
            xl = pd.ExcelFile(uploaded_file)
            sheets = xl.sheet_names
            sheet = st.selectbox(
                "Select sheet:", sheets)
            df = pd.read_excel(
                uploaded_file,
                sheet_name=sheet)
            st.success(
                f"✅ Loaded sheet: {sheet}")

        col1,col2,col3 = st.columns(3)
        with col1:
            st.metric("Rows",
                f"{df.shape[0]:,}")
        with col2:
            st.metric("Columns",
                df.shape[1])
        with col3:
            st.metric("Missing",
                df.isnull().sum().sum())

        with st.expander("👀 Preview Data"):
            st.dataframe(df.head(10),
                use_container_width=True)

        st.markdown("---")

        # ── STEP 2: DXPO DOC ──
        st.subheader(
            "🏥 Step 2 — DXPO DOC Interview")
        st.caption(
            "Like Ningendokku — "
            "we listen first!!")

        col1, col2 = st.columns(2)

        with col1:
            industry = st.radio(
                "Q1: Your industry?",
                ["🛒 Retail/E-commerce",
                 "🏭 Manufacturing",
                 "💰 Financial Services",
                 "🏥 Healthcare",
                 "🚚 Logistics/Supply Chain",
                 "🔧 Other"])

            concern_opts = [
                "📉 Revenue declining",
                "💸 Costs too high",
                "👥 Losing customers/churn",
                "⏱️ Processes too slow",
                "🔍 Cannot identify best customers",
                "📢 Marketing not effective"]

            concern_primary = st.selectbox(
                "Q2: PRIMARY concern:",
                concern_opts)

            concern_secondary = st.selectbox(
                "Q2: SECONDARY concern:",
                ["None"] + concern_opts)

        with col2:
            dept_opts = [
                "📊 Sales & Marketing",
                "⚙️ Operations",
                "💹 Finance",
                "🤝 Customer Service",
                "🏢 All equally"]

            dept_primary = st.selectbox(
                "Q3: PRIMARY department:",
                dept_opts)

            dept_secondary = st.selectbox(
                "Q3: SECONDARY department:",
                ["None"] + dept_opts)

            data_age = st.radio(
                "Q4: Data recency?",
                ["📅 Last 3 months",
                 "📆 Last 1 year",
                 "🗓️ Last 3 years",
                 "📂 More than 3 years",
                 "❓ Not sure"])

            dx_history = st.radio(
                "Q5: Previous DX attempts?",
                ["🆕 No — first attempt",
                 "❌ Previous attempts failed",
                 "⚡ Partial success",
                 "🔄 In progress"])

        st.markdown("---")

        # ── STEP 3: RUN ANALYSIS ──
        if st.button(
            "🔬 Run Marketing Dokku + "
            "Generate DXPO Report!!",
            type="primary",
            use_container_width=True):

            with st.spinner(
                "🪄 Analyzing your data..."):

                # Detect columns
                amt_cols = [
                    c for c in df.columns
                    if '-Amt' in c or
                    'Amt' in c or
                    'amount' in c.lower()]

                if not amt_cols:
                    amt_cols = [
                        c for c in
                        df.select_dtypes(
                        include=[np.number]
                        ).columns
                        if 'id' not in
                        c.lower()]

                df['Total-Amt'] = (
                    df[amt_cols].sum(axis=1))
                n = len(df)
                pain_points = []

                # Status column
                status_col = None
                for c in df.columns:
                    if 'status' in c.lower():
                        status_col = c
                        break

                # Internet column
                internet_col = None
                internet_pct = 0
                for c in df.columns:
                    if 'internet' in c.lower():
                        internet_col = c
                        break

                inactive = 0
                inactive_spend = 0
                active_spend = 0

                # TEST 1: Retention
                if status_col:
                    inactive = (
                        df[status_col]
                        =='Inactive').sum()
                    inactive_pct = inactive/n*100
                    active_spend = df[
                        df[status_col]=='Active'][
                        'Total-Amt'].mean()
                    inactive_spend = df[
                        df[status_col]=='Inactive'][
                        'Total-Amt'].mean()
                    spend_gap = (
                        active_spend -
                        inactive_spend)

                    if inactive_pct > 15:
                        flag = ("🔴 RED"
                            if inactive_pct > 30
                            else "🟡 YELLOW")
                        pain_points.append({
                            "test":
                                "Customer Retention",
                            "finding":
                                f"{inactive_pct:.1f}%"
                                f" inactive · "
                                f"${spend_gap:,.0f}"
                                f" gap",
                            "flag": flag})

                # TEST 2: Digital Gap
                if internet_col:
                    internet_pct = (
                        df[internet_col]>0
                        ).sum()/n*100
                    if internet_pct < 25:
                        flag = ("🔴 RED"
                            if internet_pct < 10
                            else "🟡 YELLOW")
                        pain_points.append({
                            "test":
                                "Digital Channel Gap",
                            "finding":
                                f"Only "
                                f"{internet_pct:.1f}%"
                                f" ordering online",
                            "flag": flag})

                # TEST 3: Revenue
                rev_by_prod = {
                    c.replace('-Amt',''):
                    df[c].sum()
                    for c in amt_cols}
                total_rev = sum(
                    rev_by_prod.values())
                sorted_prods = sorted(
                    rev_by_prod.items(),
                    key=lambda x: x[1],
                    reverse=True)
                top_pct = (
                    sorted_prods[0][1]/
                    total_rev*100)
                finding = ("Top 3: " +
                    ", ".join([
                        f"{p}({r/total_rev*100:.1f}%)"
                        for p,r in
                        sorted_prods[:3]]))
                if top_pct > 25:
                    flag = ("🔴 RED"
                        if top_pct > 40
                        else "🟡 YELLOW")
                    pain_points.append({
                        "test":
                            "Revenue Concentration",
                        "finding": finding,
                        "flag": flag})

                # ADAPTIVE: Churn
                churn_triggers = [
                    "👥 Losing customers/churn",
                    "🔍 Cannot identify best customers"]
                if (concern_primary
                    in churn_triggers or
                    concern_secondary
                    in churn_triggers):
                    if status_col:
                        rev_at_risk = (
                            inactive *
                            inactive_spend)
                        pain_points.append({
                            "test": "Churn Risk",
                            "finding":
                                f"${rev_at_risk:,.0f}"
                                f" revenue at risk",
                            "flag": "🔴 RED"})

                # ── SHOW RESULTS ──
                st.markdown("---")
                st.subheader(
                    "🔬 Step 3 — "
                    "Marketing Dokku Results")

                red_pts = [p for p in
                    pain_points
                    if 'RED' in p['flag']]
                yel_pts = [p for p in
                    pain_points
                    if 'YELLOW' in p['flag']]

                col1,col2,col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Total Pain Points",
                        len(pain_points))
                with col2:
                    st.metric(
                        "🔴 RED Critical",
                        len(red_pts))
                with col3:
                    st.metric(
                        "🟡 YELLOW Monitor",
                        len(yel_pts))

                for p in pain_points:
                    st.write(
                        f"{p['flag']} "
                        f"**{p['test']}**: "
                        f"{p['finding']}")

                # Pain Point Chart
                pain_names = [
                    p['test']
                    for p in pain_points]
                pain_sevs = [
                    3 if 'RED' in p['flag']
                    else 2
                    for p in pain_points]
                colors = [
                    '#E74C3C'
                    if 'RED' in p['flag']
                    else '#F39C12'
                    for p in pain_points]

                fig1 = go.Figure()
                fig1.add_trace(go.Bar(
                    x=pain_sevs,
                    y=pain_names,
                    orientation='h',
                    marker_color=colors,
                    text=[f"{s}/3"
                        for s in pain_sevs],
                    textposition='outside'))
                fig1.update_layout(
                    title=dict(
                        text='🏥 Pain Point Summary',
                        x=0.5,
                        font=dict(
                            size=16,
                            color='#1B3A6B')),
                    xaxis=dict(
                        range=[0,4],
                        tickvals=[0,1,2,3],
                        ticktext=[
                            '0','Low',
                            'Medium','High']),
                    yaxis=dict(
                        autorange='reversed'),
                    plot_bgcolor='#FAFAFA',
                    paper_bgcolor='white',
                    height=350,
                    showlegend=False)

                st.plotly_chart(fig1,
                    use_container_width=True)

                # Download Object 1
                fig1.write_html(
                    'obj1_painpoints.html')
                with open(
                    'obj1_painpoints.html',
                    'rb') as f_html:
                    st.download_button(
                        "📥 Download Pain Point Chart",
                        f_html,
                        "DXPO_PainPoints.html",
                        use_container_width=True)

                st.markdown("---")

                # ── IMPACT EVALUATION ──
                st.subheader(
                    "🎯 Step 4 — "
                    "DXPO Impact Evaluation")
                st.caption(
                    "Figure 4 · "
                    "Dr. Jay Rajasekera · "
                    "APO Framework · Springer")

                impact_scores = []
                for i, p in enumerate(
                        pain_points, 1):
                    st.write(
                        f"**{p['flag']} "
                        f"{p['test']}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        a = st.slider(
                            f"A — Customer Value",
                            1, 10, 7,
                            key=f"a_{i}")
                    with col2:
                        b = st.slider(
                            f"B — Implementation",
                            1, 10, 5,
                            key=f"b_{i}")
                    impact_scores.append({
                        "pain_point": p['test'],
                        "finding"  : p['finding'],
                        "flag"     : p['flag'],
                        "A": a, "B": b,
                        "impact": a*b})
                    st.write(
                        f"Impact = "
                        f"{a} × {b} = **{a*b}**")
                    st.markdown("---")

                impact_scores.sort(
                    key=lambda x: x['impact'],
                    reverse=True)
                for i,p in enumerate(
                        impact_scores,1):
                    p['rank'] = i

                # Impact Table
                processes = [p['pain_point']
                    for p in impact_scores]
                a_vals = [p['A']
                    for p in impact_scores]
                b_vals = [p['B']
                    for p in impact_scores]
                impacts = [p['impact']
                    for p in impact_scores]
                ranks = [f"#{p['rank']}"
                    for p in impact_scores]
                colors2 = [
                    '#2ECC71' if i>=70 else
                    '#F39C12' if i>=50 else
                    '#E74C3C'
                    for i in impacts]

                fig2 = go.Figure(data=[
                    go.Table(
                        columnwidth=[
                            260,70,70,90,70],
                        header=dict(
                            values=[
                                '<b>Process</b>',
                                '<b>A</b>',
                                '<b>B</b>',
                                '<b>Impact</b>',
                                '<b>Rank</b>'],
                            fill_color='#1B3A6B',
                            font=dict(
                                color='white',
                                size=12),
                            align='center',
                            height=45),
                        cells=dict(
                            values=[
                                processes,
                                a_vals,
                                b_vals,
                                impacts,
                                ranks],
                            fill_color=[
                                ['#F8F9FA']*
                                len(processes),
                                ['#EBF5FB']*
                                len(processes),
                                ['#EBF5FB']*
                                len(processes),
                                colors2,
                                ['#F8F9FA']*
                                len(processes)],
                            font=dict(
                                color=[
                                    ['#1B3A6B']*
                                    len(processes),
                                    ['#1B3A6B']*
                                    len(processes),
                                    ['#1B3A6B']*
                                    len(processes),
                                    ['white']*
                                    len(processes),
                                    ['#1B3A6B']*
                                    len(processes)],
                                size=12),
                            align='center',
                            height=38))])

                fig2.update_layout(
                    title=dict(
                        text='🎯 DXPO Impact Table · '
                             'Dr. Jay Rajasekera',
                        x=0.5,
                        font=dict(
                            size=14,
                            color='#1B3A6B')),
                    height=300,
                    margin=dict(
                        l=10,r=10,t=60,b=10))

                st.plotly_chart(fig2,
                    use_container_width=True)

                fig2.write_html(
                    'obj2_impact.html')
                with open(
                    'obj2_impact.html',
                    'rb') as f_html:
                    st.download_button(
                        "📥 Download Impact Table",
                        f_html,
                        "DXPO_ImpactTable.html",
                        use_container_width=True)

                st.markdown("---")

                # ── CLAUDE REPORT ──
                st.subheader(
                    "🪄 Step 5 — DXPO Report")

                summary = (
                    f"Industry: {industry}\n"
                    f"Concern: {concern_primary}\n"
                    f"Pain points found: "
                    f"{len(pain_points)}\n")
                for p in impact_scores:
                    summary += (
                        f"#{p['rank']} "
                        f"{p['pain_point']}: "
                        f"Impact={p['impact']}/100\n")

                try:
                    api_key = os.environ.get(
                        "ANTHROPIC_API_KEY","")
                    client = anthropic.Anthropic(
                        api_key=api_key)
                    message = (
                        client.messages.create(
                        model="claude-opus-4-5",
                        max_tokens=1500,
                        messages=[{
                            "role":"user",
                            "content":
                            f"""
You are DXPO AI Magic Box by
Dr. Jay Rajasekera,
Tokyo International University.

Generate professional DXPO report:
{summary}

Include:
1. EXECUTIVE SUMMARY
2. TOP PAIN POINTS
3. RECOMMENDED DX APPROACH
4. QUICK WINS (30 days)
5. STRATEGIC ROADMAP
\"\"\"
                        }]))
                    report = (
                        message.content[0].text)
                except Exception as e:
                    report = f"Error: {e}"

                st.markdown(report)

                st.download_button(
                    "📥 Download DXPO Report",
                    report,
                    "DXPO_Report.txt",
                    use_container_width=True)

                st.success(
                    "✅ Analysis complete!!")
                st.balloons()

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.write(str(e))

st.markdown("---")
st.caption(
    "🪄 DXPO AI Magic Box | "
    "Dr. Jay Rajasekera | "
    "Tokyo International University | "
    "Powered by Claude AI")
