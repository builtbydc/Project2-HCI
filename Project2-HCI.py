import streamlit as st
import requests as rq
import datetime as dt
import geocoder
from matplotlib import pyplot as plt
from bokeh.models.widgets import Div

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
pageTitle = "Current Weather Info"
st.set_page_config(
    page_title=pageTitle,
    menu_items={
        "About": "HCI Project 2"
    }
)

st.title(pageTitle)

# search or get city from ip
citySearchInput = st.text_input("Search for a city:")
if citySearchInput:
    citySearchURL = "https://nominatim.openstreetmap.org/search?city=" + citySearchInput + "&format=json"
    citySearchResponse = rq.get(citySearchURL).json()
    if len(citySearchResponse) > 0:
        cityOptions = []
        for item in citySearchResponse:
            if item["display_name"] not in cityOptions:
                cityOptions.append(item["display_name"])
        # cityOptions = list(set(cityOptions))
        noOfCityOptions = len(cityOptions)
        if noOfCityOptions > 1:
            selectedCity = st.selectbox(str(noOfCityOptions) + " results for \"" + citySearchInput + "\"", cityOptions)
        else:
            selectedCity = st.selectbox("1 result for \"" + citySearchInput + "\"", cityOptions)
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
    else:
        st.error("Your search for \"" + citySearchInput + "\" returned 0 results. Try another city.")
        # lat lon from ip
        g = geocoder.ipinfo('me')
        lat = g.latlng[0]
        lon = g.latlng[1]
        city = g.city
        st.info("Based on your IP address, you are in or near " + city + ".")
else:
    # lat lon from ip
    g = geocoder.ipinfo('me')
    lat = g.latlng[0]
    lon = g.latlng[1]
    city = g.city
    st.info("Based on your IP address, you are in or near " + city + ".")

# header
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

# selectbox
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

# TODO: get hourly forecast from response

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

seeUVI = st.checkbox("See UV Index information.")
if seeUVI:
    c1, c2 = st.columns([2, 1])
    with c1:
        UVILabel = [""]
        UVIWidth = 2
        UVIYTicks = [0, 3, 6, 8, 11]

        fig, ax = plt.subplots()

        ax.bar(UVILabel, 10, UVIWidth, bottom=11, label='Extreme', color="#B94375")
        ax.bar(UVILabel, 3, UVIWidth, bottom=8, label='Very High', color="#C73734")
        ax.bar(UVILabel, 2, UVIWidth, bottom=6, label='High', color="#E09945")
        ax.bar(UVILabel, 3, UVIWidth, bottom=3, label='Moderate', color="#F9DC4F")
        ax.bar(UVILabel, 3, UVIWidth, bottom=0, label='Low', color="#8DBF89")
        ax.plot(0.5, currentUVI, "k*", markersize=20)

        ax.set_title("UV Index")
        ax.set_yticks(UVIYTicks)
        ax.set_xticks([])
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        plt.xlim(0, 1)
        plt.ylim(0, 15)
        ax.legend()
        st.pyplot(fig)

        if currentUVI < 3:
            currentUVIStr = "low"
        elif currentUVI < 6:
            currentUVIStr = "moderate"
        elif currentUVI < 8:
            currentUVIStr = "high"
        elif currentUVI < 11:
            currentUVIStr = "very high"
        else:
            currentUVIStr = "extreme"

    with c2:
        st.write("###")
        st.info("The UV Index in this area is **" + currentUVIStr + "** (" + str(currentUVI) + ").")
        link = '[Find out more about the UV Index.](https://www.epa.gov/sites/default/files/documents/uviguide.pdf)'
        st.markdown(link, unsafe_allow_html=True)

st.write("Wind Speed: " + currentWindSpeedStr)
st.write("Visibility: " + currentVisibilityStr)

st.write("Weather Description: " + currentWeatherStr)

