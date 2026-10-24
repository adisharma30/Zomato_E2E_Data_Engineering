with spine as (
    select dateadd(day,seq4(), '2024-01-01'::date) as date_day
    from table(generator(rowcount => 1200))
)

select
    date_day,
    year(date_day) as year,
    month(date_day) as month,
    day(date_day) as day,
    dayname(date_day) as day_name,
    weekofyear(date_day) as week_of_year,
    quarter(date_day) as quarter
from spine
where date_day <= '2026-12-31'