# database.py
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "sistema_estoque")
        )
    
    @staticmethod
    def execute_query(query, params=None, fetch=False):
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        result = None
        
        try:
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
                
        except Exception as e:
            conn.rollback()
            print(f"Erro no banco de dados: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
            
        return result