import streamlit as st
from bs4 import BeautifulSoup, FeatureNotFound
import requests
import pandas as pd
import base64
import plotly.graph_objects as go
import json

import firebase_admin
from firebase_admin import credentials, db

# ---------------- FIREBASE INIT ----------------
if not firebase_admin._apps:
    key_dict = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(
        cred,
        {"databaseURL": "https://ugc-net-marks-f2f20-default-rtdb.firebaseio.com/"}
    )

# ---------------- CONFIG ----------------
PAPER1_COUNT = 50
PAPER2_COUNT = 100

# ---------------- HELPERS ----------------
def get_best_soup(content):
    for p in ["html5lib", "lxml", "html.parser"]:
        try:
            return BeautifulSoup(content, p)
        except FeatureNotFound:
            continue
    raise FeatureNotFound

def encode_url(url):
    return base64.urlsafe_b64encode(url.encode()).decode()

def save_to_firebase(url, name, roll, application, total_marks):
    key = encode_url(url)
    ref = db.reference(f"results/{key}")
    if ref.get() is not None:
        return False

    ref.set({
        "candidate_name": name,
        "roll_no": roll,
        "application_no": application,
        "total_marks": total_marks,
        "url": url
    })
    return True

# ---------------- PLOTLY PIE ----------------
def animated_pie(title, correct, wrong, colors):
    fig = go.Figure(
        data=[go.Pie(
            labels=["Correct", "Wrong"],
            values=[correct, wrong],
            hole=0.5,
            pull=[0.08, 0],
            marker=dict(colors=colors),
            textinfo="label+percent"
        )]
    )
    fig.update_layout(title=title, title_x=0.5)
    return fig

# ---------------- FULL ACTUAL ANSWER KEY ----------------
actual_answer = {
'4255894905':'2','4255894906':'4','4255894907':'1','4255894908':'3','4255894909':'2',
'4255894910':'1','4255894911':'2','4255894912':'2','4255894913':'3','4255894914':'3',
'4255894915':'2','4255894916':'3','4255894917':'2','4255894918':'3','4255894919':'3',
'4255894920':'1','4255894921':'2','4255894922':'2','4255894923':'1','4255894924':'3',
'4255894925':'1','4255894926':'1','4255894927':'1','4255894928':'2','4255894929':'1',
'4255894930':'3','4255894931':'2','4255894932':'1','4255894933':'4','4255894934':'3',
'4255894935':'1','4255894936':'2','4255894937':'3','4255894938':'4','4255894939':'3',
'4255894940':'4','4255894941':'3','4255894942':'4','4255894943':'4','4255894944':'4',
'4255894945':'3','4255894946':'2','4255894947':'1','4255894948':'4','4255894949':'4',
'4255894951':'3','4255894952':'3','4255894953':'1','4255894954':'4','4255894955':'3',
'4255894956':'2','4255894957':'3','4255894958':'2','4255894959':'4','4255894960':'1',
'4255894961':'3','4255894962':'2','4255894963':'3','4255894964':'2','4255894965':'2',
'4255894966':'3','4255894967':'1','4255894968':'4','4255894969':'2','4255894970':'3',
'4255894971':'1','4255894972':'1','4255894973':'4','4255894974':'3','4255894975':'2',
'4255894976':'1','4255894977':'4','4255894978':'1','4255894979':'3','4255894980':'4',
'4255894981':'4','4255894982':'3','4255894983':'3','4255894984':'4','4255894985':'2',
'4255894986':'4','4255894987':'4','4255894988':'3','4255894989':'1','4255894990':'3',
'4255894991':'3','4255894992':'3','4255894993':'1','4255894994':'1','4255894995':'1',
'4255894996':'3','4255894997':'1','4255894998':'3','4255894999':'3','4255895000':'4',
'4255895001':'3','4255895002':'3','4255895003':'2','4255895004':'3','4255895005':'4',
'4255895006':'3','4255895007':'4','4255895008':'2','4255895009':'1','4255895010':'2',
'4255895011':'3','4255895012':'1','4255895013':'3','4255895014':'4','4255895015':'3',
'4255895016':'4','4255895017':'4','4255895018':'1','4255895019':'2','4255895020':'4',
'4255895021':'2','4255895022':'4','4255895023':'2','4255895024':'4','4255895025':'3',
'4255895026':'2','4255895027':'2','4255895028':'3','4255895029':'2','4255895030':'3',
'4255895031':'3','4255895032':'3','4255895033':'1','4255895034':'3','4255895035':'2',
'4255895036':'2','4255895037':'1','4255895038':'2','4255895039':'1','4255895040':'2',
'4255895041':'3','4255895042':'2','4255895043':'2','4255895044':'3','4255895045':'1',
'4255895047':'4','4255895048':'4','4255895049':'1','4255895050':'1','4255895051':'3',
'4255895053':'3','4255895054':'3','4255895055':'3','4255895056':'4','4255895057':'1'
}

# ---------------- MAIN LOGIC ----------------
def process_url(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    soup = get_best_soup(r.content)

    application = candidate_name = roll_no = "N/A"

    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            k = cols[0].get_text(strip=True).lower()
            v = cols[1].get_text(strip=True)
            if "application" in k:
                application = v
            elif "candidate name" in k:
                candidate_name = v
            elif "roll" in k:
                roll_no = v

    bold_tds = soup.find_all("td", class_="bold")
    q, a, qf, af = [], [], 0, 0

    for td in bold_tds:
        t = td.get_text(strip=True)
        if qf:
            q.append(t); qf = 0
        if af:
            a.append(t); af = 0
        if t == "MCQ":
            qf = 1
        if t == "Answered":
            af = 1

    n = min(len(q), len(a))
    q, a = q[:n], a[:n]

    rows = []
    p1c = p2c = 0

    for i, qid in enumerate(q):
        correct = a[i] == actual_answer.get(qid)
        paper = "Paper 1" if i < PAPER1_COUNT else "Paper 2"
        if correct:
            p1c += paper == "Paper 1"
            p2c += paper == "Paper 2"

        rows.append({
            "Question ID": qid,
            "Given Answer": a[i],
            "Actual Answer": actual_answer.get(qid, "N/A"),
            "Correct": correct,
            "Paper": paper
        })

    df = pd.DataFrame(rows)
    p1_marks = p1c * 2
    p2_marks = p2c * 2
    total = p1_marks + p2_marks

    return application, candidate_name, roll_no, p1c, p2c, total, df, p1_marks, p2_marks

# ---------------- STREAMLIT UI ----------------
st.title("🎓 UGC NET Marks Analyzer")

url = st.text_input("Enter Result URL")

if st.button("Get Marks"):
    result = process_url(url)
    if result:
        app, name, roll, p1c, p2c, total, df, p1m, p2m = result

        st.markdown(f"""
        **Name:** {name}  
        **Roll No:** {roll}  
        **Application No:** {app}  
        **Paper-1 Marks:** {p1m}  
        **Paper-2 Marks:** {p2m}  
        ### 🎯 Total Marks: **{total}**
        """)

        c1, c2, c3 = st.columns(3)
        c1.plotly_chart(animated_pie("Paper 1", p1c, PAPER1_COUNT-p1c, ["green","red"]))
        c2.plotly_chart(animated_pie("Paper 2", p2c, PAPER2_COUNT-p2c, ["green","red"]))
        c3.plotly_chart(animated_pie("Combined", p1c+p2c, 150-(p1c+p2c), ["green","red"]))

        saved = save_to_firebase(url, name, roll, app, total)
        st.success("✅ Data saved to Firebase" if saved else "ℹ️ Result already exists")

        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            "ugc_net_result.csv",
            "text/csv"
        )
