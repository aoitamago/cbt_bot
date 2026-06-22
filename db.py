import sqlite3
import json

DB_NAME = "cbt.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        question TEXT,
        choices TEXT,
        answer TEXT,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_questions(category, questions):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for q in questions:
        cur.execute("""
        INSERT INTO questions (category, question, choices, answer, image)
        VALUES (?, ?, ?, ?, ?)
        """, (
            category,
            q["question"],
            json.dumps(q["choices"], ensure_ascii=False),
            q["answer"],
            q.get("image")
        ))

    conn.commit()
    conn.close()

def load_questions(category):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if category == "all":
        cur.execute("SELECT * FROM questions")
    else:
        cur.execute("SELECT * FROM questions WHERE category=?", (category,))

    rows = cur.fetchall()

    questions = []
    for r in rows:
        questions.append({
            "question": r[2],
            "choices": json.loads(r[3]),
            "answer": r[4],
            "image": r[5]
        })

    conn.close()
    return questions

def reset_all():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM questions")

    conn.commit()
    conn.close()
