import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv


# =========================================================
# INDIA STATES AND CITIES (major cities per state)
# =========================================================

INDIA_STATES_CITIES = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati"],
    "Arunachal Pradesh": ["Itanagar", "Naharlagun"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur"],
    "Chhattisgarh": ["Raipur", "Bilaspur", "Durg"],
    "Goa": ["Panaji", "Margao"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Manipur": ["Imphal"],
    "Meghalaya": ["Shillong"],
    "Mizoram": ["Aizawl"],
    "Nagaland": ["Kohima", "Dimapur"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela"],
    "Punjab": ["Amritsar", "Ludhiana", "Jalandhar", "Chandigarh"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota"],
    "Sikkim": ["Gangtok"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "Tripura": ["Agartala"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Noida"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Nainital"],
    "West Bengal": ["Kolkata", "Howrah", "Siliguri", "Darjeeling"],
    "Delhi (NCT)": ["New Delhi", "Dwarka", "Rohini"],
    "Jammu and Kashmir": ["Srinagar", "Jammu"],
    "Ladakh": ["Leh", "Kargil"],
}


# =========================================================
# CITY CLASS
# =========================================================

class City:

    def __init__(self, name, state, country="India"):
        self.name = name
        self.state = state
        self.country = country

    def display(self):
        return self.name + ", " + self.state + ", " + self.country


# =========================================================
# WEATHER RECORD CLASS
# =========================================================

class WeatherRecord:

    def __init__(self, date, temperature, rainfall, humidity, condition):
        self.date = date
        self.temperature = temperature
        self.rainfall = rainfall
        self.humidity = humidity
        self.condition = condition

    def validate(self):

        if self.temperature < -60 or self.temperature > 60:
            return False

        if self.rainfall < 0:
            return False

        if self.humidity < 0 or self.humidity > 100:
            return False

        return True

    def to_dict(self):
        return {
            "Date": self.date,
            "Temperature (°C)": self.temperature,
            "Rainfall (mm)": self.rainfall,
            "Humidity (%)": self.humidity,
            "Condition": self.condition,
        }


# =========================================================
# CSV HELPER
# =========================================================

def records_to_csv(records):

    lines = []
    lines.append("Date,Temperature (°C),Rainfall (mm),Humidity (%),Condition")

    for r in records:
        lines.append(
            str(r.date) + "," +
            str(r.temperature) + "," +
            str(r.rainfall) + "," +
            str(r.humidity) + "," +
            str(r.condition)
        )

    return "\n".join(lines)


# =========================================================
# SEASON FUNCTION
# =========================================================

def get_season(date):

    month = int(date.split("-")[1])

    if month == 12 or month == 1 or month == 2:
        return "Winter"

    elif month == 3 or month == 4 or month == 5:
        return "Summer"

    elif month == 6 or month == 7 or month == 8 or month == 9:
        return "Monsoon"

    else:
        return "Post-Monsoon"


# =========================================================
# BULK WEATHER DATA GENERATOR (city/state specific, seeded)
# =========================================================

def generate_bulk_weather_data(city, state, num_records=1000, start_year=2015, end_year=None):

    # Automatically include the current year, including 2026.
    # Data never goes beyond today's date.
    today = datetime.now()

    if end_year is None:
        end_year = today.year

    start_date = datetime(start_year, 1, 1)

    if end_year == today.year:
        end_date = today
    else:
        end_date = datetime(end_year, 12, 31)

    total_days = (end_date - start_date).days

    records = []

    if total_days <= 0:
        return records

    # No random library is used. Values are generated deterministically
    # from the date and city/state so the same selection gives stable data.
    city_seed = 0
    for character in city + state:
        city_seed += ord(character)

    for i in range(num_records):
        day_offset = (i * 37 + city_seed * 13) % (total_days + 1)
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")

        season = get_season(date_str)
        day_value = current_date.toordinal() + city_seed

        if season == "Winter":
            temperature = round(8 + (day_value % 180) / 10, 1)
            rainfall = round((day_value % 81) / 10, 1)
            humidity = round(30 + (day_value % 351) / 10, 1)
            conditions = ["Sunny", "Foggy", "Cloudy", "Clear"]

        elif season == "Summer":
            temperature = round(28 + (day_value % 181) / 10, 1)
            rainfall = round((day_value % 121) / 10, 1)
            humidity = round(15 + (day_value % 351) / 10, 1)
            conditions = ["Sunny", "Hot", "Clear", "Dry"]


        elif season == "Monsoon":
            temperature = round(23 + (day_value % 111) / 10, 1)
            rainfall = round(15 + (day_value % 1651) / 10, 1)
            humidity = round(65 + (day_value % 301) / 10, 1)
            conditions = ["Rainy", "Cloudy", "Stormy", "Heavy Rain"]

        else:
            temperature = round(18 + (day_value % 151) / 10, 1)
            rainfall = round((day_value % 251) / 10, 1)
            humidity = round(45 + (day_value % 301) / 10, 1)
            conditions = ["Cloudy", "Sunny", "Clear", "Humid"]

        condition = conditions[day_value % len(conditions)]
        record = WeatherRecord(date_str, temperature, rainfall, humidity, condition)

        if record.validate():
            records.append(record)

    # Latest date first.
    records.sort(key=lambda r: r.date, reverse=True)

    return records

# =========================================================
# FUTURE WEATHER PREDICTION FUNCTION
# =========================================================

def predict_future_weather(records, future_date_str):

    future_month = int(future_date_str.split("-")[1])
    future_season = get_season(future_date_str)

    month_matches = [r for r in records if int(r.date.split("-")[1]) == future_month]

    # Fall back to season-level data if no exact-month records exist
    if len(month_matches) == 0:
        month_matches = [r for r in records if get_season(r.date) == future_season]

    if len(month_matches) == 0:
        return None

    total_temperature = 0
    total_rainfall = 0
    total_humidity = 0
    rainy_count = 0

    for r in month_matches:

        total_temperature += r.temperature
        total_rainfall += r.rainfall
        total_humidity += r.humidity

        if r.rainfall >= 5 or r.condition in ["Rainy", "Stormy", "Heavy Rain"]:
            rainy_count += 1

    count = len(month_matches)

    average_temperature = round(total_temperature / count, 2)
    average_rainfall = round(total_rainfall / count, 2)
    average_humidity = round(total_humidity / count, 2)
    rain_probability = round((rainy_count / count) * 100, 2)

    if rain_probability >= 50:
        predicted_condition = "Rainy"
    elif average_humidity >= 70 and average_temperature < 30:
        predicted_condition = "Cloudy"
    elif average_temperature >= 33:
        predicted_condition = "Sunny"
    else:
        predicted_condition = "Cloudy" if average_humidity >= 55 else "Sunny"

    return {
        "date": future_date_str,
        "season": future_season,
        "based_on_records": count,
        "average_temperature": average_temperature,
        "average_rainfall": average_rainfall,
        "average_humidity": average_humidity,
        "rain_probability": rain_probability,
        "predicted_condition": predicted_condition
    }


# =========================================================
# CUSTOM-CONDITION WEATHER PREDICTION (rule based, no history)
# =========================================================

def predict_from_conditions(temperature, rainfall, humidity):

    is_rainy = rainfall >= 5 or humidity >= 80

    is_sunny = (
        not is_rainy
        and temperature >= 30
        and humidity < 55
    )

    is_cloudy = (
        not is_rainy
        and not is_sunny
        and humidity >= 55
    )

    # If none of the specific rules match, default to sunny/clear
    if not is_rainy and not is_sunny and not is_cloudy:
        is_sunny = True

    if is_rainy:
        overall_condition = "Rainy"
    elif is_cloudy:
        overall_condition = "Cloudy"
    else:
        overall_condition = "Sunny"

    return {
        "is_rainy": is_rainy,
        "is_sunny": is_sunny,
        "is_cloudy": is_cloudy,
        "overall_condition": overall_condition
    }


# =========================================================
# STREAMLIT CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Weather Data Analysis System",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Weather Data Analysis System")

st.write("### Industry: Climate Analytics")


# =========================================================
# SESSION STATE
# =========================================================

if "weather_records" not in st.session_state:
    st.session_state.weather_records = []

if "selected_city" not in st.session_state:
    st.session_state.selected_city = ""

if "selected_state" not in st.session_state:
    st.session_state.selected_state = ""


# =========================================================
# SIDEBAR
# =========================================================

option = st.sidebar.selectbox(
    "Select Operation",
    [
        "Home",
        "Load Weather Data",
        "Upload CSV Data",
        "Web Scraping",
        "Temperature Analysis",
        "Rainfall Analysis",
        "Seasonal Analysis",
        "Extreme Weather",
        "Add / Find Weather Record",
        "Future Weather Prediction",
        "Weather Report",
        "Historical Data"
    ]
)


# =========================================================
# HOME
# =========================================================

if option == "Home":

    st.header("🌤️ Welcome")

    st.write(
        "Weather Data Analysis System"
    )

    st.write(
        "This project performs climate analytics "
    )

    st.subheader("Project Features")

    st.write("✅ OOP")
    st.write("✅ Bulk Weather Data Generation (1000+ records)")
    st.write("✅ State & City Selection (All India)")
    st.write("✅ Temperature Trend Analysis")
    st.write("✅ Rainfall Analysis")
    st.write("✅ Seasonal Pattern Detection")
    st.write("✅ Extreme Weather Detection")
    st.write("✅ Weather Report Generation")
    st.write("✅ Historical Climate Data")
    st.write("✅ Web Scraping using Requests and BeautifulSoup")
    st.write("✅ CSV Download of Generated / Filtered Data")


# =========================================================
# LOAD WEATHER DATA
# =========================================================

elif option == "Load Weather Data":

    st.header("🌤️ Load Weather Data")

    st.write("Select a state and city, choose the number of records, then generate data.")

    col_a, col_b = st.columns(2)

    with col_a:
        state_name = st.selectbox(
            "Select State",
            sorted(INDIA_STATES_CITIES.keys())
        )

    with col_b:
        city_name = st.selectbox(
            "Select City",
            sorted(INDIA_STATES_CITIES[state_name])
        )

    num_records = st.slider(
        "Number of Records to Generate",
        min_value=10,
        max_value=5000,
        value=100,
        step=10
    )

    if st.button("Generate Weather Data"):

        city = City(city_name, state_name)

        records = generate_bulk_weather_data(
            city_name,
            state_name,
            num_records=num_records
        )

        st.session_state.weather_records = records
        st.session_state.selected_city = city_name
        st.session_state.selected_state = state_name

        st.success(
            str(len(records)) + " weather records generated successfully!"
        )

        st.info(
            "City: " + city.display()
        )

    records = st.session_state.weather_records

    if records:

        st.subheader(
            "Weather Records for "
            + st.session_state.selected_city
            + ", "
            + st.session_state.selected_state
            + " (showing "
            + str(len(records))
            + " records)"
        )

        records_list = [r.to_dict() for r in records]

        st.dataframe(records_list, use_container_width=True, height=400)

        csv_data = records_to_csv(records)

        st.download_button(
            label="📥 Download Generated Data (CSV)",
            data=csv_data,
            file_name=st.session_state.selected_city + "_weather_data.csv",
            mime="text/csv"
        )


# =========================================================
# UPLOAD CSV DATA
# =========================================================

elif option == "Upload CSV Data":

    st.header("📂 Upload Weather CSV File")

    st.write(
        "Upload a CSV file containing State, City, Date, Temperature, "
        "Rainfall, Humidity and Condition."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:

            csv_text = uploaded_file.getvalue().decode("utf-8")
            lines = csv_text.splitlines()
            reader = csv.DictReader(lines)

            required_columns = [
                "State",
                "City",
                "Date",
                "Temperature (°C)",
                "Rainfall (mm)",
                "Humidity (%)",
                "Condition"
            ]

            missing_columns = [
                column for column in required_columns
                if column not in reader.fieldnames
            ]

            if missing_columns:

                st.error(
                    "Missing CSV columns: "
                    + ", ".join(missing_columns)
                )

            else:

                csv_records = []

                for row in reader:

                    try:

                        record = WeatherRecord(
                            row["Date"],
                            float(row["Temperature (°C)"]),
                            float(row["Rainfall (mm)"]),
                            float(row["Humidity (%)"]),
                            row["Condition"]
                        )

                        # Keep State and City with the record
                        # without changing the existing WeatherRecord class.
                        record.state_name = row["State"]
                        record.city_name = row["City"]

                        if record.validate():
                            csv_records.append(record)

                    except (ValueError, TypeError):
                        # Ignore invalid numeric rows.
                        continue

                # Latest date first
                csv_records.sort(
                    key=lambda r: r.date,
                    reverse=True
                )

                st.session_state.weather_records = csv_records

                if csv_records:

                    st.success(
                        str(len(csv_records))
                        + " CSV weather records loaded successfully!"
                    )

                    # -------------------------------------------------
                    # DISPLAY CSV DATA
                    # -------------------------------------------------

                    st.subheader("📊 CSV Weather Data")

                    records_list = []

                    for r in csv_records:
                        records_list.append({
                            "State": getattr(r, "state_name", ""),
                            "City": getattr(r, "city_name", ""),
                            "Date": r.date,
                            "Temperature (°C)": r.temperature,
                            "Rainfall (mm)": r.rainfall,
                            "Humidity (%)": r.humidity,
                            "Condition": r.condition
                        })

                    st.dataframe(
                        records_list,
                        use_container_width=True,
                        height=500
                    )

                    # -------------------------------------------------
                    # LATEST RECORD
                    # -------------------------------------------------

                    st.subheader("🆕 Latest Weather Record")

                    latest_record = csv_records[0]

                    st.dataframe(
                        [{
                            "State": getattr(
                                latest_record, "state_name", ""
                            ),
                            "City": getattr(
                                latest_record, "city_name", ""
                            ),
                            "Date": latest_record.date,
                            "Temperature (°C)": latest_record.temperature,
                            "Rainfall (mm)": latest_record.rainfall,
                            "Humidity (%)": latest_record.humidity,
                            "Condition": latest_record.condition
                        }],
                        use_container_width=True
                    )

                    # -------------------------------------------------
                    # LATEST CITY WEATHER GRAPH
                    # -------------------------------------------------

                    st.subheader("📈 Latest Weather Trend")

                    cities = sorted(
                        list(
                            set(
                                getattr(r, "city_name", "")
                                for r in csv_records
                                if getattr(r, "city_name", "")
                            )
                        )
                    )

                    selected_city = st.selectbox(
                        "Select City",
                        cities,
                        key="csv_graph_city"
                    )

                    city_records = [
                        r for r in csv_records
                        if getattr(r, "city_name", "") == selected_city
                    ]

                    # Sort oldest -> latest so the X-axis follows time.
                    city_records.sort(key=lambda r: r.date)

                    # Show the latest 10 records while preserving date order.
                    latest_city_records = city_records[-10:]

                    if latest_city_records:

                        graph_data = []

                        for r in latest_city_records:
                            graph_data.append({
                                "Date": r.date,
                                "Temperature (°C)": r.temperature,
                                "Rainfall (mm)": r.rainfall,
                                "Humidity (%)": r.humidity
                            })

                        st.subheader(
                            "📈 Temperature Trend by Date - " + selected_city
                        )

                        st.line_chart(
                            graph_data,
                            x="Date",
                            y="Temperature (°C)"
                        )

                        st.subheader(
                            "🌧️ Rainfall Trend by Date - " + selected_city
                        )

                        st.bar_chart(
                            graph_data,
                            x="Date",
                            y="Rainfall (mm)"
                        )

                        st.subheader(
                            "💧 Humidity Trend by Date - " + selected_city
                        )

                        st.line_chart(
                            graph_data,
                            x="Date",
                            y="Humidity (%)"
                        )

                        st.write(
                            "Showing the latest "
                            + str(len(latest_city_records))
                            + " records for "
                            + selected_city
                            + " in date-wise order."
                        )

                        st.subheader("📋 Date-wise Graph Data")

                        st.dataframe(
                            graph_data,
                            use_container_width=True
                        )

                else:

                    st.warning(
                        "No valid weather records were found in the CSV file."
                    )

        except Exception as e:

            st.error(
                "Error while reading CSV file: "
                + str(e)
            )


# =========================================================
# WEB SCRAPING
# =========================================================

elif option == "Web Scraping":

    st.header("🌐 Weather Web Scraping")

    st.write(
        "Enter a webpage URL containing weather information."
    )

    url = st.text_input(
        "Website URL"
    )

    if st.button("Scrape Website"):

        if url == "":

            st.warning(
                "Please enter a URL."
            )

        else:

            try:

                headers = {
                    "User-Agent": "Mozilla/5.0"
                }

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:

                    soup = BeautifulSoup(
                        response.text,
                        "html.parser"
                    )

                    st.success(
                        "Website successfully accessed!"
                    )

                    # Find tables
                    tables = soup.find_all("table")

                    if len(tables) > 0:

                        st.write(
                            "Weather tables found:"
                        )

                        for table in tables:

                            rows = table.find_all("tr")

                            for row in rows:

                                cells = row.find_all(
                                    ["th", "td"]
                                )

                                text = []

                                for cell in cells:

                                    text.append(
                                        cell.get_text(
                                            strip=True
                                        )
                                    )

                                if len(text) > 0:

                                    st.write(text)

                    else:

                        st.write(
                            "No table found."
                        )

                        st.subheader(
                            "Page Text"
                        )

                        text = soup.get_text(
                            " ",
                            strip=True
                        )

                        st.write(
                            text[:5000]
                        )

                else:

                    st.error(
                        "Website could not be accessed."
                    )

            except Exception as e:

                st.error(
                    "Error: " + str(e)
                )


# =========================================================
# TEMPERATURE ANALYSIS
# =========================================================

elif option == "Temperature Analysis":

    st.header("🌡️ Temperature Trend Analysis")

    records = st.session_state.weather_records

    if len(records) == 0:

        st.warning(
            "First load weather data."
        )

    else:

        total = 0

        maximum = records[0].temperature
        minimum = records[0].temperature

        for record in records:

            total = total + record.temperature

            if record.temperature > maximum:
                maximum = record.temperature

            if record.temperature < minimum:
                minimum = record.temperature

        average = total / len(records)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Average Temperature",
            str(round(average, 2)) + " °C"
        )

        col2.metric(
            "Maximum Temperature",
            str(maximum) + " °C"
        )

        col3.metric(
            "Minimum Temperature",
            str(minimum) + " °C"
        )

        st.subheader("📈 Temperature Trend by Date")

        chart_records = sorted(records, key=lambda r: r.date)

        chart_data = []
        for r in chart_records:
            chart_data.append({
                "Date": r.date,
                "Temperature (°C)": r.temperature
            })

        st.line_chart(
            chart_data,
            x="Date",
            y="Temperature (°C)"
        )

        st.dataframe(
            chart_data,
            use_container_width=True,
            height=350
        )


# =========================================================
# RAINFALL ANALYSIS
# =========================================================

elif option == "Rainfall Analysis":

    st.header("🌧️ Rainfall Analysis")

    records = st.session_state.weather_records

    if len(records) == 0:

        st.warning(
            "First load weather data."
        )

    else:

        total = 0

        maximum = records[0].rainfall

        for record in records:

            total = total + record.rainfall

            if record.rainfall > maximum:

                maximum = record.rainfall

        average = total / len(records)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Rainfall",
            str(round(total, 2)) + " mm"
        )

        col2.metric(
            "Average Rainfall",
            str(round(average, 2)) + " mm"
        )

        col3.metric(
            "Maximum Rainfall",
            str(maximum) + " mm"
        )

        st.subheader("📊 Rainfall by Date")

        chart_records = sorted(records, key=lambda r: r.date)

        chart_data = []
        for r in chart_records:
            chart_data.append({
                "Date": r.date,
                "Rainfall (mm)": r.rainfall
            })

        st.bar_chart(
            chart_data,
            x="Date",
            y="Rainfall (mm)"
        )

        st.dataframe(
            chart_data,
            use_container_width=True,
            height=350
        )


# =========================================================
# SEASONAL ANALYSIS
# =========================================================

elif option == "Seasonal Analysis":

    st.header("🍂 Seasonal Pattern Detection")

    records = st.session_state.weather_records

    if len(records) == 0:

        st.warning(
            "First load weather data."
        )

    else:

        seasons = [
            "Winter",
            "Summer",
            "Monsoon",
            "Post-Monsoon"
        ]

        for season in seasons:

            st.subheader(
                "🌿 " + season
            )

            total_temperature = 0
            total_rainfall = 0
            count = 0

            for record in records:

                record_season = get_season(
                    record.date
                )

                if record_season == season:

                    total_temperature += record.temperature
                    total_rainfall += record.rainfall
                    count += 1

            if count > 0:

                average_temperature = (
                    total_temperature / count
                )

                st.write(
                    "Records: " + str(count)
                )

                st.write(
                    "Average Temperature: "
                    + str(
                        round(
                            average_temperature,
                            2
                        )
                    )
                    + " °C"
                )

                st.write(
                    "Total Rainfall: "
                    + str(
                        round(
                            total_rainfall,
                            2
                        )
                    )
                    + " mm"
                )

            else:

                st.write(
                    "No data available."
                )


# =========================================================
# EXTREME WEATHER
# =========================================================

elif option == "Extreme Weather":

    st.header("⚠️ Extreme Weather Detection")

    records = st.session_state.weather_records

    if len(records) == 0:

        st.warning(
            "First load weather data."
        )

    else:

        temperature_limit = st.number_input(
            "Extreme Temperature Limit",
            value=40
        )

        rainfall_limit = st.number_input(
            "Heavy Rainfall Limit",
            value=50
        )

        st.subheader(
            "🔥 Extreme Temperature Events"
        )

        extreme_temp_records = [
            r for r in records if r.temperature >= temperature_limit
        ]

        if extreme_temp_records:
            temp_list = [r.to_dict() for r in extreme_temp_records]
            st.dataframe(temp_list, use_container_width=True, height=300)
        else:
            st.write("No extreme temperature events.")

        st.subheader(
            "🌧️ Heavy Rainfall Events"
        )

        heavy_rain_records = [
            r for r in records if r.rainfall >= rainfall_limit
        ]

        if heavy_rain_records:
            rain_list = [r.to_dict() for r in heavy_rain_records]
            st.dataframe(rain_list, use_container_width=True, height=300)
        else:
            st.write("No heavy rainfall events.")


# =========================================================
# ADD / FIND WEATHER RECORD (latest user-entered record)
# =========================================================

elif option == "Add / Find Weather Record":

    st.header("📝 Add / Find Weather Record")

    tab_add, tab_find = st.tabs(["➕ Add New Record", "🔎 Find a Record"])

    # ---------------- ADD NEW RECORD ----------------

    with tab_add:

        st.write("Enter today's (or any) weather reading. It will be added to your loaded dataset.")

        with st.form("add_record_form", clear_on_submit=True):

            input_date = st.date_input(
                "Date",
                value=datetime.now()
            )

            input_temperature = st.number_input(
                "Temperature (°C)",
                min_value=-60.0,
                max_value=60.0,
                value=30.0,
                step=0.1
            )

            input_rainfall = st.number_input(
                "Rainfall (mm)",
                min_value=0.0,
                value=0.0,
                step=0.1
            )

            input_humidity = st.number_input(
                "Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=60.0,
                step=0.1
            )

            input_condition = st.selectbox(
                "Condition",
                ["Sunny", "Cloudy", "Rainy", "Hot", "Foggy", "Stormy", "Clear", "Humid"]
            )

            submitted = st.form_submit_button("Add Record")

            if submitted:

                new_record = WeatherRecord(
                    input_date.strftime("%Y-%m-%d"),
                    input_temperature,
                    input_rainfall,
                    input_humidity,
                    input_condition
                )

                if new_record.validate():

                    st.session_state.weather_records.append(new_record)

                    st.session_state.weather_records.sort(
                        key=lambda r: r.date
                    )

                    st.success(
                        "New record added for "
                        + new_record.date
                        + "! Total records: "
                        + str(len(st.session_state.weather_records))
                    )

                else:

                    st.error(
                        "Invalid values. Please check temperature, rainfall, and humidity ranges."
                    )

    # ---------------- FIND A RECORD ----------------

    with tab_find:

        records = st.session_state.weather_records

        if len(records) == 0:

            st.warning(
                "No records loaded yet. Generate data or add a record first."
            )

        else:

            st.subheader("📌 Latest Record")

            latest_record = max(records, key=lambda r: r.date)

            st.dataframe(
                [latest_record.to_dict()],
                use_container_width=True
            )

            st.subheader("🔍 Search by Date")

            search_date = st.date_input(
                "Find records on this date",
                value=datetime.now(),
                key="search_date_input"
            )

            search_date_str = search_date.strftime("%Y-%m-%d")

            matches = [r for r in records if r.date == search_date_str]

            if matches:

                st.success(
                    str(len(matches)) + " record(s) found for " + search_date_str
                )

                st.dataframe(
                    [r.to_dict() for r in matches],
                    use_container_width=True
                )

            else:

                st.info(
                    "No record found for " + search_date_str
                )


# =========================================================
# FUTURE WEATHER PREDICTION
# =========================================================

elif option == "Future Weather Prediction":

    st.header("🔮 Future Weather Prediction")

    tab_history, tab_custom = st.tabs(
        ["📅 Predict by Future Date (uses history)", "🎚️ Predict by Custom Conditions"]
    )

    # ---------------- PREDICT USING HISTORICAL DATA ----------------

    with tab_history:

        records = st.session_state.weather_records

        if len(records) == 0:

            st.warning(
                "First load or add weather data (needed to base the prediction on)."
            )

        else:

            st.write(
                "Pick a future date. The prediction is based on historical records "
                "from the same month/season in your current dataset (no data is "
                "fetched from the internet)."
            )

            future_date = st.date_input(
                "Select Future Date",
                value=datetime.now() + timedelta(days=1),
                key="future_date_input"
            )

            future_date_str = future_date.strftime("%Y-%m-%d")

            if st.button("Predict Weather", key="predict_by_date_btn"):

                result = predict_future_weather(records, future_date_str)

                if result is None:

                    st.error(
                        "Not enough historical data to make a prediction. Load more records."
                    )

                else:

                    st.subheader(
                        "Prediction for " + result["date"] + " (" + result["season"] + ")"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Predicted Condition",
                        result["predicted_condition"]
                    )

                    col2.metric(
                        "Rain Probability",
                        str(result["rain_probability"]) + " %"
                    )

                    col3.metric(
                        "Expected Avg Temperature",
                        str(result["average_temperature"]) + " °C"
                    )

                    col4, col5 = st.columns(2)

                    col4.metric(
                        "Expected Avg Rainfall",
                        str(result["average_rainfall"]) + " mm"
                    )

                    col5.metric(
                        "Expected Avg Humidity",
                        str(result["average_humidity"]) + " %"
                    )

                    if result["rain_probability"] >= 50:

                        st.warning(
                            "☔ High chance of rain on this day based on historical patterns."
                        )

                    elif result["predicted_condition"] == "Cloudy":

                        st.info(
                            "☁️ Likely to be cloudy, with a low-to-moderate chance of rain."
                        )

                    else:

                        st.success(
                            "☀️ Likely to be sunny/clear with little to no rain expected."
                        )

                    st.caption(
                        "Based on " + str(result["based_on_records"])
                        + " historical record(s) from the same period."
                    )

    # ---------------- PREDICT USING USER-GIVEN CONDITIONS ----------------

    with tab_custom:

        st.write(
            "Enter your own temperature, rainfall, and humidity values. "
            "This checks Rainy / Sunny / Cloudy directly from the numbers you give "
            "— it does not use any stored history."
        )

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            custom_temperature = st.number_input(
                "Temperature (°C)",
                min_value=-60.0,
                max_value=60.0,
                value=32.0,
                step=0.1,
                key="custom_temp_input"
            )

        with col_b:
            custom_rainfall = st.number_input(
                "Rainfall (mm)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key="custom_rainfall_input"
            )

        with col_c:
            custom_humidity = st.number_input(
                "Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                step=0.1,
                key="custom_humidity_input"
            )

        if st.button("Check Weather Condition", key="predict_by_condition_btn"):

            outcome = predict_from_conditions(
                custom_temperature,
                custom_rainfall,
                custom_humidity
            )

            st.subheader("Result")

            col1, col2, col3 = st.columns(3)

            col1.metric("Rainy?", "Yes" if outcome["is_rainy"] else "No")
            col2.metric("Sunny?", "Yes" if outcome["is_sunny"] else "No")
            col3.metric("Cloudy?", "Yes" if outcome["is_cloudy"] else "No")

            if outcome["overall_condition"] == "Rainy":
                st.warning("☔ Overall prediction: Rainy")
            elif outcome["overall_condition"] == "Cloudy":
                st.info("☁️ Overall prediction: Cloudy")
            else:
                st.success("☀️ Overall prediction: Sunny")


# =========================================================
# WEATHER REPORT
# =========================================================

elif option == "Weather Report":

    st.header("📊 Weather Report Generation")

    records = st.session_state.weather_records

    if len(records) == 0:

        st.warning(
            "First load weather data."
        )

    else:

        total_temperature = 0
        total_rainfall = 0
        total_humidity = 0

        maximum_temperature = records[0].temperature
        minimum_temperature = records[0].temperature

        maximum_rainfall = records[0].rainfall

        for record in records:

            total_temperature += record.temperature
            total_rainfall += record.rainfall
            total_humidity += record.humidity

            if record.temperature > maximum_temperature:

                maximum_temperature = record.temperature

            if record.temperature < minimum_temperature:

                minimum_temperature = record.temperature

            if record.rainfall > maximum_rainfall:

                maximum_rainfall = record.rainfall

        average_temperature = (
            total_temperature / len(records)
        )

        average_rainfall = (
            total_rainfall / len(records)
        )

        average_humidity = (
            total_humidity / len(records)
        )

        report = (
            "WEATHER DATA ANALYSIS REPORT\n"
            "============================\n\n"

            "Location: "
            + st.session_state.selected_city
            + ", "
            + st.session_state.selected_state
            + "\n\n"

            "Report Generated: "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            + "\n\n"

            "Number of Records: "
            + str(len(records))
            + "\n\n"

            "TEMPERATURE STATISTICS\n"
            "----------------------\n"

            "Average Temperature: "
            + str(round(average_temperature, 2))
            + " °C\n"

            "Maximum Temperature: "
            + str(maximum_temperature)
            + " °C\n"

            "Minimum Temperature: "
            + str(minimum_temperature)
            + " °C\n\n"

            "RAINFALL STATISTICS\n"
            "-------------------\n"

            "Total Rainfall: "
            + str(round(total_rainfall, 2))
            + " mm\n"

            "Average Rainfall: "
            + str(round(average_rainfall, 2))
            + " mm\n"

            "Maximum Rainfall: "
            + str(maximum_rainfall)
            + " mm\n\n"

            "HUMIDITY STATISTICS\n"
            "-------------------\n"

            "Average Humidity: "
            + str(round(average_humidity, 2))
            + " %\n"
        )

        st.text_area(
            "Generated Weather Report",
            report,
            height=400
        )

        st.download_button(
            label="📥 Download Weather Report",
            data=report,
            file_name="weather_report.txt",
            mime="text/plain"
        )


# =========================================================
# HISTORICAL DATA
# =========================================================

elif option == "Historical Data":

    st.header("🗄️ Historical Climate Data")

    records = st.session_state.weather_records

    if len(records) == 0:

        st.warning(
            "No historical data available. Go to 'Load Weather Data' first."
        )

    else:

        st.write(
            "Total Records: " + str(len(records))
        )

        records_list = [r.to_dict() for r in records]

        st.dataframe(records_list, use_container_width=True, height=500)

        csv_data = records_to_csv(records)

        st.download_button(
            label="📥 Download Historical Data (CSV)",
            data=csv_data,
            file_name="historical_weather_data.csv",
            mime="text/csv"
        )

        st.success(
            "Historical climate data is ready."
        )