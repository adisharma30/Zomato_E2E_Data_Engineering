select 
restaurant_id,
restaurant_name,
city,
rating,
rating_count,
cost_for_two,
cuisine,
license_number
from {{ref('stg_restaurants')}}