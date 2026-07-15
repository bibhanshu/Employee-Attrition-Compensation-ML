import urllib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine

## Reading the Data from SQL :
params = urllib.parse.quote_plus(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=DESKTOP-J1C95IE\SQLEXPRESS01;"
    r"DATABASE=EmployeeDB;"
    r"Trusted_Connection=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

df = pd.read_sql("SELECT * FROM employees_clean", engine)
print(df.columns)
xcb = df.drop(columns=['monthly_salary','employee_id', 'name'])
ycb = df['monthly_salary']
xcb_encoding = pd.get_dummies(xcb, columns=['department', 'job_role'], drop_first=True) ## as they are non numeric
pd.set_option('display.max_columns', None)
print(xcb_encoding.head())

##Train Test Split :
xcb_encoding_train,xcb_encoding_test,ycb_train,ycb_test = train_test_split(
    xcb_encoding,ycb,
    test_size=0.3,
    random_state=7
)

model_Comp_Benchmark = LinearRegression()
model_Comp_Benchmark.fit(xcb_encoding_train,ycb_train)
Predicted_Comp_Benchmark_Linn_Regg = model_Comp_Benchmark.predict(xcb_encoding_test)
print('Actual',ycb_test[:10].values,'Predicted',Predicted_Comp_Benchmark_Linn_Regg[:10])
R2_Linn_Regg = r2_score(ycb_test,Predicted_Comp_Benchmark_Linn_Regg)
#print('R2',R2_Linn_Regg) ##R2 -0.05849349540627724
MSE_Linn_Regg = mean_squared_error(ycb_test,Predicted_Comp_Benchmark_Linn_Regg)
RMSE_Linn_Regg = np.sqrt(MSE_Linn_Regg)
print('RMSE_Linn_Regg',RMSE_Linn_Regg) ##RMSE_Linn_Regg 25544.372825719205

##R2 is bad and so as RMSE

##Random Forest :
model_Comp_Benchmark_Random_Forest = RandomForestRegressor(
    n_estimators=500,
    random_state=42,
)
model_Comp_Benchmark_Random_Forest.fit(xcb_encoding_train,ycb_train)
Predicted_Comp_Benchmark_Random_Forest = model_Comp_Benchmark_Random_Forest.predict(xcb_encoding_test)
print('Actual',ycb_test[:10].values)
print('Predicted',Predicted_Comp_Benchmark_Random_Forest[:10])
R2_Random_Forest = r2_score(ycb_test,Predicted_Comp_Benchmark_Random_Forest)
print('R2_Random_Forest',R2_Random_Forest) ##R2_Random_Forest -0.07036943386603589
MSE_Random_forest = mean_squared_error(ycb_test,Predicted_Comp_Benchmark_Random_Forest)
RMSE_Random_forest = np.sqrt(MSE_Random_forest)
print('RMSE_Random_forest',RMSE_Random_forest) ##RMSE_Random_forest 25687.272726653926

##- 28 salary values replaced with dept average (NULL imputation)
##- 9 outlier salaries replaced with dept average
##- Total affected = 37/500 rows = 7.4% of salary data is artificial

## Removing artificial data
df_clean_salary = df[
    (df['monthly_salary'] > 1000) &
    (df['monthly_salary'] < 500000)
]
xcb_clean_salary = df_clean_salary.drop(columns=['monthly_salary','employee_id', 'name'])
ycb_clean_salary = df_clean_salary['monthly_salary']
##encoding
xcb_encoding_clean_salary = pd.get_dummies(xcb_clean_salary, columns=['department', 'job_role'], drop_first=True) ## as they are non numeric
pd.set_option('display.max_columns', None)
##Train test Split

xcb_encoding_clean_salary_train,xcb_encoding_clean_salary_test,ycb_clean_salary_train,ycb_clean_salary_test = train_test_split(
    xcb_encoding_clean_salary,ycb_clean_salary ,
    test_size=0.3,
    random_state=7
)
##Gradient Boosting:
model_Comp_Benchmark_GB = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)
model_Comp_Benchmark_GB.fit(xcb_encoding_clean_salary_train,ycb_clean_salary_train)
Predicted_Comp_Benchmark_GB = model_Comp_Benchmark_GB.predict(xcb_encoding_clean_salary_test)
print('Actual',ycb_clean_salary_test[:10].values)
print('Predicted',Predicted_Comp_Benchmark_GB[:10])
R2_GB = r2_score(ycb_clean_salary_test,Predicted_Comp_Benchmark_GB)
MSE_GB = mean_squared_error(ycb_clean_salary_test,Predicted_Comp_Benchmark_GB)
RMSE_GB = np.sqrt(MSE_GB)
print('R2_GB',R2_GB)
print('RMSE_GB',RMSE_GB)

##
#("Regression models struggled due to fundamental data quality issue — salary was synthetically generated "
# "randomly with no correlation to features like age, department or performance. In real world HR data with "
# "genuine compensation patterns, tree-based models like Gradient Boosting would significantly outperform "
# "Linear Regression.)

##Key learning: Model performance is bounded by data quality — garbage in, garbage out!"
##EMP ID compensation lookup tool

##Adding employee_id back to encoded dataframe because we dropped Emp ID while encoding
xcb_encoding_with_id = xcb_encoding.copy()
xcb_encoding_with_id['employee_id'] = df['employee_id'].values

##User inputs EMP ID
emp_id = int(input("Enter Employee ID: "))

##Finding that employee's encoded row - This will match user input to specific emp id in encoded
emp_row = xcb_encoding_with_id[xcb_encoding_with_id['employee_id'] == emp_id]
#print(emp_row)

## Dropping employee_id before predicting
emp_features = emp_row.drop(columns=['employee_id'])
#print(emp_features)

##Step 5 - Predict - Model comp benchmark is Linn regg Model , emp_features is kind of user input
predicted_salary = model_Comp_Benchmark.predict(emp_features)[0]

#Get actual salary
actual_salary = df[df['employee_id'] == emp_id]['monthly_salary'].values[0]

##pay Diff
difference_pay = predicted_salary - actual_salary
##logic
if difference_pay < -5000:
    print(f'Emp Id :{emp_id} Actual Salary : {actual_salary} predicted Salary : {predicted_salary} --- Overpaid by '
          f'{((actual_salary - predicted_salary)/predicted_salary) * 100}% ')
elif difference_pay> 5000:
    print(f'Emp Id :{emp_id} Actual Salary : {actual_salary} predicted Salary : {predicted_salary} --- Underpaid by '
          f'{((actual_salary - predicted_salary)/predicted_salary) * 100}% ')
else:
    print(f'Emp Id :{emp_id} Actual Salary : {actual_salary} predicted Salary : {predicted_salary} --- Fair ')


print("--- New Employee Salary Estimator ---")
age = int(input("Enter Age: "))
department = input("Enter Department (HR/Finance/Engineering/Marketing/Sales): ")
job_role = input("Enter Job Role: ")
years = int(input("Enter Years at Company(Please enter 0 for new joiner): "))
performance = int(input("Enter Performance Score (1-5)(for new joiner by default rating is 2 ): "))
hours = int(input("Enter Work Hours Per Week:(for new joiner by default Working hours  is 40 ) "))

##Convert into dataframe:
User_data = pd.DataFrame({
    'age': [age],
    'department': [department],
    'job_role': [job_role],
    'years_at_company': [years],
    'performance_score': [performance],
    'work_hours_per_week': [hours]
})
##user data encoding
User_data_encoded = pd.get_dummies(User_data)
User_data_encoded = User_data_encoded.reindex(columns = xcb_encoding.columns ,fill_value=0)
New_Employee_status_prediction = model_Comp_Benchmark.predict(User_data_encoded)[0]

# Feature importance from Linear Regression
#feature_importance = pd.Series(
#    np.abs(model_Comp_Benchmark.coef_),
#    index=xcb_encoding.columns
#).sort_values(ascending=False)

#top_3 = feature_importance.head(3).index.tolist()

print(f'New Employee Pay prediction : {New_Employee_status_prediction} '
      f'Please note the Model predict Salary based on the previous data base of existing employee '
     )


