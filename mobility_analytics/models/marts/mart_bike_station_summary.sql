{{ config(materialized='table') }}

SELECT
    station_id,
    station_name,
    address,
    latitude,
    longitude,
    capacity,

    COUNT(*) AS observation_count,

    ROUND(AVG(num_bikes_available)::numeric, 2)
        AS avg_bikes_available,

    ROUND(AVG(num_docks_available)::numeric, 2)
        AS avg_docks_available,

    ROUND(
        AVG(
            (num_bikes_available::numeric / NULLIF(capacity, 0)) * 100
        ),
        2
    ) AS avg_bike_availability_pct,

    ROUND(
        AVG(
            (num_docks_available::numeric / NULLIF(capacity, 0)) * 100
        ),
        2
    ) AS avg_dock_availability_pct,

    COUNT(*) FILTER (
        WHERE num_bikes_available = 0
    ) AS empty_station_observations,

    COUNT(*) FILTER (
        WHERE num_docks_available = 0
    ) AS full_station_observations,

    MIN(last_reported_dt) AS first_observed_at,
    MAX(last_reported_dt) AS latest_observed_at

FROM {{ ref('stg_dublin_bikes_station_status') }}

GROUP BY
    station_id,
    station_name,
    address,
    latitude,
    longitude,
    capacity