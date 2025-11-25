import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def simple_test():
    """Test kết nối đơn giản"""
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),  # Đọc từ .env
            charset='utf8mb4'
        )
        
        print(" Kết nối MySQL thành công!")
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(" Danh sách databases:")
            for db in databases:
                print(f"  - {db[0]}")
        
        connection.close()
        print(" Test kết nối thành công!")
        
    except Exception as e:
        print(f" Lỗi: {e}")
        print(f" Loại lỗi: {type(e).__name__}")

if __name__ == "__main__":
    simple_test()