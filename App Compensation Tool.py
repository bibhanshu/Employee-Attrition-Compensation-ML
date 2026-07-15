import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import urllib

st.set_page_config(
    page_title="Compensation Analysis Tool",
    page_icon="💼",
    layout="centered"
)

# ── LOAD DATA + TRAIN MODEL ONCE ──────────────────────────
@st.cache_data
def load_and_train():
    params = urllib.parse.quote_plus(
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=DESKTOP-J1C95IE\SQLEXPRESS01;"
        r"DATABASE=EmployeeDB;"
        r"Trusted_Connection=yes;"
    )
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    df = pd.read_sql("SELECT * FROM employees_clean", engine)

    xcb = df.drop(columns=['monthly_salary', 'employee_id', 'name'])
    ycb = df['monthly_salary']
    xcb_encoding = pd.get_dummies(xcb, columns=['department', 'job_role'], drop_first=True)

    xcb_train, xcb_test, ycb_train, ycb_test = train_test_split(
        xcb_encoding, ycb, test_size=0.3, random_state=7
    )
    model = LinearRegression()
    model.fit(xcb_train, ycb_train)

    return df, xcb_encoding, model

df, xcb_encoding, model = load_and_train()

# ── HEADER ─────────────────────────────────────────────────
st.title("💼 Compensation Analysis Tool")
st.subheader("Internal Salary Benchmarking — Powered by ML")
st.caption("⚠️ Predictions based on internal workforce data only — not market benchmarks")
st.markdown("---")

# ── MODE SELECTION ─────────────────────────────────────────
mode = st.radio(
    "What would you like to do?",
    ["Analyze Existing Employee", "Estimate New Employee Salary"]
)
st.markdown("---")

# ── MODE 1 — EXISTING EMPLOYEE ─────────────────────────────
if mode == "Analyze Existing Employee":
    st.header("Existing Employee Pay Analysis")
    st.write("Enter an Employee ID to compare their actual salary against the model prediction.")

    emp_id = st.number_input("Employee ID:", min_value=1, max_value=500, step=1, value=1)

    if st.button("🔍 Analyze"):
        xcb_with_id = xcb_encoding.copy()
        xcb_with_id['employee_id'] = df['employee_id'].values

        emp_row = xcb_with_id[xcb_with_id['employee_id'] == emp_id]

        if emp_row.empty:
            st.error("❌ Employee ID not found!")
        else:
            emp_features = emp_row.drop(columns=['employee_id'])
            predicted_salary = model.predict(emp_features)[0]
            actual_salary = df[df['employee_id'] == emp_id]['monthly_salary'].values[0]
            difference = predicted_salary - actual_salary
            pct = ((predicted_salary - actual_salary) / predicted_salary) * 100

            # Status
            if difference > 5000:
                st.warning(" This employee appears to be UNDERPAID")
            elif difference < -5000:
                st.info(" This employee appears to be OVERPAID")
            else:
                st.success("✅ This employee's pay appears FAIR")

            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Actual Salary", f"₹{actual_salary:,.0f}")
            col2.metric("Predicted Salary", f"₹{predicted_salary:,.0f}")
            col3.metric("Pay Gap %", f"{pct:.2f}%")

            st.markdown("---")
            st.caption("Note: Employee name withheld for privacy. Prediction based on internal workforce data only.")

# ── MODE 2 — NEW EMPLOYEE ──────────────────────────────────
elif mode == "Estimate New Employee Salary":
    st.header("New Employee Salary Estimator")
    st.write("Enter candidate details to estimate an appropriate salary range.")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age:", min_value=18, max_value=65, value=25)
        department = st.selectbox("Department:", [
            "HR", "Finance", "Engineering", "Marketing", "Sales"
        ])
        job_role = st.selectbox("Job Role:", [
            "Analyst", "Senior Analyst", "Manager", "Senior Manager",
            "Director", "Associate", "Intern", "Lead",
            "Consultant", "Unknown Job Family"
        ])
    with col2:
        years = st.number_input("Years at Company:", min_value=0, max_value=40, value=0)
        st.info("Performance Score → Default: 2 (Generally Meets Expectations)")
        st.info("Work Hours → Default: 40 hrs/week (Standard)")

    if st.button("Estimate Salary"):
        user_data = pd.DataFrame({
            'age': [age],
            'department': [department],
            'job_role': [job_role],
            'years_at_company': [years],
            'performance_score': [2],
            'work_hours_per_week': [40]
        })

        user_encoded = pd.get_dummies(user_data, columns=['department', 'job_role'], drop_first=True)
        user_encoded = user_encoded.reindex(columns=xcb_encoding.columns, fill_value=0)
        predicted = model.predict(user_encoded)[0]

        st.success(f" Estimated Salary: ₹{predicted:,.0f} per month")
        st.markdown("---")
        st.caption(" This is an internal estimate only — not a market benchmark")
        st.caption("Assumptions: Performance Score = 2, Work Hours = 40/week")
        st.caption("For accurate market benchmarking, refer to external compensation surveys")