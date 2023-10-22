import json
import datetime
import gspread
import requests
from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.common.by import By
from oauth2client.service_account import ServiceAccountCredentials

translator = Translator()
driver = webdriver.Chrome()
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "/home/lkbrntgh/Desktop/configuration/air/secret_key.json", scopes=scopes
)

date = requests.get("https://api.keybit.ir/time/")
date = date.text
date = json.loads(date)
today_date = date["date"]["full"]["official"]["iso"]["en"]
year = date["date"]["year"]["number"]["en"]
month = date["date"]["month"]["number"]["en"]
day = date["date"]["day"]["number"]["en"]

delta = 10

search_date = f"{year}-{month}-{day}"
if int(day) > (30 - delta):
    search_date = f"{year}-{int(month)+1}-{delta+30-int(day)}"
print(f"search_date : {search_date}")

test_url = f"https://mrbilit.com/flights/THR-OMH??departureDate=1402-08-02"

currency_api_key = "freeRVbZJEXDSQqaSnnUvSxVXzibAACx"

usd_rate = requests.get(f"http://api.navasan.tech/latest/?api_key={currency_api_key}")
usd_rate = usd_rate.text
usd_rate = json.loads(usd_rate)
usd_rate = usd_rate["usd_sell"]["value"]

domestic_0 = f"https://mrbilit.com/flights/THR-OMH??departureDate={search_date}"
domestic_1 = f"https://mrbilit.com/flights/OMH-THR??departureDate={search_date}"
abroad_0 = f"https://mrbilit.com/flights/IKA-TBS?departureDate={search_date}&cabinClass=%2FY&stopCount=0"
abroad_1 = f"https://mrbilit.com/flights/TBS-IKA?departureDate={search_date}&cabinClass=/Y&stopCount=0"

# the-auto-reserve-card-root
# info-section
# card-section-container
# trip-card-container

def flight_info(url):
    driver.get(url)
    elements = []
    while not elements:
        elements = driver.find_elements(By.CLASS_NAME, f"trip-card-wrapper")
    flights = []
    for element in elements:
        flight_info = []
        for i in element.text.splitlines():
            flight_info.append(translator.translate(i).text)
        if len(flight_info) > 11:
            flights.append(flight_info)
    return flights

domestic_0_flights = flight_info(domestic_0)
abroad_0_flights = flight_info(abroad_0)
domestic_1_flights = flight_info(domestic_1)
abroad_1_flights = flight_info(abroad_1)

file = gspread.authorize(creds)
workbook = file.open("Term Homework")
sheet = workbook.get_worksheet(19)

def array_cal(domestic, abroad):
    final = []
    for i in range(min(len(domestic), len(abroad))):
        time_start = domestic[i][2]
        time_end = domestic[i][4]
        start = datetime.datetime.strptime(time_start, "%H:%M")
        end = datetime.datetime.strptime(time_end, "%H:%M")
        time_diff = end - start
        total_seconds = time_diff.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        d_from = domestic[i][3]
        d_to = domestic[i][5]
        d_total_time = f"{hours}:{minutes}",
        d_total_time = d_total_time[0]
        d_distance = 600
        d_class = domestic[i][7]
        d_d_time = f"{search_date} {time_start}"
        d_a_time = f"{search_date} {time_end}"
        d_aircraft = domestic[i][8]
        d_airline = domestic[i][0]
        d_cost_toman = int("".join(filter(str.isdigit, domestic[i][11])))
        rate = 1 / int(usd_rate)
        d_cost_dollar = d_cost_toman / int(usd_rate)
        d_record_period = f"{search_date} {search_date}"
        number_of_records = 1

        time_start = abroad[i][2]
        time_end = abroad[i][5]
        
        a_from = abroad[i][3]
        a_to = abroad[i][6]
        a_total_time = str(abroad[i][4]),
        a_total_time = a_total_time[0]
        a_distance = 881.55
        a_class = abroad[i][8]
        a_d_time = f"{search_date} {time_start}"
        a_a_time = f"{search_date} {time_end}"
        a_aircraft = abroad[i][9]
        a_airline = abroad[i][0]
        a_cost_toman = int("".join(filter(str.isdigit, abroad[i][12])))
        rate = 1 / int(usd_rate)
        a_cost_dollar = d_cost_toman / int(usd_rate)
        a_record_period = f"{search_date} {search_date}"
        number_of_records = 1

        new_flight = [
            d_from,
            d_to,
            d_total_time,
            d_distance,
            d_class,
            d_d_time,
            d_a_time,
            d_aircraft,
            d_airline,
            d_cost_toman,
            rate,
            d_cost_dollar,
            d_record_period,
            number_of_records,
            "",
            a_from,
            "-",
            a_to,
            a_total_time,
            a_distance,
            a_class,
            a_d_time,
            a_a_time,
            a_aircraft,
            a_airline,
            a_cost_toman,
            rate,
            a_cost_dollar,
            a_record_period,
            number_of_records,
        ]
        
        final.append(new_flight)
    print(final)

    sheet.append_rows(final, table_range="A1")

array_cal(domestic_0_flights, abroad_0_flights)
array_cal(domestic_1_flights, abroad_1_flights)