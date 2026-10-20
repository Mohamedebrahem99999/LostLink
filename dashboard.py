import json
import re
from pathlib import Path
from datetime import date, datetime
import html

import altair as alt
import pandas as pd
import streamlit as st

from constants import Email_REGEX, PHONE_REGEX


BASE_DIR = Path(__file__).resolve().parent
ITEMS_FILE = BASE_DIR / "items.json"
USERS_FILE = BASE_DIR / "users.json"

st.set_page_config(
    page_title="LostLink | Campus Recovery",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#0B1120"
CYAN = "#38BDF8"


# =========================================================
# JSON HELPERS
# =========================================================

def load_json(path):
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError):
        return {}


def save_json(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def next_id(data):
    nums = []

    for key in data:
        try:
            nums.append(int(key))
        except (ValueError, TypeError):
            pass

    return str(max(nums, default=0) + 1)


def normalize_status(item):
    if item.get("status"):
        return str(item["status"]).strip().lower()

    return "open" if item.get("is_open", True) else "closed"


def item_records():
    items = load_json(ITEMS_FILE)
    rows = []

    for item_id, item in items.items():
        if not isinstance(item, dict):
            continue

        row = dict(item)
        row["item_id"] = str(item_id)
        row["status"] = normalize_status(item)

        row.setdefault("name", "Unnamed item")
        row.setdefault("category", "other")
        row.setdefault("location", "Not specified")
        row.setdefault("report_type", "lost")
        row.setdefault("date", "")
        row.setdefault("description", "")
        row.setdefault("color", "Not specified")

        rows.append(row)

    return rows


def user_by_email(email):
    users = load_json(USERS_FILE)
    email = email.strip().lower()

    for user_id, user in users.items():
        if not isinstance(user, dict):
            continue

        if str(user.get("email", "")).strip().lower() == email:
            return user_id, user

    return None, None


def safe_text(value):
    return html.escape(str(value if value is not None else ""))


# =========================================================
# VALIDATION HELPERS
# =========================================================

def valid_email(email):
    """Validate email using the existing constants.py rule."""
    email = email.strip()

    if not email:
        return False

    return bool(re.fullmatch(Email_REGEX, email, re.IGNORECASE))


def valid_phone(phone):
    """
    Phone is optional.
    If provided, it must match the existing Egyptian phone pattern.
    """
    phone = phone.strip()

    if not phone:
        return True

    return bool(re.fullmatch(PHONE_REGEX, phone))


def valid_report_date(report_date):
    """Accept a date or ISO date string, but reject future dates."""
    try:
        if isinstance(report_date, datetime):
            parsed_date = report_date.date()
        elif isinstance(report_date, date):
            parsed_date = report_date
        else:
            parsed_date = datetime.strptime(
                str(report_date).strip(), "%Y-%m-%d"
            ).date()

        return parsed_date <= date.today()

    except (ValueError, TypeError):
        return False


def valid_report_fields(
    name,
    category,
    location,
    report_date,
    report_type,
    color,
    description,
):
    required_values = [
        name,
        category,
        location,
        color,
        description,
    ]

    all_required = all(
        isinstance(value, str) and bool(value.strip())
        for value in required_values
    )

    return (
        all_required
        and report_type in ("lost", "found")
        and valid_report_date(report_date)
        and 5 <= len(description.strip()) <= 300
    )


# =========================================================
# STYLING
# =========================================================

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root { color-scheme: dark; }

    html, body, .stApp, [data-testid="stAppViewContainer"] {
      background: radial-gradient(ellipse at 90% 0%, rgba(56,189,248,.12), transparent 35%),
                  linear-gradient(145deg,#080D19 0%,#0B1120 60%,#0C1728 100%) !important;
      color: #F8FAFC !important;
      font-family: Inter, "Segoe UI", sans-serif !important;
    }

    [data-testid="stHeader"] {
      background: rgba(8,13,25,.88) !important;
      border-bottom: 1px solid rgba(56,189,248,.12);
      backdrop-filter: blur(14px);
    }

    .block-container {
      max-width:1500px;
      padding-top:2rem;
      padding-bottom:3rem;
    }

    [data-testid="stSidebar"] {
      background:linear-gradient(180deg,#080E1A 0%,#0B1425 100%) !important;
      border-right:1px solid rgba(56,189,248,.18);
    }

    [data-testid="stSidebar"] * { color:#F1F5F9; }

    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] .stMarkdown p {
      color:#A7B7CC;
    }

    .brand {
      padding:1.2rem;
      margin-bottom:1rem;
      border:1px solid rgba(56,189,248,.25);
      border-radius:18px;
      background:linear-gradient(140deg,rgba(56,189,248,.15),rgba(15,23,42,.4));
    }

    .brand-kicker {
      font-size:.65rem;
      font-weight:800;
      letter-spacing:.16em;
      color:#7DD3FC;
    }

    .brand-name {
      font-size:2rem;
      font-weight:800;
      letter-spacing:-.06em;
      color:#F8FAFC;
      margin:.25rem 0;
    }

    .brand-sub {
      font-size:.76rem;
      color:#B6C5D8;
    }

    .hero {
      padding:1.1rem 0 1.4rem 1.2rem;
      border-left:3px solid #38BDF8;
      margin-bottom:1.3rem;
    }

    .hero h1 {
      font-size:clamp(2rem,4vw,3rem);
      font-weight:800;
      letter-spacing:-.06em;
      line-height:1.1;
      margin:0 0 .6rem;
      color:#F8FAFC;
    }

    .hero p {
      color:#B6C5D8;
      line-height:1.7;
      margin:0;
      max-width:760px;
    }

    .eyebrow {
      color:#7DD3FC;
      font-size:.68rem;
      font-weight:800;
      letter-spacing:.16em;
      text-transform:uppercase;
    }

    .metric {
      background:linear-gradient(145deg,#192D46,#101D31);
      border:1px solid rgba(148,163,184,.22);
      border-radius:18px;
      padding:1.1rem 1.2rem;
      min-height:130px;
      position:relative;
      overflow:hidden;
      box-shadow:0 10px 28px rgba(0,0,0,.16);
    }

    .metric:before {
      content:"";
      position:absolute;
      top:0;
      left:1rem;
      right:1rem;
      height:2px;
      background:linear-gradient(90deg,transparent,#38BDF8,transparent);
    }

    .metric-label {
      font-size:.72rem;
      font-weight:700;
      letter-spacing:.07em;
      color:#C0D0E2;
      text-transform:uppercase;
    }

    .metric-value {
      font-size:2rem;
      font-weight:800;
      letter-spacing:-.05em;
      color:#FFFFFF;
      margin:.45rem 0 .25rem;
    }

    .metric-hint {
      font-size:.75rem;
      color:#A5B6CB;
    }

    .item-card {
      height:100%;
      padding:1.1rem;
      background:linear-gradient(145deg,#17263D,#101B2D);
      border:1px solid rgba(148,163,184,.2);
      border-radius:17px;
      transition:all .18s ease;
      box-shadow:0 8px 24px rgba(0,0,0,.12);
    }

    .item-card:hover {
      border-color:rgba(56,189,248,.65);
      transform:translateY(-2px);
    }

    .item-title {
      font-size:1.08rem;
      font-weight:750;
      color:#F8FAFC;
      margin:.5rem 0;
    }

    .item-meta {
      color:#C0CDDD;
      font-size:.82rem;
      line-height:1.8;
    }

    .pill {
      display:inline-block;
      padding:.25rem .55rem;
      margin-right:.2rem;
      border-radius:999px;
      font-size:.66rem;
      font-weight:800;
      letter-spacing:.05em;
      text-transform:uppercase;
      background:rgba(56,189,248,.16);
      border:1px solid rgba(56,189,248,.32);
      color:#BAE6FD;
    }

    .pill-lost {
      background:rgba(251,191,36,.13);
      border-color:rgba(251,191,36,.32);
      color:#FDE68A;
    }

    .pill-found {
      background:rgba(52,211,153,.13);
      border-color:rgba(52,211,153,.32);
      color:#A7F3D0;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
      background:linear-gradient(145deg,rgba(23,38,61,.96),rgba(14,25,43,.98));
      border:1px solid rgba(148,163,184,.2) !important;
      border-radius:17px !important;
    }

    .stButton button,
    [data-testid="stFormSubmitButton"] button {
      border-radius:10px;
      border:1px solid rgba(56,189,248,.45);
      background:linear-gradient(135deg,#0891B2,#0E7490);
      color:#FFFFFF !important;
      font-weight:700;
      transition:all .18s ease;
    }

    .stButton button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
      border-color:#7DD3FC;
      background:linear-gradient(135deg,#0E7490,#155E75);
      box-shadow:0 0 0 3px rgba(56,189,248,.13);
      color:#FFFFFF !important;
    }

    input, textarea, [data-baseweb="select"] > div,
    [data-testid="stDateInput"] input {
      background:#111C2E !important;
      border-color:#344963 !important;
      border-radius:10px !important;
      color:#F8FAFC !important;
    }

    input::placeholder, textarea::placeholder {
      color:#9AAEC4 !important;
    }

    [data-baseweb="popover"], [data-baseweb="menu"],
    [role="listbox"] {
      background:#152238 !important;
      color:#F8FAFC !important;
    }

    [role="option"] { color:#F8FAFC !important; }
    [role="option"]:hover { background:#1E3A5F !important; }

    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label {
      color:#E2E8F0 !important;
    }

    [data-testid="stDataFrame"] {
      border:1px solid #344963;
      border-radius:12px;
      overflow:hidden;
    }

    [data-testid="stExpander"] {
      background:#111C2E;
      border:1px solid #344963;
      border-radius:12px;
    }

    [data-testid="stAlert"] { border-radius:12px; }

    h1,h2,h3,h4 {
      color:#F8FAFC;
      letter-spacing:-.03em;
    }

    p, li, label, .stMarkdown { color:#E2E8F0; }

    [data-testid="stCaptionContainer"] { color:#A5B6CB; }

    hr { border-color:rgba(148,163,184,.18); }

    footer { color:#94A3B8; }

    @media (max-width:768px) {
      .block-container { padding:1.2rem .85rem 2rem; }
      .hero h1 { font-size:1.8rem; }
      .metric { padding:.9rem; }
      .metric-value { font-size:1.6rem; }
    }
    </style>
    """, unsafe_allow_html=True)


inject_css()


# =========================================================
# SESSION STATE
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-kicker">CAMPUS RECOVERY</div>
      <div class="brand-name">LostLink</div>
      <div class="brand-sub">Lost & found, connected.</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.user:
        current = st.session_state.user
        st.markdown(
            f"**Welcome, {safe_text(current.get('name', 'Member'))}**"
        )
        st.caption(current.get("role", "Member"))

        page_options = [
            "Home",
            "Browse Items",
            "Report an Item",
            "My Reports",
            "My Profile",
        ]

        role = str(current.get("role", "Member")).strip().lower()

        if role in ("admin", "manager"):
            page_options += ["Admin Panel", "Analytics"]

        page = st.radio(
            "NAVIGATION",
            page_options,
            label_visibility="visible",
        )

        if st.button("Log out", use_container_width=True):
            st.session_state.user = None
            st.session_state.user_id = None
            st.rerun()

    else:
        page = "Welcome"
        st.markdown("### Find what matters.")
        st.caption(
            "Sign in to report, browse, and reconnect lost items."
        )


# =========================================================
# REUSABLE UI COMPONENTS
# =========================================================

def hero(title, subtitle, kicker="LOSTLINK PLATFORM"):
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">{safe_text(kicker)}</div>
      <h1>{safe_text(title)}</h1>
      <p>{safe_text(subtitle)}</p>
    </div>
    """, unsafe_allow_html=True)


def metric(label, value, hint):
    st.markdown(f"""
    <div class="metric">
      <div class="metric-label">{safe_text(label)}</div>
      <div class="metric-value">{safe_text(value)}</div>
      <div class="metric-hint">{safe_text(hint)}</div>
    </div>
    """, unsafe_allow_html=True)


def item_card(item):
    report_type = str(item.get("report_type", "lost")).lower()
    pill_class = "pill-lost" if report_type == "lost" else "pill-found"
    status = normalize_status(item)

    st.markdown(f"""
    <div class="item-card">
      <span class="pill {pill_class}">{safe_text(report_type)} item</span>
      <span class="pill">{safe_text(status)}</span>
      <div class="item-title">{safe_text(item.get("name", "Unnamed item"))}</div>
      <div class="item-meta">
        <b>Category:</b> {safe_text(item.get("category", "other")).title()}<br>
        <b>Color:</b> {safe_text(item.get("color", "Not specified")).title()}<br>
        <b>Location:</b> {safe_text(item.get("location", "Not specified"))}<br>
        <b>Date:</b> {safe_text(item.get("date", "Not specified"))}
      </div>
      <hr>
      <div class="item-meta">{safe_text(item.get("description", ""))}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SIGN IN AND REGISTRATION
# =========================================================

def sign_in_page():
    hero(
        "Your campus. Better connected.",
        "A simple, secure place to report lost belongings, browse found "
        "items, and help items get back to their owners.",
        "WELCOME TO LOSTLINK",
    )

    left, right = st.columns([1.05, .95], gap="large")

    with left:
        st.markdown("### A little lost. A lot more connected.")
        st.markdown(
            "Browse reports, narrow results by category and location, "
            "and submit a clear report so the community can help."
        )

        st.markdown("""
        - **Browse** recent lost and found reports
        - **Report** an item with useful details
        - **Track** report status
        - **Explore** activity insights (admins/managers)
        """)

    with right:
        with st.container(border=True):
            login_tab, register_tab = st.tabs(
                ["Sign in", "Create account"]
            )

            # -------------------------
            # LOGIN
            # -------------------------
            with login_tab:
                with st.form("login_form"):
                    email = st.text_input("Email")
                    password = st.text_input(
                        "Password",
                        type="password",
                    )

                    submitted = st.form_submit_button(
                        "Sign in",
                        use_container_width=True,
                    )

                if submitted:
                    if not email.strip() or not password:
                        st.error("Please enter your email and password.")
                    else:
                        user_id, user = user_by_email(email)

                        if user and user.get("password") == password:
                            st.session_state.user_id = user_id
                            st.session_state.user = user
                            st.rerun()
                        else:
                            st.error("Email or password is incorrect.")

            # -------------------------
            # REGISTER
            # -------------------------
            with register_tab:
                with st.form("register_form"):
                    name = st.text_input("Full name")
                    email_new = st.text_input("Email address")
                    phone = st.text_input("Phone (optional)")

                    password_new = st.text_input(
                        "Create password",
                        type="password",
                    )
                    password_confirm = st.text_input(
                        "Confirm password",
                        type="password",
                    )

                    submitted_new = st.form_submit_button(
                        "Create account",
                        use_container_width=True,
                    )

                if submitted_new:
                    users = load_json(USERS_FILE)

                    if not name.strip():
                        st.error("Please enter your full name.")

                    elif not valid_email(email_new):
                        st.error(
                            "Enter a valid Gmail address "
                            "ending with @gmail.com."
                        )

                    elif not valid_phone(phone):
                        st.error(
                            "Enter a valid Egyptian mobile number "
                            "starting with 010, 011, 012, or 015."
                        )

                    elif user_by_email(email_new)[0] is not None:
                        st.error(
                            "An account with this email already exists."
                        )

                    elif len(password_new) < 6:
                        st.error(
                            "Use a password with at least 6 characters."
                        )

                    elif password_new != password_confirm:
                        st.error("Passwords do not match.")

                    else:
                        uid = next_id(users)

                        users[uid] = {
                            "name": name.strip(),
                            "email": email_new.strip(),
                            "password": password_new,
                            "phone": phone.strip(),
                            "age": 0,
                            "gender": "",
                            "role": "Member",
                            "borrowed_items": [],
                        }

                        save_json(USERS_FILE, users)
                        st.success(
                            "Account created. You can now sign in."
                        )


# =========================================================
# APP ENTRY
# =========================================================

if not st.session_state.user:
    sign_in_page()
    st.stop()


user = st.session_state.user
all_items = item_records()
df = pd.DataFrame(all_items)


# =========================================================
# HOME
# =========================================================

if page == "Home":
    hero(
        f"Welcome back, {user.get('name', 'Member')}.",
        "A clearer view of lost and found activity across your campus.",
        "YOUR LOSTLINK SPACE",
    )

    total = len(all_items)
    open_count = sum(
        normalize_status(x) == "open" for x in all_items
    )
    lost_count = sum(
        str(x.get("report_type", "")).lower() == "lost"
        for x in all_items
    )
    found_count = sum(
        str(x.get("report_type", "")).lower() == "found"
        for x in all_items
    )

    cols = st.columns(4, gap="medium")

    with cols[0]:
        metric("Total reports", total, "All submitted reports")

    with cols[1]:
        metric("Open reports", open_count, "Still active")

    with cols[2]:
        metric("Lost items", lost_count, "Items being searched for")

    with cols[3]:
        metric("Found items", found_count, "Items reported found")

    st.write("")
    st.subheader("Recently reported")

    recent = sorted(
        all_items,
        key=lambda x: str(x.get("date", "")),
        reverse=True,
    )[:6]

    if not recent:
        st.info("No reports yet. Be the first to add one.")

    else:
        for start in range(0, len(recent), 3):
            row = st.columns(3, gap="medium")

            for col, item in zip(row, recent[start:start + 3]):
                with col:
                    item_card(item)


# =========================================================
# BROWSE ITEMS
# =========================================================

elif page == "Browse Items":
    hero(
        "Browse reports",
        "Search the current reports and filter down to the details "
        "that matter.",
        "ITEM EXPLORER",
    )

    with st.container(border=True):
        c1, c2, c3 = st.columns([1.5, 1, 1])

        with c1:
            query = st.text_input(
                "Search",
                placeholder="Name, description, color, location…",
            )

        with c2:
            type_filter = st.selectbox(
                "Report type",
                ["All", "Lost", "Found"],
            )

        with c3:
            status_filter = st.selectbox(
                "Status",
                ["All", "Open", "Matched", "Claimed", "Closed"],
            )

        categories = sorted({
            str(x.get("category", "other")).title()
            for x in all_items
        })

        locations = sorted({
            str(x.get("location", "Not specified"))
            for x in all_items
        })

        f1, f2 = st.columns(2)

        with f1:
            category_filter = st.multiselect(
                "Category",
                categories,
            )

        with f2:
            location_filter = st.multiselect(
                "Location",
                locations,
            )

    results = []

    for item in all_items:
        searchable = " ".join(
            str(item.get(k, ""))
            for k in [
                "name",
                "description",
                "color",
                "location",
                "category",
                "keywords",
            ]
        ).lower()

        if query and query.lower() not in searchable:
            continue

        if (
            type_filter != "All"
            and str(item.get("report_type", "")).lower()
            != type_filter.lower()
        ):
            continue

        if (
            status_filter != "All"
            and normalize_status(item) != status_filter.lower()
        ):
            continue

        if (
            category_filter
            and str(item.get("category", "other")).title()
            not in category_filter
        ):
            continue

        if (
            location_filter
            and str(item.get("location", "Not specified"))
            not in location_filter
        ):
            continue

        results.append(item)

    st.caption(f"{len(results)} report(s) found")

    if results:
        for start in range(0, len(results), 3):
            row = st.columns(3, gap="medium")

            for col, item in zip(row, results[start:start + 3]):
                with col:
                    item_card(item)

    else:
        st.info("No reports match these filters.")


# =========================================================
# REPORT AN ITEM
# =========================================================

elif page == "Report an Item":
    hero(
        "Report an item",
        "Share clear details to help the right item find its way back.",
        "NEW REPORT",
    )

    with st.container(border=True):
        with st.form("report_form", clear_on_submit=True):
            a, b = st.columns(2)

            with a:
                report_type = st.selectbox(
                    "Report type",
                    ["lost", "found"],
                )

                name = st.text_input(
                    "Item name",
                    placeholder="e.g. Black leather wallet",
                )

                category = st.selectbox(
                    "Category",
                    [
                        "phone",
                        "wallet",
                        "keys",
                        "bag",
                        "document",
                        "electronics",
                        "clothing",
                        "other",
                    ],
                )

                color = st.text_input(
                    "Color",
                    placeholder="e.g. Black",
                )

            with b:
                location = st.text_input(
                    "Location",
                    placeholder="Where was it lost or found?",
                )

                report_date = st.date_input(
                    "Date",
                    value=date.today(),
                    max_value=date.today(),
                )

                status = st.selectbox(
                    "Status",
                    ["open", "matched", "claimed", "closed"],
                    index=0,
                )

            description = st.text_area(
                "Description",
                placeholder="Add identifying details (5–300 characters).",
                max_chars=300,
            )

            submitted = st.form_submit_button(
                "Submit report",
                use_container_width=True,
            )

        if submitted:
            if not valid_report_fields(
                name=name,
                category=category,
                location=location,
                report_date=report_date,
                report_type=report_type,
                color=color,
                description=description,
            ):
                st.error(
                    "Please check your report details. "
                    "Name, category, location, color, and description "
                    "are required. Description must contain 5–300 "
                    "characters, report type must be lost or found, "
                    "and the date cannot be in the future."
                )

            else:
                items = load_json(ITEMS_FILE)
                item_id = next_id(items)

                items[item_id] = {
                    "name": name.strip(),
                    "category": category,
                    "color": color.strip(),
                    "location": location.strip(),
                    "date": report_date.isoformat(),
                    "description": description.strip(),
                    "keywords": list(
                        dict.fromkeys(
                            (
                                name + " " + description
                            ).lower().split()
                        )
                    ),
                    "related_user": st.session_state.user_id,
                    "report_type": report_type,
                    "is_open": status == "open",
                    "status": status,
                }

                save_json(ITEMS_FILE, items)

                st.success(
                    f"Report submitted successfully. Report ID: {item_id}"
                )
                st.rerun()


# =========================================================
# MY REPORTS
# =========================================================

elif page == "My Reports":
    hero(
        "My reports",
        "Track the items you have reported and update a report "
        "when it is resolved.",
        "YOUR ACTIVITY",
    )

    my_reports = [
        item
        for item in all_items
        if str(item.get("related_user", ""))
        == str(st.session_state.user_id)
    ]

    if not my_reports:
        st.info(
            "You have not submitted any reports yet. "
            "Use ‘Report an Item’ to add one."
        )

    else:
        st.caption(
            f"{len(my_reports)} report(s) linked to your account"
        )

        for item in sorted(
            my_reports,
            key=lambda x: str(x.get("date", "")),
            reverse=True,
        ):
            item_id = str(item.get("item_id", ""))

            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    item_card(item)

                with right:
                    st.markdown(f"**Report ID:** {safe_text(item_id)}")
                    st.markdown(
                        f"**Current status:** "
                        f"{safe_text(normalize_status(item).title())}"
                    )

                    if normalize_status(item) not in ("closed", "claimed"):
                        with st.form(f"close_my_report_{item_id}"):
                            confirm = st.checkbox(
                                "I confirm this report is resolved",
                                key=f"confirm_my_{item_id}",
                            )

                            close_clicked = st.form_submit_button(
                                "Mark as resolved",
                                use_container_width=True,
                            )

                        if close_clicked:
                            if not confirm:
                                st.warning(
                                    "Please confirm before closing this report."
                                )

                            else:
                                latest_items = load_json(ITEMS_FILE)
                                latest = latest_items.get(item_id)

                                if (
                                    latest
                                    and str(
                                        latest.get("related_user", "")
                                    ) == str(st.session_state.user_id)
                                ):
                                    latest["status"] = "closed"
                                    latest["is_open"] = False

                                    save_json(ITEMS_FILE, latest_items)

                                    st.success(
                                        "Your report has been marked as resolved."
                                    )
                                    st.rerun()

                                else:
                                    st.error(
                                        "This report could not be updated. "
                                        "Refresh and try again."
                                    )


# =========================================================
# MY PROFILE
# =========================================================

elif page == "My Profile":
    hero(
        "Your profile",
        "Review your account details.",
        "ACCOUNT",
    )

    with st.container(border=True):
        st.markdown(
            f"### {safe_text(user.get('name', 'Member'))}"
        )

        st.write(f"**Email:** {user.get('email', '—')}")
        st.write(f"**Phone:** {user.get('phone') or 'Not provided'}")
        st.write(f"**Role:** {user.get('role', 'Member')}")

        with st.form("profile_form"):
            new_name = st.text_input(
                "Update name",
                value=user.get("name", ""),
            )

            new_phone = st.text_input(
                "Update phone",
                value=user.get("phone", ""),
            )

            save_profile = st.form_submit_button("Save profile")

        if save_profile:
            users = load_json(USERS_FILE)
            uid = st.session_state.user_id

            if not new_name.strip():
                st.error("Name cannot be empty.")

            elif not valid_phone(new_phone):
                st.error(
                    "Enter a valid Egyptian mobile number starting "
                    "with 010, 011, 012, or 015, or leave the field empty."
                )

            elif uid not in users:
                st.error(
                    "User account not found. Please sign in again."
                )

            elif str(
                users[uid].get("role", "Member")
            ).strip().lower() in ("admin", "manager"):
                st.info(
                    "Profile editing is disabled for admin/manager "
                    "accounts in this interface."
                )

            else:
                users[uid]["name"] = new_name.strip()
                users[uid]["phone"] = new_phone.strip()

                save_json(USERS_FILE, users)

                st.session_state.user = users[uid]

                st.success("Profile updated.")
                st.rerun()


# =========================================================
# ADMIN PANEL
# =========================================================

elif page == "Admin Panel":
    if str(user.get("role", "")).strip().lower() not in (
        "admin",
        "manager",
    ):
        st.error("You do not have permission to access this page.")
        st.stop()

    hero(
        "Admin panel",
        "Manage reports and keep the campus item records up to date.",
        "ADMINISTRATION",
    )

    items = load_json(ITEMS_FILE)

    if not items:
        st.info("No reports to manage.")

    else:
        admin_rows = []

        for iid, item in items.items():
            if not isinstance(item, dict):
                continue

            admin_rows.append({
                "ID": iid,
                "Name": item.get("name", ""),
                "Type": item.get("report_type", ""),
                "Category": item.get("category", ""),
                "Location": item.get("location", ""),
                "Status": normalize_status(item),
                "Date": item.get("date", ""),
            })

        st.dataframe(
            pd.DataFrame(admin_rows),
            use_container_width=True,
            hide_index=True,
        )

        with st.container(border=True):
            st.subheader("Update report status")

            with st.form("admin_status_form"):
                selected_id = st.selectbox(
                    "Report ID",
                    list(items.keys()),
                )

                current_status = normalize_status(items[selected_id])

                allowed_statuses = [
                    "open",
                    "matched",
                    "claimed",
                    "closed",
                ]

                new_status = st.selectbox(
                    "New status",
                    allowed_statuses,
                    index=(
                        allowed_statuses.index(current_status)
                        if current_status in allowed_statuses
                        else 0
                    ),
                )

                update_status = st.form_submit_button("Update status")

            if update_status:
                items[selected_id]["status"] = new_status
                items[selected_id]["is_open"] = new_status == "open"

                save_json(ITEMS_FILE, items)

                st.success("Report status updated.")
                st.rerun()

        with st.container(border=True):
            st.subheader("Delete report")

            with st.form("admin_delete_form"):
                delete_id = st.selectbox(
                    "Select report to delete",
                    list(items.keys()),
                    key="delete_id",
                )

                confirm_delete = st.checkbox(
                    "I understand this permanently deletes the report."
                )

                delete_submit = st.form_submit_button("Delete report")

            if delete_submit:
                if confirm_delete:
                    items.pop(delete_id, None)
                    save_json(ITEMS_FILE, items)

                    st.success("Report deleted.")
                    st.rerun()

                else:
                    st.warning("Confirm the deletion first.")

    st.write("")

    with st.container(border=True):
        st.subheader("Registered users")

        users = load_json(USERS_FILE)
        user_rows = []

        for uid, record in users.items():
            if not isinstance(record, dict):
                continue

            user_rows.append({
                "ID": uid,
                "Name": record.get("name", ""),
                "Email": record.get("email", ""),
                "Role": record.get("role", "Member"),
                "Phone": record.get("phone", ""),
            })

        st.dataframe(
            pd.DataFrame(user_rows),
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# ANALYTICS
# =========================================================

elif page == "Analytics":
    if str(user.get("role", "")).strip().lower() not in (
        "admin",
        "manager",
    ):
        st.error("You do not have permission to access analytics.")
        st.stop()

    hero(
        "LostLink analytics",
        "Explore live report activity, categories, locations, and data quality.",
        "INSIGHTS CONSOLE",
    )

    analytics_df = pd.DataFrame(item_records())

    if analytics_df.empty:
        st.info("No report data is available yet.")
        st.stop()

    # Normalize values for consistent analytics without modifying JSON records.
    for column in ["category", "location", "report_type", "status"]:
        if column in analytics_df.columns:
            analytics_df[column] = (
                analytics_df[column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .str.lower()
            )

    analytics_df["date_parsed"] = pd.to_datetime(
        analytics_df.get("date", pd.Series(dtype=str)),
        errors="coerce",
    )

    with st.container(border=True):
        st.subheader("Filter analytics")

        f1, f2, f3 = st.columns(3)

        types = ["All"] + sorted(
            analytics_df["report_type"].dropna().unique().tolist()
        )

        statuses = ["All"] + sorted(
            analytics_df["status"].dropna().unique().tolist()
        )

        categories = ["All"] + sorted(
            analytics_df["category"].dropna().unique().tolist()
        )

        with f1:
            analytics_type = st.selectbox(
                "Report type",
                types,
                key="analytics_type",
            )

        with f2:
            analytics_status = st.selectbox(
                "Status",
                statuses,
                key="analytics_status",
            )

        with f3:
            analytics_category = st.selectbox(
                "Category",
                categories,
                key="analytics_category",
            )

        locations = sorted(
            analytics_df["location"].dropna().unique().tolist()
        )

        selected_locations = st.multiselect(
            "Locations",
            locations,
            default=locations,
            key="analytics_locations",
        )

        valid_dates = analytics_df["date_parsed"].dropna()

        if not valid_dates.empty:
            date_range = st.date_input(
                "Date range",
                value=(
                    valid_dates.min().date(),
                    valid_dates.max().date(),
                ),
                min_value=valid_dates.min().date(),
                max_value=valid_dates.max().date(),
                key="analytics_date_range",
            )
        else:
            date_range = ()

    filtered = analytics_df.copy()

    if analytics_type != "All":
        filtered = filtered[
            filtered["report_type"] == analytics_type
        ]

    if analytics_status != "All":
        filtered = filtered[
            filtered["status"] == analytics_status
        ]

    if analytics_category != "All":
        filtered = filtered[
            filtered["category"] == analytics_category
        ]

    filtered = filtered[
        filtered["location"].isin(selected_locations)
    ]

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range

        if start_date and end_date:
            filtered = filtered[
                filtered["date_parsed"].isna()
                | (
                    (filtered["date_parsed"] >= pd.Timestamp(start_date))
                    & (
                        filtered["date_parsed"]
                        <= (
                            pd.Timestamp(end_date)
                            + pd.Timedelta(days=1)
                            - pd.Timedelta(microseconds=1)
                        )
                    )
                )
            ]

    if filtered.empty:
        st.info("No reports match the selected filters.")
        st.stop()

    total = len(filtered)
    open_count = int((filtered["status"] == "open").sum())
    closed_count = int((filtered["status"] == "closed").sum())
    matched_count = int((filtered["status"] == "matched").sum())

    closure_rate = closed_count / total * 100 if total else 0

    k1, k2, k3, k4 = st.columns(4, gap="medium")

    with k1:
        metric("Total reports", total, "Reports in current filters")

    with k2:
        metric("Open reports", open_count, "Still awaiting resolution")

    with k3:
        metric("Matched reports", matched_count, "Potential successful matches")

    with k4:
        metric(
            "Closure rate",
            f"{closure_rate:.1f}%",
            "Closed ÷ filtered total",
        )

    chart_axis = {
        "labelColor": "#CBD5E1",
        "titleColor": "#94A3B8",
        "gridColor": "#1E3A5F",
    }

    left, right = st.columns(2, gap="large")

    with left:
        with st.container(border=True):
            st.subheader("Reports by category")

            category_data = (
                filtered["category"]
                .value_counts()
                .rename_axis("Category")
                .reset_index(name="Reports")
            )

            chart = (
                alt.Chart(category_data)
                .mark_bar(
                    cornerRadiusTopLeft=7,
                    cornerRadiusTopRight=7,
                    color="#38BDF8",
                )
                .encode(
                    x=alt.X(
                        "Category:N",
                        sort="-y",
                        axis=alt.Axis(labelAngle=-25),
                        title=None,
                    ),
                    y=alt.Y("Reports:Q", title="Reports"),
                    tooltip=["Category", "Reports"],
                )
                .properties(height=300)
                .configure(background="transparent")
                .configure_view(strokeWidth=0)
                .configure_axis(**chart_axis)
            )

            st.altair_chart(chart, use_container_width=True)

    with right:
        with st.container(border=True):
            st.subheader("Reports by status")

            status_data = (
                filtered["status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Reports")
            )

            chart2 = (
                alt.Chart(status_data)
                .mark_arc(innerRadius=65, outerRadius=110)
                .encode(
                    theta=alt.Theta("Reports:Q"),
                    color=alt.Color(
                        "Status:N",
                        legend=alt.Legend(
                            labelColor="#CBD5E1",
                            titleColor="#94A3B8",
                        ),
                    ),
                    tooltip=["Status", "Reports"],
                )
                .properties(height=300)
                .configure(background="transparent")
            )

            st.altair_chart(chart2, use_container_width=True)

    left2, right2 = st.columns(2, gap="large")

    with left2:
        with st.container(border=True):
            st.subheader("Reports by location")

            location_data = (
                filtered["location"]
                .value_counts()
                .rename_axis("Location")
                .reset_index(name="Reports")
            )

            location_chart = (
                alt.Chart(location_data)
                .mark_bar(
                    cornerRadiusEnd=6,
                    color="#22D3EE",
                )
                .encode(
                    x=alt.X("Reports:Q", title="Reports"),
                    y=alt.Y(
                        "Location:N",
                        sort="-x",
                        title=None,
                    ),
                    tooltip=["Location", "Reports"],
                )
                .properties(
                    height=max(
                        220,
                        min(420, 35 * len(location_data) + 30),
                    )
                )
                .configure(background="transparent")
                .configure_view(strokeWidth=0)
                .configure_axis(**chart_axis)
            )

            st.altair_chart(
                location_chart,
                use_container_width=True,
            )

    with right2:
        with st.container(border=True):
            st.subheader("Monthly activity")

            monthly = filtered.dropna(
                subset=["date_parsed"]
            ).copy()

            if monthly.empty:
                st.info(
                    "No valid dates are available for a monthly chart."
                )

            else:
                monthly["Month"] = (
                    monthly["date_parsed"]
                    .dt.to_period("M")
                    .astype(str)
                )

                monthly = (
                    monthly.groupby("Month", as_index=False)
                    .size()
                    .rename(columns={"size": "Reports"})
                )

                line = alt.Chart(monthly).encode(
                    x=alt.X(
                        "Month:N",
                        title=None,
                        sort=None,
                    ),
                    y=alt.Y("Reports:Q", title="Reports"),
                    tooltip=["Month", "Reports"],
                )

                trend = (
                    line.mark_area(
                        color="#38BDF8",
                        opacity=.12,
                    )
                    + line.mark_line(
                        color="#38BDF8",
                        strokeWidth=3,
                    )
                    + line.mark_circle(
                        color="#7DD3FC",
                        size=70,
                    )
                ).properties(
                    height=280
                ).configure(
                    background="transparent"
                ).configure_view(
                    strokeWidth=0
                ).configure_axis(
                    **chart_axis
                )

                st.altair_chart(
                    trend,
                    use_container_width=True,
                )

    # -------------------------
    # INSIGHTS
    # -------------------------
    with st.container(border=True):
        st.subheader("Key insights")

        category_counts = filtered["category"].value_counts()
        location_counts = filtered["location"].value_counts()

        insight_columns = st.columns(3)

        with insight_columns[0]:
            if not category_counts.empty:
                st.markdown("**Most reported category**")
                st.write(str(category_counts.index[0]).title())
                st.caption(
                    f"{int(category_counts.iloc[0])} report(s)"
                )
            else:
                st.info("No category data available.")

        with insight_columns[1]:
            if not location_counts.empty:
                st.markdown("**Most reported location**")
                st.write(str(location_counts.index[0]).title())
                st.caption(
                    f"{int(location_counts.iloc[0])} report(s)"
                )
            else:
                st.info("No location data available.")

        with insight_columns[2]:
            monthly_insights = filtered.dropna(
                subset=["date_parsed"]
            ).copy()

            if not monthly_insights.empty:
                monthly_insights["Month"] = (
                    monthly_insights["date_parsed"]
                    .dt.to_period("M")
                    .astype(str)
                )

                month_counts = monthly_insights["Month"].value_counts()

                st.markdown("**Busiest reporting month**")
                st.write(str(month_counts.index[0]))
                st.caption(
                    f"{int(month_counts.iloc[0])} report(s)"
                )
            else:
                st.info("No valid dates for monthly insights.")

    # -------------------------
    # DATA EXPLORER
    # -------------------------
    with st.container(border=True):
        st.subheader("Data explorer")

        visible_columns = [
            c for c in [
                "item_id",
                "name",
                "category",
                "location",
                "report_type",
                "status",
                "date",
                "description",
                "related_user",
            ]
            if c in filtered.columns
        ]

        st.dataframe(
            filtered[visible_columns],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download filtered reports (CSV)",
            data=filtered[visible_columns].to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="lostlink_filtered_reports.csv",
            mime="text/csv",
            use_container_width=False,
        )

    # -------------------------
    # DATA QUALITY
    # -------------------------
    with st.container(border=True):
        st.subheader("Data quality")

        quality = {
            "Missing values by field": (
                filtered[visible_columns]
                .isna()
                .sum()
                .to_dict()
            ),
            "Duplicate item IDs": (
                int(filtered["item_id"].duplicated().sum())
                if "item_id" in filtered.columns
                else 0
            ),
            "Invalid or missing dates": int(
                filtered["date_parsed"].isna().sum()
            ),
        }

        st.json(quality)
