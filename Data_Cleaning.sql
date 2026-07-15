-- See the raw messy data
--USE EmployeeDB;
--SELECT TOP 20 * FROM employees_raw;

-- See all the department variants we need to fix
--SELECT department, COUNT(*) AS count
--FROM employees_raw
--GROUP BY department
--ORDER BY count DESC;
select * from [dbo].[employees_raw]
--I will analyze the missing value on basis on emp ID assuming thats the primary key with no repetation!

-- These are employeeId whose name are missing -- What you want to do with these ?(My question to stakeholders)
--my advise we can call these peoples ate "No Name" that wil help us in grouping and calculations like 
-- this amount of money we are using for employees whose name is not known"
with CTE as (select employee_id,count(name) as Name_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where Name_count = 0

--These are employeeId whose Age are missing
--My sujjetion to stakeholders is to add a Average age it depends if they want to add avg age of the whole data set or average age 
--of that specific department or identify this as an outliner by marking it because let say we want to see at what age our emploees are 
-- who are making above 10 lakhs if we would have taken average that might be an issue 
with CTE as (select employee_id,count(age) as Age_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where Age_count = 0

--These are employeeId whose Dep name are missing might be they are not tageed they are new or changed department (BTW the data is null) 
--That means all the emp are tageed to a specific dep
with CTE as (select employee_id,count(department) as Dep_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where Dep_count = 0

--These are employeeId whose job role is blank , eighter its a miss or they are new 
--my sujjestion would be to give a specific name like "Unknown Job family" so that we can see analytics like 
-- Sum min max , Hightest pay lowest pay in unknown job falily and so on .. but upto stakeholders what they want to do 
with CTE as (select employee_id,count(job_role) as Job_role_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where Job_role_count = 0


--These are employeeId whose years in comp are missing , eighter they are new joiner even if they are new we should mention zero 
--because now we dont know if they are new or missed and its upto the stakeholders what to do shall we mention zero ?
-- adding zero will impact the over all calculations 
with CTE as (select employee_id,count(years_at_company) as years_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where years_count = 0

--These are employeeId whose monthly salary is missing and thats a big miss thats litrally the main thing 
-- My suggetion is to compare the department avg and the whole company avg and see outliners before just jumping to avg and adding it 
-- this will affect dep and company avg also making them zero or adding one more coloumn and naming or highlight them is also an option 
-- upto the stakeholders and business case
with CTE as (select employee_id,count(monthly_salary) as Monthly_salary_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where Monthly_salary_count = 0

--These are employeeId whose performance score are null , they can be new employees but if so they should have a zero null 
--creates a confussion we can replace the nulls with zero though but upto the stakeholders
with CTE as (select employee_id,count(performance_score) as Performance_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where Performance_count = 0


--These are employeeId whose work hour is null there can be multiple resons
-- Might be they are not filling the timesheet or their nfc card is not functioning or might be they didnt work but if so it should be zero
-- again upto the stakeolders
with CTE as (select employee_id,count(work_hours_per_week) as work_hour_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where work_hour_count = 0

--These are employeeId who left the company it has to be zero or 1 0 means no 1 means they left null might indicate a big disturbance 
-- might be they are in notice period but stiill it should not be null as they are activly billed and payed 
-- this will play an imp role if we want to calculate metrix like active emp total pay or active emp in a dep avg etc 
-- we might see if there is work hour 
with CTE as (select employee_id,count(left_company) as left_company_count from [dbo].[employees_raw]
group by employee_id)
select employee_id from CTE
where left_company_count = 0

--------------------Data Cleaning---------------------
---Backup---
SELECT * INTO employees_backup_20260605 FROM [dbo].[employees_raw]

--- STart 
--dep col cleaning 
select department,count(employee_id) Test_count from [dbo].[employees_raw]
group by department

--How many variants exist per department
with CTE as (select*, ROW_NUMBER() over(partition by department order by age desc)as row_count from [dbo].[employees_raw])
select department from CTE
where row_count = 1


--map the messy names to clean ones 


UPDATE [dbo].[employees_raw]
SET department = CASE
    WHEN UPPER(REPLACE(department, '.', '')) IN ('HR', 'HRS') THEN 'HR'
    WHEN UPPER(REPLACE(department, '.', '')) IN ('FIN', 'FINANCE') THEN 'Finance'
    WHEN UPPER(REPLACE(department, '.', '')) IN ('ENG', 'ENGINEERING') THEN 'Engineering'
    WHEN UPPER(REPLACE(department, '.', '')) IN ('MKTG', 'MARKETING') THEN 'Marketing'
    WHEN UPPER(REPLACE(department, '.', '')) = 'SALES' THEN 'Sales'
    ELSE department
END
-- test 
select department from [dbo].[employees_raw]
group by department

-- name cloloumn cleaning:
--select employee_id from [dbo].[employees_raw]
--where name is null

--update [dbo].[employees_raw]
--set name = 'Unknown'
--where employee_id in (select employee_id from [dbo].[employees_raw]
--where name is null)

-- the above is bit complex i can also :
update [dbo].[employees_raw]
set name = 'Unknown'
where name is null

---age modify :

--Avg age per dep 
with CTE as (select department,AVG(age) over(partition by department) as avg_age
from [dbo].[employees_raw])
select department,Max(avg_age) as Dep_avg from CTE 
group by department

--Dont run again
update [dbo].[employees_raw]
set age = 43
where department = 'Engineering' and age is null 

--dont run again 
update [dbo].[employees_raw]
set age = case
when department = 'Engineering' and age is null Then 43
when department = 'Finance' and age is null Then 43
when department = 'HR' and age is null Then 42
when department = 'Marketing' and age is null Then 40
when department = 'Sales' and age is null Then 41
end

-- Redo 

UPDATE e
SET e.age = b.age
FROM [dbo].[employees_raw] e
INNER JOIN  employees_backup_20260605 b
ON e.employee_id = b.employee_id

-- age coloumn:
UPDATE e
SET age = avg_ages.dept_avg
FROM [dbo].[employees_raw] e
INNER JOIN ( -- second join
    SELECT department, AVG(age) AS dept_avg ---1st exicuted
    FROM [dbo].[employees_raw]
    WHERE age IS NOT NULL
    GROUP BY department
) avg_ages
ON e.department = avg_ages.department
WHERE e.age IS NULL

--Identify nulls and replace it with dep avg :

--Dep avg - 
with CTE as (select department,AVG(age) over(partition by department) as avg_age
from [dbo].[employees_raw]),
CTE2 as (
select department,Max(avg_age) as Dep_avg from CTE 
group by department)
select Null_Table.employee_id,
Null_Table.name,
Avg_table.Dep_avg as age,
Null_Table.department,
Null_Table.job_role,
Null_Table.years_at_company,
Null_Table.monthly_salary,
Null_Table.performance_score,
Null_Table.work_hours_per_week,
Null_Table.left_company
from CTE2 Avg_table
inner join (select * from [dbo].[employees_raw]
where age is null) Null_Table on Null_Table.department = Avg_table.department

--Cation Update :
WITH CTE AS (
    SELECT department, AVG(age) OVER(PARTITION BY department) AS avg_age
    FROM [dbo].[employees_raw]
),
CTE2 AS (
    SELECT department, MAX(avg_age) AS Dep_avg 
    FROM CTE 
    GROUP BY department
)
UPDATE Null_Table                        -- ← was SELECT
SET age = Avg_table.Dep_avg             -- ← was your column list
FROM CTE2 Avg_table
INNER JOIN (
    SELECT * FROM [dbo].[employees_raw] WHERE age IS NULL
) Null_Table ON Null_Table.department = Avg_table.department

--Ages updated with Avg

select * from [dbo].[employees_raw]

--"Update the job_role to 'Unknown Job Family' for all employees where job_role is NULL"

update [dbo].[employees_raw]
set job_role = 'Unknown Job Family'
where job_role is null

--"Update years_at_company to 0 for all employees where it is NULL"
update [dbo].[employees_raw]
set years_at_company = 0
where years_at_company is null

--Monthly_salary 
select min(monthly_salary) as Min_pay,avg(monthly_salary) as Avg_pay,max(monthly_salary) as Max_pay  from [dbo].[employees_raw]

--no of rows :
SELECT COUNT(*) 
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000

-- identify 
SELECT *
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000

--impact emp ID :
SELECT employee_id
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000

--impact dep id
SELECT department
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000
group by department

--  first final select:
with CTE as (select department,
AVG(monthly_salary) over( Partition by department) as Avg_salary_per_deptt
from [dbo].[employees_raw]
where department in (SELECT department
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000
group by department)
and employee_id not in (
SELECT employee_id
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000
))
select department,max(Avg_salary_per_deptt) as Avg_salary_per_deptt from CTE 
group by department


-- final select not updated :
with CTE as (select department,
AVG(monthly_salary) over( Partition by department) as Avg_salary_per_deptt
from [dbo].[employees_raw]
where department in (SELECT department
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000
group by department)
and employee_id not in (
SELECT employee_id
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000
)), cte_2 as (
select department,max(Avg_salary_per_deptt) as Avg_salary_per_deptt from CTE 
group by department)
select
impacted_emp.employee_id,
impacted_emp.name,
impacted_emp.age,
impacted_emp.department,
impacted_emp.job_role,
impacted_emp.years_at_company,
avg_pay_dep.Avg_salary_per_deptt as monthly_salary,
impacted_emp.performance_score,
impacted_emp.work_hours_per_week,
impacted_emp.left_company
from cte_2 avg_pay_dep
inner join (
SELECT *
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000) impacted_emp on avg_pay_dep.department = impacted_emp.department


WITH CTE AS (...),        -- ← exact same
CTE2 AS (...)             -- ← exact same
UPDATE impacted_emp       -- ← was SELECT
SET monthly_salary = avg_pay_dep.Avg_salary_per_deptt  -- ← was your column
FROM cte_2 avg_pay_dep    -- ← exact same
INNER JOIN (...) impacted_emp 
ON avg_pay_dep.department = impacted_emp.department  -- ← exact same

-- Update ran dont run again !!!!!!!!!!!!!!
with CTE as (select department,
AVG(monthly_salary) over( Partition by department) as Avg_salary_per_deptt
from [dbo].[employees_raw]
where department in (SELECT department
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000
group by department)
and employee_id not in (
SELECT employee_id
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000
)), cte_2 as (
select department,max(Avg_salary_per_deptt) as Avg_salary_per_deptt from CTE 
group by department)
UPDATE impacted_emp  
SET monthly_salary = avg_pay_dep.Avg_salary_per_deptt
from cte_2 avg_pay_dep
inner join (
SELECT *
FROM [dbo].[employees_raw]
WHERE monthly_salary < 1000 OR monthly_salary > 500000) impacted_emp on avg_pay_dep.department = impacted_emp.department


---
select * from [dbo].[employees_raw]
-- update Null monthly salary to dep avrage 

--Null pay identification:
select * from [dbo].[employees_raw]
where monthly_salary is null 

--departents by emp Id for those having null monthly pay :
select employee_id from [dbo].[employees_raw]
where monthly_salary is null 

--null depp
select department from [dbo].[employees_raw]
where monthly_salary is null 


-- Finding avg monthly pay for the null emp id for specific depp :
with CTE as (select department,Avg(monthly_salary) over(partition by department) as Dep_avg from [dbo].[employees_raw]
where department in (select department from [dbo].[employees_raw]
where monthly_salary is null) and employee_id not in (select employee_id from [dbo].[employees_raw]
where monthly_salary is null)),
CTE_2 as (
select department,max(Dep_avg) as required_dep_avg from CTE
group by department)
UPDATE Null_pay_req
SET monthly_salary = Dep_avg_req.required_dep_avg
from CTE_2 Dep_avg_req
inner join (select * from [dbo].[employees_raw]
where monthly_salary is null) Null_pay_req on Dep_avg_req.department = Null_pay_req.department

-- Performance score of 2 :
select * from [dbo].[employees_raw]
where performance_score is null 

--This is done dont run again !!!
update [dbo].[employees_raw]
set performance_score = 2
where performance_score is null 

--work hours 
select * from [dbo].[employees_raw]
where work_hours_per_week is null and left_company = 1

--This is done dont run again !!!
update [dbo].[employees_raw]
set work_hours_per_week = case
    WHEN left_company = 1 THEN 0
    WHEN left_company = 0 THEN 40
    ELSE work_hours_per_week
END
where work_hours_per_week is null

--- till here all done :
select * from [dbo].[employees_raw]

--Left company 
SELECT COUNT(*) FROM [dbo].[employees_raw] WHERE left_company IS NULL

--final view :
CREATE VIEW employees_clean AS
SELECT * FROM [dbo].[employees_raw]

SELECT TOP 10 * FROM employees_clean