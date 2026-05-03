import pandas as pd


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


def load_resourcing_file(file_path):
    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    required_columns = [
        "Name",
        "Role",
        "Availability",
        "Project Requirements"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[required_columns].dropna()

    df["Name"] = df["Name"].astype(str).str.strip()
    df["Role"] = df["Role"].astype(str).str.strip()
    df["Project Requirements"] = df["Project Requirements"].astype(str).str.strip()

    return df

def assign_staff(data):
    assignments = []
    risks = []

    staff_data = data.copy()
    staff_data["Available"] = staff_data["Availability"].apply(convert_availability)

    staff_data = staff_data[["Name", "Role", "Available"]].drop_duplicates()
    remaining_capacity = dict(zip(staff_data["Name"], staff_data["Available"]))

    project_groups = data.groupby("Project Requirements")

    for project_requirement, project_df in project_groups:
        project_name = project_requirement
        required_hours = project_df["Availability"].apply(convert_availability).sum()

        # 🔥 KEY FIX: flexible matching instead of exact match
        suitable_staff = staff_data[
            staff_data["Role"].apply(
                lambda role: str(role).lower() in str(project_requirement).lower()
                or str(project_requirement).lower() in str(role).lower()
            )
        ].copy()

        # fallback if no match
        if suitable_staff.empty:
            suitable_staff = staff_data.copy()

        suitable_staff["Remaining"] = suitable_staff["Name"].map(remaining_capacity)
        suitable_staff = suitable_staff[suitable_staff["Remaining"] > 0]
        suitable_staff = suitable_staff.sort_values("Remaining", ascending=False)

        if suitable_staff.empty:
            risks.append(f"No capacity for project '{project_name}'")
            continue

        for _, staff in suitable_staff.iterrows():
            if required_hours <= 0:
                break

            name = staff["Name"]
            available = remaining_capacity[name]

            assigned = min(available, required_hours)

            remaining_capacity[name] -= assigned
            required_hours -= assigned

            assignments.append({
                "Project": project_name,
                "Assigned Staff": name,
                "Role": staff["Role"],
                "Assigned Hours": assigned,
                "Reason for Assignment": "Best available match",
                "Remaining Capacity": remaining_capacity[name]
            })

        if required_hours > 0:
            risks.append(f"{project_name} still needs {required_hours:.0f}h")

    return pd.DataFrame(assignments), remaining_capacity, risks


def build_capacity_summary(data, assignments_df):
    rows = []

    staff_data = data.copy()
    staff_data["Available"] = staff_data["Availability"].apply(convert_availability)
    staff_data = staff_data[["Name", "Role", "Available"]].drop_duplicates()

    for _, staff in staff_data.iterrows():
        name = staff["Name"]
        available = staff["Available"]

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


def run_agent1(file_path):
    data = load_resourcing_file(file_path)

    assignments_df, remaining_capacity, risks, assumptions = assign_staff(data)
    capacity_df = build_capacity_summary(data, assignments_df)

    assignments_df.to_csv("assignments.csv", index=False)
    capacity_df.to_csv("capacity_summary.csv", index=False)
    pd.DataFrame({"Risk": risks}).to_csv("risks.csv", index=False)

    return assignments_df, capacity_df, risks


if __name__ == "__main__":
    file_path = "your_resourcing_file.csv"

    assignments_df, capacity_df, risks = run_agent1(file_path)

    print("\nProject Assignment Output")
    if assignments_df.empty:
        print("No assignments could be generated.")
    else:
        print(assignments_df.to_string(index=False))