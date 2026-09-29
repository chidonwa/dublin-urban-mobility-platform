{{ config(materialized='table') }}

WITH bike_weather AS (

    SELECT *
    FROM {{ ref('fct_bike_weather_observations') }}

),

station_hour AS (

    SELECT
        observation_hour,
        station_id,

        COUNT(*) AS station_observations,

        AVG(bike_availability_pct) AS avg_bike_availability_pct,
        AVG(dock_availability_pct) AS avg_dock_availability_pct,

        AVG(air_temperature) AS avg_air_temperature,
        AVG(precipitation_amount) AS avg_precipitation_amount,
        AVG(relative_humidity) AS avg_relative_humidity,
        AVG(air_pressure) AS avg_air_pressure

    FROM bike_weather

    GROUP BY
        observation_hour,
        station_id

)

SELECT
    observation_hour,

    SUM(station_observations) AS station_observations,
    COUNT(*) AS stations_observed,

    ROUND(
        AVG(avg_bike_availability_pct)::numeric,
        2
    ) AS avg_bike_availability_pct,

    ROUND(
        AVG(avg_dock_availability_pct)::numeric,
        2
    ) AS avg_dock_availability_pct,

    ROUND(
        AVG(avg_air_temperature)::numeric,
        2
    ) AS avg_air_temperature,

    ROUND(
        AVG(avg_precipitation_amount)::numeric,
        2
    ) AS avg_precipitation_amount,

    ROUND(
        AVG(avg_relative_humidity)::numeric,
        2
    ) AS avg_relative_humidity,

    ROUND(
        AVG(avg_air_pressure)::numeric,
        2
    ) AS avg_air_pressure

FROM station_hour

GROUP BY observation_hour

ORDER BY observation_hour