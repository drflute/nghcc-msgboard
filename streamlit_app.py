
import os, requests, streamlit as st
import pandas as pd
# URL = 'https://script.google.com/macros/s/AKfycbynOv4uMZUt5IscBJGJLoHblkN28BYdaap7oUzmm2gVxYhoikjxpf86bk7ob9h05bSNmQ/exec'
URL = 'https://script.google.com/macros/s/AKfycbwR2CIurvU4iK17AOCFRmC5WezpQHeTxzkKGupAbd1wDk4sOUw8tunagxGljO8gywmpkQ/exec'
TOKEN  = 'set-a-random-long-token'


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

name = st.text_input("稱呼 (可留白)")
message = st.text_area("留言內容", height=100)

if st.button("送出 Submit"):
    if not message.strip():
        st.error("請輸入留言內容。")
    else:
        try:
            send_message(name, message)
            st.success("已送出 ✅")
        except Exception as e:
            st.error(f"送出失敗：{e}")


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


st.title("留言板 Message Board")

# Show message list
if st.button("載入留言 Load messages"):
    try:
        df = fetch_messages()
        if df.empty:
            st.info("目前沒有留言。")
        else:
            for _, row in df.iterrows():
                ts = str(row["timestamp"])
                nm = row.get("name", "匿名")
                msg = row.get("message", "")
                st.markdown(
                    f"<div style='border:1px solid #ddd;border-radius:10px;padding:10px;margin-bottom:8px;background:#fff;'>"
                    f"<div style='font-size:12px;color:#777;margin-bottom:6px;'>{nm} · {ts}</div>"
                    f"<div style='white-space:pre-wrap;'>{msg}</div></div>",
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.error(f"載入留言失敗：{e}")
