select 
menu_id :: number as menu_id,
r_id :: number as restaurant_id,
f_id :: number as food_id,
cuisine,
try_to_decimal(price,4,2) as price
from {{ source('raw','menu')}}
where try_to_number(menu_id) is not null