select 
food_id,
item_name,
veg_or_non_veg
from {{ref('stg_food')}}