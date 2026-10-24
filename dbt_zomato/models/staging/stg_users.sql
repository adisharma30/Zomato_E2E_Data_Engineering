select
user_id::varchar as customer_id,
name as customer_name,
email as customer_email,
password as customer_password,
try_to_number(Age) as customer_age,
gender as customer_gender,
MARITAL_STATUS as customer_marital_status,
occupation as customer_occupation,
try_to_number(Monthly_Income) as cs_monthly_income,
educational_qualification as cs_edu_quali,
family_size:: number as cs_family_size
from {{ source ('raw','users')}}
where try_to_number(user_id) is not null


