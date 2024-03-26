import streamlit as st
import json
from mylogger import PerformanceLog
import pandas as pd

@st.cache_data(ttl=600)
def get_chart_data():
    with open("streamlit.log", "r") as f:
        data_list = f.readlines()

    data_dict = {}
    for data in data_list:
        data = json.loads(data)
        if data_dict.get(data["ai_type"], None) is None:
            data_dict[data["ai_type"]] = [PerformanceLog(**data)]
        else:
            data_dict[data["ai_type"]].append(PerformanceLog(**data))
    chart_data_dict = {}
    for key in data_dict.keys():
        chart_data_dict[key] = {
            "st_running_time": 0,
            "ai_running_time": 0,
            "db_running_time": 0,
            "total_count": 0
        }
    for key, value in data_dict.items():
        for val in value:
            val:PerformanceLog
            chart_data_dict[key]["total_count"] += 1
            chart_data_dict[key]["st_running_time"] += val.streamlit_running_time
            chart_data_dict[key]["ai_running_time"] += val.ai_running_time
            chart_data_dict[key]["db_running_time"] += val.db_running_time
        if chart_data_dict[key]["total_count"] != 0:
            chart_data_dict[key]["st_running_time"] /= chart_data_dict[key]["total_count"]
            chart_data_dict[key]["ai_running_time"] /= chart_data_dict[key]["total_count"]
            chart_data_dict[key]["db_running_time"] /= chart_data_dict[key]["total_count"]


    p = {
        "AI Models": [],
        "Running Time(s)": [],
        "Detailed Running Time": []
    }
    for key, val in chart_data_dict.items():
        for i in range(2):
            p["AI Models"].append(key)
        p["Running Time(s)"].append(chart_data_dict[key]["ai_running_time"])
        p["Detailed Running Time"].append("AI")

        p["Running Time(s)"].append(chart_data_dict[key]["db_running_time"])
        p["Detailed Running Time"].append("DB")

        p["AI Models"].append(f"{key}_total")
        p["Running Time(s)"].append(chart_data_dict[key]["st_running_time"])
        p["Detailed Running Time"].append("TOTAL")
        


    chart_data = pd.DataFrame(
    p
    )
    return chart_data
class Performance:
    def __init__(self) -> None:
        pass

    def performance_page(self):
        '''TODO: parse the streamlit.log file and calculate the results
        '''
        chart_data = get_chart_data()
        st.bar_chart(chart_data, x="AI Models", y="Running Time(s)", color="Detailed Running Time")


performance = Performance()