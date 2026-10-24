select
restaurant_city,
hour(order_timestamp) as order_hour,
count(iff(order_status='Delivered',1,0)) as delivered_orders,
round(median(delivery_time_min),1) as p50,
round(percentile_cont(0.9) within group (order by delivery_time_min)) as p90
from {{ref('fct_orders')}}
where order_status='Delivered'
group by 1,2