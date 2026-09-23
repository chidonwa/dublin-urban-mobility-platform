SELECT
    station_id,
    bike_observed_at,
    bike_availability_pct,
    dock_availability_pct
FROM {{ ref('fct_bike_weather_observations') }}
WHERE bike_availability_pct < 0
    OR bike_availability_pct > 100
    OR dock_availability_pct < 0
    OR dock_availability_pct > 100