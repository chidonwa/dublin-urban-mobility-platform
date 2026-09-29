SELECT
    observation_hour,
    station_observations,
    stations_observed,
    avg_bike_availability_pct,
    avg_dock_availability_pct,
    avg_precipitation_amount,
    avg_relative_humidity
FROM {{ ref('mart_hourly_bike_weather') }}
WHERE
    avg_bike_availability_pct < 0
    OR avg_bike_availability_pct > 100
    OR avg_dock_availability_pct < 0
    OR avg_dock_availability_pct > 100
    OR avg_relative_humidity < 0
    OR avg_relative_humidity > 100
    OR avg_precipitation_amount < 0
    OR station_observations <= 0
    OR stations_observed <= 0
    OR stations_observed > station_observations