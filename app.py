"""
Student Result / Grade Management System — Streamlit UI
CIA-3 Mini Project | MAT161-3

Run locally with:  streamlit run app.py
Deploy for free at: https://share.streamlit.io  (push this to a public GitHub repo)
"""

import numpy as np
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
SUBJECT_PASS_MARK = 35
OVERALL_PASS_PERCENT = 35

st.set_page_config(page_title="Student Result System", layout="wide")

# ----------------------------------------------------------------------
# Core functions (same logic as the notebook)
# ----------------------------------------------------------------------
def get_subjects(df):
    metadata_cols = ["Sl No", "Roll No", "Name"]
    return [c for c in df.columns if c not in metadata_cols]


def calculate_total(row, subjects):
    total = 0
    for subject in subjects:
        total = total + row[subject]
    return total


def calculate_percentage(total, num_subjects):
    return round((total / (num_subjects * 100)) * 100, 2)


def assign_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B+"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    elif percentage >= OVERALL_PASS_PERCENT:
        return "E"
    else:
        return "F"


def check_result(percentage):
    if percentage >= OVERALL_PASS_PERCENT:
        return "Pass"
    else:
        return "Fail"


def subjects_failed(row, subjects):
    failed = []
    for subject in subjects:
        if row[subject] < SUBJECT_PASS_MARK:
            failed.append(subject)
    if len(failed) == 0:
        return "None"
    return ", ".join(failed)


def compute_results(df, subjects):
    df["Total"] = df.apply(lambda row: calculate_total(row, subjects), axis=1)
    df["Percentage"] = df["Total"].apply(lambda t: calculate_percentage(t, len(subjects)))
    df["Grade"] = df["Percentage"].apply(assign_grade)
    df["Result"] = df["Percentage"].apply(check_result)
    df["Subjects_Failed"] = df.apply(lambda row: subjects_failed(row, subjects), axis=1)
    return df


# ----------------------------------------------------------------------
# Sidebar — data source + menu (this replaces the while/input() loop)
# ----------------------------------------------------------------------
st.sidebar.title("📋 Student Result System")

uploaded_file = st.sidebar.file_uploader("Upload student_marks.csv", type="csv")

page = st.sidebar.radio(
    "Choose a view",
    ["Display All Results", "Class Statistics", "Find Topper", "Download Results"],
)

st.title("Student Result / Grade Management System")
st.caption("CIA-3 Mini Project | MAT161-3 | Python Programming")

if uploaded_file is None:
    st.info("👈 Upload a student_marks.csv file from the sidebar to get started.")
    st.write("Expected columns: `Sl No`, `Roll No`, `Name`, then one column per subject.")
    st.stop()

df = pd.read_csv(uploaded_file)
subjects = get_subjects(df)
df = compute_results(df, subjects)

# ----------------------------------------------------------------------
# Option 1 — Display all results
# ----------------------------------------------------------------------
if page == "Display All Results":
    st.subheader("All Student Results")
    cols = ["Sl No", "Roll No", "Name"] + subjects + [
        "Total", "Percentage", "Grade", "Result", "Subjects_Failed"
    ]
    st.dataframe(df[cols], use_container_width=True)

# ----------------------------------------------------------------------
# Option 2 — Class statistics
# ----------------------------------------------------------------------
elif page == "Class Statistics":
    st.subheader("Class Statistics")

    mean = df[subjects].mean()
    maximum = df[subjects].max()
    minimum = df[subjects].min()
    std_dev = df[subjects].std()

    stats_table = pd.DataFrame({
        "Subject": subjects,
        "Mean": mean.values.round(2),
        "Maximum": maximum.values,
        "Minimum": minimum.values,
        "Std Dev": std_dev.values.round(2),
    })
    st.dataframe(stats_table, use_container_width=True)

    class_average = np.mean(df["Percentage"])
    topper_row = df.loc[df["Percentage"].idxmax()]
    lowest_row = df.loc[df["Percentage"].idxmin()]
    pass_count = (df["Result"] == "Pass").sum()
    fail_count = (df["Result"] == "Fail").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Class Average", f"{round(class_average, 2)}%")
    c2.metric("Topper", f"{topper_row['Name']}", f"{topper_row['Percentage']}%")
    c3.metric("Passed", int(pass_count))
    c4.metric("Failed", int(fail_count))

    st.markdown("**Grade distribution**")
    grade_order = ["A+", "A", "B+", "B", "C", "D", "E", "F"]
    grade_counts = df["Grade"].value_counts().reindex(grade_order, fill_value=0)
    st.bar_chart(grade_counts)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Subject-wise class average**")
        st.bar_chart(mean)
    with col_b:
        st.markdown("**Pass vs Fail**")
        st.bar_chart(pd.Series({"Pass": pass_count, "Fail": fail_count}))

    st.markdown("**Maximum vs Minimum per subject**")
    minmax_df = pd.DataFrame({"Maximum": maximum, "Minimum": minimum})
    st.bar_chart(minmax_df)

# ----------------------------------------------------------------------
# Option 3 — Find topper
# ----------------------------------------------------------------------
elif page == "Find Topper":
    st.subheader("Topper")
    topper = df.loc[df["Percentage"].idxmax()]
    st.metric("Name", topper["Name"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Roll No", topper["Roll No"])
    c2.metric("Percentage", f"{topper['Percentage']}%")
    c3.metric("Grade", topper["Grade"])

# ----------------------------------------------------------------------
# Option 4 — Download processed results
# ----------------------------------------------------------------------
elif page == "Download Results":
    st.subheader("Download Processed Results")
    st.dataframe(df, use_container_width=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download student_results_processed.csv",
        data=csv_bytes,
        file_name="student_results_processed.csv",
        mime="text/csv",
    )
