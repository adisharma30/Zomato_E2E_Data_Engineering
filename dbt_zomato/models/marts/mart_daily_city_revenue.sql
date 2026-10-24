select
    order_date,
    restaurant_city,
    count(order_id) as total_orders,
    coalesce(count_if(order_status = 'Delivered'), 0) as delivered_orders,
    round(
        100 * div0(coalesce(count_if(order_status = 'Cancelled'), 0), count(*)),
        2
    ) as cancelled_rate_pct,
    sum(iff(order_status = 'Delivered', coalesce(sales_amount, 0), 0)) as gmv,
    round(
        div0(
            sum(iff(order_status = 'Delivered', coalesce(sales_amount, 0), 0)),
            coalesce(count_if(order_status = 'Delivered'), 0)
        ),
        2
    ) as aov
from {{ ref('fct_orders') }}
group by 1, 2