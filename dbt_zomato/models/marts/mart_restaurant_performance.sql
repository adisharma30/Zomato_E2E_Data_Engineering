select
    f.r_id,
    r.restaurant_name,
    r.city,
    r.cuisine,
    count(*) as orders,
    sum(iff(f.order_status = 'Delivered', f.sales_amount, 0)) as revenue,
    round(avg(f.delivery_time_min), 1) as avg_delivery_time,
    round(avg(f.customer_rating), 2) as avg_customer_rating
from {{ ref('fct_orders') }} as f
left join {{ ref('dim_restaurant') }} as r
    on f.r_id = r.restaurant_id
group by
    f.r_id,
    r.restaurant_name,
    r.city,
    r.cuisine
