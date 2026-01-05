import streamlit as st
from bs4 import BeautifulSoup, FeatureNotFound
import requests
import pandas as pd
import base64
import plotly.graph_objects as go
import firebase_admin
from firebase_admin import credentials, db

# ---------------- FIREBASE INIT ----------------
if not firebase_admin._apps:
    cred = credentials.Certificate("cv.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://bloodbanknew-e4e64-default-rtdb.firebaseio.com/"
    })

# ---------------- CONFIG ----------------
PAPER1_COUNT = 50
PAPER2_COUNT = 100
TOTAL_QUESTIONS = 150
MAX_MARKS = 300
# ---------------- FUNCTION ----------------
def apply_chosen_answer_cell_color(df):
    """
    Color the ENTIRE Chosen Answer cell:
    - GREEN if Chosen Answer == Correct Answer
    - RED otherwise
    """

    df["Chosen Answer"] = df["Chosen Answer"].astype(str)
    df["Correct Answer"] = df["Correct Answer"].astype(str)

    def color_cell(row):
        styles = [""] * len(row)

        idx = row.index.get_loc("Chosen Answer")

        if row["Chosen Answer"] == row["Correct Answer"]:
            styles[idx] = (
                "background-color: #2ecc71; color: white; font-weight: bold;"
            )
        else:
            styles[idx] = (
                "background-color: #e74c3c; color: white; font-weight: bold;"
            )

        return styles

    return df.style.apply(color_cell, axis=1)






# ---------------- HELPERS ----------------
def get_best_soup(content):
    for p in ['html5lib', 'lxml', 'html.parser']:
        try:
            return BeautifulSoup(content, p)
        except FeatureNotFound:
            continue
    raise FeatureNotFound

def encode_url(url):
    return base64.urlsafe_b64encode(url.encode()).decode()

# ---------------- SAVE TO FIREBASE ----------------
def save_to_firebase(url, name, roll, application, total_marks):
    if total_marks <= 2:
        return False
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

# ---------------- STATISTICS ----------------
def get_marks_statistics():
    ref = db.reference("results")
    data = ref.get()
    if not data:
        return None
    marks = [v["total_marks"] for v in data.values()]
    s = pd.Series(marks)
    return {
        "highest": int(s.max()),
        "lowest": int(s.min()),
        "average": round(s.mean(), 2),
        "median": float(s.median())
    }

def get_all_marks():
    ref = db.reference("results")
    data = ref.get()
    if not data:
        return []
    return [v["total_marks"] for v in data.values()]

# ---------------- FREQUENCY DISTRIBUTION ----------------
def marks_frequency_distribution(marks, start=60, end=300, bin_size=10):
    bins = list(range(start, end + bin_size, bin_size))
    labels = [f"{b}-{b+bin_size-1}" for b in bins[:-1]]
    freq = [0] * len(labels)
    for m in marks:
        if start <= m <= end:
            idx = (m - start) // bin_size
            if idx < len(freq):
                freq[idx] += 1
    return labels, freq

def plot_frequency_graph(labels, freq):
    fig = go.Figure(
        data=[go.Bar(x=labels, y=freq, marker=dict(color="green"))]
    )
    fig.update_layout(
        title="Marks Frequency Distribution (60–300, Bin = 10)",
        xaxis_title="Marks Range",
        yaxis_title="Number of Candidates",
        title_x=0.5,
        dragmode=False
    )
    return fig

# ---------------- PIE CHART ----------------
def animated_pie(title, correct, wrong):
    fig = go.Figure(
        data=[go.Pie(
            labels=["Correct", "Wrong"],
            values=[correct, wrong],
            hole=0.5,
            marker=dict(colors=["green", "red"]),
            textinfo="label+percent"
        )]
    )
    fig.update_layout(title=title, title_x=0.5)
    return fig

# ---------------- ANSWER KEY ----------------
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

# ---------------- JRF & NET CUT-OFF DATA ----------------
JRF_CUTOFFS = {
    "UNRESERVED": {"2022":180,"2023":184,"2024":218,"2025":186},
    "OBC(NCL)":   {"2022":162,"2023":174,"2024":206,"2025":172},
    "EWS":        {"2022":166,"2023":176,"2024":202,"2025":172},
    "SC":         {"2022":150,"2023":160,"2024":194,"2025":158},
    "ST":         {"2022":148,"2023":164,"2024":196,"2025":160},
}

NET_CUTOFFS = {
    "UNRESERVED": {"2022":162,"2023":160,"2024":188,"2025":158},
    "OBC(NCL)":   {"2022":146,"2023":144,"2024":174,"2025":142},
    "EWS":        {"2022":142,"2023":146,"2024":172,"2025":144},
    "SC":         {"2022":136,"2023":138,"2024":164,"2025":136},
    "ST":         {"2022":132,"2023":138,"2024":164,"2025":136},
}

def calculate_probability(user_marks, cutoffs):
    passed = 0
    rows = []
    for year, cutoff in cutoffs.items():
        ok = user_marks >= cutoff
        rows.append({
            "Year": year,
            "Cut-off": cutoff,
            "Your Marks": user_marks,
            "Qualified": "YES" if ok else "NO"
        })
        if ok:
            passed += 1
    return (passed / len(cutoffs)) * 100, pd.DataFrame(rows)

# ---------------- PROCESS URL ----------------
def process_url(url):
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
    soup = get_best_soup(r.content)

    application = name = roll = "N/A"
    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            k = cols[0].get_text(strip=True).lower()
            v = cols[1].get_text(strip=True)
            if "application" in k: application = v
            elif "candidate name" in k: name = v
            elif "roll" in k: roll = v

    bold = soup.find_all("td", class_="bold")
    qids, answers = [], []
    qf = af = 0

    for td in bold:
        t = td.get_text(strip=True)
        if qf: qids.append(t); qf = 0
        if af: answers.append(t); af = 0
        if t == "MCQ": qf = 1
        if t == "Answered": af = 1

    rows = []
    p1c = p2c = 0

    for i, qid in enumerate(qids):
        chosen = answers[i]
        correct = actual_answer.get(qid)
        is_correct = chosen == correct
        paper = "Paper 1" if i < PAPER1_COUNT else "Paper 2"

        if is_correct:
            if paper == "Paper 1":
                p1c += 1
            else:
                p2c += 1

        rows.append({
            "Question ID": qid,
            "Chosen Answer": chosen,
            "Correct Answer": correct,
            "Is Correct": is_correct,
            "Paper": paper
        })

    df = pd.DataFrame(rows)
    total = (p1c + p2c) * 2

    return application, name, roll, p1c, p2c, total, df

# ---------------- UI ----------------
col1, col2 = st.columns([4,1])
with col1:
    st.title("🎓 UGC NET Marks Analyzer")
with col2:
    st.markdown(
        "<p style='font-size:12px;text-align:right;margin-top:35px;'>"
        "Idea by <b>Himalaya Raj</b><br>"
        "Credit goes to <b>ChatGPT</b></p>",
        unsafe_allow_html=True
    )

stats = get_marks_statistics()
if stats:
    st.markdown(
        f"🏆 Highest: {stats['highest']} | "
        f"📊 Average: {stats['average']} | "
        f"📌 Median: {stats['median']} | "
        f"📉 Lowest: {stats['lowest']}"
    )

category = st.selectbox("Select Category", list(JRF_CUTOFFS.keys()))
url = st.text_input("Enter Result URL")

if st.button("Get Marks"):
    app, name, roll, p1c, p2c, total ,df = process_url(url)

    p1m, p2m = p1c*2, p2c*2
    st.markdown(f"""
    ### 👤 Candidate Details  
    **Name:** {name}  
    **Application No:** {app}  
    **Roll No:** {roll}
    """)
    st.markdown(f"""
    ### 📘 Paper 1 Marks: **{p1m} / 100**
    ### 📕 Paper 2 Marks: **{p2m} / 200**
    ## 🎯 Total Marks: **{total} / 300**
    """)

    c1,c2,c3 = st.columns(3)
    c1.plotly_chart(animated_pie("Paper 1", p1c, PAPER1_COUNT-p1c))
    c2.plotly_chart(animated_pie("Paper 2", p2c, PAPER2_COUNT-p2c))
    c3.plotly_chart(animated_pie("Overall", p1c+p2c, TOTAL_QUESTIONS-(p1c+p2c)))

    save_to_firebase(url, name, roll, app, total)

    st.markdown("## 🎓 JRF Prediction")
    jrf_prob, jrf_df = calculate_probability(total, JRF_CUTOFFS[category])
    st.dataframe(jrf_df, use_container_width=True)
    st.metric("Chance to Qualify JRF", f"{jrf_prob:.0f}%")

    st.markdown("## 📘 NET Prediction")
    net_prob, net_df = calculate_probability(total, NET_CUTOFFS[category])
    st.dataframe(net_df, use_container_width=True)
    st.metric("Chance to Qualify NET", f"{net_prob:.0f}%")
    # CSV download
    

    st.markdown("### 📊 Overall Marks Frequency Distribution")
    labels, freq = marks_frequency_distribution(get_all_marks())
    st.plotly_chart(
        plot_frequency_graph(labels, freq),
        use_container_width=True,
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False}
    )
    print(df)
    df = df.drop(columns=["Is Correct"], errors="ignore")
    styled_df = apply_chosen_answer_cell_color(df)
    #print(styled_df.columns)
    #styled_df = styled_df.drop(columns=["Is Correct"], errors="ignore")
    #styled_df = styled_df.drop(columns=["Is Correct"], errors="ignore")
        # Display table
    st.dataframe(
    styled_df,
    use_container_width=True,
    column_config={
        "Question ID": st.column_config.NumberColumn(width="small"),
        "Chosen Answer": st.column_config.NumberColumn(width="small"),
        "Correct Answer": st.column_config.NumberColumn(width="small"),
        "Paper": st.column_config.TextColumn(width="small"),
    },
    )
    st.download_button(
        "⬇️ Download Question-wise Analysis (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        "ugc_net_question_analysis.csv",
        "text/csv"
    )



