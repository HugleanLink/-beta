import os
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="METAR 温度热图", layout="wide")

DATA_DIR = "metar_data"


# 解析 txt 为 DataFrame：按你的格式定制的
def load_metar_file(path):
    df = pd.read_csv(path)

    # 确保列名一致
    df.columns = ["ICAO", "Time", "Metar"]

    # 从 METAR 中提取温度
    # METAR 里温度格式如：M06/M07 或 01/M05
    temps = []
    for m in df["Metar"]:
        parts = m.split()
        temp = None
        for p in parts:
            if "/" in p and len(p) <= 7 and ("M" in p or p[0].isdigit()):
                try:
                    t = p.split("/")[0]
                    if t.startswith("M"):
                        temp = -int(t[1:])
                    else:
                        temp = int(t)
                    break
                except:
                    pass
        temps.append(temp)

    df["Temp_C"] = temps

    df["Time"] = pd.to_datetime(df["Time"])
    df["month"] = df["Time"].dt.month
    df["half_hour"] = df["Time"].dt.hour * 2 + df["Time"].dt.minute // 30

    return df


# 自动扫描所有机场
def get_airports():
    return sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])


# 自动扫描年份
def get_years(airport):
    files = os.listdir(os.path.join(DATA_DIR, airport))
    years = [f.replace(".txt", "") for f in files if f.endswith(".txt")]
    return sorted(years)


st.title("METAR 全年温度热图生成器")

airports = get_airports()
airport = st.selectbox("选择机场", airports)

years = get_years(airport)
year = st.selectbox("选择年份", years)

filepath = f"{DATA_DIR}/{airport}/{year}.txt"

st.info(f"当前读取：{filepath}")

df = load_metar_file(filepath)

# 构建热图透视表
pivot = df.groupby(["month", "half_hour"])["Temp_C"].mean().unstack()

# 做图
plt.figure(figsize=(18, 6))
sns.heatmap(
    pivot,
    cmap="coolwarm",
    linewidths=0.3,
    cbar_kws={"label": "Temperature (°C)"}
)
plt.title(f"{airport} {year} HeatMap")
plt.xlabel("Time")
plt.ylabel("Month")

plt.xticks(
    ticks=range(0, 48, 2),
    labels=[f"{h:02d}:00" for h in range(24)],
    rotation=45
)
plt.yticks(rotation=0)

st.pyplot(plt)
buf = io.BytesIO()
fig.savefig(buf, format='png')
st.download_button("下载 PNG", data=buf.getvalue(), file_name=f"{airport}_{year}.png")







