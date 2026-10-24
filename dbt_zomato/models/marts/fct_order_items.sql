{{
    config(
        materialized='incremental',
        unique_key='order_item_id',
        incremental_strategy='merge',
        on_schema_change='sync_all_columns'
    )
}}
select
o.order_item_id,
oi.order_id,
o.restaurant_id,
o.food_id,
o.price,
o.quantity,
o.line_amount,
oi.order_date,
oi.restaurant_city,
oi.order_timestamp as order_ts
    from {{ref('stg_order_items')}} as o
    left join
    {{ref('stg_orders')}} as oi
    using(order_id)

{% if is_incremental() %}
where oi.order_timestamp > (select coalesce(max(order_ts), '1900-01-01'::timestamp) from {{this}})
{% endif %}
