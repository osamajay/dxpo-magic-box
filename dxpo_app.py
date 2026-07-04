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

# Header Jul 04, 2026-->dxpo_app (39) in Higashi-PC) version
st.title("🪄 DXPO AI Magic Box")
st.subheader(
    "Dr. Jay Rajasekera | "
    "Tokyo International University")
st.caption(
    "Digital Transformation-driven "
    "Process Optimization ver(39)jul042026-10:54)")
st.markdown("---")

# ══════════════════════════════════════════
# STEP 0A — GENERAL PRE-VISIT QUESTIONS
# (answered BEFORE uploading any data,
#  like the Ningendokku mailed questionnaire)
# ══════════════════════════════════════════
st.subheader("📝 Step 0A — Who Are You?")
st.caption(
    "Tell us about your company before "
    "uploading any data — like the "
    "Ningendokku questionnaire you fill "
    "in at home before visiting the clinic!!")

col_0a1, col_0a2 = st.columns(2)
with col_0a1:
    company_type = st.radio(
        "What kind of company are you?",
        ["🏭 Manufacturing",
         "🛒 Service / Retail / E-commerce",
         "🔄 Both Manufacturing & Service",
         "❓ Not sure yet"],
        key="company_type_0a")

with col_0a2:
    industry_0a = st.radio(
        "Your industry?",
        ["🛒 Retail / E-commerce",
         "🏭 Manufacturing",
         "💰 Financial Services",
         "🏥 Healthcare",
         "🚚 Logistics / Supply Chain",
         "🔧 Other"],
        key="industry_0a")

st.markdown("---")

# ══════════════════════════════════════════
# STEP 0B — CONCERN AREA SELECTION
# (still before upload — tells us what
#  data to ask for in Step 0C)
# ══════════════════════════════════════════
st.subheader("📋 Step 0B — What's Bothering You?")
st.caption(
    "Select your concern areas — this tells "
    "DXPO MB what kind of data to expect "
    "and which Dokku module(s) to activate!!")

st.markdown(
    "Select the area(s) you're most "
    "concerned about:")

col_0b1, col_0b2 = st.columns(2)
with col_0b1:
    concern_hr_pre = st.checkbox(
        "👥 HR / Workforce Efficiency",
        key="pre_hr")
    concern_kpi_pre = st.checkbox(
        "📊 Data & KPI Visibility",
        key="pre_kpi")
    concern_quality_pre = st.checkbox(
        "🏭 Quality & Process Efficiency",
        key="pre_quality")
with col_0b2:
    concern_marketing_pre = st.checkbox(
        "🛒 Customer & Marketing Strategies",
        key="pre_marketing")
    concern_ops_pre = st.checkbox(
        "🚚 Supply Chain & Operations",
        key="pre_ops")
    concern_finance_pre = st.checkbox(
        "💰 Finance & Cost Control",
        key="pre_finance")

# Guidance based on selections
if concern_marketing_pre and not (
        concern_quality_pre or concern_ops_pre):
    st.info(
        "📂 For Customer & Marketing analysis, "
        "please upload customer transaction "
        "data (with columns like Customer-ID, "
        "Amount, Status, Channel).")
elif (concern_quality_pre or
        concern_ops_pre) and not (
        concern_marketing_pre):
    st.info(
        "📂 For Quality & Operations analysis, "
        "please upload production/machine data "
        "(with columns like Machine-ID, "
        "Defect-Rate, Downtime-Mins).")
elif concern_marketing_pre and (
        concern_quality_pre or concern_ops_pre):
    st.info(
        "📂 You selected both Marketing and "
        "Operations concerns — please upload "
        "both types of data files (up to 3 "
        "files supported)!!")

st.markdown("---")

# ── STEP 0C: UPLOAD YOUR DATA ──
st.subheader("📂 Step 0C — Upload Your Data")
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
        return "Customer & Marketing Strategies"
    if any(k in cols for k in [
        'defect','downtime','machine',
        'units-produced','maintenance',
        'operating-temp','product-code']):
        return "Operations / Quality"
    if any(k in cols for k in [
        'employee','headcount','salary',
        'attendance','performance',
        'department','hire-date']):
        return "HR / Workforce Efficiency"
    if any(k in cols for k in [
        'budget','profit','expense',
        'cost','invoice','ledger']):
        return "Finance & Cost Control"
    return "Unknown — please select below"

MODULE_OPTIONS = [
    "Customer & Marketing Strategies",
    "Operations / Quality",
    "HR / Workforce Efficiency",
    "Finance & Cost Control",
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

            with st.expander(
                f"👀 Preview: {uf.name}"):
                st.dataframe(
                    raw_df.head(10),
                    use_container_width=True)

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
    if l["assigned"] == "Customer & Marketing Strategies"]
ops_dfs = [
    l for l in loaded
    if l["assigned"] == "Operations / Quality"]

def try_merge(df_list, module_label):
    """When 2+ same-assigned files have
    matching columns, ASK the user explicitly
    whether to merge them or keep separate —
    no default choice, since merging is not
    always correct (e.g. different reporting
    periods, files the user wants compared
    side-by-side rather than blended)."""
    if not df_list:
        return None
    if len(df_list) == 1:
        return df_list[0]["df"]

    base_cols = set(df_list[0]["df"].columns)
    compatible = [df_list[0]]
    incompatible = []
    for item in df_list[1:]:
        if set(item["df"].columns) == base_cols:
            compatible.append(item)
        else:
            incompatible.append(item)
            st.warning(
                f"⚠️ {item['name']} has "
                f"different columns from "
                f"the other {module_label} "
                f"file(s) — kept separate, "
                f"not merged.")

    if len(compatible) <= 1:
        return compatible[0]["df"]

    names_str = ", ".join(
        c["name"] for c in compatible)
    st.markdown(
        f"**🔗 {len(compatible)} files "
        f"assigned to {module_label} have "
        f"matching columns:** {names_str}")
    choice = st.radio(
        f"How should these "
        f"{len(compatible)} files be "
        f"used for {module_label}?",
        [
            "⏸️ Please choose",
            "✅ Merge into one combined "
            "dataset",
            "📁 Keep separate — use first "
            "file only for now"
        ],
        index=0,
        key=f"merge_choice_{module_label}")

    if choice == "✅ Merge into one combined dataset":
        merged = pd.concat(
            [c["df"] for c in compatible],
            ignore_index=True)
        st.success(
            f"🔗 Merged {len(compatible)} "
            f"files into one combined "
            f"dataset ({len(merged):,} rows)")
        return merged
    elif (choice == "📁 Keep separate — "
            "use first file only for now"):
        st.info(
            f"📁 Keeping files separate — "
            f"using **{compatible[0]['name']}**"
            f" only for this analysis. "
            f"(Per-file separate analysis "
            f"for all files is a planned "
            f"future enhancement.)")
        return compatible[0]["df"]
    else:
        st.warning(
            "☝️ Please choose how to handle "
            "these files above before "
            "continuing.")
        return None

# Build the primary df for Marketing Dokku
df = None
if marketing_dfs:
    df = try_merge(
        marketing_dfs, "Customer/Marketing")
elif loaded and not ops_dfs and not marketing_dfs:
    # No marketing file and no ops file —
    # use first file anyway so preview still
    # works; data-gap check will warn the user
    df = loaded[0]["df"]

# Build the primary df for Operations/Quality
# Dokku
ops_df = None
if ops_dfs:
    ops_df = try_merge(
        ops_dfs, "Operations/Quality")

# Show combined preview if we have a
# marketing df
if df is not None:
    st.markdown(
        "**📊 Combined Dataset for Analysis "
        "(Marketing)**")
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

    with st.expander(
        "👀 Preview: Final Combined Dataset "
        "(used for Marketing analysis)"):
        st.dataframe(df.head(10),
            use_container_width=True)

    st.markdown("---")

# Show combined preview if we have an
# ops df (and no marketing df, to avoid
# showing the same preview twice)
if ops_df is not None and df is None:
    st.markdown(
        "**📊 Combined Dataset for Analysis "
        "(Operations/Quality)**")
    oc1,oc2,oc3 = st.columns(3)
    with oc1:
        st.metric("Rows",
            f"{ops_df.shape[0]:,}")
    with oc2:
        st.metric("Columns",
            ops_df.shape[1])
    with oc3:
        st.metric("Missing",
            ops_df.isnull().sum().sum())

    with st.expander(
        "👀 Preview: Final Combined Dataset "
        "(used for Operations/Quality "
        "analysis)"):
        st.dataframe(ops_df.head(10),
            use_container_width=True)

    st.markdown("---")

# Step 0 onward should render whenever we
# have EITHER a marketing df OR an ops df
# ready to analyze — not just marketing.
# When there's no marketing df, fall back
# to using ops_df as the "primary" df so
# downstream code (which historically only
# checks `df`) still has something to work
# with for things like the data preview /
# DXPO DOC interview, which are concern-
# agnostic.
if df is None and ops_df is not None:
    df = ops_df

if df is not None:
    try:

        # ── STEP 0: PRE-VISIT QUESTIONNAIRE ──
        st.subheader(
            "📝 Step 0 — Confirm Your Concerns")
        st.caption(
            "Your selections from Step 0B are "
            "shown below — adjust if needed "
            "now that your data is uploaded!!")

        st.markdown(
            "Confirm the area(s) you're most "
            "concerned about:")

        col1, col2 = st.columns(2)
        with col1:
            concern_hr = st.checkbox(
                "👥 HR / Workforce Efficiency",
                value=concern_hr_pre)
            concern_kpi = st.checkbox(
                "📊 Data & KPI Visibility",
                value=concern_kpi_pre)
            concern_quality = st.checkbox(
                "🏭 Quality & Process Efficiency",
                value=concern_quality_pre)
        with col2:
            concern_marketing = st.checkbox(
                "🛒 Customer & Marketing Strategies",
                value=concern_marketing_pre)
            concern_ops = st.checkbox(
                "🚚 Supply Chain & Operations",
                value=concern_ops_pre)
            concern_finance = st.checkbox(
                "💰 Finance & Cost Control",
                value=concern_finance_pre)

        concern_areas = []
        if concern_hr:
            concern_areas.append(
                "HR / Workforce Efficiency")
        if concern_kpi:
            concern_areas.append(
                "Data & KPI Visibility")
        if concern_quality:
            concern_areas.append(
                "Quality & Process Efficiency")
        if concern_marketing:
            concern_areas.append(
                "Customer & Marketing Strategies")
        if concern_ops:
            concern_areas.append(
                "Supply Chain & Operations")
        if concern_finance:
            concern_areas.append("Finance & Cost Control")

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
            "HR / Workforce Efficiency, "
            "Data & KPI Visibility, "
            "Quality & Process Efficiency, "
            "Customer & Marketing Strategies, "
            "Supply Chain & Operations, "
            "Finance & Cost Control, "
            "or NEW (if none fit)")

        # Category definitions for the
        # classifier — critical for avoiding
        # misclassification between similar
        # categories (e.g. machine downtime
        # is Quality & Process Efficiency,
        # NOT Supply Chain & Operations)
        cat_definitions = (
            "\n\nCategory definitions "
            "(use these to classify):\n"
            "- HR / Workforce Efficiency: "
            "staffing, headcount, employee "
            "productivity, absenteeism, "
            "training, workforce planning\n"
            "- Data & KPI Visibility: "
            "lack of dashboards, reports "
            "take too long, no real-time "
            "data, KPIs not tracked\n"
            "- Quality & Process Efficiency:"
            " defect rates, machine downtime,"
            " equipment failures, maintenance"
            " issues, production bottlenecks,"
            " process inefficiency, scrap "
            "rates, rework\n"
            "- Customer & Marketing "
            "Strategies: customer churn, "
            "revenue declining, marketing "
            "effectiveness, sales performance"
            ", customer segmentation, "
            "pricing strategy\n"
            "- Supply Chain & Operations: "
            "supplier delays, inventory "
            "management, logistics, delivery"
            " performance, procurement, "
            "warehousing\n"
            "- Finance & Cost Control: "
            "budget overruns, cost reduction"
            ", profitability, cash flow, "
            "financial reporting\n"
            "- NEW: if the concern does not "
            "fit any category above")

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
                    cat_definitions +
                    "\n\nReply with ONLY "
                    "the category name "
                    "exactly as written "
                    "above, nothing else.")
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
                    "Customer & Marketing Strategies"
                    and not concern_marketing):
                concern_marketing = True
                label_str = (
                    "Customer & Marketing Strategies "
                    "(from concern: \"" +
                    c['text'][:40] +
                    "...\")")
                if label_str not in (
                        concern_areas):
                    concern_areas.append(
                        label_str)
            # Also auto-unlock Operations/
            # Quality from symptom
            if (c['category'] in [
                    "Supply Chain & Operations",
                    "Quality & Process Efficiency"]
                    and not concern_ops
                    and not concern_quality):
                concern_ops = True
                label_str = (
                    "Supply Chain & Operations"
                    " (from concern: \"" +
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
        proceed_to_ops = False

        if not concern_areas:
            st.warning(
                "☝️ Please select at least one "
                "concern area to continue.")
        else:
            if concern_marketing:
                # ── DATA GAP CHECK (Marketing) ──
                cols_lower = [
                    c.lower() for c in df.columns]
                has_amount = any(
                    'amt' in c or 'amount' in c or
                    'price' in c or 'revenue' in c
                    or 'spend' in c
                    for c in cols_lower)
                has_status = any(
                    'status' in c
                    for c in cols_lower)
                has_customer_id = any(
                    'customer' in c or
                    'client' in c
                    for c in cols_lower)
                has_channel = any(
                    'channel' in c or
                    'internet' in c or
                    'online' in c
                    for c in cols_lower)

                data_looks_relevant = (
                    has_amount or has_status or
                    has_customer_id or
                    has_channel)

                if not data_looks_relevant:
                    st.warning(
                        "🔬 **Data Gap Detected** "
                        "— your uploaded file "
                        "doesn't look like it "
                        "has customer/marketing "
                        "data (no amount, "
                        "status, customer ID, "
                        "or channel columns "
                        "found).")
                    st.markdown(
                        "Like a specialized "
                        "clinic test, this needs"
                        " data we don't have "
                        "yet. To run Marketing "
                        "Dokku properly, please "
                        "go get a dataset with "
                        "columns such as:\n"
                        "- Customer ID / name\n"
                        "- Purchase amount / "
                        "revenue per "
                        "transaction\n"
                        "- Customer status "
                        "(Active/Inactive)\n"
                        "- Order channel "
                        "(online/in-store)\n\n"
                        "You can still proceed "
                        "with what you have, "
                        "but results may be "
                        "limited.")

                st.success(
                    "✅ Marketing Dokku is "
                    "ready for your selected "
                    "concern area(s)!!")
                proceed_to_doc = True

            if concern_ops or concern_quality:
                # ── DATA GAP CHECK (Ops) ──
                if ops_df is None and not ops_dfs:
                    st.warning(
                        "🔬 **Data Gap Detected** "
                        "— you flagged an "
                        "Operations/Quality "
                        "concern, but no "
                        "uploaded file was "
                        "detected as Operations"
                        "/Quality data. Please "
                        "go get production, "
                        "machine, or process "
                        "data and upload it.")
                elif ops_df is None and ops_dfs:
                    st.warning(
                        "☝️ Please choose how "
                        "to handle your "
                        "Operations/Quality "
                        "files above (merge "
                        "or keep separate) "
                        "before continuing.")
                else:
                    st.success(
                        "✅ Operations/Quality "
                        "Dokku is ready for "
                        "your selected concern "
                        "area(s)!!")
                    proceed_to_doc = True
                    proceed_to_ops = True

            if not proceed_to_doc and not (
                    concern_marketing or
                    concern_ops or
                    concern_quality):
                st.info(
                    "🚧 This module is coming "
                    "soon — Marketing Dokku "
                    "and Operations/Quality "
                    "Dokku are available now!!")

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
                # Q1 — pre-filled from Step 0A
                industry = st.radio(
                    "Q1: Your industry?",
                    ["🛒 Retail/E-commerce",
                     "🏭 Manufacturing",
                     "💰 Financial Services",
                     "🏥 Healthcare",
                     "🚚 Logistics/Supply Chain",
                     "🔧 Other"],
                    index=["🛒 Retail/E-commerce",
                           "🏭 Manufacturing",
                           "💰 Financial Services",
                           "🏥 Healthcare",
                           "🚚 Logistics/Supply Chain",
                           "🔧 Other"].index(
                        "🏭 Manufacturing"
                        if "Manufacturing"
                        in industry_0a else
                        "🛒 Retail/E-commerce"
                        if "Retail" in
                        industry_0a else
                        "💰 Financial Services"
                        if "Financial"
                        in industry_0a else
                        "🏥 Healthcare"
                        if "Healthcare"
                        in industry_0a else
                        "🚚 Logistics/Supply Chain"
                        if "Logistics"
                        in industry_0a else
                        "🔧 Other"))

                # Q2 — adaptive based on
                # concern selections
                is_ops_concern = (
                    concern_quality or
                    concern_ops)
                is_mkt_concern = (
                    concern_marketing)

                if is_ops_concern and not (
                        is_mkt_concern):
                    concern_opts = [
                        "⚠️ Defect rate too high",
                        "⏱️ Machine downtime "
                        "excessive",
                        "🔧 Process bottlenecks",
                        "📋 Quality control gaps",
                        "🚚 Supply chain delays",
                        "🔩 Maintenance issues"]
                elif is_mkt_concern and not (
                        is_ops_concern):
                    concern_opts = [
                        "📉 Revenue declining",
                        "💸 Costs too high",
                        "👥 Losing customers/"
                        "churn",
                        "⏱️ Processes too slow",
                        "🔍 Cannot identify "
                        "best customers",
                        "📢 Marketing not "
                        "effective"]
                else:
                    # Both or neither —
                    # show combined list
                    concern_opts = [
                        "📉 Revenue declining",
                        "⚠️ Defect rate too high",
                        "💸 Costs too high",
                        "👥 Losing customers/"
                        "churn",
                        "⏱️ Machine downtime "
                        "excessive",
                        "🔧 Process bottlenecks",
                        "🔍 Cannot identify "
                        "best customers",
                        "📢 Marketing not "
                        "effective"]

                concern_primary = st.selectbox(
                    "Q2: PRIMARY concern:",
                    concern_opts)

                concern_secondary = st.selectbox(
                    "Q2: SECONDARY concern:",
                    ["None"] + concern_opts)

            with col2:
                # Q3 — adaptive based on
                # concern selections
                if is_ops_concern and not (
                        is_mkt_concern):
                    dept_opts = [
                        "🏭 Production / "
                        "Manufacturing",
                        "🔍 Quality Control",
                        "🔧 Maintenance",
                        "🚚 Supply Chain",
                        "🏢 All equally"]
                elif is_mkt_concern and not (
                        is_ops_concern):
                    dept_opts = [
                        "📊 Sales & Marketing",
                        "⚙️ Operations",
                        "💹 Finance & Cost "
                        "Control",
                        "🤝 Customer Service",
                        "🏢 All equally"]
                else:
                    dept_opts = [
                        "📊 Sales & Marketing",
                        "🏭 Production / "
                        "Manufacturing",
                        "🔍 Quality Control",
                        "⚙️ Operations",
                        "💹 Finance & Cost "
                        "Control",
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
                        "OPT-Q3: Current "
                        "digital tools?",
                        ["Not answered",
                         "None — paper / "
                         "fax based",
                         "Basic spreadsheets"
                         " (Excel / "
                         "Google Sheets)",
                         "ERP system (SAP/"
                         "Oracle/Kintone/"
                         "Freee/弥生)",
                         "CRM system "
                         "(Salesforce/"
                         "HubSpot/Zoho)",
                         "MES / SCADA "
                         "(factory systems)",
                         "BI / Analytics "
                         "(Tableau/Power BI"
                         "/Looker)",
                         "AI / Advanced "
                         "Analytics",
                         "Mixed — several "
                         "of the above"])

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
            if concern_marketing:
                if st.button(
                    "🔬 Run Marketing Dokku + "
                    "Generate DXPO Report!!",
                    type="primary",
                    use_container_width=True):
                    st.session_state.run_analysis = True

            if proceed_to_ops:
                if st.button(
                    "🏭 Run Operations/Quality "
                    "Dokku + Generate DXPO "
                    "Report!!",
                    type="primary",
                    use_container_width=True):
                    st.session_state.run_ops_analysis = True

            if concern_marketing and (
                st.session_state.get(
                'run_analysis', False)):

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

            # ══════════════════════════════════
            # OPERATIONS / QUALITY DOKKU
            # ══════════════════════════════════
            if proceed_to_ops and (
                st.session_state.get(
                'run_ops_analysis', False)):

                with st.spinner(
                    "🏭 Analyzing your "
                    "production data..."):

                    odf = ops_df.copy()
                    on = len(odf)

                    # ── Column detection ──
                    machine_col = None
                    defect_col = None
                    downtime_col = None
                    temp_col = None
                    maint_col = None
                    shift_col_name = None
                    produced_col = None

                    for c in odf.columns:
                        cl = c.lower()
                        if 'machine' in cl:
                            machine_col = c
                        elif 'defect' in cl and (
                                'rate' in cl):
                            defect_col = c
                        elif 'downtime' in cl:
                            downtime_col = c
                        elif 'temp' in cl:
                            temp_col = c
                        elif 'maintenance' in cl:
                            maint_col = c
                        elif 'shift' in cl:
                            shift_col_name = c
                        elif 'produced' in cl:
                            produced_col = c

                    ops_pain_points = []

                    # TEST O1: Defect Rate
                    # by Machine
                    if machine_col and defect_col:
                        by_mach = (
                            odf.groupby(
                                machine_col)[
                                defect_col]
                            .mean()
                            .sort_values(
                                ascending=False))
                        worst_mach = (
                            by_mach.index[0])
                        worst_rate = (
                            by_mach.iloc[0])
                        avg_rate = (
                            odf[defect_col]
                            .mean())
                        flag = (
                            "🔴 RED" if
                            worst_rate > 10 else
                            "🟡 YELLOW" if
                            worst_rate > 5 else
                            "🟢 GREEN")
                        ops_pain_points.append({
                            "test":
                            "Defect Rate by "
                            "Machine",
                            "finding":
                            f"Machine "
                            f"{worst_mach} has "
                            f"the highest "
                            f"average defect "
                            f"rate at "
                            f"{worst_rate:.1f}%, "
                            f"vs overall "
                            f"average of "
                            f"{avg_rate:.1f}%.",
                            "flag": flag})

                    # TEST O2: Downtime
                    # by Shift
                    if (shift_col_name and
                            downtime_col):
                        by_shift = (
                            odf.groupby(
                                shift_col_name)[
                                downtime_col]
                            .mean()
                            .sort_values(
                                ascending=False))
                        worst_shift = (
                            by_shift.index[0])
                        worst_dt = (
                            by_shift.iloc[0])
                        avg_dt = (
                            odf[downtime_col]
                            .mean())
                        flag = (
                            "🔴 RED" if
                            worst_dt > 60 else
                            "🟡 YELLOW" if
                            worst_dt > 30 else
                            "🟢 GREEN")
                        ops_pain_points.append({
                            "test":
                            "Downtime by "
                            "Shift",
                            "finding":
                            f"{worst_shift} "
                            f"shift averages "
                            f"{worst_dt:.0f} "
                            f"minutes of "
                            f"downtime, vs "
                            f"overall average "
                            f"of {avg_dt:.0f} "
                            f"minutes.",
                            "flag": flag})

                    # TEST O3: Temperature
                    # correlation with
                    # defects
                    if temp_col and defect_col:
                        corr = (
                            odf[[temp_col,
                                 defect_col]]
                            .corr()
                            .iloc[0,1])
                        flag = (
                            "🔴 RED" if
                            corr > 0.6 else
                            "🟡 YELLOW" if
                            corr > 0.3 else
                            "🟢 GREEN")
                        ops_pain_points.append({
                            "test":
                            "Temperature / "
                            "Defect "
                            "Correlation",
                            "finding":
                            f"Operating "
                            f"temperature and "
                            f"defect rate show "
                            f"a correlation of "
                            f"{corr:.2f} "
                            f"(1.0 = perfect "
                            f"link). Higher "
                            f"values suggest "
                            f"temperature "
                            f"control may be "
                            f"contributing to "
                            f"quality issues.",
                            "flag": flag})

                    # TEST O4: Maintenance
                    # Flag Frequency
                    if maint_col:
                        maint_pct = (
                            (odf[maint_col]
                             =='YES').sum()
                            / on * 100)
                        flag = (
                            "🔴 RED" if
                            maint_pct > 20 else
                            "🟡 YELLOW" if
                            maint_pct > 10 else
                            "🟢 GREEN")
                        ops_pain_points.append({
                            "test":
                            "Maintenance "
                            "Flag Frequency",
                            "finding":
                            f"{maint_pct:.1f}% "
                            f"of production "
                            f"records were "
                            f"flagged for "
                            f"maintenance "
                            f"attention — "
                            f"worth reviewing "
                            f"preventive "
                            f"maintenance "
                            f"scheduling.",
                            "flag": flag})

                    # TEST O5: Overall
                    # Production Volume
                    if produced_col:
                        total_units = (
                            odf[produced_col]
                            .sum())
                        avg_units = (
                            odf[produced_col]
                            .mean())
                        ops_pain_points.append({
                            "test":
                            "Production "
                            "Volume Overview",
                            "finding":
                            f"Total units "
                            f"produced: "
                            f"{total_units:,.0f}"
                            f" across "
                            f"{on:,} records "
                            f"(avg "
                            f"{avg_units:.0f} "
                            f"units/record).",
                            "flag":
                            "🟢 GREEN"})

                    # ── SHOW RESULTS ──
                    st.markdown("---")
                    st.subheader(
                        "🏭 Step 3 — "
                        "Operations/Quality "
                        "Dokku Results")

                    red_o = [p for p in
                        ops_pain_points
                        if 'RED' in p['flag']]
                    yel_o = [p for p in
                        ops_pain_points
                        if 'YELLOW' in
                        p['flag']]

                    oc1,oc2,oc3 = st.columns(3)
                    with oc1:
                        st.metric(
                            "Total Pain Points",
                            len(ops_pain_points))
                    with oc2:
                        st.metric(
                            "🔴 Critical",
                            len(red_o))
                    with oc3:
                        st.metric(
                            "🟡 Watch",
                            len(yel_o))

                    why_ops = {
                        "Defect Rate by "
                        "Machine":
                        "Standard test — "
                        "identifies which "
                        "machine is driving "
                        "quality issues!!",
                        "Downtime by Shift":
                        "Standard test — "
                        "identifies "
                        "operational "
                        "inefficiency "
                        "patterns by shift"
                        "!!",
                        "Temperature / "
                        "Defect Correlation":
                        "Standard test — "
                        "checks if "
                        "environmental "
                        "factors are "
                        "linked to defects"
                        "!!",
                        "Maintenance Flag "
                        "Frequency":
                        "Standard test — "
                        "flags how often "
                        "equipment needs "
                        "attention!!",
                        "Production Volume "
                        "Overview":
                        "Standard test — "
                        "baseline context "
                        "for production "
                        "capacity!!"
                    }

                    ops_test_labels = {
                        "Defect Rate by "
                        "Machine": "O-TEST 1",
                        "Downtime by "
                        "Shift": "O-TEST 2",
                        "Temperature / "
                        "Defect "
                        "Correlation":
                        "O-TEST 3",
                        "Maintenance Flag "
                        "Frequency":
                        "O-TEST 4",
                        "Production Volume "
                        "Overview":
                        "O-TEST 5"
                    }

                    for p in ops_pain_points:
                        icon = (
                            "🔴" if 'RED' in
                            p['flag'] else
                            "🟡" if 'YELLOW'
                            in p['flag'] else
                            "🟢")
                        label = (
                            ops_test_labels
                            .get(p['test'],
                            "O-TEST"))
                        urgency_ops = (
                            "🚨 Immediate "
                            "attention needed"
                            if 'RED' in
                            p['flag'] else
                            "⚠️ Monitor "
                            "closely"
                            if 'YELLOW' in
                            p['flag'] else
                            "✅ Healthy — "
                            "maintain "
                            "current practice")

                        with st.expander(
                            f"{icon} "
                            f"{label}: "
                            f"{p['test']} — "
                            f"{p['flag']}",
                            expanded=True):

                            ecol1, ecol2 = (
                                st.columns(2))
                            with ecol1:
                                st.markdown(
                                    "**📋 "
                                    "Finding:**")
                                st.write(
                                    p['finding'])
                                st.markdown(
                                    "**🎯 "
                                    "Urgency:**")
                                st.write(
                                    urgency_ops)
                            with ecol2:
                                st.markdown(
                                    "**❓ Why "
                                    "Tested:**")
                                st.write(
                                    why_ops.get(
                                    p['test'],
                                    "Standard "
                                    "test."))

                            st.markdown(
                                "**📊 "
                                "Statistical "
                                "Note:**")
                            if p['test'] == (
                                "Defect Rate "
                                "by Machine"):
                                st.write(
                                    "Threshold:"
                                    " >10% avg "
                                    "defect rate"
                                    " = 🔴 RED · "
                                    ">5% = 🟡 "
                                    "YELLOW · "
                                    "≤5% = 🟢 "
                                    "GREEN")
                                if (machine_col
                                        and
                                        defect_col):
                                    by_m = (
                                        odf
                                        .groupby(
                                        machine_col
                                        )[defect_col]
                                        .mean()
                                        .sort_values(
                                        ascending=
                                        False))
                                    st.write(
                                        "Your "
                                        "rates: " +
                                        ", ".join(
                                        f"{m}: "
                                        f"{r:.1f}%"
                                        for m,r
                                        in by_m
                                        .items()))
                            elif p['test'] == (
                                "Downtime by "
                                "Shift"):
                                st.write(
                                    "Threshold:"
                                    " >60 min "
                                    "avg = 🔴 "
                                    "RED · >30 "
                                    "min = 🟡 "
                                    "YELLOW · "
                                    "≤30 min = "
                                    "🟢 GREEN")
                                if (shift_col_name
                                        and
                                        downtime_col):
                                    by_s = (
                                        odf
                                        .groupby(
                                        shift_col_name
                                        )[downtime_col]
                                        .mean()
                                        .sort_values(
                                        ascending=
                                        False))
                                    st.write(
                                        "Your "
                                        "rates: " +
                                        ", ".join(
                                        f"{s}: "
                                        f"{d:.0f}"
                                        " min"
                                        for s,d
                                        in by_s
                                        .items()))
                            elif p['test'] == (
                                "Temperature "
                                "/ Defect "
                                "Correlation"):
                                st.write(
                                    "Threshold:"
                                    " correlation"
                                    " >0.6 = 🔴 "
                                    "RED · >0.3"
                                    " = 🟡 "
                                    "YELLOW · "
                                    "≤0.3 = 🟢 "
                                    "GREEN")
                                if (temp_col
                                        and
                                        defect_col):
                                    corr_val = (
                                        odf[[
                                        temp_col,
                                        defect_col
                                        ]].corr()
                                        .iloc[0,1])
                                    corr_str = (
                                        f"{corr_val:.2f}")
                                    st.write(
                                        "Your "
                                        "correlation"
                                        ": " +
                                        corr_str)
                            elif p['test'] == (
                                "Maintenance "
                                "Flag "
                                "Frequency"):
                                st.write(
                                    "Threshold:"
                                    " >20% "
                                    "flagged = "
                                    "🔴 RED · "
                                    ">10% = 🟡 "
                                    "YELLOW · "
                                    "≤10% = 🟢 "
                                    "GREEN")
                                if maint_col:
                                    m_pct = (
                                        (odf[
                                        maint_col]
                                        == 'YES')
                                        .sum() /
                                        on * 100)
                                    m_pct_str = (
                                        f"{m_pct:.1f}%")
                                    st.write(
                                        "Your "
                                        "rate: " +
                                        m_pct_str)
                            elif p['test'] == (
                                "Production "
                                "Volume "
                                "Overview"):
                                st.write(
                                    "Informational"
                                    " — no fixed "
                                    "threshold. "
                                    "Baseline "
                                    "context for "
                                    "capacity "
                                    "planning.")

                    st.markdown("---")
                    st.markdown(
                        "### 📊 "
                        "Operations/Quality "
                        "Dokku — Complete "
                        "Test Results")
                    ops_table_rows = (
                        [[p['test'],
                          'Standard',
                          p['finding'],
                          p['flag']]
                         for p in
                         ops_pain_points])
                    if ops_table_rows:
                        ops_fig = go.Figure(
                            data=[go.Table(
                            header=dict(
                                values=[
                                "Test","Type",
                                "Finding",
                                "Status"],
                                fill_color=
                                '#1F4E79',
                                font=dict(
                                    color=
                                    'white',
                                    size=12),
                                align='left'),
                            cells=dict(
                                values=list(
                                    zip(
                                    *ops_table_rows)),
                                fill_color=
                                'lavender',
                                align='left'))
                        ])
                        ops_fig.update_layout(
                            height=300)
                        st.plotly_chart(
                            ops_fig,
                            use_container_width=
                            True)

                    st.markdown("---")

                    # ── OPS STEP 4: IMPACT ──
                    st.subheader(
                        "🎯 Step 4 — "
                        "DXPO Impact Evaluation")
                    st.caption(
                        "Figure 4 · "
                        "Dr. Jay Rajasekera · "
                        "APO Framework · Springer")
                    st.info(
                        "Rate each pain point "
                        "found in your "
                        "Operations/Quality "
                        "data. Your DX team "
                        "decides — not the AI!!")

                    ops_impact_scores = []
                    for oi, op in enumerate(
                            ops_pain_points, 1):
                        st.write(
                            f"**{op['flag']} "
                            f"{op['test']}**")
                        ocol1, ocol2 = (
                            st.columns(2))
                        with ocol1:
                            oa = st.slider(
                                "A — Customer "
                                "Value",
                                1, 10, 7,
                                key=
                                f"ops_a_{oi}")
                        with ocol2:
                            ob = st.slider(
                                "B — "
                                "Implementation"
                                " Potential",
                                1, 10, 5,
                                key=
                                f"ops_b_{oi}")
                        ops_impact_scores.append(
                            {
                            "pain_point":
                                op['test'],
                            "finding":
                                op['finding'],
                            "flag":
                                op['flag'],
                            "A": oa,
                            "B": ob,
                            "impact": oa*ob
                            })
                        st.write(
                            "Impact = "
                            f"{oa} × {ob} = "
                            f"**{oa*ob}**")
                        st.markdown("---")

                    ops_impact_scores.sort(
                        key=lambda x:
                        x['impact'],
                        reverse=True)
                    for oi, op in enumerate(
                            ops_impact_scores,
                            1):
                        op['rank'] = oi

                    # Impact Table
                    o_processes = [
                        p['pain_point']
                        for p in
                        ops_impact_scores]
                    o_a_vals = [
                        p['A'] for p in
                        ops_impact_scores]
                    o_b_vals = [
                        p['B'] for p in
                        ops_impact_scores]
                    o_impacts = [
                        p['impact'] for p in
                        ops_impact_scores]
                    o_ranks = [
                        f"#{p['rank']}"
                        for p in
                        ops_impact_scores]
                    o_colors = [
                        '#2ECC71' if i>=70
                        else '#F39C12'
                        if i>=50 else
                        '#E74C3C'
                        for i in o_impacts]

                    ofig2 = go.Figure(
                        data=[go.Table(
                        columnwidth=[
                            260,70,70,90,70],
                        header=dict(
                            values=[
                            '<b>Process</b>',
                            '<b>A</b>',
                            '<b>B</b>',
                            '<b>Impact</b>',
                            '<b>Rank</b>'],
                            fill_color=
                            '#1B3A6B',
                            font=dict(
                                color='white',
                                size=12),
                            align='center',
                            height=45),
                        cells=dict(
                            values=[
                            o_processes,
                            o_a_vals,
                            o_b_vals,
                            o_impacts,
                            o_ranks],
                            fill_color=[
                            ['#F8F9FA']*
                            len(o_processes),
                            ['#EBF5FB']*
                            len(o_processes),
                            ['#EBF5FB']*
                            len(o_processes),
                            o_colors,
                            ['#F8F9FA']*
                            len(o_processes)],
                            font=dict(
                                color=[
                                ['#1B3A6B']*
                                len(
                                o_processes),
                                ['#1B3A6B']*
                                len(
                                o_processes),
                                ['#1B3A6B']*
                                len(
                                o_processes),
                                ['white']*
                                len(
                                o_processes),
                                ['#1B3A6B']*
                                len(
                                o_processes)],
                                size=12),
                            align='center',
                            height=38))])

                    ofig2.update_layout(
                        title=dict(
                            text=
                            '🎯 DXPO Impact '
                            'Table · '
                            'Dr. Jay '
                            'Rajasekera',
                            x=0.5,
                            font=dict(
                                size=14,
                                color=
                                '#1B3A6B')),
                        height=300,
                        margin=dict(
                            l=10,r=10,
                            t=60,b=10))

                    st.plotly_chart(
                        ofig2,
                        use_container_width=
                        True)

                    ofig2.write_html(
                        'ops_impact.html')
                    with open(
                        'ops_impact.html',
                        'rb') as f_html:
                        st.download_button(
                            "📥 Download "
                            "Impact Table",
                            f_html,
                            "DXPO_Ops_"
                            "ImpactTable"
                            ".html",
                            use_container_width
                            =True)

                    st.markdown("---")

                    # ── OPS STEP 5: REPORT ──
                    st.subheader(
                        "🪄 Step 5 — "
                        "DXPO Report")
                    st.caption(
                        "Operations/Quality "
                        "Edition")

                    ops_summary = (
                        "Industry: " +
                        industry + "\n"
                        "Company type: " +
                        company_type + "\n"
                        "Primary concern: " +
                        concern_primary + "\n"
                        "Pain points found: "
                        + str(len(
                        ops_pain_points))
                        + "\n")
                    for op in (
                            ops_impact_scores):
                        ops_summary += (
                            "#" +
                            str(op['rank']) +
                            " " +
                            op['pain_point'] +
                            ": Impact=" +
                            str(op['impact'])
                            + "/100\n")

                    try:
                        api_key = (
                            os.environ.get(
                            "ANTHROPIC_"
                            "API_KEY", ""))
                        client = (
                            anthropic
                            .Anthropic(
                            api_key=api_key))
                        ops_msg = (
                            client.messages
                            .create(
                            model=
                            "claude-opus-4-5",
                            max_tokens=1500,
                            messages=[{
                                "role":
                                "user",
                                "content":
                                "You are DXPO"
                                " AI Magic Box"
                                " by Dr. Jay "
                                "Rajasekera, "
                                "Tokyo "
                                "International"
                                " University."
                                "\n\nGenerate "
                                "a professional"
                                " DXPO report "
                                "for an "
                                "Operations/"
                                "Quality DX "
                                "diagnostic:\n"
                                + ops_summary
                                + "\n\nInclude:"
                                "\n1. EXECUTIVE"
                                " SUMMARY"
                                "\n2. TOP "
                                "OPERATIONAL "
                                "PAIN POINTS"
                                "\n3. RECOMMENDED"
                                " DX APPROACH"
                                "\n4. QUICK WINS"
                                " (30 days)"
                                "\n5. STRATEGIC"
                                " ROADMAP "
                                "(6 months)"}
                            ]))
                        ops_report = (
                            ops_msg
                            .content[0]
                            .text)
                    except Exception as e:
                        ops_report = (
                            "Error generating"
                            " report: " +
                            str(e))

                    st.markdown(ops_report)
                    st.download_button(
                        "📥 Download "
                        "DXPO Operations "
                        "Report",
                        ops_report,
                        "DXPO_Ops_"
                        "Report.txt",
                        use_container_width=
                        True)

                    st.success(
                        "✅ Operations/"
                        "Quality analysis "
                        "complete!!")
                    st.balloons()

            # End of Operations Dokku block

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.write(str(e))

st.markdown("---")
st.caption(
    "🪄 DXPO AI Magic Box | "
    "Dr. Jay Rajasekera | "
    "Tokyo International University | "
    "Powered by Claude AI")
