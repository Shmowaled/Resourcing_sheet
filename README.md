# Resourcing Sheet - Project Assignment & Dashboard

A comprehensive resource management system with two main agents for project staffing and visualization.

## Overview

This project implements:
- Agent 1: Project Assignment Agent - Intelligently assigns staff to projects
- Agent 2: Visual Dashboard Agent - Provides real-time metrics and visualizations
- Streamlit Web Application - Interactive, dynamic dashboard for resource planning

## Agent 1: Project Assignment Your task is to read the timesheet for Consuluum and assign staff to projects.

### Use these fields when available:

- Name
- Role
- Availability
- Project Requirements

### Rules:

1. Match staff to projects based on role fit, availability, and project requirements.
2. Do not assign someone to a project if their availability is too low.
3. Prioritize staff whose role directly matches the project requirement.
4. If one person cannot cover the required hours, split the project across multiple suitable staff.
5. Avoid over-allocation.
6. If data is unclear, make a reasonable assumption and clearly state it.
7. Output the result as a clean table with:
   - Project
   - Assigned Staff
   - Role
   - Assigned Hours
   - Reason for Assignment
   - Remaining Capacity
8. Highlight any risks, missing data, or staffing gaps.

### Logic Flow:

```
1. Read staff data from timesheet
2. Convert availability to hours (Full-time: 40h, Part-time: 20h, On-demand: 10h)
3. For each project:
   - Find suitable staff by role match
   - Sort by available capacity (descending)
   - Assign hours up to availability
   - Track remaining capacity
4. Flag understaffed projects as risks
5. Generate assignment table and capacity summary
```

---

## Agent 2: Visual Dashboard

**Your task is to create a visual dashboard from the project assignment and timesheet data.**

### Dashboard Theme:

**Core Palette:**
- `#1D1D1D` - Dark background
- `#4F5052` - Dark gray
- `#828281` - Medium gray
- `#CCC8BD` - Light gray
- `#F8FAF9` - Off-white

**Accent Palette:**
- `#475751` - Dark green
- `#6D7668` - Medium green
- `#C0CEBC` - Light green

### Dashboard Components:

1. **Summary Cards**
   - Total Assigned Hours
   - Utilization Rate (%)
   - Fully Utilized Staff Count
   - Understaffed Projects Count

2. **Charts & Visualizations**
   - Bar chart for project hours
   - Stacked bar chart for staff capacity
   - Role coverage heatmap by project

3. **Tables**
   - Assignment details
   - Staff capacity summary
   - Role coverage by project

4. **Risk/Status Section**
   - Overloaded staff alerts (Critical)
   - Underutilized staff (Warning)
   - Understaffed projects (Alert)

5. **Executive Summary**
   - Key highlights
   - Key findings
   - Recommendations

---

## Quick Start

### Prerequisites
```bash
pip install pandas matplotlib streamlit openpyxl
```

### Run the Interactive Dashboard
```bash
streamlit run streamlit_app.py
```

The app will open at: `http://localhost:8501`

**Getting Started:**
1. Upload your timesheet file (CSV or Excel) in the sidebar
2. Configure your projects or use the defaults
3. View real-time assignments and visualizations
4. Export results as needed

### Run Python Agents Directly
```bash
# Agent 1: Generate assignments
python3 agent1.py

# Agent 2: Generate visualizations
python3 agent2.py
```

---

## File Structure

```
/workspaces/Resourcing_sheet/
├── README.md                          # This file
├── timesheet(Dummy).csv               # Input data (CSV format)
├── agent1.py                          # Project assignment agent
├── agent2.py                          # Dashboard visualization agent
├── streamlit_app.py                   # Interactive Streamlit dashboard
├── assignments.csv                    # Output: Assignment results
```

---

## Streamlit Dashboard Features

The interactive Streamlit app provides:

### File Upload (Dynamic Input)
- **Upload your own timesheet**: Support for CSV and Excel files
- **Real-time processing**: Instant analysis of uploaded data
- **Session persistence**: Uploaded files remain available during session

### Configuration Panel (Sidebar)
- View loaded staff data
- Dynamically configure projects
- Modify project requirements and hours
- Add/remove projects on the fly

### Assignment View
- Real-time assignment table
- Staff capacity summary with status indicators
- Staffing gap alerts and risks

### Dashboard View
- Summary cards with key metrics
- Interactive charts (project hours, staff capacity)
- Role coverage analysis

### Executive Summary Card
- **Styled container**: Professional card design with borders and shadows
- **Auto-generated insights**: Key highlights, findings, and recommendations
- **High-quality UI**: Clean typography and color-coded sections

### Export Options
- Download assignments as CSV
- Download capacity summary as CSV
- Download role coverage as CSV

---

## Workflow

1. **Load Data**: Read timesheet with staff and roles
2. **Configuration**: Define projects and requirements
3. **Assignment**: Agent 1 matches staff to projects
4. **Visualization**: Agent 2 creates charts and dashboards
5. **Export**: Download results in CSV format

---

## Risk Assessment

The system automatically identifies:
- UNDERSTAFFED PROJECTS: Projects with insufficient hours assigned
- OVERLOADED STAFF: Staff with negative remaining capacity
- UNDERUTILIZED STAFF: Staff with >15 hours remaining
- UTILIZATION RATE: Overall team utilization percentage

---

## Notes

- All availability times converted to hours: Full-time (40h), Part-time (20h), On-demand (10h)
- Projects are assigned based on exact role match
- Staffing gaps are flagged as risks
- Utilization calculated as: Assigned Hours / Available Hours
- Dashboard updates dynamically when projects are modified