-- STAGING LAYER
-- Staging models do minimal work: light renaming, type casting,
-- and deduplication. They are the "single source of truth" that
-- every downstream model builds on, so we never write business
-- logic here - just cleanup.

with source as (

    select * from {{ source('raw', 'raw_crypto_prices') }}

),

renamed as (

    select
        coin_id,
        symbol,
        name,
        price_usd::numeric              as price_usd,
        market_cap_usd::numeric         as market_cap_usd,
        market_cap_rank::int            as market_cap_rank,
        volume_24h_usd::numeric         as volume_24h_usd,
        price_change_pct_24h::numeric   as price_change_pct_24h,
        circulating_supply::numeric     as circulating_supply,
        last_updated::timestamp         as last_updated_at,
        extracted_at::timestamp         as extracted_at

    from source

)

select * from renamed
