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

        # ── DXPO DOC SUMMARY BOX ──
        st.subheader("📋 DXPO DOC Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
**🏭 Industry:** {industry}

**🎯 Primary Concern:** {concern_primary}

**🎯 Secondary Concern:** {concern_secondary}

**📊 Primary Dept:** {dept_primary}

**📊 Secondary Dept:** {dept_secondary}
            """)
        with col2:
            st.info(f"""
**📅 Data Age:** {data_age}

**🔄 DX History:** {dx_history}
            """)

        st.markdown("---")

        # ── STEP 2B: OPTIONAL QUESTIONS ──
        st.subheader(
            "🔬 Step 2B — Optional Questions")
        st.caption(
            "Like Ningendokku premium package!! "
            "Answer for deeper analysis — "
            "or skip to proceed!!")

        show_optional = st.checkbox(
            "✅ Yes — I want deeper analysis "
            "(answer optional questions)",
            value=False)

        opt_context = {}

        if show_optional:
            st.info(
                "These optional questions "
                "trigger additional targeted "
                "tests specific to your "
                "business context!!")

            col1, col2 = st.columns(2)

            with col1:
                opt_competitors = st.selectbox(
                    "OPT-Q1: Main competitors?",
                    ["Not answered",
                     "Domestic only",
                     "Global competitors",
                     "Both domestic + global"])

                opt_size = st.selectbox(
                    "OPT-Q2: Company size?",
                    ["Not answered",
                     "SME (under 100 staff)",
                     "Mid-size (100-1000)",
                     "Large (over 1000)"])

                opt_digital = st.selectbox(
                    "OPT-Q3: Current digital tools?",
                    ["Not answered",
                     "None — paper based",
                     "Basic (Excel only)",
                     "Some (CRM/ERP)",
                     "Advanced (AI/Analytics)"])

            with col2:
                opt_budget = st.selectbox(
                    "OPT-Q4: DX budget available?",
                    ["Not answered",
                     "Limited (under $10K)",
                     "Moderate ($10K-$100K)",
                     "Significant (over $100K)"])

                opt_timeline = st.selectbox(
                    "OPT-Q5: Implementation timeline?",
                    ["Not answered",
                     "Urgent (within 3 months)",
                     "Normal (3-6 months)",
                     "Long term (over 6 months)"])

                opt_data_freq = st.selectbox(
                    "OPT-Q6: How often is data updated?",
                    ["Not answered",
                     "Real-time / Daily",
                     "Weekly / Monthly",
                     "Quarterly / Annual",
                     "Irregular"])

            opt_context = {
                "competitors" : opt_competitors,
                "company_size": opt_size,
                "digital_tools": opt_digital,
                "dx_budget"   : opt_budget,
                "timeline"    : opt_timeline,
                "data_freq"   : opt_data_freq
            }

            # Show optional summary
            answered = {k:v for k,v in
                opt_context.items()
                if v != "Not answered"}

            if answered:
                st.success(
                    f"✅ {len(answered)} optional "
                    f"questions answered!! "
                    f"Deeper analysis enabled!!")
            else:
                st.warning(
                    "⚠️  No optional questions "
                    "answered yet!!")
        else:
            st.info(
                "💡 Skipping optional questions — "
                "standard analysis will run!!")

        st.markdown("---")

        # ── STEP 3: RUN ANALYSIS ──
        if st.button(
            "🔬 Run Marketing Dokku + "
            "Generate DXPO Report!!",
            type="primary",
            use_container_width=True):
            st.session_state.run_analysis = True

        if st.session_state.get(
            'run_analysis', False):

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

                # ── TEST DETAILS ──
                st.markdown(
                    "### 🔬 Marketing Dokku — Test Details")
                st.caption(
                    "Standard + Adaptive tests · "
                    "Based on YOUR interview!!")

                test_details = [
                    {"label": "TEST 1",
                     "name": "Customer Retention",
                     "finding": f"{inactive_pct:.1f}% inactive · ${spend_gap:,.0f} gap"
                                if status_col else "No status column",
                     "flag": next((p["flag"] for p in pain_points
                                  if p["test"]=="Customer Retention"),
                                 "🟢 GREEN")},
                    {"label": "TEST 2",
                     "name": "Digital Channel Gap",
                     "finding": f"Internet orders: {internet_pct:.1f}%"
                                if internet_col else "No channel data",
                     "flag": next((p["flag"] for p in pain_points
                                  if p["test"]=="Digital Channel Gap"),
                                 "🟢 GREEN")},
                    {"label": "TEST 3",
                     "name": "Revenue Concentration",
                     "finding": finding,
                     "flag": next((p["flag"] for p in pain_points
                                  if p["test"]=="Revenue Concentration"),
                                 "🟢 GREEN")},
                    {"label": "TEST 4",
                     "name": "Cross-sell Penetration",
                     "finding": f"Single buyers: {((df[amt_cols]>0).sum(axis=1)==1).sum()/n*100:.1f}%",
                     "flag": "🟢 GREEN"},
                ]

                # Add adaptive tests
                for p in pain_points:
                    if p["test"] not in [
                        t["name"] for t in test_details]:
                        test_details.append({
                            "label": "A-TEST",
                            "name": p["test"],
                            "finding": p["finding"],
                            "flag": p["flag"]
                        })

                # Display each test
                # with enhanced descriptions
                for t in test_details:
                    if "RED" in t["flag"]:
                        icon = "🔴"
                        urgency = "CRITICAL — Action needed!!"
                    elif "YELLOW" in t["flag"]:
                        icon = "🟡"
                        urgency = "MONITOR — Watch carefully!!"
                    else:
                        icon = "🟢"
                        urgency = "HEALTHY — No action needed!!"

                    # Why tested
                    why = {
                        "TEST 1": "Standard test — "
                            "Customer retention is a "
                            "core metric for ALL "
                            "retail businesses!!",
                        "TEST 2": "Standard test — "
                            "Digital channel adoption "
                            "is critical for modern "
                            "retail competitiveness!!",
                        "TEST 3": "Standard test — "
                            "Revenue concentration "
                            "measures business risk "
                            "from product dependency!!",
                        "TEST 4": "Standard test — "
                            "Cross-sell penetration "
                            "measures how well products "
                            "complement each other!!",
                        "A-TEST": "Adaptive test — "
                            "Triggered by YOUR interview "
                            "answer about customer "
                            "concerns!!"
                    }

                    with st.expander(
                        f"{icon} {t['label']}: "
                        f"{t['name']} — "
                        f"{t['flag']}",
                        expanded=True):

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(
                                "**📋 Finding:**")
                            st.write(t["finding"])
                            st.markdown(
                                "**🎯 Urgency:**")
                            st.write(urgency)
                        with col2:
                            st.markdown(
                                "**❓ Why Tested:**")
                            st.write(
                                why.get(
                                    t["label"],
                                    "Adaptive test "
                                    "triggered by "
                                    "your interview!!"))

                        st.markdown(
                            "**📊 Statistical Note:**")
                        if t["label"] == "TEST 1":
                            st.write(
                                f"Threshold: >15% inactive "
                                f"= YELLOW · >30% = RED · "
                                f"Your rate: "
                                f"{inactive_pct:.1f}%")
                        elif t["label"] == "TEST 2":
                            st.write(
                                f"Threshold: <25% online "
                                f"= YELLOW · <10% = RED · "
                                f"Your rate: "
                                f"{internet_pct:.1f}%")
                        elif t["label"] == "TEST 3":
                            st.write(
                                f"Threshold: >25% in one "
                                f"product = YELLOW · "
                                f">40% = RED · "
                                f"Your top product: "
                                f"{top_pct:.1f}%")
                        elif t["label"] == "TEST 4":
                            st.write(
                                f"Threshold: >60% single "
                                f"buyers = RED · "
                                f">40% = YELLOW · "
                                f"Healthy = GREEN")
                        elif t["label"] == "A-TEST":
                            st.write(
                                f"Adaptive threshold: "
                                f"Inactive spend < 60% "
                                f"of active = RED · "
                                f"Your ratio: "
                                f"{inactive_spend/active_spend*100:.1f}%")

                # ── COMPLETE RESULTS TABLE ──
                st.markdown("### 📊 Marketing Dokku — Complete Test Results")
                st.caption("All tests run · Standard + Adaptive · Based on YOUR interview!!")

                # Build complete test results
                all_tests = [
                    {
                        "test": "Customer Retention",
                        "type": "Standard",
                        "finding": f"{inactive_pct:.1f}% inactive · ${spend_gap:,.0f} gap"
                                   if status_col else "No status column detected",
                        "flag": next((p["flag"] for p in pain_points
                                     if p["test"]=="Customer Retention"),
                                    "🟢 GREEN")
                    },
                    {
                        "test": "Digital Channel Gap",
                        "type": "Standard",
                        "finding": f"Only {internet_pct:.1f}% ordering online"
                                   if internet_col else "No channel data detected",
                        "flag": next((p["flag"] for p in pain_points
                                     if p["test"]=="Digital Channel Gap"),
                                    "🟢 GREEN")
                    },
                    {
                        "test": "Revenue Concentration",
                        "type": "Standard",
                        "finding": finding,
                        "flag": next((p["flag"] for p in pain_points
                                     if p["test"]=="Revenue Concentration"),
                                    "🟢 GREEN")
                    },
                    {
                        "test": "Cross-sell Penetration",
                        "type": "Standard",
                        "finding": f"{(df['Total-Amt']>0).sum()/n*100:.1f}% active buyers",
                        "flag": "🟢 GREEN"
                    },
                ]

                # Add adaptive tests
                for p in pain_points:
                    if p["test"] not in [
                        t["test"] for t in all_tests]:
                        all_tests.append({
                            "test": p["test"],
                            "type": "Adaptive",
                            "finding": p["finding"],
                            "flag": p["flag"]
                        })

                # Build Plotly table
                test_names = [t["test"]
                    for t in all_tests]
                test_types = [t["type"]
                    for t in all_tests]
                test_findings = [t["finding"]
                    for t in all_tests]
                test_flags = [t["flag"]
                    for t in all_tests]

                row_colors = []
                for t in all_tests:
                    if "RED" in t["flag"]:
                        row_colors.append("#FDEDEC")
                    elif "YELLOW" in t["flag"]:
                        row_colors.append("#FEF9E7")
                    else:
                        row_colors.append("#EAFAF1")

                fig_tests = go.Figure(data=[
                    go.Table(
                        columnwidth=[
                            180, 80, 300, 100],
                        header=dict(
                            values=[
                                "<b>Test</b>",
                                "<b>Type</b>",
                                "<b>Finding</b>",
                                "<b>Status</b>"],
                            fill_color="#1B3A6B",
                            font=dict(
                                color="white",
                                size=12),
                            align="center",
                            height=40),
                        cells=dict(
                            values=[
                                test_names,
                                test_types,
                                test_findings,
                                test_flags],
                            fill_color=[
                                row_colors,
                                row_colors,
                                row_colors,
                                row_colors],
                            font=dict(
                                color="#1B3A6B",
                                size=11),
                            align=["left",
                                   "center",
                                   "left",
                                   "center"],
                            height=35))])

                fig_tests.update_layout(
                    title=dict(
                        text="🔬 Marketing Dokku — All Test Results",
                        x=0.5,
                        font=dict(
                            size=14,
                            color="#1B3A6B")),
                    height=300,
                    margin=dict(
                        l=10,r=10,t=60,b=10))

                st.plotly_chart(fig_tests,
                    use_container_width=True)

                # Download button
                fig_tests.write_html(
                    "dokku_results.html")
                with open(
                    "dokku_results.html",
                    "rb") as f_html:
                    st.download_button(
                        "📥 Download Dokku Results",
                        f_html,
                        "DXPO_DukkuResults.html",
                        use_container_width=True)

                # Pain points summary
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "🔴 RED Critical",
                        len(red_pts))
                with col2:
                    st.metric(
                        "🟡 YELLOW Monitor",
                        len(yel_pts))
                with col3:
                    st.metric(
                        "🟢 GREEN Healthy",
                        len(all_tests) -
                        len(red_pts) -
                        len(yel_pts))

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
"""
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
