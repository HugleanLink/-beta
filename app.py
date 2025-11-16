import os
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import io

data = "metar_data"

def ReadMetar(path):
    df = pd.read_csv(path)
    df.columns = ["ICAO", "Time", "Metar"]
    
    temperature = []
    for metar in df["Metar"]:
        parts = metar.split()
        temp = None
        for p in parts:
            # 寻找类似  M06/M07  或  06/07 的部分
            if "/" in p and len(p) <= 7:
                t = p.split("/")[0]
                if t.startswith("M"):
                    temp = -int(t[1:])
                elif t[0].isdigit():
                    temp = int(t)
                break
        temperature.append(temp)

    df["Temp_C"] = temperature
    df["Time"] = pd.to_datetime(df["Time"])
    df["month"] = df["Time"].dt.month
    df["half_hour"] = df["Time"].dt.hour * 2 + df["Time"].dt.minute // 30
    return df


def ReadAirports():
    airports = []
    for item in os.listdir(data):
        if os.path.isdir(os.path.join(data, item)):
            airports.append(item)
    return sorted(airports)


def ReadYears(airport):
    years = []
    path = os.path.join(data, airport)
    for f in os.listdir(path):
        if f.endswith(".txt"):
            years.append(f.replace(".txt", ""))
    return sorted(years)


airports = ReadAirports()
airport = st.selectbox("选择机场", airports)
years = ReadYears(airport)
year = st.selectbox("选择年份", years)

filepath = f"{data}/{airport}/{year}.txt"
st.info(f"当前读取：{filepath}")

df = ReadMetar(filepath)
pivot = df.groupby(["month", "half_hour"])["Temp_C"].mean().unstack()

fig, ax = plt.subplots(figsize=(18, 6))
sns.heatmap(
    pivot,
    cmap="coolwarm",
    linewidths=0.3,
    cbar_kws={"label": "气温 (°C)"},
    ax=ax
)

ax.set_title(f"{airport} {year} 温度热力图")
ax.set_xlabel("时间")
ax.set_ylabel("月份")

ax.set_xticks(range(0, 48, 2))
ax.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

st.pyplot(fig)

buf = io.BytesIO()
fig.savefig(buf, format='png')
st.download_button("下载 PNG", data=buf.getvalue(), file_name=f"{airport}_{year}.png")




