
import pandas as pd
from sqlalchemy import create_engine
import urllib

params = urllib.parse.quote_plus(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=DESKTOP-J1C95IE\SQLEXPRESS01;"
    r"DATABASE=EmployeeDB;"
    r"Trusted_Connection=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

df = pd.read_sql("SELECT * FROM employees_clean", engine)
print(df.head())
print(df.shape)
print(df.columns)
print(df['department'])
print(df[['name','department','monthly_salary']])
print(df.describe())
##"Using iloc, how do you fetch the first row of the dataframe?"
print(df.iloc[0,:])
##"Using iloc, how do you fetch rows 5 to 10, and only the first 3 columns?"
print(df.iloc[5:11,:3]) ##5-11 which is 5 to 10 and after , :3

##"Using loc, fetch all employees where department is 'HR' and show only name, department and monthly_salary columns"
Table_1 = df[df['department'] == 'HR']
print(Table_1.head())
print(Table_1.loc[:,['name','department','monthly_salary']])

##"Filter all employees whose monthly_salary is greater than 80000"
print(df[df['monthly_salary'] > 80000])
##"Filter all employees whose monthly_salary is greater than 80000 AND who are in the Engineering department"
print(df[(df['monthly_salary'] > 80000) & (df['department'] == 'Engineering')])
##Filter all employees who are either in HR OR have a performance_score of 5"
print(df[(df['department'] == 'HR')| (df['performance_score'] == 5)])
##"Filter all employees who have NOT left the company"
print(df[df['left_company'] == False])

##"Filter employees whose age is between 30 and 40 AND have years_at_company greater than 5 AND have NOT left the company"
print(df[((df['age'] > 30) & (df['age'] < 40)) & (df['years_at_company'] > 5) & (df['left_company'] == False) ])

##"Create a new column called yearly_salary which is monthly_salary multiplied by 12
df['yearly_salary'] = df['monthly_salary'] * 12
print(df.head())

##"Create a new column called salary_per_hour which is monthly_salary divided by (work_hours_per_week multiplied by 4)"
##df['Salary_per_hour'] = df['monthly_salary'] / (df['work_hours_per_week'] * 4)
import numpy as np
df['salary_per_hour'] = df['monthly_salary'] / df['work_hours_per_week'].replace(0, np.nan) * 4
print(df.head())

##"Create a new column called full_profile that combines name, department and job_role like this:"
df['full_profile'] = df['name'] +' | ' +  df['department'] + ' | ' +  df['job_role']
print(df.head())

##"Create a new column called experience_salary_ratio which is monthly_salary
# divided by years_at_company — but only where years_at_company is greater than 0, else put 0"


df['experience_salary_ratio'] = df.apply(
    lambda row: row['monthly_salary'] / row['years_at_company']
    if row['years_at_company'] > 0 else 0, axis=1
)

##"Using map, replace the department values so that any department called 'HR' shows as 'Human Resources'"
## " and 'Engineering' shows as 'Tech' — create it as a new column called department_mapped"

code_map = {'HR':'Human Resources','Engineering': 'Tech'}
df['department_mapped'] = df['department'].map(code_map).fillna(df['department'])

print(df.columns)


df_ml = df.drop(columns=['employee_id', 'name', 'department_mapped'])