select
order_item_id :: number as order_item_id,
order_id :: number as order_id,
r_id :: number as restaurant_id,
f_id :: number as food_id,
try_to_decimal(price,3,2) as price,
quantity :: number as quantity,
line_amount :: decimal as line_amount
from {{ source('raw','order_items')}}
where try_to_number(order_item_id) is not null