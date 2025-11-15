from os import write
from altair.vegalite.v5.schema import ParameterName
import requests
import streamlit as st
import pandas as pd
import altair as alt

st.title("台灣氣象資料 Dashboard")

API_KEY="CWA-89A375B4-FEED-4029-9E3D-CEAAACC7EF6B"
LOCATION=st.selectbox("選擇城市",["Taipei","Taichung","Kaohsiung"])

url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-89A375B4-FEED-4029-9E3D-CEAAACC7EF6B"
res = requests.get(url)
data = res.json()

location =data['records']['location'][0]
st.subheader(f"{location['locationName']}36小時預報")

for element in location["weatherElement"]:
  name = element["elementName"]
  value = element["time"][0]["parameter"]["parameterName"]
  st.write(f"{name}：{value}")

#圖表
weather_data = []
for element in location["weatherElement"]:
    elem = element["elementName"]
    for t in element["time"]:
        weather_data.append({
            "element": elem,
            "startTime": t["startTime"],
            "value": t["parameter"]["parameterName"]
        })

df = pd.DataFrame(weather_data)

# 使用 MinT、MaxT 製作平均氣溫
temp_min = df[df["element"] == "MinT"].rename(columns={"value": "MinT"})
temp_max = df[df["element"] == "MaxT"].rename(columns={"value": "MaxT"})

temp_df = pd.merge(temp_min[["startTime", "MinT"]],
                   temp_max[["startTime", "MaxT"]],
                   on="startTime")

temp_df["MinT"] = temp_df["MinT"].astype(float)
temp_df["MaxT"] = temp_df["MaxT"].astype(float)
temp_df["Temp"] = (temp_df["MinT"] + temp_df["MaxT"]) / 2

# 降雨機率 PoP
rain_df = df[df["element"] == "PoP"][["startTime", "value"]]
rain_df["value"] = rain_df["value"].astype(float)
rain_df.rename(columns={"value": "PoP"}, inplace=True)

# 合併資料
chart_df = pd.merge(temp_df, rain_df, on="startTime")
chart_df["startTime"] = pd.to_datetime(chart_df["startTime"])

# --- Altair 圖表 ---
temp_line = alt.Chart(chart_df).mark_line(color="red").encode(
    x="startTime:T",
    y=alt.Y("Temp:Q", title="平均氣溫 (°C)"),
    tooltip=["startTime:T", "Temp"]
)

rain_line = alt.Chart(chart_df).mark_line(color="blue").encode(
    x="startTime:T",
    y=alt.Y("PoP:Q", title="降雨機率 (%)"),
    tooltip=["startTime:T", "PoP"]
)

st.altair_chart(temp_line + rain_line, use_container_width=True)