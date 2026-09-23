SELECT
    station_id,
    bike_observed_at,
    COUNT(*) AS observation_count
FROM {{ ref('fct_bike_weather_observations') }}
GROUP BY
    station_id,
    bike_observed_at
HAVING COUNT(*) > 1