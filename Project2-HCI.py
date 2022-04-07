from time import strftime

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
    layout="wide",
    menu_items=None
)

c1, c2 = st.columns([2, 1])

response = {}

with c2:
    # search or get city from ip
    st.write("#")
    st.write("###")
    st.write("###")
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

    # get response from openWeatherMap api
    apiKey = "f2753510aec1cb9ef2f826c3edd452ad"
    apiURL = "https://api.openweathermap.org/data/2.5/onecall?lat="+str(lat)+"&lon="+str(lon)+"&appid=" + apiKey
    response = rq.get(apiURL).json()

    #parse response
    utcTime = dt.datetime.utcnow()
    systemTime = dt.datetime.now()
    myOffset = systemTime.timestamp() - utcTime.timestamp()

    currentDateTime = dt.datetime.fromtimestamp(response["current"]["dt"] - myOffset + response["timezone_offset"])
    currentDateTimeStr = currentDateTime.strftime("%I:%M %p")
    sunriseToday = dt.datetime.fromtimestamp(response["current"]["sunrise"] - myOffset + response["timezone_offset"])
    sunriseTodayStr = sunriseToday.strftime("%I:%M %p")
    sunsetToday = dt.datetime.fromtimestamp(response["current"]["sunset"] - myOffset + response["timezone_offset"])
    sunsetTodayStr = sunsetToday.strftime("%I:%M %p")

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

    seeUVI = st.checkbox("See UV Index information.")
    if seeUVI:
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
        st.info("The UV Index in this area is **" + currentUVIStr + "** (" + str(currentUVI) + ").")
        UVILabel = [""]
        UVIWidth = 2
        UVIYTicks = [0, 3, 6, 8, 11]

        UVIfig, UVIax = plt.subplots()

        UVIax.bar(UVILabel, 9.9, UVIWidth, bottom=11, label='Extreme', color="#B94375")
        UVIax.bar(UVILabel, 2.9, UVIWidth, bottom=8, label='Very High', color="#C73734")
        UVIax.bar(UVILabel, 1.9, UVIWidth, bottom=6, label='High', color="#E09945")
        UVIax.bar(UVILabel, 2.9, UVIWidth, bottom=3, label='Moderate', color="#F9DC4F")
        UVIax.bar(UVILabel, 2.9, UVIWidth, bottom=0, label='Low', color="#8DBF89")
        UVIax.plot(0.5, currentUVI, "k*", markersize=20)

        UVIax.set_title("UV Index", fontsize=20)
        UVIax.set_yticks(UVIYTicks)
        plt.yticks(fontsize=12)
        UVIax.set_xticks([])
        UVIax.spines["top"].set_visible(False)
        UVIax.spines["left"].set_visible(False)
        UVIax.spines["right"].set_visible(False)
        UVIax.spines["bottom"].set_visible(False)
        plt.xlim(0, 1)
        plt.ylim(0, 15)
        UVIax.legend(fontsize=12)
        st.pyplot(UVIfig)

        link = '[Find out more.](https://www.epa.gov/sites/default/files/documents/uviguide.pdf)'
        st.markdown(link, unsafe_allow_html=True)

# TODO: get hourly forecast from response

# all info should be available now, the rest of the app is below

# display all possible information

with c1:
    # header
    cityShortName = ""
    for i in range(len(city)):
        if city[i] != ',':
            cityShortName += city[i]
            continue
        break
    st.title("Weather in " + cityShortName)
    st.markdown("""
        <style>
            .big-font {
                font-size:8rem !important;
            }
            .small-font {
                font-size:3rem !important;
            }
            .little-font {
                font-size:
            }
            .my {
            line-height:1.1;
            }
        </style>
    """, unsafe_allow_html=True)

    icon = response["current"]["weather"][0]["icon"]
    iconSource = "http://openweathermap.org/img/wn/" + icon + "@2x.png"

    st.markdown("""
        <div class='my' style='background:lightblue; padding:1rem; margin-bottom:1rem; border-radius:1rem'>
            <span style='display:flex; align-items:center; margin:0; padding:0;'>
                <p style='display: inline; margin:0; padding:0;' class='big-font'>""" + currentTempStr + """</p>
                <img style='display: inline; margin:0; padding:0; width: 8rem; height: 8rem;' src='""" + iconSource + """' width='0' height='0'>
                <div style='height:100%; width:100%;'>
                    <p class='small-font'>""" + currentDateTimeStr + """</p>
                    <p class='small-font'>12:59PM</p>
                </div>
            </span>
            <p style='margin:0; padding:0;' class='small-font'><i>""" + currentWeatherStr + """</i></p>
            <p style='margin:0; padding:0;' class='small-font'>Feels like """ + currentFeelsLikeStr + """</p>
            <p style='margin:0; padding:0;' class='small-font'>Humidity: """ + currentHumidityStr + """</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("Current Time: " + str(currentDateTime))
    st.write("Sunrise Today: " + str(sunriseToday))
    st.write("Sunset Today: " + str(sunsetToday))

    st.write("Current Temperature: " + currentTempStr)
    st.write("Feels Like: " + currentFeelsLikeStr)
    st.write("Dew Point: " + currentDewPointStr)

    st.write("Pressure: " + currentPressureStr)

    st.write("Clouds: " + currentCloudsStr)
    st.write("Humidity: " + currentHumidityStr)

    st.write("Wind Speed: " + currentWindSpeedStr)
    st.write("Visibility: " + currentVisibilityStr)

    st.write("Weather Description: " + currentWeatherStr)

