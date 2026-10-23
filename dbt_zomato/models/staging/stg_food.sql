select
f_id :: number as food_id,
item as food_name,
initcap(trim(veg_or_non_veg)) as food_type
from {{source('raw','food')}}
where try_to_number(f_id) is not null
