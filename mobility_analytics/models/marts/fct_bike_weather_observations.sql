{{ config(materialized='table') }}

SELECT
    b.station_id,
    b.station_name,
    b.address,
    b.latitude,
    b.longitude,
    b.capacity,
    b.num_bikes_available,
    b.num_docks_available,

    ROUND(
        (b.num_bikes_available::numeric / NULLIF(b.capacity, 0)) * 100,
        2
    ) AS bike_availability_pct,

    ROUND(
        (b.num_docks_available::numeric / NULLIF(b.capacity, 0)) * 100,
        2
    ) AS dock_availability_pct,

    b.last_reported_dt AS bike_observed_at,
    DATE_TRUNC('hour', b.last_reported_dt) AS observation_hour,

    w.observed_at AS weather_observed_at,
    w.air_temperature,
    w.air_pressure,
    w.precipitation_amount,
    w.relative_humidity

FROM {{ ref('stg_dublin_bikes_station_status') }} b

INNER JOIN {{ ref('stg_phoenix_park_weather') }} w
    ON DATE_TRUNC('hour', b.last_reported_dt)
       = DATE_TRUNC('hour', w.observed_at)