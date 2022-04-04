import streamlit as st
import requests as rq
import datetime as dt
import geocoder

# functions below


def k2c(k):
    return k - 273.15


def c2f(c):
    return c * 1.8 + 32


def m2mi(m):
    return m / 1609.344


def ms2mph(ms):
    return 3600 * m2mi(ms)


# streamlit structure below
pageTitle = "Weather"
st.set_page_config(
    page_title=pageTitle,
    menu_items={
        "About": "HCI Project 2"
    }
)

st.title(pageTitle)
# lat lon from ip
g = geocoder.ipinfo('me')
lat = g.latlng[0]
lon = g.latlng[1]
city = g.city

st.info("Based on your IP address, you are in or near " + city + ".")
citySearchInput = st.text_input("Search for a city:")
if citySearchInput:
    citySearchURL = "https://nominatim.openstreetmap.org/search?city=" + citySearchInput + "&format=json"
    citySearchResponse = rq.get(citySearchURL).json()
    cityOptions = []
    for item in citySearchResponse:
        if item["display_name"] not in cityOptions:
            cityOptions.append(item["display_name"])
    # cityOptions = list(set(cityOptions))
    selectedCity = st.selectbox(str(len(cityOptions)) + " results for " + citySearchInput, cityOptions)
    selectedLat = 0.
    selectedLon = 0.
    for item in citySearchResponse:
        if item["display_name"] == selectedCity:
            selectedLat = item["lat"]
            selectedLon = item["lon"]
            break
    city = selectedCity
    lat = selectedLat
    lon = selectedLon

cityShortName = ""
for i in range(len(city)):
    if city[i] != ',':
        cityShortName += city[i]
        continue
    break
st.header("Statistics for " + cityShortName)

# get response from openWeatherMap api
apiKey = "f2753510aec1cb9ef2f826c3edd452ad"
apiURL = "https://api.openweathermap.org/data/2.5/onecall?lat="+str(lat)+"&lon="+str(lon)+"&appid=" + apiKey
response = rq.get(apiURL).json()

#parse response
currentDateTime = dt.datetime.fromtimestamp(response["current"]["dt"])
sunriseToday = dt.datetime.fromtimestamp(response["current"]["sunrise"])
sunsetToday = dt.datetime.fromtimestamp(response["current"]["sunset"])

currentTempKelvin = response["current"]["temp"]
currentFeelsLikeKelvin = response["current"]["feels_like"]
currentDewPointKelvin = response["current"]["dew_point"]

currentPressure = response["current"]["pressure"]
currentPressureStr = str(currentPressure) + " hPa"

currentHumidity = response["current"]["humidity"]
currentClouds = response["current"]["clouds"]
currentHumidityStr = str(currentHumidity) + "%"
currentCloudsStr = str(currentClouds) + "%"

currentUVI = response["current"]["uvi"]
currentUVIStr = str(currentUVI)

currentVisibilityM = response["current"]["visibility"]
currentWindSpeedMS = response["current"]["wind_speed"]

currentWindDeg = response["current"]["wind_deg"]
currentWindDirStr = ""
if (currentWindDeg >= 337.5) | (currentWindDeg < 22.5):
    currentWindDirStr = "N"
elif currentWindDeg < 67.5:
    currentWindDirStr = "NE"
elif currentWindDeg < 112.5:
    currentWindDirStr = "E"
elif currentWindDeg < 157.5:
    currentWindDirStr = "SE"
elif currentWindDeg < 202.5:
    currentWindDirStr = "S"
elif currentWindDeg < 247.5:
    currentWindDirStr = "SW"
elif currentWindDeg < 292.5:
    currentWindDirStr = "W"
else:
    currentWindDirStr = "NW"

currentWeatherStr = response["current"]["weather"][0]["description"]

temperatureUnit = st.selectbox("Select a unit of temperature", ["Fahrenheit", "Celsius"])

# convert to selected unit and build strings
currentTemp = k2c(currentTempKelvin)
currentFeelsLike = k2c(currentFeelsLikeKelvin)
currentDewPoint = k2c(currentDewPointKelvin)
if temperatureUnit == "Fahrenheit":
    currentTemp = c2f(currentTemp)
    currentFeelsLike = c2f(currentFeelsLike)
    currentDewPoint = c2f(currentDewPoint)
currentTempStr = str(int(currentTemp)) + "°" + temperatureUnit[0]
currentFeelsLikeStr = str(int(currentFeelsLike)) + "°" + temperatureUnit[0]
currentDewPointStr = str(int(currentDewPoint)) + "°" + temperatureUnit[0]

currentVisibility = currentVisibilityM
currentWindSpeed = currentWindSpeedMS
currentVisibilityStr = ""
currentWindSpeedStr = ""
if temperatureUnit == "Fahrenheit":
    currentVisibility = m2mi(currentVisibility)
    currentWindSpeed = ms2mph(currentWindSpeed)
    currentVisibilityStr = str(int(currentVisibility)) + " miles"
    currentWindSpeedStr = str(int(10*currentWindSpeed) / 10) + " mph"
else:
    currentVisibilityStr = str(int(currentVisibility / 1000)) + " kilometers"
    currentWindSpeedStr = str(int(10*currentWindSpeed) / 10) + " m/s"

currentWindSpeedStr += " " + currentWindDirStr
# all info should be available now, the rest of the app is below

# display all possible information
st.write("Current Time: " + str(currentDateTime))
st.write("Sunrise Today: " + str(sunriseToday))
st.write("Sunset Today: " + str(sunsetToday))

st.write("Current Temperature: " + currentTempStr)
st.write("Feels Like: " + currentFeelsLikeStr)
st.write("Dew Point: " + currentDewPointStr)

st.write("Pressure: " + currentPressureStr)

st.write("Clouds: " + currentCloudsStr)
st.write("Humidity: " + currentHumidityStr)

st.write("UV Index: " + currentUVIStr)

st.write("Wind Speed: " + currentWindSpeedStr)
st.write("Visibility: " + currentVisibilityStr)

st.write("Weather Description: " + currentWeatherStr)

