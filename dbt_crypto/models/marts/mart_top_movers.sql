-- MART: TOP MOVERS
-- Business question this answers: "Which coins moved the most in
-- the last 24 hours, and how does that compare to their market cap
-- tier?" This is the kind of table a Data Analyst would plug
-- straight into a Tableau/Power BI dashboard.

with latest as (

    select * from {{ ref('mart_latest_prices') }}

),

categorized as (

    select
        *,
        case
            when market_cap_rank <= 10 then 'Top 10'
            when market_cap_rank <= 50 then 'Top 11-50'
            else 'Top 51-100'
        end as market_cap_tier,
        case
            when price_change_pct_24h >= 0 then 'gainer'
            else 'loser'
        end as movement_type

    from latest

)

select
    coin_id,
    symbol,
    name,
    market_cap_tier,
    movement_type,
    price_usd,
    price_change_pct_24h,
    market_cap_usd,
    as_of
from categorized
order by price_change_pct_24h desc
