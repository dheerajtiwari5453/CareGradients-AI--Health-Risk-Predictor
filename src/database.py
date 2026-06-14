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



