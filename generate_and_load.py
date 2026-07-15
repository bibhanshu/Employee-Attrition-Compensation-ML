"""
STEP 1 — Generate messy HR dataset and load into SQL Server
============================================================
Run this once to create the database, table, and insert all rows.
"""

import pyodbc
import random
import string

# ── CONFIG ─────────────────────────────────────────────────────────────────────
SERVER   = r"DESKTOP-J1C95IE\SQLEXPRESS01"
DATABASE = "EmployeeDB"          # will be created if it doesn't exist
TABLE    = "employees_raw"
# ───────────────────────────────────────────────────────────────────────────────

random.seed(42)

# ── MESSY DATA POOLS ───────────────────────────────────────────────────────────
DEPARTMENTS = [
    # intentionally inconsistent casing / punctuation
    "HR", "hr", "H.R", "H.R.", "Hr",
    "Finance", "finance", "FINANCE", "Fin",
    "Engineering", "engineering", "Eng", "ENGINEERING",
    "Marketing", "marketing", "Mktg", "MARKETING",
    "Sales", "sales", "SALES",
]

JOB_ROLES = [
    "Analyst", "Senior Analyst", "Manager", "Senior Manager",
    "Director", "Associate", "Intern", "Lead", "Consultant",
]

FIRST_NAMES = [
    "Aarav", "Priya", "Rohit", "Sneha", "Vikram", "Ananya", "Kiran",
    "Meera", "Arjun", "Divya", "Rajesh", "Pooja", "Suresh", "Nisha",
    "Amit", "Deepa", "Sanjay", "Kavya", "Ravi", "Lakshmi",
]

LAST_NAMES = [
    "Sharma", "Patel", "Nair", "Reddy", "Gupta", "Iyer", "Singh",
    "Mehta", "Joshi", "Kumar", "Verma", "Das", "Rao", "Pillai",
]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def maybe_null(value, null_prob=0.08):
    """Return None with null_prob probability, else return value."""
    return None if random.random() < null_prob else value


def generate_employees(n=500):
    rows = []
    for i in range(1, n + 1):
        dept = random.choice(DEPARTMENTS)

        # salary has mild outliers (~3% of rows)
        base_salary = random.randint(30000, 120000)
        if random.random() < 0.03:
            base_salary = random.choice([5, 999999])   # obvious bad values

        left = random.choices([0, 1], weights=[70, 30])[0]   # 30 % attrition

        row = (
            i,                                                  # employee_id
            maybe_null(random_name(), 0.05),                   # name
            maybe_null(random.randint(22, 60), 0.06),          # age
            dept,                                               # department (messy)
            maybe_null(random.choice(JOB_ROLES), 0.07),        # job_role
            maybe_null(random.randint(0, 20), 0.06),           # years_at_company
            maybe_null(base_salary, 0.05),                     # monthly_salary
            maybe_null(random.randint(1, 5), 0.07),            # performance_score
            maybe_null(random.randint(35, 65), 0.06),          # work_hours_per_week
            left,                                               # left_company
        )
        rows.append(row)
    return rows


# ── SQL HELPERS ────────────────────────────────────────────────────────────────
CREATE_DB_SQL = f"""
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{DATABASE}')
BEGIN
    CREATE DATABASE [{DATABASE}]
END
"""

CREATE_TABLE_SQL = f"""
IF OBJECT_ID('{TABLE}', 'U') IS NOT NULL
    DROP TABLE {TABLE};

CREATE TABLE {TABLE} (
    employee_id          INT            NOT NULL,
    name                 NVARCHAR(100)  NULL,
    age                  INT            NULL,
    department           NVARCHAR(50)   NOT NULL,
    job_role             NVARCHAR(50)   NULL,
    years_at_company     INT            NULL,
    monthly_salary       FLOAT          NULL,
    performance_score    INT            NULL,
    work_hours_per_week  INT            NULL,
    left_company         BIT            NOT NULL
);
"""

INSERT_SQL = f"""
INSERT INTO {TABLE}
    (employee_id, name, age, department, job_role,
     years_at_company, monthly_salary, performance_score,
     work_hours_per_week, left_company)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    # 1. Connect to master first to create the database
    print("Connecting to SQL Server...")
    conn_master = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE=master;"
        f"Trusted_Connection=yes;"
    )
    conn_master.autocommit = True
    conn_master.execute(CREATE_DB_SQL)
    conn_master.close()
    print(f"  ✔ Database '{DATABASE}' ready.")

    # 2. Connect to EmployeeDB and create table
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    print(f"  ✔ Table '{TABLE}' created (or replaced).")

    # 3. Generate and insert rows
    print("Generating 500 messy employee records...")
    rows = generate_employees(500)
    cursor.fast_executemany = True
    cursor.executemany(INSERT_SQL, rows)
    conn.commit()
    print(f"  ✔ Inserted {len(rows)} rows into '{TABLE}'.")

    # 4. Quick sanity check
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE}")
    total = cursor.fetchone()[0]
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE} WHERE name IS NULL")
    null_names = cursor.fetchone()[0]
    cursor.execute(f"SELECT COUNT(DISTINCT department) FROM {TABLE}")
    dept_variants = cursor.fetchone()[0]

    print("\n── Sanity Check ──────────────────────────────")
    print(f"  Total rows          : {total}")
    print(f"  Rows with NULL name : {null_names}")
    print(f"  Distinct dept values: {dept_variants}  (should be messy ~15+)")
    print("──────────────────────────────────────────────")
    print("\n✅ Step 1 complete! Open SSMS and verify the data, then move to 2_clean.sql")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()