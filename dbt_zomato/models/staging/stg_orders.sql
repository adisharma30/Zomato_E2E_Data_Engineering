select
    order_id :: number as order_id,
    order_timestamp :: timestamp as order_timestamp,
    order_date :: date as order_date,
    user_id :: number as user_id,
    r_id :: number as r_id,
    restaurant_city :: string as restaurant_city,
    cuisine,
    try_to_number(items_count) as items_count,
    try_to_number(sales_qty) as sales_qty,
    try_to_number(subtotal) as subtotal,
    try_to_number(discount) as discount,
    try_to_number(delivery_fee) as delivery_fee,
    try_to_number(gst) as gst,
    try_to_number(sales_amount) as sales_amount,
    currency,
    payment_method,
    order_status,
    customer_rating,
    delivery_time_min
    from {{source('raw','orders')}}
    where try_to_number(order_id) is not null

