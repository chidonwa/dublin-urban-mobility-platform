{{ config(materialized='view') }}

SELECT
    entity_id,
    vehicle_id,
    trip_id,
    route_id,
    direction_id,
    start_time,
    start_date,
    latitude,
    longitude,
    observed_at,
    ingested_at
FROM {{ source('raw', 'nta_vehicle_positions') }}