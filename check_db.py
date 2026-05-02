import sqlite3

def check_db():
    try:
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Count for {table_name}: {count}")
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            info = cursor.fetchall()
            print(f"Schema for {table_name}: {info}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
