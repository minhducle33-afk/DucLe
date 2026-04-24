import os
import pandas as pd
from supabase import create_client
from datetime import datetime

# Lấy thông tin từ GitHub Secrets (đã thiết lập ở bước trước)
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")

# QUAN TRỌNG: Thay tên các bảng dưới đây bằng tên bảng thực tế trong Supabase của bạn
# Ví dụ: nếu bạn có bảng tên là 'du_an' và 'cong_viec', hãy sửa lại cho đúng
TABLES = ['projects', 'tasks'] 

def run_backup():
    if not URL or not KEY:
        print("Lỗi: Không tìm thấy SUPABASE_URL hoặc SUPABASE_KEY trong Secrets!")
        return

    try:
        supabase = create_client(URL, KEY)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Tạo thư mục backups nếu chưa có
        if not os.path.exists("backups"):
            os.makedirs("backups")
            print("Đã tạo thư mục backups")

        for table in TABLES:
            print(f"Đang lấy dữ liệu từ bảng: {table}...")
            # Lấy toàn bộ dữ liệu từ bảng
            response = supabase.table(table).select("*").execute()
            
            # Chuyển dữ liệu sang dạng bảng (DataFrame)
            df = pd.DataFrame(response.data)
            
            # Lưu thành file CSV trong thư mục backups
            file_path = f"backups/{table}_{today}.csv"
            df.to_csv(file_path, index=False)
            print(f"---> Đã lưu thành công: {file_path}")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    run_backup()
