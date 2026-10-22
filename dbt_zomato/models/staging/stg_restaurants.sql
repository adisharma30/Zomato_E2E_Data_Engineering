select 
id::number as restaurant_id,
name as restaurant_name,
trim(coalesce(REGEXP_SUBSTR(city,'[^,]+$'),city)) as city,
try_to_decimal(nullif(rating,'--'),3,1) as rating,
try_to_number(REGEXP_SUBSTR(rating_count,'[0-9]+')) as rating_count,
try_to_number(REGEXP_SUBSTR(cost,'[0-9]+')) as cost_for_two,
cuisine as cuisine,
lic_no as license_number
from {{ source('raw','restaurants')}}
where try_to_number(id) is not null
