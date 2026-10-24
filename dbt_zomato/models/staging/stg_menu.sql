select 
menu_id :: varchar as menu_id,
r_id :: number as restaurant_id,
f_id :: varchar as food_id,
cuisine,
try_to_decimal(price,4,2) as price
from {{ source('raw','menu')}}
where menu_id is not null