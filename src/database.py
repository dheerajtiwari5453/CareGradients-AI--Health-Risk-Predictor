"""Database module for CareGradients AI.

Provides a lightweight SQLite persistence layer for patient risk records.
The module defines a simple CRUD interface used by the Streamlit app.
"""

import sqlite3
from pathlib import Path
import pandas as pd
from datetime import datetime

# Default database path – stored in the project root.
DB_FILE: Path = Path(__file__).resolve().parents[1] / "caregradients_records.db"

def init_db(db_path: Path = DB_FILE) -> None:
    """Create the SQLite database and the ``patient_records`` table if needed.

    Parameters
    ----------
    db_path: Path, optional
        Path to the SQLite database file. Defaults to ``DB_FILE``.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patient_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            bmi REAL NOT NULL,
            systolic_bp INTEGER NOT NULL,
            diastolic_bp INTEGER NOT NULL,
            cholesterol INTEGER NOT NULL,
            glucose INTEGER NOT NULL,
            smoking TEXT NOT NULL,
            physical_activity TEXT NOT NULL,
            heart_risk REAL NOT NULL,
            diabetes_risk REAL NOT NULL,
            stroke_risk REAL NOT NULL,
            composite_risk REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def save_record(
    patient_id: str,
    patient_name: str,
    age: int,
    gender: str,
    bmi: float,
    sys_bp: int,
    dia_bp: int,
    cholesterol: int,
    glucose: int,
    smoking: str,
    activity: str,
    heart_risk: float,
    diabetes_risk: float,
    stroke_risk: float,
    composite_risk: float,
    db_path: Path = DB_FILE,
) -> None:
    """Insert a new patient risk record into the SQLite database.

    Args:
        patient_id: Identifier supplied by the user (e.g., medical record number).
        patient_name: Human‑readable patient name.
        age, gender, bmi, sys_bp, dia_bp, cholesterol, glucose, smoking, activity: Clinical inputs.
        heart_risk, diabetes_risk, stroke_risk, composite_risk: Calculated risk values (as percentages).
        db_path: Optional custom path to the SQLite file.
    """
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO patient_records (
            patient_id, patient_name, timestamp, age, gender, bmi,
            systolic_bp, diastolic_bp, cholesterol, glucose, smoking,
            physical_activity, heart_risk, diabetes_risk, stroke_risk, composite_risk
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            patient_name,
            timestamp,
            int(age),
            gender,
            float(bmi),
            int(sys_bp),
            int(dia_bp),
            int(cholesterol),
            int(glucose),
            smoking,
            activity,
            float(heart_risk),
            float(diabetes_risk),
            float(stroke_risk),
            float(composite_risk),
        ),
    )
    conn.commit()
    conn.close()

def load_records(search_query: str | None = None, db_path: Path = DB_FILE) -> pd.DataFrame:
    """Load patient records from the SQLite database optionally filtered by a search term.

    Args:
        search_query: Substring to match against patient_name or patient_id. If None, all rows are returned.
        db_path: Path to the SQLite file.
    """
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM patient_records"
    params: list = []
    if search_query:
        query += " WHERE patient_name LIKE ? OR patient_id LIKE ?"
        like = f"%{search_query}%"
        params.extend([like, like])
    query += " ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def delete_record(record_id: int, db_path: Path = DB_FILE) -> None:
    """Delete a patient record from the database by its primary key ``id``.

    Args:
        record_id: The integer ``id`` column value of the row to remove.
        db_path: Optional path to the SQLite file.
    """
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patient_records WHERE id = ?", (int(record_id),))
    conn.commit()
    conn.close()


# ==========================================
# USER MANAGEMENT DATABASE LAYER
# ==========================================

def init_users_db(db_path: Path = DB_FILE) -> None:
    """Create the ``users`` table if it does not exist and seed the default admin account.

    The admin account uses the same credentials as the legacy ``secrets.toml`` entry:
    username ``admin``, password ``16061119``.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            verified INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL,
            last_login DATETIME
        )
        """
    )
    conn.commit()
    
     
    
    # Seed default admin if the table is empty
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = cursor.fetchone()[0]
    if admin_count == 0:
        import hashlib
        admin_hash = hashlib.sha256("16061119".encode()).hexdigest()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (username, full_name, email, password_hash, role, verified, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("admin", "Administrator", "dheerajtiwari.pandit@gmail.com", admin_hash, "admin", 1, now),
        )
        conn.commit()
    conn.close()


def create_user(
    username: str,          
    full_name: str,
    email: str,
    password_hash: str,
    role: str = "user",
    db_path: Path = DB_FILE,
) -> bool:
    """Insert a new verified user into the ``users`` table.

    Returns True on success, False if the username or email already exists.
    """
    init_users_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            """
            INSERT INTO users (username, full_name, email, password_hash, role, verified, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?)
            """,
            (username, full_name, email, password_hash, role, now),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user_by_username(username: str, db_path: Path = DB_FILE) -> dict | None:
    """Return the user row as a dict, or None if not found."""
    init_users_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_email(email: str, db_path: Path = DB_FILE) -> dict | None:
    """Return the user row as a dict, or None if not found."""
    init_users_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users(db_path: Path = DB_FILE) -> pd.DataFrame:
    """Return all users as a DataFrame for the admin panel."""
    init_users_db(db_path)
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT id, username, full_name, email, role, created_at, last_login FROM users ORDER BY created_at DESC",
        conn,
    )
    conn.close()
    return df


def delete_user(user_id: int, db_path: Path = DB_FILE) -> None:
    """Delete a user by their primary key ``id``."""
    init_users_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ? AND role != 'admin'", (int(user_id),))
    conn.commit()
    conn.close()


def update_last_login(username: str, db_path: Path = DB_FILE) -> None:
    """Set the ``last_login`` timestamp for the given user."""
    init_users_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", (now, username))
    conn.commit()
    conn.close()


def update_user_role(user_id: int, new_role: str, db_path: Path = DB_FILE) -> None:
    """Change a user's role (e.g. 'user' → 'admin' or vice versa)."""
    init_users_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, int(user_id)))
    conn.commit()
    conn.close()