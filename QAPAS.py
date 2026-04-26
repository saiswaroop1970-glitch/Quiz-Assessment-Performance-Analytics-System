import sqlite3
import os

# =========================
# DATABASE SETUP
# =========================
def init_db():
    conn = sqlite3.connect("qapas.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        question TEXT,
        op1 TEXT,
        op2 TEXT,
        op3 TEXT,
        op4 TEXT,
        correct INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        quiz_id INTEGER,
        score INTEGER,
        total INTEGER
    )
    """)

    conn.commit()
    conn.close()


# =========================
# USER FUNCTIONS
# =========================
def create_user(name):
    conn = sqlite3.connect("qapas.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()

    uid = cur.lastrowid
    conn.close()
    return uid


# =========================
# QUIZ MANAGEMENT
# =========================
def create_quiz():
    title = input("Enter quiz title: ")
    conn = sqlite3.connect("qapas.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO quizzes (title) VALUES (?)", (title,))
    conn.commit()
    print("Quiz created!")

    conn.close()


def add_question():
    quiz_id = int(input("Enter Quiz ID: "))
    question = input("Enter question: ")

    options = []
    for i in range(1, 5):
        options.append(input(f"Option {i}: "))

    correct = int(input("Correct option (1-4): "))

    conn = sqlite3.connect("qapas.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO questions (quiz_id, question, op1, op2, op3, op4, correct)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (quiz_id, question, options[0], options[1], options[2], options[3], correct))

    conn.commit()
    conn.close()

    print("Question added!")


def list_quizzes():
    conn = sqlite3.connect("qapas.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM quizzes")
    quizzes = cur.fetchall()

    print("\nAvailable Quizzes:")
    for q in quizzes:
        print(f"{q[0]}. {q[1]}")

    conn.close()


# =========================
# QUIZ ATTEMPT
# =========================
def attempt_quiz(user_id):
    list_quizzes()
    quiz_id = int(input("Enter quiz ID to attempt: "))

    conn = sqlite3.connect("qapas.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = cur.fetchall()

    score = 0

    for q in questions:
        print("\n", q[2])
        print("1.", q[3])
        print("2.", q[4])
        print("3.", q[5])
        print("4.", q[6])

        try:
            ans = int(input("Your answer: "))
        except:
            ans = 0

        if ans == q[7]:
            score += 1

    total = len(questions)

    print(f"\nFinal Score: {score}/{total}")

    # Save attempt
    cur.execute("""
    INSERT INTO attempts (user_id, quiz_id, score, total)
    VALUES (?, ?, ?, ?)
    """, (user_id, quiz_id, score, total))

    conn.commit()
    conn.close()

    # Save to file (Week 7 feature)
    with open("scores.txt", "a") as f:
        f.write(f"{user_id}:{quiz_id}:{score}/{total}\n")


# =========================
# ANALYTICS
# =========================
def user_report(user_id):
    conn = sqlite3.connect("qapas.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT quizzes.title, attempts.score, attempts.total
    FROM attempts
    JOIN quizzes ON attempts.quiz_id = quizzes.id
    WHERE attempts.user_id=?
    """, (user_id,))

    data = cur.fetchall()

    print("\n📊 Your Performance:")
    for d in data:
        print(f"{d[0]} → {d[1]}/{d[2]}")

    conn.close()


def overall_analytics():
    conn = sqlite3.connect("qapas.db")
    cur = conn.cursor()

    cur.execute("SELECT score, total FROM attempts")
    rows = cur.fetchall()

    if not rows:
        print("No data available")
        return

    total_score = sum(r[0] for r in rows)
    total_questions = sum(r[1] for r in rows)

    avg = (total_score / total_questions) * 100

    print(f"\n📈 Overall Average Score: {round(avg,2)}%")

    conn.close()


def show_file_scores():
    if not os.path.exists("scores.txt"):
        print("No file data yet.")
        return

    print("\n📁 File Records:")
    with open("scores.txt", "r") as f:
        for line in f:
            print(line.strip())


# =========================
# MENU SYSTEM
# =========================
def menu():
    print("\n====== QAPAS SYSTEM ======")
    print("1. Create Quiz")
    print("2. Add Question")
    print("3. Attempt Quiz")
    print("4. User Report")
    print("5. Overall Analytics")
    print("6. Show File Records")
    print("7. Exit")


# =========================
# MAIN PROGRAM
# =========================
def main():
    init_db()

    name = input("Enter your name: ")
    user_id = create_user(name)

    while True:
        menu()
        choice = input("Enter choice: ")

        if choice == "1":
            create_quiz()

        elif choice == "2":
            add_question()

        elif choice == "3":
            attempt_quiz(user_id)

        elif choice == "4":
            user_report(user_id)

        elif choice == "5":
            overall_analytics()

        elif choice == "6":
            show_file_scores()

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()



