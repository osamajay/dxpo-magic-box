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

# Header Jun 27, 2026-->dxpo_app (31-reset to 29 at Urasa PC) version
st.title("🪄 DXPO AI Magic Box")
st.subheader(
    "Dr. Jay Rajasekera | "
    "Tokyo International University")
st.caption(
    "Digital Transformation-driven "
    "Process Optimization ver(29-jun272026-1106pm)")
st.markdown("---")

# ── STEP 1: FILE UPLOAD ──
st.subheader("📂 Step 1 — Upload Your Data")
st.caption(
    "Upload up to 3 files (Excel or CSV). "
    "DXPO MB will auto-detect what each file "
    "contains — you can confirm or override!!")

MAX_FILES = 3

def detect_file_type(df):
    """Auto-detect which Dokku module a
    dataframe belongs to based on column
    fingerprints. Returns a category string."""
    cols = " ".join(
        c.lower() for c in df.columns)
    if any(k in cols for k in [
        'total-amt','amount','revenue',
        'spend','price','unit-price',
        'customer','status','channel',
        'payment']):
        return "Customer / Marketing"
    if any(k in cols for k in [
        'defect','downtime','machine',
        'units-produced','maintenance',
        'operating-temp','product-code']):
        return "Operations / Quality"
    if any(k in cols for k in [
        'employee','headcount','salary',
        'attendance','performance',
        'department','hire-date']):
        return "HR / Workforce"
    if any(k in cols for k in [
        'budget','profit','expense',
        'cost','invoice','ledger']):
        return "Finance"
    return "Unknown — please select below"

MODULE_OPTIONS = [
    "Customer / Marketing",
    "Operations / Quality",
    "HR / Workforce",
    "Finance",
    "Unknown — please select below"
]

# Render up to 3 upload slots
uploaded_files = []
for fi in range(MAX_FILES):
    label = (
        "📁 File 1 (required)"
        if fi == 0 else
        f"📁 File {fi+1} (optional)")
    uf = st.file_uploader(
        label,
        type=["xlsx","xls","xlsm","csv"],
        key=f"uploader_{fi}")
    if uf is not None:
        uploaded_files.append(uf)

if not uploaded_files:
    st.info(
        "☝️ Please upload at least one "
        "file to begin.")

# Process each uploaded file
loaded = []   # list of dicts:
              # {name, df, detected, assigned}

if uploaded_files:
    st.markdown("---")
    st.markdown(
        "**🔍 File Detection & Assignment**")

    for fi, uf in enumerate(uploaded_files):
        try:
            if uf.name.endswith(".csv"):
                raw_df = pd.read_csv(uf)
            else:
                xl = pd.ExcelFile(uf)
                sheets = xl.sheet_names
                if len(sheets) > 1:
                    sheet = st.selectbox(
                        f"Sheet for "
                        f"{uf.name}:",
                        sheets,
                        key=f"sheet_{fi}")
                else:
                    sheet = sheets[0]
                raw_df = pd.read_excel(
                    uf,
                    sheet_name=sheet)

            detected = detect_file_type(raw_df)

            col_a, col_b = st.columns([2,2])
            with col_a:
                st.success(
                    f"✅ **{uf.name}** — "
                    f"{raw_df.shape[0]:,} rows, "
                    f"{raw_df.shape[1]} cols")
                st.caption(
                    f"🩺 Auto-detected as: "
                    f"**{detected}**")
            with col_b:
                assigned = st.selectbox(
                    f"Confirm or change "
                    f"type for file {fi+1}:",
                    MODULE_OPTIONS,
                    index=MODULE_OPTIONS.index(
                        detected)
                    if detected in
                    MODULE_OPTIONS else 4,
                    key=f"assign_{fi}")

            loaded.append({
                "name":     uf.name,
                "df":       raw_df,
                "detected": detected,
                "assigned": assigned})

        except Exception as e:
            st.error(
                f"❌ Could not load "
                f"{uf.name}: {e}")

# ── MERGE SAME-STRUCTURE FILES ──────────────
# Group by assigned module; if >1 file shares
# the same module AND has matching columns,
# merge them into one combined df.
marketing_dfs = [
    l for l in loaded
    if l["assigned"] == "Customer / Marketing"]
ops_dfs = [
    l for l in loaded
    if l["assigned"] == "Operations / Quality"]

def try_merge(df_list):
    """Merge a list of same-assigned dfs if
    their columns match. Returns one df."""
    if not df_list:
        return None
    if len(df_list) == 1:
        return df_list[0]["df"]
    base_cols = set(df_list[0]["df"].columns)
    compatible = [df_list[0]["df"]]
    for item in df_list[1:]:
        if set(item["df"].columns) == base_cols:
            compatible.append(item["df"])
        else:
            st.warning(
                f"⚠️ {item['name']} has "
                f"different columns — "
                f"kept separate, not merged.")
    if len(compatible) > 1:
        merged = pd.concat(
            compatible,
            ignore_index=True)
        st.success(
            f"🔗 Merged {len(compatible)} "
            f"files into one combined "
            f"dataset ({len(merged):,} rows)")
        return merged
    return compatible[0]

# Build the primary df for Marketing Dokku
# (the only active Dokku right now)
df = None
if marketing_dfs:
    df = try_merge(marketing_dfs)
elif loaded:
    # No marketing file — use first file
    # anyway so preview still works;
    # data-gap check will warn the user
    df = loaded[0]["df"]

# Show ops/quality files as coming soon
if ops_dfs:
    for item in ops_dfs:
        st.info(
            f"🚧 **{item['name']}** detected "
            f"as Operations/Quality data — "
            f"this Dokku module is coming "
            f"soon!! Your file is ready "
            f"and waiting.")

# Show combined preview if we have a df
if df is not None:
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

if df is not None:
    try:

        # ── STEP 0: PRE-VISIT QUESTIONNAIRE ──
        st.subheader(
            "📝 Step 0 — Pre-Visit Questionnaire")
        st.caption(
            "Like the Ningendokku pre-visit form — "
            "tell us where it hurts before we run "
            "any tests!!")

        st.markdown(
            "Select the area(s) you're most "
            "concerned about:")

        col1, col2 = st.columns(2)
        with col1:
            concern_hr = st.checkbox(
                "👥 HR / Workforce efficiency")
            concern_kpi = st.checkbox(
                "📊 Not using data to drive KPIs")
            concern_quality = st.checkbox(
                "🏭 Product Quality Problems")
        with col2:
            concern_marketing = st.checkbox(
                "🛒 Customer / Marketing")
            concern_ops = st.checkbox(
                "🚚 Supply chain / Operations")
            concern_finance = st.checkbox(
                "💰 Finance")

        concern_areas = []
        if concern_hr:
            concern_areas.append(
                "HR / Workforce efficiency")
        if concern_kpi:
            concern_areas.append(
                "Not using data to drive KPIs")
        if concern_quality:
            concern_areas.append(
                "Product Quality Problems")
        if concern_marketing:
            concern_areas.append(
                "Customer / Marketing")
        if concern_ops:
            concern_areas.append(
                "Supply chain / Operations")
        if concern_finance:
            concern_areas.append("Finance")

        # ── OPEN SYMPTOMS (multi-concern) ──
        st.markdown(
            "Anything else bothering you that "
            "isn't listed above? *(optional — "
            "like telling the nurse about "
            "multiple symptoms, each in their "
            "own words)*")

        # Initialise concern count in
        # session_state (persists across reruns)
        if 'num_concerns' not in (
            st.session_state):
            st.session_state['num_concerns'] = 1

        MAX_CONCERNS = 5
        cat_list = (
            "HR / Workforce efficiency, "
            "Not using data to drive KPIs, "
            "Product Quality Problems, "
            "Customer / Marketing, "
            "Supply chain / Operations, "
            "Finance, or NEW (if none fit)")

        # Cached concerns dict: key = index,
        # value = {text, category}
        if 'concerns_cache' not in (
            st.session_state):
            st.session_state[
                'concerns_cache'] = {}

        def classify_concern(text):
            """Call Claude to classify one
            concern text. Returns category
            string or None on error."""
            try:
                api_key = os.environ.get(
                    "ANTHROPIC_API_KEY", "")
                client = anthropic.Anthropic(
                    api_key=api_key)
                content = (
                    "A company described "
                    "this concern in their "
                    "own words:\n\"" +
                    text +
                    "\"\n\nClassify it into "
                    "EXACTLY ONE of these "
                    "categories: " +
                    cat_list +
                    "\n\nReply with ONLY "
                    "the category name, "
                    "nothing else.")
                msg = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=100,
                    messages=[{
                        "role": "user",
                        "content": content}])
                return (msg.content[0]
                        .text.strip())
            except Exception as e:
                st.warning(
                    "Could not classify: "
                    + str(e))
                return None

        # Render one text_area per concern
        for i in range(
            st.session_state['num_concerns']):
            cached = (
                st.session_state[
                    'concerns_cache']
                .get(i, {}))
            label = (
                "Concern " + str(i + 1) +
                ":")
            placeholder = (
                "e.g., 'Worrying about "
                "trend analysis for "
                "sales items'"
                if i > 0 else
                "e.g., 'Do not have good "
                "marketing intelligence'")
            typed = st.text_area(
                label,
                key="concern_" + str(i),
                placeholder=placeholder)

            if typed and typed.strip():
                # Auto-classify on blur if
                # text changed since last run
                if typed != cached.get(
                        'text', ''):
                    with st.spinner(
                        "🩺 Reviewing "
                        "concern " +
                        str(i + 1) + "..."):
                        cat = classify_concern(
                            typed)
                    if cat:
                        st.session_state[
                            'concerns_cache'
                        ][i] = {
                            'text': typed,
                            'category': cat}
                        cached = (
                            st.session_state[
                                'concerns_cache'
                            ][i])
                else:
                    pass  # use cached

                if cached.get('category'):
                    st.info(
                        "🩺 Concern " +
                        str(i + 1) +
                        " → **" +
                        cached['category'] +
                        "**")

        # ➕ Add another concern button
        if (st.session_state['num_concerns']
                < MAX_CONCERNS):
            if st.button(
                "➕ Add another concern"):
                st.session_state[
                    'num_concerns'] += 1
                st.rerun()

        # Build a flat list of all classified
        # concerns for downstream use
        all_concerns = [
            v for v in
            st.session_state[
                'concerns_cache'].values()
            if v.get('text', '').strip()
            and v.get('category')]

        # Persist Marketing/Customer unlock
        # across reruns from any concern slot
        for c in all_concerns:
            if (c['category'] ==
                    "Customer / Marketing"
                    and not concern_marketing):
                concern_marketing = True
                label_str = (
                    "Customer / Marketing "
                    "(from concern: \"" +
                    c['text'][:40] +
                    "...\")")
                if label_str not in (
                        concern_areas):
                    concern_areas.append(
                        label_str)

        # Keep backward-compat keys so DOC
        # Summary and S-TEST still work
        # (use first classified concern)
        if all_concerns:
            st.session_state[
                'open_symptom_text'] = (
                all_concerns[0]['text'])
            st.session_state[
                'symptom_category'] = (
                all_concerns[0]['category'])
            # Store full list for S-TEST loop
            st.session_state[
                'all_concerns'] = (
                all_concerns)
        else:
            st.session_state[
                'all_concerns'] = []

        proceed_to_doc = False

        if not concern_areas:
            st.warning(
                "☝️ Please select at least one "
                "concern area to continue.")
        elif concern_marketing:
            # ── DATA GAP CHECK ──
            # Lightweight check: does this file
            # look like it has ANY
            # customer/marketing-relevant
            # columns? (amount, status, customer
            # id, or channel-like). Mirrors (but
            # does not duplicate) the stricter
            # detection Step 3 runs later.
            cols_lower = [
                c.lower() for c in df.columns]
            has_amount = any(
                'amt' in c or 'amount' in c or
                'price' in c or 'revenue' in c or
                'spend' in c
                for c in cols_lower)
            has_status = any(
                'status' in c for c in cols_lower)
            has_customer_id = any(
                'customer' in c or 'client' in c
                for c in cols_lower)
            has_channel = any(
                'channel' in c or 'internet' in c
                or 'online' in c
                for c in cols_lower)

            data_looks_relevant = (
                has_amount or has_status or
                has_customer_id or has_channel)

            if not data_looks_relevant:
                st.warning(
                    "🔬 **Data Gap Detected** — "
                    "your uploaded file doesn't "
                    "look like it has "
                    "customer/marketing data "
                    "(no amount, status, "
                    "customer ID, or channel "
                    "columns found).")
                st.markdown(
                    "Like a specialized clinic "
                    "test, this needs data we "
                    "don't have yet. To run "
                    "Marketing Dokku properly, "
                    "please go get a dataset "
                    "with columns such as:\n"
                    "- Customer ID / name\n"
                    "- Purchase amount / "
                    "revenue per transaction\n"
                    "- Customer status "
                    "(Active/Inactive)\n"
                    "- Order channel "
                    "(online/in-store)\n\n"
                    "You can still proceed with "
                    "what you have, but results "
                    "may be limited.")

            st.success(
                "✅ Marketing Dokku is ready for "
                "your selected concern area(s)!!")
            proceed_to_doc = True
        else:
            st.info(
                "🚧 This module is coming soon — "
                "Marketing Dokku is available now!!")

        st.markdown("---")

        if proceed_to_doc:
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
                all_c = st.session_state.get(
                    'all_concerns', [])
                concerns_line = ""
                if all_c:
                    concerns_line = (
                        "\n\n**🩺 Additional "
                        "Concerns:**")
                    for ci, cv in enumerate(
                            all_c):
                        concerns_line += (
                            "\n" +
                            str(ci+1) + ". \"" +
                            cv.get('text','') +
                            "\" → *" +
                            cv.get('category','')
                            + "*")
                st.info(f"""
    **📅 Data Age:** {data_age}

    **🔄 DX History:** {dx_history}
    {concerns_line}
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
                    opt_country = st.selectbox(
                        "OPT-Q0: Country/Region?",
                        ["Not answered",
                         "🇯🇵 Japan",
                         "🌏 Southeast Asia",
                         "🌏 South Asia",
                         "🌏 East Asia",
                         "🌍 Middle East",
                         "🌐 Global"])

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
                    "country"     : opt_country,
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
                        total_rev*100
                        if sorted_prods else 0)
                    finding = ("Top 3: " +
                        ", ".join([
                            f"{p}({r/total_rev*100:.1f}%)"
                            for p,r in
                            sorted_prods[:3]])
                        if sorted_prods else
                        "No revenue data found")
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

                    # SYMPTOM TESTS: one per
                    # concern the user described
                    # in Step 0. Each gets its
                    # own S-TEST entry in results.
                    all_concerns_for_test = (
                        st.session_state.get(
                            'all_concerns', []))
                    if all_concerns_for_test:
                        try:
                            total_rev_val = (
                                df['Total-Amt']
                                .sum())
                            avg_txn_val = (
                                df['Total-Amt']
                                .mean())
                            data_summary = (
                                "Rows: " + str(n)
                                + "\nColumns: " +
                                str(list(
                                    df.columns))
                                + "\nTotal "
                                "revenue: $" +
                                f"{total_rev_val:,.0f}"
                                + "\nAvg "
                                "transaction: $" +
                                f"{avg_txn_val:,.0f}")
                            if status_col:
                                data_summary += (
                                    "\nActive: " +
                                    str(n-inactive)
                                    + " · "
                                    "Inactive: " +
                                    str(inactive))
                            api_key = (
                                os.environ.get(
                                    "ANTHROPIC_"
                                    "API_KEY", ""))
                            client = (
                                anthropic.Anthropic(
                                    api_key=
                                    api_key))
                            for idx, c in enumerate(
                                all_concerns_for_test):
                                c_text = (
                                    c.get(
                                        'text', ''))
                                c_cat = (
                                    c.get(
                                        'category',
                                        ''))
                                test_name = (
                                    "Your Concern "
                                    + str(idx+1) +
                                    " — AI Review")
                                prompt_text = (
                                    "A company "
                                    "described "
                                    "this concern:"
                                    " \"" +
                                    c_text +
                                    "\"\n(Classified"
                                    " as: " +
                                    c_cat +
                                    ")\n\nHere is "
                                    "a summary of "
                                    "their actual "
                                    "data:\n" +
                                    data_summary +
                                    "\n\nIn 1-2 "
                                    "short sentences"
                                    ", does this "
                                    "data give any "
                                    "evidence "
                                    "relevant to "
                                    "their concern?"
                                    " Be specific "
                                    "and factual. "
                                    "If the summary"
                                    " doesn't have "
                                    "enough detail,"
                                    " say so "
                                    "plainly.")
                                try:
                                    msg = (
                                        client
                                        .messages
                                        .create(
                                        model=
                                        "claude-"
                                        "opus-4-5",
                                        max_tokens=
                                        200,
                                        messages=[{
                                            "role":
                                            "user",
                                            "content"
                                            :
                                            prompt_text
                                        }]))
                                    finding = (
                                        msg
                                        .content[0]
                                        .text
                                        .strip())
                                except Exception:
                                    finding = (
                                        "Could not "
                                        "run AI "
                                        "review.")
                                pain_points.append(
                                    {
                                    "test":
                                        test_name,
                                    "finding":
                                        finding,
                                    "flag":
                                        "🟡 YELLOW"
                                    })
                        except Exception as e:
                            st.warning(
                                "S-TEST error: "
                                + str(e))

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

                    # ── OPTIONAL TRIGGERED TESTS ──
                    if opt_context:
                        opt_pain = []

                        # Digital Maturity Test
                        if opt_context.get(
                            "digital_tools") in [
                            "None — paper based",
                            "Basic (Excel only)"]:
                            opt_pain.append({
                                "test": "Digital Maturity Gap",
                                "finding": f"Current tools: {opt_context.get('digital_tools')} — significant DX opportunity!!",
                                "flag": "🔴 RED",
                                "type": "Optional"})

                        # Budget vs Urgency Test
                        if (opt_context.get("timeline")
                            == "Urgent (within 3 months)"
                            and opt_context.get("dx_budget")
                            == "Limited (under $10K)"):
                            opt_pain.append({
                                "test": "Budget-Urgency Mismatch",
                                "finding": "Urgent timeline but limited budget — risk of failed implementation!!",
                                "flag": "🔴 RED",
                                "type": "Optional"})

                        # Data Freshness Test
                        if opt_context.get(
                            "data_freq") in [
                            "Quarterly / Annual",
                            "Irregular"]:
                            opt_pain.append({
                                "test": "Data Freshness Risk",
                                "finding": f"Data updated {opt_context.get('data_freq')} — insights may be outdated!!",
                                "flag": "🟡 YELLOW",
                                "type": "Optional"})

                        # Competitive Risk Test
                        if opt_context.get(
                            "competitors") in [
                            "Global competitors",
                            "Both domestic + global"]:
                            opt_pain.append({
                                "test": "Global Competition Risk",
                                "finding": f"Facing global competitors with only {internet_pct:.1f}% digital orders — critical gap!!",
                                "flag": "🔴 RED",
                                "type": "Optional"})

                        if opt_pain:
                            st.markdown("---")
                            st.markdown(
                                "### 🔬 Optional Tests — "
                                "Triggered by Your Answers")
                            st.caption(
                                "These tests ran because "
                                "of your Step 2B answers!!")

                            for p in opt_pain:
                                if "RED" in p["flag"]:
                                    icon = "🔴"
                                else:
                                    icon = "🟡"
                                st.markdown(
                                    f"**{icon} {p['test']}**")
                                st.write(
                                    f"📋 {p['finding']}")
                                st.write(
                                    f"Status: {p['flag']}")
                                st.markdown("---")

                            # Add to pain points
                            pain_points.extend(opt_pain)

                            st.success(
                                f"✅ {len(opt_pain)} additional "
                                f"pain points found from "
                                f"optional questions!!")

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
                            is_symptom_test = (
                                "AI Review"
                                in p["test"])
                            test_details.append({
                                "label":
                                "S-TEST" if
                                is_symptom_test
                                else "A-TEST",
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
                                "concerns!!",
                            "S-TEST": "Specialized test — "
                                "Triggered by the concern "
                                "YOU described in your own "
                                "words (Step 0). Like a "
                                "specific test a clinic runs "
                                "because the patient flagged "
                                "a symptom not on the "
                                "standard form!!"
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
                            elif t["label"] == "S-TEST":
                                st.write(
                                    "No fixed statistical "
                                    "threshold — this is "
                                    "Claude's interpretation "
                                    "of your actual data in "
                                    "light of the concern "
                                    "you described. Treat "
                                    "as a starting point for "
                                    "discussion, not a "
                                    "precise measurement.")

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
