-- MART: LATEST PRICES
-- Business question this answers: "What is the current price and
-- rank of every coin, right now?"
--
-- Because our raw table is append-only (every pipeline run adds new
-- rows), this model uses a window function to keep only the most
-- recent row per coin. This is a classic, resume-worthy SQL pattern:
-- deduplicating a time-series table down to "current state."

with staged as (

    select * from {{ ref('stg_crypto_prices') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by coin_id
            order by extracted_at desc
        ) as recency_rank

    from staged

)

select
    coin_id,
    symbol,
    name,
    price_usd,
    market_cap_usd,
    market_cap_rank,
    volume_24h_usd,
    price_change_pct_24h,
    circulating_supply,
    extracted_at as as_of
from ranked
where recency_rank = 1
