import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


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


def load_outputs():
    assignments_df = pd.read_csv("assignments.csv")
    capacity_df = pd.read_csv("capacity_summary.csv")
    risks_df = pd.read_csv("risks.csv")

    return assignments_df, capacity_df, risks_df


def save_project_hours_chart(assignments_df):
    if assignments_df.empty:
        return

    project_hours = assignments_df.groupby("Project", as_index=False)["Assigned Hours"].sum()

    plt.figure(figsize=(11, 5))
    bars = plt.bar(
        project_hours["Project"],
        project_hours["Assigned Hours"],
        color=ACCENT["dark_green"]
    )

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.0f}h",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    plt.title("Total Assigned Hours by Project")
    plt.xlabel("Project")
    plt.ylabel("Hours")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig("project_hours.png", dpi=150)
    plt.close()


def save_capacity_chart(capacity_df):
    if capacity_df.empty:
        return

    x = np.arange(len(capacity_df))

    assigned = capacity_df["Assigned Hours"]
    remaining = capacity_df["Remaining Hours"].clip(lower=0)

    fig, ax = plt.subplots(figsize=(11, 5))

    ax.bar(
        x,
        assigned,
        label="Assigned",
        color=ACCENT["medium_green"]
    )

    ax.bar(
        x,
        remaining,
        bottom=assigned,
        label="Remaining",
        color=ACCENT["light_green"]
    )

    ax.set_xticks(x)
    ax.set_xticklabels(capacity_df["Staff"], rotation=35, ha="right")
    ax.set_title("Assigned vs Remaining Staff Capacity")
    ax.set_xlabel("Staff")
    ax.set_ylabel("Hours")
    ax.legend(frameon=False)

    plt.tight_layout()
    plt.savefig("staff_capacity.png", dpi=150)
    plt.close()


def save_status_chart(capacity_df):
    if capacity_df.empty:
        return

    status_counts = capacity_df["Status"].value_counts()

    plt.figure(figsize=(8, 5))
    plt.bar(
        status_counts.index,
        status_counts.values,
        color=ACCENT["dark_green"]
    )

    plt.title("Staff Utilization Status")
    plt.xlabel("Status")
    plt.ylabel("Number of Staff")
    plt.tight_layout()
    plt.savefig("staff_status.png", dpi=150)
    plt.close()


def save_role_coverage_chart(assignments_df):
    if assignments_df.empty:
        return

    role_data = assignments_df.groupby(
        ["Project", "Role"],
        as_index=False
    )["Assigned Hours"].sum()

    pivot = role_data.pivot(
        index="Project",
        columns="Role",
        values="Assigned Hours"
    ).fillna(0)

    ax = pivot.plot(
        kind="bar",
        stacked=True,
        figsize=(11, 5),
        color=[
            ACCENT["dark_green"],
            ACCENT["medium_green"],
            ACCENT["light_green"],
            CORE["medium_gray"],
            CORE["light_gray"]
        ]
    )

    ax.set_title("Role Coverage by Project")
    ax.set_xlabel("Project")
    ax.set_ylabel("Hours")
    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")

    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig("role_coverage.png", dpi=150)
    plt.close()


def print_summary(assignments_df, capacity_df, risks_df):
    total_projects = assignments_df["Project"].nunique() if not assignments_df.empty else 0
    total_staff = capacity_df["Staff"].nunique() if not capacity_df.empty else 0
    total_assigned = capacity_df["Assigned Hours"].sum() if not capacity_df.empty else 0
    total_available = capacity_df["Available Hours"].sum() if not capacity_df.empty else 0
    utilization = (total_assigned / total_available * 100) if total_available > 0 else 0

    print("\nSummary")
    print(f"Total Projects: {total_projects}")
    print(f"Total Staff: {total_staff}")
    print(f"Total Assigned Hours: {total_assigned:.0f}")
    print(f"Total Available Hours: {total_available:.0f}")
    print(f"Utilization Rate: {utilization:.1f}%")

    print("\nStaff Status")
    print(capacity_df.to_string(index=False))

    risks = risks_df["Risk"].dropna().tolist() if "Risk" in risks_df.columns else []

    print("\nRisks")
    if risks:
        for risk in risks:
            print(f"- {risk}")
    else:
        print("No staffing gaps detected.")

    print("\nExecutive Summary")
    print(
        f"The resourcing allocation assigned {total_assigned:.0f} hours "
        f"across {total_projects} project requirement groups, with "
        f"overall utilization of {utilization:.1f}%."
    )


def run_agent2():
    assignments_df, capacity_df, risks_df = load_outputs()

    save_project_hours_chart(assignments_df)
    save_capacity_chart(capacity_df)
    save_status_chart(capacity_df)
    save_role_coverage_chart(assignments_df)

    print_summary(assignments_df, capacity_df, risks_df)

    print("\nSaved charts:")
    print("- project_hours.png")
    print("- staff_capacity.png")
    print("- staff_status.png")
    print("- role_coverage.png")


if __name__ == "__main__":
    run_agent2()