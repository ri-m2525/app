from flask import Flask, render_template, request, redirect
import sqlite3
import random

app = Flask(__name__)


# =========================
# 時間割の時間
# =========================

sch = [
    ["1限目", 8, 50],
    ["2限目", 10, 35],
    ["昼休み", 12, 0],
    ["3限目", 13, 0],
    ["4限目", 14, 45],
    ["5限目", 16, 30],
    ["6限目", 18, 15]
]


# =========================
# データベースを作る
# =========================

def init_db():

    conn = sqlite3.connect("schedule.db")

    # 予定
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            title TEXT NOT NULL
        )
    """)

    # 時間割
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            period TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# トップページ
# =========================

@app.route('/')
def index():

    conn = sqlite3.connect("schedule.db")

    # 予定を取得
    event_rows = conn.execute("""
        SELECT id, date, title
        FROM events
        ORDER BY date
    """).fetchall()

    # 時間割を取得
    subject_rows = conn.execute("""
        SELECT day, period, subject
        FROM subjects
    """).fetchall()

    conn.close()


    # =========================
    # JavaScript用の時間割データ
    # =========================

    subjects = {
        "月": {},
        "火": {},
        "水": {},
        "木": {},
        "金": {}
    }


    for row in subject_rows:

        day = row[0]
        period = row[1]
        subject = row[2]

        if day not in subjects:
            subjects[day] = {}

        subjects[day][period] = subject


    return render_template(
        "index.html",
        sch=sch,
        events=event_rows,
        subjects=subjects
    )


# =========================
# 予定を追加
# =========================

@app.route('/add_event', methods=['POST'])
def add_event():

    date = request.form['date']
    title = request.form['title']

    conn = sqlite3.connect("schedule.db")

    conn.execute("""
        INSERT INTO events (date, title)
        VALUES (?, ?)
    """, (date, title))

    conn.commit()
    conn.close()

    return redirect('/')


# =========================
# 予定を削除
# =========================

@app.route('/delete_event/<int:event_id>')
def delete_event(event_id):

    conn = sqlite3.connect("schedule.db")

    conn.execute("""
        DELETE FROM events
        WHERE id = ?
    """, (event_id,))

    conn.commit()
    conn.close()

    return redirect('/')


# =========================
# 時間割を保存
# =========================

@app.route('/save_schedule', methods=['POST'])
def save_schedule():

    subjects = request.get_json()

    if not subjects:
        return {"success": False}


    conn = sqlite3.connect("schedule.db")


    for day in subjects:

        # その曜日の古い時間割を削除
        conn.execute("""
            DELETE FROM subjects
            WHERE day = ?
        """, (day,))


        # 新しい時間割を保存
        for period in subjects[day]:

            subject = subjects[day][period]


            # 空欄なら保存しない
            if subject.strip() == "":
                continue


            conn.execute("""
                INSERT INTO subjects
                (day, period, subject)
                VALUES (?, ?, ?)
            """, (
                day,
                period,
                subject
            ))


    conn.commit()
    conn.close()


    return {"success": True}


# =========================
# 今日の運勢
# =========================

@app.route('/fortune')
def fortune():

    fortunes = [
        "大吉",
        "中吉",
        "小吉",
        "吉",
        "末吉",
        "凶"
    ]

    colors = [
        "赤",
        "オレンジ",
        "黄色",
        "緑",
        "青",
        "紫"
    ]

    items = [
        "財布",
        "傘",
        "靴",
        "時計",
        "カバン",
        "スマホ"
    ]


    result = random.choice(fortunes)
    color = random.choice(colors)
    item = random.choice(items)


    return render_template(
        "fortune.html",
        result=result,
        color=color,
        item=item
    )


# =========================
# アプリ起動
# =========================

if __name__ == '__main__':

    init_db()

    app.run(
        debug=True
    )