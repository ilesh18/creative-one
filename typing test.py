import mysql.connector
from contextlib import contextmanager
import random
import time
import matplotlib.pyplot as plt
import difflib
import getpass  

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'charset': 'utf8'
}

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        raise
    finally:
        if conn:
            conn.close()

def create_database_and_table():
    # Prompt for password once and add to DB_CONFIG
    password = getpass.getpass("Enter MySQL password for user 'root': ")
    DB_CONFIG['password'] = password
    
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS typing_speed_db")
        cursor.execute("USE typing_speed_db")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS result (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                typing_speed FLOAT NOT NULL,
                time_taken FLOAT NOT NULL,
                wrong_words INT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                achievement VARCHAR(100) NOT NULL,
                UNIQUE KEY unique_achievement (username, achievement)
            )
        """)
        db.commit()
        print("Database and tables created successfully.")

def save_result(username: str, speed: float, time_taken: float, wrong_words: int):
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("USE typing_speed_db")
        cursor.execute(
            "INSERT INTO result (username, typing_speed, time_taken, wrong_words) VALUES (%s, %s, %s, %s)",
            (username, speed, time_taken, wrong_words)
        )
        db.commit()

def save_achievement(username: str, achievement: str):
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("USE typing_speed_db")
        cursor.execute(
            "INSERT IGNORE INTO achievements (username, achievement) VALUES (%s, %s)",
            (username, achievement)
        )
        db.commit()

def plot_attempts(username: str):
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("USE typing_speed_db")
        cursor.execute("""
            SELECT typing_speed 
            FROM result 
            WHERE username = %s 
            ORDER BY timestamp DESC 
            LIMIT 5
        """, (username,))
        attempts = cursor.fetchall()

    if not attempts:
        print("No attempts to plot.")
        return

    speeds = [row[0] for row in attempts]
    attempt_nums = list(range(1, len(speeds) + 1))

    plt.figure(figsize=(10, 5))
    plt.plot(attempt_nums, speeds, marker='o', linestyle='-', color='blue')
    plt.title(f"Typing Speed Progress for {username}")
    plt.xlabel("Recent Attempt # (Last 5)")
    plt.ylabel("Speed (WPM)")
    plt.grid(True, alpha=0.5)
    plt.tight_layout()
    plt.show()

def check_achievements(username: str, speed: float, wrong_words: int, is_challenge: bool):
    if speed >= 60:
        save_achievement(username, "speedster")
    if speed >= 80:
        save_achievement(username, "quick_fingers")
    if speed >= 100:
        save_achievement(username, "fast_and_furious")

    if wrong_words == 0:
        save_achievement(username, "perfectionist")
    if wrong_words <= 1:
        save_achievement(username, "accuracy_master")

    if not is_challenge:
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute("USE typing_speed_db")
            cursor.execute("SELECT COUNT(*) FROM result WHERE username = %s", (username,))
            total_tests = cursor.fetchone()[0]
            if total_tests >= 5:
                save_achievement(username, "consistent_typist")

def calculate_wpm_and_errors(user_input: str, target_sentence: str, duration: float) -> tuple[float, int, str]:
    """Calculate WPM, wrong words, and incorrect words using better matching."""
    user_words = user_input.lower().split()
    target_words = target_sentence.lower().split()

    matcher = difflib.SequenceMatcher(None, user_words, target_words)
    similarity = matcher.ratio()

    total_words = len(target_words)
    correct_words = int(similarity * total_words)
    wrong_words = max(0, total_words - correct_words)

    incorrect_words = ' '.join(set(target_words) - set(user_words)) or 'None'

    effective_words = max(0, len(user_words) - wrong_words)
    wpm = (effective_words / (duration / 60)) if duration > 0 else 0
    
    return wpm, wrong_words, incorrect_words

def typing_test():
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be blank.")
        return

    sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "A journey of a thousand miles begins with a single step.",
        "To be or not to be, that is the question.",
        "All that glitters is not gold.",
        "The only thing we have to fear is fear itself.",
        "In the middle of difficulty lies opportunity.",
        "You miss 100% of the shots you don't take.",
        "Success is not final, failure is not fatal.",
        "Life is what happens when you're busy making other plans."
    ]
    random.shuffle(sentences)

    total_speed = 0.0
    total_wrong = 0
    attempts = 5

    for i in range(attempts):
        print(f"\nAttempt {i + 1}:")
        print(sentences[i])
        
        start = time.time()
        user_input = input("Type the sentence:\n").strip()
        end = time.time()
        duration = end - start
        
        wpm, wrong_words, incorrect_words = calculate_wpm_and_errors(user_input, sentences[i], duration)
        save_result(username, wpm, duration, wrong_words)
        
        total_speed += wpm
        total_wrong += wrong_words
        
        print(f"Speed: {wpm:.2f} WPM | Time: {duration:.2f}s | Mistakes: {wrong_words} ({incorrect_words})")

    avg_speed = total_speed / attempts
    print(f"\nAverage Speed: {avg_speed:.2f} WPM")
    
    check_achievements(username, avg_speed, total_wrong, is_challenge=False)
    plot_attempts(username)

def typing_challenge():
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be blank.")
        return

    print("\nChoose Difficulty:")
    print("1. Easy (60s)")
    print("2. Medium (45s)")
    print("3. Hard (30s)")
    
    choice = input("Your choice (1-3): ").strip()
    time_limits = {'1': 60, '2': 45, '3': 30}
    time_limit = time_limits.get(choice, 30)
    
    sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "A journey of a thousand miles begins with a single step.",
        "To be or not to be, that is the question.",
        "Success is not final, failure is not fatal."
    ]
    sentence = random.choice(sentences)
    
    print(f"\nType this in {time_limit} seconds:\n{sentence}")
    print("Get ready... (3 seconds)")
    time.sleep(3)
    print("Go!")
    
    start = time.time()
    user_input = input().strip()
    end = time.time()
    total_time = end - start
    
    if total_time > time_limit:
        print(f"Time's up! You took {total_time:.2f}s (limit: {time_limit}s). No score saved.")
        return
    
    wpm, wrong_words, incorrect_words = calculate_wpm_and_errors(user_input, sentence, total_time)
    save_result(username, wpm, total_time, wrong_words)
    
    print(f"Speed: {wpm:.2f} WPM | Time: {total_time:.2f}s | Mistakes: {wrong_words} ({incorrect_words})")
    
    check_achievements(username, wpm, wrong_words, is_challenge=True)

ACHIEVEMENTS = {
    "speedster": "Reach 60 WPM in a test.",
    "perfectionist": "Type with 0 errors.",
    "quick_fingers": "Reach 80 WPM.",
    "fast_and_furious": "Reach 100 WPM.",
    "accuracy_master": "Have ≤1 incorrect words.",
    "consistent_typist": "Complete 5 typing tests."
}

def view_results(username: str):
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("USE typing_speed_db")
        cursor.execute("""
            SELECT id, typing_speed, time_taken, wrong_words, timestamp 
            FROM result 
            WHERE username = %s 
            ORDER BY timestamp DESC
        """, (username,))
        results = cursor.fetchall()
    
    if not results:
        print("No results found for this user.")
        return
    
    print(f"\n=== Results for {username} ===")
    for row in results:
        print(f"ID: {row[0]} | Speed: {row[1]:.2f} WPM | Time: {row[2]:.2f}s | Mistakes: {row[3]} | Date: {row[4]}")

def view_achievements():
    username = input("Enter your username: ").strip()
    
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("USE typing_speed_db")
        cursor.execute("SELECT achievement FROM achievements WHERE username = %s", (username,))
        unlocked = {row[0] for row in cursor.fetchall()}
    
    print(f"\n=== Achievements for {username} ===")
    for key, desc in ACHIEVEMENTS.items():
        status = "Unlocked " if key in unlocked else "Locked "
        print(f"{desc} — {status}")

def show_instructions():
    print("""
=== Typing Test Instructions ===
1. You'll get 5 sentences to type one by one.
2. Type as accurately and quickly as possible.
3. Speed is calculated in Words Per Minute (WPM), with penalties for errors.
4. Your average speed and progress will be shown at the end.
5. Have fun improving your skills!
""")

def main_menu():
    while True:
        print("\n=== Typing Speed Test Menu ===")
        print("1. Start Typing Test")
        print("2. Typing Challenge")
        print("3. View Results")
        print("4. View Achievements")
        print("5. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            show_instructions()
            typing_test()
        elif choice == "2":
            typing_challenge()
        elif choice == "3":
            username = input("Enter username: ").strip()
            view_results(username)
        elif choice == "4":
            view_achievements()
        elif choice == "5":
            print("Thanks for playing! Goodbye.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    create_database_and_table()
    main_menu()
