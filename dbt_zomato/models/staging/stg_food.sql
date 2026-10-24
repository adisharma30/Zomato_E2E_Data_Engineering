select
f_id :: varchar as food_id,
item as item_name,
initcap(trim(veg_or_non_veg)) as veg_or_non_veg
from {{source('raw','food')}}
where f_id is not null
