import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Resourcing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

CORE = {
    "dark": "#1D1D1D",
    "dark_gray": "#4F5052",
    "medium_gray": "#828281",
    "light_gray": "#CCC8BD",
    "off_white": "#F8FAF9"
}

ACCENT = {
    "dark_green": "#475751",
    "medium_green": "#6D7668",
    "light_green": "#C0CEBC"
}

st.markdown(f"""
<style>
.stApp {{
    background-color: {CORE["off_white"]};
    color: {CORE["dark"]};
}}

.main-title {{
    font-size: 34px;
    font-weight: 700;
    color: {CORE["dark"]};
    margin-bottom: 4px;
}}

.subtitle {{
    font-size: 15px;
    color: {CORE["dark_gray"]};
    margin-bottom: 24px;
}}

.section-title {{
    font-size: 22px;
    font-weight: 700;
    color: {CORE["dark"]};
    margin-top: 20px;
    margin-bottom: 12px;
}}

.info-card {{
    background: white;
    border: 1px solid {CORE["light_gray"]};
    border-left: 6px solid {ACCENT["dark_green"]};
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    margin-bottom: 12px;
}}

.card-title {{
    font-size: 14px;
    font-weight: 600;
    color: {CORE["dark_gray"]};
}}

.card-value {{
    font-size: 28px;
    font-weight: 700;
    color: {CORE["dark"]};
    margin-top: 6px;
}}

[data-testid="stSidebar"] {{
    background-color: #FFFFFF;
}}
</style>
""", unsafe_allow_html=True)


def convert_availability(value):
    if pd.isna(value):
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    mapping = {
        "Full-time": 40,
        "Part-time": 20,
        "On-demand": 10
    }

    return float(mapping.get(value, 0))


def load_file(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)


def validate_columns(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        st.error(f"Missing required columns: {missing}")
        st.stop()

    return df[required_columns]


def prepare_data(data):
    data = data.copy()

    data = data.dropna(
        subset=["Name", "Role", "Availability", "Project Requirements"]
    )

    data["Name"] = data["Name"].astype(str).str.strip()
    data["Role"] = data["Role"].astype(str).str.strip()
    data["Project Requirements"] = data["Project Requirements"].astype(str).str.strip()
    data["Available Hours"] = data["Availability"].apply(convert_availability)

    return data


def role_matches_requirement(role, requirement):
    role = str(role).lower().strip()
    requirement = str(requirement).lower().strip()

    if role in requirement or requirement in role:
        return True

    role_words = set(role.replace("-", " ").split())
    requirement_words = set(requirement.replace("-", " ").split())

    return len(role_words.intersection(requirement_words)) > 0


def assign_staff(data):
    assignments = []
    risks = []
    assumptions = []

    staff_data = data[["Name", "Role", "Availability", "Available Hours"]].drop_duplicates()
    remaining_capacity = dict(zip(staff_data["Name"], staff_data["Available Hours"]))

    project_groups = data.groupby("Project Requirements")

    for project_requirement, project_df in project_groups:
        project_name = project_requirement
        required_hours = project_df["Available Hours"].sum()

        suitable_staff = staff_data[
            staff_data["Role"].apply(
                lambda role: role_matches_requirement(role, project_requirement)
            )
        ].copy()

        if suitable_staff.empty:
            suitable_staff = staff_data.copy()
            assumptions.append(
                f"No direct role match found for '{project_name}'. Assigned based on available capacity."
            )

        suitable_staff["Remaining Capacity"] = suitable_staff["Name"].map(remaining_capacity)
        suitable_staff = suitable_staff[suitable_staff["Remaining Capacity"] > 0]
        suitable_staff = suitable_staff.sort_values("Remaining Capacity", ascending=False)

        if suitable_staff.empty:
            risks.append(f"No remaining capacity available for project '{project_name}'.")
            continue

        for _, staff in suitable_staff.iterrows():
            if required_hours <= 0:
                break

            name = staff["Name"]
            available = remaining_capacity[name]

            if available <= 0:
                continue

            assigned = min(available, required_hours)

            remaining_capacity[name] -= assigned
            required_hours -= assigned

            if role_matches_requirement(staff["Role"], project_requirement):
                reason = "Direct or partial role match with project requirement"
            else:
                reason = "Assigned based on available capacity; role match unclear"

            assignments.append({
                "Project": project_name,
                "Assigned Staff": name,
                "Role": staff["Role"],
                "Assigned Hours": assigned,
                "Reason for Assignment": reason,
                "Remaining Capacity": remaining_capacity[name]
            })

        if required_hours > 0:
            risks.append(
                f"Project '{project_name}' still requires {required_hours:.0f} additional hours."
            )

    return pd.DataFrame(assignments), remaining_capacity, risks, assumptions


def build_capacity_summary(data, assignments_df):
    rows = []

    staff_data = data[["Name", "Role", "Availability", "Available Hours"]].drop_duplicates()

    for _, staff in staff_data.iterrows():
        name = staff["Name"]
        available = staff["Available Hours"]

        assigned = 0
        if not assignments_df.empty:
            assigned = assignments_df[
                assignments_df["Assigned Staff"] == name
            ]["Assigned Hours"].sum()

        remaining = available - assigned

        if remaining < 0:
            status = "Overloaded"
        elif assigned == 0:
            status = "Unassigned"
        elif remaining > 15:
            status = "Underutilized"
        else:
            status = "Balanced"

        rows.append({
            "Staff": name,
            "Role": staff["Role"],
            "Available Hours": available,
            "Assigned Hours": assigned,
            "Remaining Hours": remaining,
            "Status": status
        })

    return pd.DataFrame(rows)


def render_card(title, value):
    st.markdown(f"""
    <div class="info-card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def style_chart(fig, ax, title, xlabel=None, ylabel=None):
    ax.set_title(title, fontsize=14, fontweight="bold", color=CORE["dark"], pad=16)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11, color=CORE["dark_gray"])

    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11, color=CORE["dark_gray"])

    ax.set_facecolor(CORE["off_white"])
    fig.patch.set_facecolor(CORE["off_white"])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)

    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()

    return fig


def plot_project_hours(assignments_df):
    project_hours = assignments_df.groupby("Project", as_index=False)["Assigned Hours"].sum()

    fig, ax = plt.subplots(figsize=(11, 5))

    bars = ax.bar(
        project_hours["Project"],
        project_hours["Assigned Hours"],
        color=ACCENT["dark_green"]
    )

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.0f}h",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    return style_chart(fig, ax, "Total Assigned Hours by Project", "Project", "Hours")


def plot_capacity(capacity_df):
    fig, ax = plt.subplots(figsize=(11, 5))

    x = np.arange(len(capacity_df))
    assigned = capacity_df["Assigned Hours"]
    remaining = capacity_df["Remaining Hours"].clip(lower=0)

    ax.bar(x, assigned, label="Assigned", color=ACCENT["medium_green"])
    ax.bar(x, remaining, bottom=assigned, label="Remaining", color=ACCENT["light_green"])

    ax.set_xticks(x)
    ax.set_xticklabels(capacity_df["Staff"])
    ax.legend(frameon=False)

    return style_chart(fig, ax, "Assigned vs Remaining Staff Capacity", "Staff", "Hours")


def plot_role_coverage(assignments_df):
    role_data = assignments_df.groupby(["Project", "Role"], as_index=False)["Assigned Hours"].sum()
    pivot = role_data.pivot(index="Project", columns="Role", values="Assigned Hours").fillna(0)

    fig, ax = plt.subplots(figsize=(11, 5))
    pivot.plot(kind="bar", stacked=True, ax=ax, color=[
        ACCENT["dark_green"],
        ACCENT["medium_green"],
        ACCENT["light_green"],
        CORE["medium_gray"],
        CORE["light_gray"]
    ])

    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")

    return style_chart(fig, ax, "Role Coverage by Project", "Project", "Hours")


def plot_status_distribution(capacity_df):
    status_counts = capacity_df["Status"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        status_counts.index,
        status_counts.values,
        color=ACCENT["dark_green"]
    )

    return style_chart(fig, ax, "Staff Utilization Status", "Status", "Number of Staff")


st.markdown("""
<div class="main-title">Resourcing and Project Assignment Dashboard</div>
<div class="subtitle">
Upload one file containing staff availability and project requirements to generate assignments, charts, risks, and exportable outputs.
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.header("Input File")

    uploaded_file = st.file_uploader(
        "Upload resourcing file",
        type=["csv", "xlsx"],
        help="Required columns: Name, Role, Availability, Project Requirements"
    )


if uploaded_file is None:
    st.info("Upload one CSV or Excel file to begin.")
    st.stop()


raw_data = load_file(uploaded_file)

data = validate_columns(
    raw_data,
    ["Name", "Role", "Availability", "Project Requirements"]
)

data = prepare_data(data)

if data.empty:
    st.error("The uploaded file does not contain valid rows.")
    st.stop()


assignments_df, remaining_capacity, risks, assumptions = assign_staff(data)
capacity_df = build_capacity_summary(data, assignments_df)

total_staff = data["Name"].nunique()
total_projects = data["Project Requirements"].nunique()
total_available = capacity_df["Available Hours"].sum()
total_assigned = capacity_df["Assigned Hours"].sum()
utilization = (total_assigned / total_available * 100) if total_available > 0 else 0
risk_count = len(risks)


st.markdown('<div class="section-title">Executive Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_card("Total Staff", total_staff)

with col2:
    render_card("Projects", total_projects)

with col3:
    render_card("Assigned Hours", f"{total_assigned:.0f}h")

with col4:
    render_card("Utilization", f"{utilization:.1f}%")


st.markdown(f"""
<div class="info-card">
    <div class="card-title">Executive Summary</div>
    <p>
        The dashboard assigned <b>{total_assigned:.0f}</b> hours out of
        <b>{total_available:.0f}</b> available hours across
        <b>{total_projects}</b> project requirement groups.
        Current utilization is <b>{utilization:.1f}%</b>.
        There are <b>{risk_count}</b> identified staffing risks.
    </p>
</div>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Input Data",
    "Assignments",
    "Dashboard",
    "Risks",
    "Exports"
])


with tab1:
    st.markdown('<div class="section-title">Uploaded Data</div>', unsafe_allow_html=True)
    st.dataframe(data, use_container_width=True, hide_index=True)


with tab2:
    st.markdown('<div class="section-title">Project Assignment Output</div>', unsafe_allow_html=True)

    if assignments_df.empty:
        st.warning("No assignments could be generated. Check role matching and capacity.")
    else:
        st.dataframe(assignments_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Staff Capacity Summary</div>', unsafe_allow_html=True)
    st.dataframe(capacity_df, use_container_width=True, hide_index=True)

    if assumptions:
        st.markdown('<div class="section-title">Assumptions</div>', unsafe_allow_html=True)
        for assumption in assumptions:
            st.info(assumption)


with tab3:
    st.markdown('<div class="section-title">Visual Dashboard</div>', unsafe_allow_html=True)

    if assignments_df.empty:
        st.info("Charts will appear once assignments are generated.")
    else:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig = plot_project_hours(assignments_df)
            st.pyplot(fig)
            plt.close(fig)

        with chart_col2:
            fig = plot_capacity(capacity_df)
            st.pyplot(fig)
            plt.close(fig)

        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            fig = plot_role_coverage(assignments_df)
            st.pyplot(fig)
            plt.close(fig)

        with chart_col4:
            fig = plot_status_distribution(capacity_df)
            st.pyplot(fig)
            plt.close(fig)


with tab4:
    st.markdown('<div class="section-title">Risks and Staffing Gaps</div>', unsafe_allow_html=True)

    if risks:
        for risk in risks:
            st.warning(risk)
    else:
        st.success("No staffing gaps detected.")

    overloaded = capacity_df[capacity_df["Status"] == "Overloaded"]
    underutilized = capacity_df[capacity_df["Status"] == "Underutilized"]
    unassigned = capacity_df[capacity_df["Status"] == "Unassigned"]

    if not overloaded.empty:
        st.error("Overloaded staff")
        st.dataframe(overloaded, use_container_width=True, hide_index=True)

    if not underutilized.empty:
        st.info("Underutilized staff")
        st.dataframe(underutilized, use_container_width=True, hide_index=True)

    if not unassigned.empty:
        st.info("Unassigned staff")
        st.dataframe(unassigned, use_container_width=True, hide_index=True)


with tab5:
    st.markdown('<div class="section-title">Export Files</div>', unsafe_allow_html=True)

    export_col1, export_col2, export_col3, export_col4 = st.columns(4)

    with export_col1:
        st.download_button(
            label="Download assignments",
            data=assignments_df.to_csv(index=False),
            file_name="assignments.csv",
            mime="text/csv"
        )

    with export_col2:
        st.download_button(
            label="Download capacity summary",
            data=capacity_df.to_csv(index=False),
            file_name="capacity_summary.csv",
            mime="text/csv"
        )

    with export_col3:
        risks_df = pd.DataFrame({"Risk": risks})
        st.download_button(
            label="Download risks",
            data=risks_df.to_csv(index=False),
            file_name="risks.csv",
            mime="text/csv"
        )

    with export_col4:
        assumptions_df = pd.DataFrame({"Assumption": assumptions})
        st.download_button(
            label="Download assumptions",
            data=assumptions_df.to_csv(index=False),
            file_name="assumptions.csv",
            mime="text/csv"
        )


st.caption(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")