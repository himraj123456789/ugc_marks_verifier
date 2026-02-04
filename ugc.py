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


# ---------------- CELL COLOR FUNCTION ----------------
def apply_chosen_answer_cell_color(df):

    df["Chosen Answer"] = df["Chosen Answer"].astype(str)
    df["Correct Answer"] = df["Correct Answer"].astype(str)

    def color_cell(row):
        styles = [""] * len(row)
        idx = row.index.get_loc("Chosen Answer")

        if row["Chosen Answer"] == row["Correct Answer"]:
            styles[idx] = "background-color: #2ecc71; color: white; font-weight: bold;"
        else:
            styles[idx] = "background-color: #e74c3c; color: white; font-weight: bold;"

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
        data=[go.Bar(x=labels, y=freq)]
    )

    fig.update_layout(
        title="Marks Frequency Distribution (60–300, Bin = 10)",
        xaxis_title="Marks Range",
        yaxis_title="Candidates",
        title_x=0.5
    )

    return fig


# ---------------- PIE CHART ----------------
def animated_pie(title, correct, wrong):

    fig = go.Figure(
        data=[go.Pie(
            labels=["Correct", "Wrong"],
            values=[correct, wrong],
            hole=0.5,
            textinfo="label+percent"
        )]
    )

    fig.update_layout(title=title, title_x=0.5)

    return fig


# ---------------- ANSWER KEY (UPDATED) ----------------
actual_answer = {

    '6119872158':'1','6119872159':'1','6119872160':'2','6119872161':'3','6119872162':'4',
    '6119872163':'3','6119872164':'2','6119872165':'2','6119872166':'2','6119872167':'3',
    '6119872168':'4','6119872169':'2','6119872170':'1','6119872171':'3','6119872172':'4',
    '6119872173':'1','6119872174':'3','6119872175':'1','6119872176':'1','6119872177':'2',
    '6119872178':'4','6119872179':'3','6119872180':'4','6119872181':'1','6119872182':'3',
    '6119872183':'4','6119872184':'4','6119872185':'1','6119872186':'3','6119872187':'4',
    '6119872188':'2','6119872189':'4','6119872190':'1','6119872191':'3','6119872192':'2',
    '6119872193':'2','6119872194':'1','6119872195':'2','6119872196':'1','6119872197':'1',
    '6119872198':'1','6119872199':'1','6119872200':'4','6119872201':'4','6119872202':'1',
    '6119872204':'3','6119872205':'2','6119872206':'4','6119872207':'1','6119872208':'3',
    '6119872209':'2','6119872210':'4','6119872211':'3','6119872212':'4','6119872213':'3',
    '6119872214':'3','6119872215':'3','6119872216':'2','6119872217':'2','6119872218':'2',
    '6119872219':'1','6119872220':'3','6119872221':'3','6119872222':'4','6119872223':'4',
    '6119872224':'2','6119872225':'3','6119872226':'1','6119872227':'3','6119872228':'4',
    '6119872229':'3','6119872230':'4','6119872231':'3','6119872232':'3','6119872233':'1',
    '6119872234':'1','6119872235':'3','6119872236':'2','6119872237':'3','6119872238':'2',
    '6119872239':'2','6119872240':'3','6119872241':'3','6119872242':'3','6119872243':'3',
    '6119872244':'2','6119872245':'1','6119872246':'1','6119872247':'2','6119872248':'4',
    '6119872249':'1','6119872250':'3','6119872251':'3','6119872252':'1','6119872253':'1',
    '6119872254':'4','6119872255':'3','6119872256':'2','6119872257':'2','6119872258':'1',
    '6119872259':'1','6119872260':'1','6119872261':'3','6119872262':'3','6119872263':'4',
    '6119872264':'3','6119872265':'2','6119872266':'3','6119872267':'3','6119872268':'2',
    '6119872269':'2','6119872270':'1','6119872271':'1','6119872272':'1','6119872273':'3',
    '6119872274':'4','6119872275':'4','6119872276':'3','6119872277':'3','6119872278':'2',
    '6119872279':'3','6119872280':'3','6119872281':'3','6119872282':'3','6119872283':'1',
    '6119872284':'3','6119872285':'2','6119872286':'1','6119872287':'3','6119872288':'1',
    '6119872289':'4','6119872290':'3','6119872291':'2','6119872292':'4','6119872293':'3',
    '6119872294':'1','6119872295':'1','6119872296':'1','6119872297':'4','6119872298':'4',
    '6119872300':'3','6119872301':'3','6119872302':'2','6119872303':'3','6119872304':'2',
    '6119872306':'3','6119872307':'1','6119872308':'1','6119872309':'1','6119872310':'2'
}


# ---------------- PROCESS URL ----------------
def process_url(url):

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    soup = get_best_soup(r.content)

    application = name = roll = "N/A"

    for row in soup.find_all("tr"):

        cols = row.find_all("td")

        if len(cols) >= 2:

            k = cols[0].get_text(strip=True).lower()
            v = cols[1].get_text(strip=True)

            if "application" in k:
                application = v
            elif "candidate name" in k:
                name = v
            elif "roll" in k:
                roll = v


    bold = soup.find_all("td", class_="bold")

    qids, answers = [], []
    qf = af = 0


    for td in bold:

        t = td.get_text(strip=True)

        if qf:
            qids.append(t)
            qf = 0

        if af:
            answers.append(t)
            af = 0

        if t == "MCQ":
            qf = 1

        if t == "Answered":
            af = 1


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
st.title("🎓 UGC NET Marks Analyzer")

url = st.text_input("Enter Result URL")


if st.button("Get Marks"):

    app, name, roll, p1c, p2c, total, df = process_url(url)


    p1m = p1c * 2
    p2m = p2c * 2


    st.markdown(f"""
    ### 👤 Candidate Details
    **Name:** {name}
    **Application:** {app}
    **Roll:** {roll}
    """)


    st.markdown(f"""
    ### 📘 Paper 1: {p1m} / 100
    ### 📕 Paper 2: {p2m} / 200
    ## 🎯 Total: {total} / 300
    """)


    c1, c2, c3 = st.columns(3)

    c1.plotly_chart(animated_pie("Paper 1", p1c, PAPER1_COUNT - p1c))
    c2.plotly_chart(animated_pie("Paper 2", p2c, PAPER2_COUNT - p2c))
    c3.plotly_chart(animated_pie("Overall", p1c + p2c, TOTAL_QUESTIONS - (p1c + p2c)))


    save_to_firebase(url, name, roll, app, total)


    df = df.drop(columns=["Is Correct"], errors="ignore")

    styled_df = apply_chosen_answer_cell_color(df)


    st.dataframe(
        styled_df,
        use_container_width=True
    )


    st.download_button(
        "⬇️ Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        "ugc_net_analysis.csv",
        "text/csv"
    )
