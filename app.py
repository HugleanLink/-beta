import os
import io
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt


st.set_page_config(page_tite="气温热图查询",layout="wide")
data="metar_data"


def ReadMetar(path):
    temperatures = []
    df=pd.read_csv(path)
    df.columns["ICAO","Time","Metar"]
    for i1 in df["Metar"]:
        parts=i1.split()
        temperature=None
        for i2 in parts:
            if "/" in i2 and len(i2)<=7 and ("M" in i2 or i2[0].isdigit()):
                PositiveOrNegative=i2.split("/")[0]
                if  PositiveOrNegative.startwith("M"):
                    temperature=-int(PositiveOrNegative[1:])
                else:
                    temperature=int(PositiveOrNegative)
            else:
                pass
        temperatures.append(temperature)
    df["Temp_C"]=temperatures
    df["Time"]=pd.to_datetime(df["Time"])
    df["Month"]=df["Time"].dt.month
    df["hour"] = df["Time"].dt.hour
    return df


def ReadAirports():
    WhatAirport=[]
    for item in os.listdir(data):
        if os.path.isdir(os.path.join(data, item)):
            WhatAirport.append(item)
    return sorted(WhatAirport)


def Readyears(airport):
    WhatYear = []
    path = os.path.join(data, airport)
    for f in os.listdir(path):
        if f.endswith(".txt"):
            WhatYear.append(f.replace(".txt", ""))
    return sorted(WhatYear)


st.title("气温热图查询")
airports= ReadAirports()
airport=st.selectbox("选择要查询的机场",airports)
years=Readyears(airport)
year=st.selectbox("选择要查询的年份",years)
filepath=f"{data}/{airport}/{year}.txt"
df=ReadMetar(filepath)


pivot = df.groupby(["month", "hour"])["Temp_C"].mean().unstack()
plt.figure(figsize=(18, 6))
sns.heatmap(pivot,camp="coolwarm",linewidths=0.3,cbar_kws={"label": "Temperature (°C)"})
plt.title(f"{airport} {year} HeatMap")
plt.xlabel("Time")
plt.ylabel("Month")
plt.xticks(
    ticks=range(24),
    labels=[f"{h:02d}:00" for h in range(24)],
    rotation=45
)
plt.yticks(rotation=0)


st.pyplot(plt)
buf = io.BytesIO()
plt.savefig(buf, format='png')
st.download_button("下载 PNG", data=buf.getvalue(), file_name=f"{airport}_{year}.png")










