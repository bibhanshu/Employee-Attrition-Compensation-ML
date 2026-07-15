# 🏢 Employee Attrition & Compensation Benchmarking ML Tool

> End-to-end HR Analytics project combining SQL Server data cleaning, Python Machine Learning, and a Streamlit web application for internal salary benchmarking and employee attrition prediction.

---

## 📌 Project Statement

Given a messy HR dataset, clean and transform it using SQL Server, then build ML models in Python to:
1. **Predict whether an employee will leave the company** (Classification)
2. **Predict what salary an employee should be earning internally** (Regression)
3. **Deploy as an interactive Streamlit web application** for HR stakeholders

---

## 🗂️ Project Structure

```
├── generate_and_load.py              # Step 1 — Generate messy dataset + load into SQL Server
├── Attrition Model.py                # Step 2 — Classification ML models (predict attrition)
├── Compensation Benchmarking ML tool.py  # Step 3 — Regression ML models (predict salary)
├── App Compensation Tool.py          # Step 4 — Streamlit web application
└── README.md
```

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Database | Microsoft SQL Server (SSMS) |
| Data Cleaning | SQL (CTEs, Window Functions, CASE WHEN) |
| Python Connection | SQLAlchemy + pyodbc |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn, XGBoost |
| Web Application | Streamlit |

---

## 📊 Dataset Overview

- **500 rows** of synthetic HR employee data
- **10 columns** — age, department, job role, salary, performance score, work hours, attrition
- Intentionally messy — NULLs, outliers, inconsistent department naming

---

## 🧹 Part 1 — SQL Data Cleaning

All cleaning performed in **SQL Server** before touching Python:

| Column | Issue | Fix |
|---|---|---|
| `department` | Inconsistent casing (`hr`, `H.R`, `HR`) | `UPPER()` + `REPLACE()` + `CASE WHEN` |
| `name` | NULL values | Replaced with `'Unknown'` |
| `age` | NULL values | Replaced with department average using Window Function |
| `job_role` | NULL values | Replaced with `'Unknown Job Family'` |
| `years_at_company` | NULL values | Replaced with `0` |
| `monthly_salary` | NULLs + outliers (₹5 and ₹999,999) | Outliers → dept avg (excluding outliers), NULLs → dept avg |
| `performance_score` | NULL values | Replaced with `2` (Generally Meets Expectations) |
| `work_hours_per_week` | NULL values | `0` for employees who left, `40` for active employees |

### Key SQL Concepts Used:
- `CASE WHEN` for data standardization
- `COALESCE` and `UPDATE` for NULL handling
- `AVG() OVER (PARTITION BY department)` for smart imputation
- CTEs for multi-step cleaning logic
- `CREATE VIEW employees_clean` as final clean output

---

## 🤖 Part 2 — Classification (Attrition Prediction)

**Target:** `left_company` (0 = Stayed, 1 = Left)

### Models Compared:

| Model | Test Accuracy | True Recall | True F1 | Overfitting |
|---|---|---|---|---|
| Logistic Regression | 68% | 2% | 0.04 | No |
| Logistic Regression (balanced) | 49% | 48% | 0.38 | No |
| Random Forest | 68% | 4% | 0.08 | Yes ⚠️ |
| Random Forest (balanced) | 60% | 10% | 0.14 | Yes ⚠️ |
| Gradient Boosting | 68% | 17% | 0.25 | Yes ⚠️ |
| XGBoost | 59% | 15% | 0.19 | Yes ⚠️ |
| KNN (K=6) | 68% | 6% | 0.11 | No |

### ✅ Final Model: Logistic Regression (class_weight='balanced')
> Selected for highest **True Recall (48%)** — critical for HR use case where catching potential leavers matters more than overall accuracy.

### Key Learning:
> Class imbalance (72% stayed vs 28% left) meant accuracy alone was misleading. F1 Score and Recall were the real metrics for this business problem.

### Feature Importance (Random Forest):
1. `monthly_salary` — underpaid employees leave more
2. `work_hours_per_week` — overworked employees leave more
3. `age` — career stage affects attrition
4. `years_at_company` — early tenure = higher flight risk
5. `performance_score` — low and high performers both at risk

---

## 💰 Part 3 — Regression (Salary Prediction)

**Target:** `monthly_salary`

### Models Compared:

| Model | R² | RMSE |
|---|---|---|
| Linear Regression | -0.058 | 25,544 |
| Random Forest | -0.070 | 25,687 |
| Gradient Boosting | -0.237 | 27,621 |

### Key Learning — Data Quality Impact:
> All regression models performed poorly due to a fundamental data quality issue — salary was synthetically generated randomly with no real correlation to features. Additionally, 7.4% of salary values were imputed averages (28 NULLs + 9 outliers = 37/500 rows).
>
> **In real world HR data with genuine compensation patterns, tree-based models like Gradient Boosting would significantly outperform Linear Regression.**
>
> *Garbage in = Garbage out — model performance is always bounded by data quality.*

---

## 🖥️ Part 4 — Streamlit Web Application

Interactive compensation analysis tool with two modes:

### Mode 1 — Existing Employee Analysis
- Input: Employee ID
- Output: Actual Salary vs Predicted Salary vs Pay Gap %
- Status: Underpaid / Fair / Overpaid
- Privacy: Employee name withheld — ID only shown to stakeholders

### Mode 2 — New Employee Salary Estimator
- Input: Age, Department, Job Role, Years at Company
- Defaults: Performance Score = 2, Work Hours = 40
- Output: Estimated salary range based on internal workforce data

---

## 🚀 How to Run

### Prerequisites:
```
pip install pandas sqlalchemy pyodbc scikit-learn xgboost streamlit
```

### Step 1 — Generate and load data:
```
python generate_and_load.py
```

### Step 2 — Run Streamlit app:
```
streamlit run "App Compensation Tool.py"
```

---

## 📈 Business Insights

1. **Salary and overwork are the top drivers of attrition** — not just performance
2. **HR department itself has high attrition** — internal irony!
3. **Early tenure employees (0-3 years) are highest flight risk**
4. **Data quality directly limits ML model performance** — clean data is more valuable than complex models
5. **For attrition prediction — Recall beats Accuracy** — missing a leaver is more costly than a false alarm

---

## 👤 Author

**Bibhanshu Swain**


---

## ⚠️ Disclaimer

> This project uses **synthetic data** — all employee records are artificially generated for learning purposes. Salary predictions are based on internal workforce patterns only and should not be used as market benchmarks.


App output:
<img width="974" height="730" alt="Screenshot 2026-07-16 050112" src="https://github.com/user-attachments/assets/8217f174-1b31-432e-b3dc-a2ecb4c70829" />

<img width="1435" height="849" alt="Screenshot 2026-07-16 050144" src="https://github.com/user-attachments/assets/700b221e-5718-47d0-a8eb-7b72a9065246" />

<img width="1436" height="850" alt="Screenshot 2026-07-16 050214" src="https://github.com/user-attachments/assets/a50e7320-4ef8-4658-9328-50e6d4d20087" />








