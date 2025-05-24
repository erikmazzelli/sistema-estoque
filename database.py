# database.py
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host=os.getenv('MYSQLHOST'),
            port=int(os.getenv('MYSQLPORT')),
            user=os.getenv('MYSQLUSER'),
            password=os.getenv('MYSQLPASSWORD'),
            database=os.getenv('MYSQLDATABASE'),
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