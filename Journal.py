import sqlite3
from datetime import datetime
import os

from Account import signed_in_account

##############################################################################################################################################################

def get_path():
    if signed_in_account():
        return os.path.join("User", signed_in_account(), "Journal.db")
    else:
        return None

def create_db():
    db = sqlite3.connect(get_path())
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journal_id INTEGER,
        image_data BLOB,
        filename TEXT,
        upload_date TEXT,
        FOREIGN KEY (journal_id) REFERENCES Journal(id)
    )
    """)

    db.commit()
    db.close()

def add_journal(debit, credit, amount, narration):
    create_db()
    date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    record = (date_time, debit.capitalize(), credit.capitalize(), amount, narration)

    db_path = get_path()
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    cur.execute(f'''INSERT INTO Journal (date, debit_account, credit_account, amount, narration)
    VALUES (?, ?, ?, ?, ?)''', record)


    db.commit()
    db.close()

def add_document(journal_id, image_data, filename):
    db = sqlite3.connect(get_path())
    cur = db.cursor()
    upload_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute('''INSERT INTO Documents (journal_id, image_data, filename, upload_date)
                   VALUES (?, ?, ?, ?)''', (journal_id, image_data, filename, upload_date))
    db.commit()
    db.close()

def edit_journal(index, new_debit, new_credit, new_amount, new_narration):
    db = sqlite3.connect(get_path())
    cur = db.cursor()
    cur.execute('''UPDATE Journal 
                    SET debit_account = ?, credit_account = ?, amount = ?, narration = ?
                    WHERE id = ?''', 
                (new_debit.capitalize(), new_credit.capitalize(), new_amount, new_narration, index))
    db.commit()
    db.close()
    return True

def dele_journal(index):
    db = sqlite3.connect(get_path())
    cur = db.cursor()
    cur.execute('DELETE FROM Journal WHERE id = ?', (index,))
    db.commit()
    db.close()
    return True

def all_journals():
    db = sqlite3.connect(get_path())
    cur = db.cursor()
    cur.execute('SELECT * FROM Journal ORDER BY date')
    journals = cur.fetchall()
    db.close()
    return journals
    
def all_accounts():
    accounts = set()
    for journal in all_journals():
        accounts.add(journal[2])  # Debit account
        accounts.add(journal[3])  # Credit account
    return accounts

def assets_liabilities():
    db = sqlite3.connect(get_path())
    cur = db.cursor()
    
    cur.execute('SELECT debit_account, credit_account, amount FROM Journal')
    entries = cur.fetchall()
    
    balances = {}
    
    for debit_account, credit_account, amount in entries:
        balances[debit_account] = balances.get(debit_account, 0) + amount
        balances[credit_account] = balances.get(credit_account, 0) - amount
    
    assets = {}
    liabilities = {}
    
    for account, balance in balances.items():
        if balance > 0:
            assets[account] = balance
        elif balance < 0:
            liabilities[account] = -balance  # Convert to positive value for display
    
    db.close()
    return assets, liabilities
