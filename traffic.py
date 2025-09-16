import streamlit as st
import pymysql
import mysql.connector
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
def get_data(query, params=None):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jan@9302",
        database="traffic"
    )
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df
def fetch_data(query, params=None):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jan@9302",
        database="traffic"
    )
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(result, columns=columns)
    cursor.close()
    conn.close()
    return df
    
    # ------------------ Streamlit Page Config ------------------
st.set_page_config(page_title="Traffic Stops Dashboard", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Introduction", "Data Explorer", "SQL Analytics", "Traffic Log", "Visual Trends", "Creator Info"]
)

# ------------------ 1. Introduction Page ------------------
if page == "Introduction":
    st.title("🚦 Traffic Stops Data Dashboard")
    st.write("""
    This dashboard provides insights into traffic stop incidents, driver demographics,
    violations, arrest/search rates, and more using SQL queries and visual analytics.
    """)

# ------------------ 2. Data Explorer ------------------
elif page == "Data Explorer":
    st.title(" Explore Traffic Data")

    df = get_data("SELECT * FROM traffic_data LIMIT 100")
    st.write("### Sample Data", df)

    gender = st.selectbox("Filter by Gender", ["All", "M", "F"])
    violation = st.text_input("Search Violation")

    query = "SELECT * FROM traffic_data WHERE 1=1"
    params = {}

    if gender != "All":
        query += " AND driver_gender=:gender"
        params['gender'] = gender
    if violation:
        query += " AND violation LIKE :violation"
        params['violation'] = f"%{violation}%"

    df_filtered = get_data(query, params)
    st.dataframe(df_filtered)

# ------------------ 3. SQL Analytics ------------------
elif page == "SQL Analytics":
    st.title("SQL Analytics")

queries = {
    "Vehicle-Based": {
        "Top 10 vehicle numbers in drug-related stops":
            "SELECT vehicle_number, COUNT(*) AS count "
            "FROM traffic_data "
            "WHERE violation = 'DUI' "
            "GROUP BY vehicle_number "
            "ORDER BY count DESC LIMIT 10",

        "Vehicles most frequently searched":
            "SELECT vehicle_number, AVG(search_conducted='TRUE') AS search_rate "
            "FROM traffic_data "
            "GROUP BY vehicle_number "
            "ORDER BY search_rate DESC LIMIT 10"
    },

    "Demographic-Based": {
        "Driver age group with highest arrest rate":
            "SELECT driver_age, AVG(is_arrested='TRUE') AS arrest_rate "
            "FROM traffic_data "
            "GROUP BY driver_age "
            "ORDER BY arrest_rate DESC",

        "Gender distribution by country":
            "SELECT country_name, driver_gender, COUNT(*) AS count "
            "FROM traffic_data "
            "GROUP BY country_name, driver_gender",

        "Race & gender combination with highest search rate":
            "SELECT driver_race, driver_gender, AVG(search_conducted='TRUE') AS search_rate "
            "FROM traffic_data "
            "GROUP BY driver_race, driver_gender "
            "ORDER BY search_rate DESC LIMIT 1"
    },

    "Time & Duration-Based": {
        "Most traffic stops by hour":
            "SELECT HOUR(stop_time) AS hour, COUNT(*) AS stops "
            "FROM traffic_data "
            "GROUP BY hour "
            "ORDER BY stops DESC",

        "Average stop duration by violation":
            "SELECT violation, AVG(stop_duration) AS avg_duration "
            "FROM traffic_data "
            "GROUP BY violation "
            "ORDER BY avg_duration DESC",

        "Night stops leading to arrests":
            "SELECT AVG(is_arrested='TRUE') AS night_arrest_rate "
            "FROM traffic_data "
            "WHERE HOUR(stop_time) >= 20 OR HOUR(stop_time) < 6"
    },

    "Violation-Based": {
        "Violations associated with searches/arrests":
            "SELECT violation, AVG(search_conducted='TRUE') AS search_rate, AVG(is_arrested='TRUE') AS arrest_rate "
            "FROM traffic_data "
            "GROUP BY violation "
            "ORDER BY search_rate DESC, arrest_rate DESC",

        "Violations most common among drivers <25":
            "SELECT violation, COUNT(*) AS count "
            "FROM traffic_data "
            "WHERE driver_age < 25 "
            "GROUP BY violation "
            "ORDER BY count DESC",

        "Violations rarely resulting in search/arrest":
            "SELECT violation, AVG(search_conducted='TRUE') AS search_rate, AVG(is_arrested='TRUE') AS arrest_rate "
            "FROM traffic_data "
            "GROUP BY violation "
            "HAVING search_rate < 0.05 AND arrest_rate < 0.05"
    },

    "Location-Based": {
        "Countries with highest drug-related stops":
            "SELECT country_name, COUNT(*) AS count "
            "FROM traffic_data "
            "WHERE violation LIKE '%drug%' "
            "GROUP BY country_name "
            "ORDER BY count DESC",

        "Arrest rate by country & violation":
            "SELECT country_name, violation, AVG(is_arrested='TRUE') AS arrest_rate "
            "FROM traffic_data "
            "GROUP BY country_name, violation "
            "ORDER BY arrest_rate DESC",

        "Country with most stops with search conducted":
            "SELECT country_name, COUNT(*) AS count "
            "FROM traffic_data "
            "WHERE search_conducted='TRUE' "
            "GROUP BY country_name "
            "ORDER BY count DESC"
    },

    "Complex Queries": {
        "Yearly breakdown of stops & arrests by country":
            "SELECT country_name, YEAR(stop_date) AS year, COUNT(*) AS stops, AVG(is_arrested='TRUE') AS arrest_rate "
            "FROM traffic_data "
            "GROUP BY country_name, year "
            "ORDER BY year, country_name",

        "Driver violation trends by age & race":
            "SELECT driver_age, driver_race, violation, COUNT(*) AS count "
            "FROM traffic_data "
            "GROUP BY driver_age, driver_race, violation "
            "ORDER BY count DESC",

        "Time period analysis of stops (Year/Month/Hour)":
            "SELECT YEAR(stop_date) AS year, MONTH(stop_date) AS month, HOUR(stop_time) AS hour, COUNT(*) AS stops "
            "FROM traffic_data "
            "GROUP BY year, month, hour "
            "ORDER BY year, month, hour",

        "Top 5 violations with highest arrest rates":
            "SELECT violation, AVG(is_arrested='TRUE') AS arrest_rate "
            "FROM traffic_data "
            "GROUP BY violation "
            "ORDER BY arrest_rate DESC LIMIT 5"
    }
}
category = st.selectbox("Select Query Category", list(queries.keys()))
query_name = st.selectbox("Select Query", list(queries[category].keys()))
query = queries[category][query_name]

st.write(f"**Running Query:** {query_name}")
df_query = get_data(query)
st.dataframe(df_query)  
#-------------4. Traffic Log Prediction ------------ 
def get_data(query):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jan@9302",
        database="traffic"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df
data = get_data("SELECT * FROM traffic_data")
with st.form("traffic_log_form", clear_on_submit=True):
    st.title(" Traffic Log and Prediction")

    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["Male", "Female"])
    driver_age_raw = st.text_input("Driver Age (Raw)")
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.selectbox("Driver Race", data['driver_race'].dropna().unique())
    violation_raw = st.text_input("Violation (Raw)")
    search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    stop_outcome_input = st.text_input("Stop Outcome (Optional)")
    is_arrested = st.selectbox("Was Driver Arrested?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    drugs_related_stop = st.selectbox("Drug Related Stop?", ["0", "1"])
    vehicle_number = st.text_input("Vehicle Number")
    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

if submitted:
    filtered_data = data[
        (data['driver_gender'] == driver_gender) &
        (data['driver_age'] == driver_age) &
        (data['search_conducted'] == search_conducted) &
        (data['stop_duration'] == stop_duration)
    ]
    
    if not filtered_data.empty:
        predicted_outcome = filtered_data['stop_outcome'].mode()[0]
        predicted_violation = filtered_data['violation'].mode()[0]
    else:
        predicted_outcome = "warning"
        predicted_violation = "speeding"

    st.markdown(f"""
    **Prediction Summary**
    - **Predicted Violation:** {predicted_violation}
    - **Predicted Stop Outcome:** {predicted_outcome}
    """)    
# ------------------ 5. Visual Trends ------------------
# elif page == "Visual Trends":
st.title("Visual Trends")
hourly_query = """
SELECT HOUR(stop_time) AS hour, COUNT(*) AS stops
FROM traffic_data
GROUP BY hour
ORDER BY hour
"""
hourly_counts = get_data(hourly_query)
hourly_counts['hour'] = hourly_counts['hour'].astype(int)  # ensure numeric
st.subheader("Hourly Traffic Stops")
st.line_chart(hourly_counts.set_index('hour'))

# ------------------ Monthly Stops ------------------
monthly_query = """
SELECT MONTH(stop_date) AS month, COUNT(*) AS stops
FROM traffic_data
GROUP BY month
ORDER BY month
"""
monthly_counts = get_data(monthly_query)
monthly_counts['month'] = monthly_counts['month'].astype(int)
st.subheader("Monthly Traffic Stops")
st.line_chart(monthly_counts.set_index('month'))

# ------------------ Yearly Stops ------------------
yearly_query = """
SELECT YEAR(stop_date) AS year, COUNT(*) AS stops
FROM traffic_data
GROUP BY year
ORDER BY year
"""
yearly_counts = get_data(yearly_query)
yearly_counts['year'] = yearly_counts['year'].astype(int)
st.subheader("Yearly Traffic Stops")
st.line_chart(yearly_counts.set_index('year'))
# ------------------ 6. Creator Info ----------------
# elif page == "Creator Info":
st.title(" Creator of this Project")
st.write("""
**Developed by:** JANANI ELANGO
    **Skills:** Python, SQL, Data Analysis, Streamlit, Pandas
""")