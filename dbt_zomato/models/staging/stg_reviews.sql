select
r.review_id :: number as review_id,
r.order_id :: number as order_id,
r.user_id :: number as user_id,
r.restaurant_id :: number as restaurant_id,
r.rating :: decimal(3,2) as rating,
comment as review_comment,
r.review_date :: date as review_date,
s.city as restaurant_city
from {{ source('raw','reviews')}} r
left join {{ref('stg_restaurants')}} s on r.restaurant_id = s.restaurant_id
where r.comment is not null