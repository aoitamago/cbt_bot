import psycopg2
import json
import os

DB_URL = os.getenv("DATABASE_URL")

def connect():
    return psycopg2.connect(DB_URL)

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id SERIAL PRIMARY KEY,
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
    conn = connect()
    cur = conn.cursor()

    for q in questions:
        cur.execute("""
        INSERT INTO questions (category, question, choices, answer, image)
        VALUES (%s, %s, %s, %s, %s)
        """, (
            category,
            q["question"],
            json.dumps(q["choices"]),
            q["answer"],
            q.get("image")
        ))

    conn.commit()
    conn.close()

def load_questions(category):
    conn = connect()
    cur = conn.cursor()

    if category == "all":
        cur.execute("SELECT * FROM questions")
    else:
        cur.execute("SELECT * FROM questions WHERE category=%s", (category,))

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
    conn = connect()
    cur = conn.cursor()

    cur.execute("DELETE FROM questions")

    conn.commit()
    conn.close()
