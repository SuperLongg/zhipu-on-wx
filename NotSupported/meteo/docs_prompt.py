OPEN_METEO_DOCS = """BASE URL: https://api.open-meteo.com/

API Documentation
The API endpoint /v1/forecast accepts a geographical coordinate, a list of weather variables and responds with a JSON hourly weather forecast for 7 days. Time always starts at 0:00 today and contains 168 hours. All URL parameters are listed below:

Parameter	Format	Required	Default	Description
latitude, longitude	Floating point	Yes		Geographical WGS84 coordinate of the location.
temperature_unit	String	No	celsius	If fahrenheit is set, all temperature values are converted to Fahrenheit.
windspeed_unit	String	No	kmh	Other wind speed speed units: ms, mph and kn
precipitation_unit	String	No	mm	Other precipitation amount units: inch
timeformat	String	No	iso8601	If format unixtime is selected, all time values are returned in UNIX epoch time in seconds. Please note that all timestamp are in GMT+0! For daily values with unix timestamps, please apply utc_offset_seconds again to get the correct date.
timezone	String	No	GMT	If timezone is set, all timestamps are returned as local-time and data is returned starting at 00:00 local-time. Any time zone name from the time zone database is supported. If auto is set as a time zone, the coordinates will be automatically resolved to the local time zone.
past_days	Integer (0-2)	No	0	If past_days is set, yesterday or the day before yesterday data are also returned.
forecast_days	Integer (0-16)	No	7	Per default, only 7 days are returned. Up to 16 days of forecast are possible.

Hourly Parameter Definition:
The parameter &hourly= accepts the following values; note that you cannot use Daily Parameter in &hourly=.
Most weather variables are given as an instantaneous value for the indicated hour. 
Some variables like precipitation are calculated from the preceding hour as an average or sum.

Variable	Valid time	Unit	Description
temperature_2m	Instant	°C (°F)	Air temperature at 2 meters above ground
relative_humidity_2m	Instant	%	Relative humidity at 2 meters above ground
cloudcover	Instant	%	Total cloud cover as an area fraction
precipitation	Preceding hour sum	mm (inch)	Total precipitation (rain, showers, snow) sum of the preceding hour
snowfall	Preceding hour sum	cm (inch)	Snowfall amount of the preceding hour in centimeters. For the water equivalent in millimeter, divide by 7. E.g. 7 cm snow = 10 mm precipitation water equivalent
rain	Preceding hour sum	mm (inch)	Rain from large scale weather systems of the preceding hour in millimeter
weathercode	Instant	WMO code	Weather condition as a numeric code. Follow WMO weather interpretation codes.   
windspeed_10m & windspeed_80m & windspeed_120m & windspeed_180m	Instant	km/h (mph, m/s, knots)	Wind speed at 10, 80, 120 or 180 meters above ground. Wind speed on 10 meters is the standard level.

Let's break it down step by step:
1. Use only the parameters mentioned in this document to create the API URL. Do not invent parameters. You must include the parameter for hourly details. If there is a parameter for daily details, you must also include it.
2. Retrieve weather information for a maximum of 3 days using either the start_date or end_date parameters.
3. The past_days parameter cannot be used together with start_date and end_date.
4. the timezone parameter is auto.
5. Provide only the URL as output; no need for an explanation.
6. Add as many weather parameters as possible,must include Hourly Parameter Definition。

"""