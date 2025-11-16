import os
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="METAR 温度热图", layout="wide")
data="metar_data"

def ReadMetar(path):
    dataframe=pd.read_csv(path)
    dataframe.columns=["ICAO", "Time", "Metar"]
    temperature=[]
    for i in dataframe["Metar"]:
        parts=i.split()
        temp=None
        for i1 in parts:
            if "/" in i1 and len(i1)<=7 and ("M" in i1 or i1[0].isdigit()):
                tem=i1.split("/")[0]
                if tem.startswith("M"):
                    temp = -int(tem[1:])
                else:
                    temp = int(tem)
            else:
                pass
        temperature.append(temp)
    dataframe["Temp_C"]=temperature
    dataframe["Time"] = pd.to_datetime(dataframe["Time"])
    dataframe["month"] = dataframe["Time"].dt.month
    dataframe["half_hour"]=dataframe["Time"].dt.hour * 2 + dataframe["Time"].dt.minute // 30
    return dataframe


def ReadAirports():
    airports=[]
    whatisinside=os.listdir(data)
    for i3 in whatisinside:
        full_path=os.path.join(data, i3)
        if os.path.isdir(full_path):
            airports.append(i3)
            SortedAirports=sorted(airports)
    return SortedAirports


def ReadYears(airport):
    years=[]
    path1=os.path.join(data, airport)
    flies=os.listdir(path1)
    for i4 in flies:
        if i4.endswith(".txt"):
            i4.replace(".txt", "")
            years.append(i4)
    return sorted(years)


airports=ReadAirports()
airport=st.selectbox("选择机场", airports)
years = ReadYears(airport)
year = st.selectbox("选择年份", years)
filepath = f"{data}/{airport}/{year}.txt"
st.info(f"当前读取：{filepath}")
df = ReadMetar(filepath)
pivot = df.groupby(["month", "half_hour"])["Temp_C"].mean().unstack()


plt.figure(figsize=(18, 6))
sns.heatmap(
    pivot,
    cmap="coolwarm",
    linewidths=0.3,
    cbar_kws={"label": "气温 (°C)"}
)
plt.title(f"{airport} {year} 温度热力图")
plt.xlabel("时间")
plt.ylabel("月份")
plt.xticks(
    ticks=range(0, 48, 2),
    labels=[f"{h:02d}:00" for h in range(24)],
    rotation=45
)
plt.yticks(rotation=0)
fig, ax = plt.subplots()
st.pyplot(plt)


buf = io.BytesIO()
plt.savefig(buf, format='png')
st.download_button("下载 PNG", data=buf.getvalue(), file_name=f"{airport}_{year}.png")

