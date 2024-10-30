import sqlite3
import random
import datetime as dt
import json
import os

###########################################################################################################################################################################

db_path = "User\\User Accounts.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    dob DATE,
    phone_number TEXT,
    profile_picture BLOB,
    biography TEXT,
    recovery_key TEXT NOT NULL
)
''')
conn.commit()
conn.close()

def signed_in_account():                    # Checking which account is signed in
    try:
        with open("Log\\Signed_In.txt") as f:
            return f.read().strip("\n")
    except:
        return None

def log(action, username, details=None):
    timestamp = dt.datetime.now().isoformat()
    log_entry = { "timestamp": timestamp, "username": username, "action": action }
    
    if details:
        log_entry["details"] = details
    
    try:                                            # Taking all data in log file
        with open("Log\\activity_log.json", 'r') as log_file:
            log_data = json.load(log_file)
    except:
        log_data = []
    
    log_data.append(log_entry)                      # Adding newest log
    
    with open("Log\\activity_log.json", 'w') as log_file:           # Writing entire log
        json.dump(log_data, log_file, indent=2)

def generate_recovery_key():                # Creating a recovery key of 10 chrs
    """Generate a random recovery key of 10 characters (letters and digits)."""
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'       # a-z, A-Z, 0-9
    return ''.join(random.choice(characters) for _ in range(10))

def sign_out():
    log("sign_out", signed_in_account())
    import os
    try:
        os.remove("Log/Signed_In.txt")
    except FileNotFoundError:
        pass  # File doesn't exist, so no need to delete

def sign_in(usr,pas):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (usr, pas))
    user = cursor.fetchone()
    conn.close()

    if user:
        with open("Log/Signed_In.txt", "w") as f:
            f.write(usr)
        log("sign_in", usr)
        return True
    return False

def create_files(username):
    os.mkdir("User\\" + username)
    db = sqlite3.connect("User\\" + username + "\\Journal.db")
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        debit_account TEXT NOT NULL,
        credit_account TEXT NOT NULL,
        amount REAL NOT NULL,
        narration TEXT NOT NULL
    )
    """)

    db.commit()
    db.close

    for i in ["\\Ledger.db", "\\Trial Balance.db"]:
        conn = sqlite3.connect(f"User\\{username}\\{i}")
        conn.close()

def sign_up(username, password, email, dob, phone_number, profile_picture=None, biography=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        recovery_key = generate_recovery_key()
        cursor.execute('''
        INSERT INTO users (username, password, email, dob, phone_number, profile_picture, biography, recovery_key)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, email, dob, phone_number, profile_picture, biography, recovery_key))
        conn.commit()
        log("Account Created:", username)
        create_files(username)
        return True, recovery_key
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    finally:
        conn.close()

def reset_pas(usr, rc, npas):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ? AND recovery_key = ?", (usr, rc))
    user = cursor.fetchone()
    
    if user:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (npas, usr))
        conn.commit()
        log("password_reset", usr)
        conn.close()
        return True
    
    conn.close()
    return False

def get_user_info():
    username = signed_in_account()
    if not username:
        return None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email, dob, phone_number, profile_picture, biography FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return {
            'email': user_data[0],
            'dob': user_data[1],
            'phone_number': user_data[2],
            'profile_picture': user_data[3],
            'biography': user_data[4]
        }
    return None

def update_profile(email, dob, phone_number, profile_picture, biography):
    username = signed_in_account()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if profile_picture != None:
        try:
            cursor.execute('''
            UPDATE users
            SET email = ?, dob = ?, phone_number = ?, profile_picture = ?, biography = ?
            WHERE username = ?
            ''', (email, dob, phone_number, profile_picture, biography, username))
            conn.commit()
            log("profile_update", username)
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()
    else:
        try:
            cursor.execute('''
            UPDATE users
            SET email = ?, dob = ?, phone_number = ?, biography = ?
            WHERE username = ?
            ''', (email, dob, phone_number, biography, username))
            conn.commit()
            log("profile_update", username)
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

def change_password(current_password, new_password):
    username = signed_in_account()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password = cursor.fetchone()
    
    if stored_password and stored_password[0] == current_password:
        try:
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
            conn.commit()
            log("password_change", username)
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()
    else:
        conn.close()
        return False

def get_password(a = signed_in_account()):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (a))
    password = cursor.fetchone()
    conn.close()
    return password[0]

def delete_account(password):
    if get_password() == password:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE username = ?", (signed_in_account(),))
            conn.commit()
            log("account_deletion", signed_in_account())
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()
    else:
        return False
