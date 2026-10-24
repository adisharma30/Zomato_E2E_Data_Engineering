select 
customer_id,
customer_name,
customer_email,
customer_age,
case 
    when customer_age < 18 then 'Teenager'
    when customer_age between 18 and 35 then 'Millenials'
    when customer_age between 36 and 55 then 'Gen X'
    when customer_age > 55 then 'Senior Citizen'
    else 'unknown' end as age_group,
customer_gender,
customer_marital_status,
customer_occupation,
cs_monthly_income,
cs_edu_quali,
cs_family_size
from {{ref('stg_users')}}
