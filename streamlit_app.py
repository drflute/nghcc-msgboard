
import os, requests, streamlit as st
import pandas as pd
from streamlit import session_state as ss
st.set_page_config(page_title='北門兒主退修會留言板', page_icon='💓', layout='wide')
st.title('北門兒主退修會留言板')
URL = st.secrets["collector_url"]
TOKEN = st.secrets["collector_token"]
def send_message(name: str, message: str):
    payload = {"name": name or "", "message": message or ""}
    params = {"token": TOKEN, "origin": "streamlit.app"}
    r = requests.post(URL, params=params, json=payload, timeout=15)

    # If the response isn't JSON, show the raw text so you see what's wrong.
    ctype = r.headers.get("Content-Type", "")
    if "application/json" not in ctype.lower():
        st.error(f"Collector returned non-JSON (status {r.status_code}).")
        st.code(r.text[:1000])  # show first 1000 chars for debugging
        r.raise_for_status()
        raise RuntimeError("Collector did not return JSON.")

    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("error", "unknown error"))
    return data

@st.cache_data(ttl=60, show_spinner=False)
def fetch_messages():
    params = {"token": TOKEN}
    r = requests.get(URL, params=params, timeout=10)
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("error", "fetch failed"))
    df = pd.DataFrame(data.get("items", []))
    if not df.empty:
        df = df.sort_values("timestamp")
    return df


def fetch_new_messages():
    params = {"token": TOKEN}
    r = requests.get(URL, params=params, timeout=10)
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("error", "fetch failed"))
    df = pd.DataFrame(data.get("items", []))
    if not df.empty:
        df = df.sort_values("timestamp")
    return df

def reload_message(mode):
    try:
        if mode=='cache':
          df = fetch_messages()
        if mode=='new':
          df = fetch_new_messages()
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        # Format to yyyy-mm-dd HH:MM:SS
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df = df.iloc[::-1]
        # st.write(df)
        ss.df=df.copy()
        if df.empty:
            st.info("目前沒有留言。")
        else:

            count=0
            for _, row in df.iterrows():
                ts = str(row["timestamp"])
                user = row.get("name", "匿名")
                msg = row.get("message", "")
                with st.chat_message('user'):
                  if count % 2==0:
                    st.success(msg)
                  if count % 2==1:
                    st.info(msg)
                  # if count % 3==2:
                  #   st.warning(msg)
                  st.write(ts)
                count+=1
                # st.markdown(
                #     f"<div style='border:1px solid #ddd;border-radius:10px;padding:10px;margin-bottom:8px;background:#fff;'>"
                #     f"<div style='font-size:12px;color:#777;margin-bottom:6px;'>{nm} · {ts}</div>"
                #     f"<div style='white-space:pre-wrap;'>{msg}</div></div>",
                #     unsafe_allow_html=True
                # )
    except Exception as e:
        st.error(f"載入留言失敗：{e}")


name = st.text_input("稱呼 (可留白)")
message = st.text_area("留言內容", height=100)
# st.success('hahaha',icon="")
if st.button("送出留言",type='primary'):
    if not message.strip():
        st.error("請輸入留言內容。")
    else:
        try:
            send_message(name, message)
            st.success("已送出 ✅, 耶穌愛你~ 💓",icon="💓")
            st.balloons()
            reload_message('new')
        except Exception as e:
            st.error(f"送出失敗：{e}")

if st.button("載入留言"):
  reload_message('new')
