import sqlite3

def get_connection():
    conn = sqlite3.connect('tareas.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn 

def create_table():
    conn = get_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS tareas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descripcion TEXT,
                    completada NOT NULL DEFAULT O,
                    fecha TEXT DEFAULT CURRENT_TIMESTAMP
                )""")
    conn.commit()
    conn.close()
