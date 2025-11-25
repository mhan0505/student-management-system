# Hướng dẫn sử dụng Student Management System

## 📚 Cấu trúc Project 

```
[DSEB]FINAL/
├── src/                     # Source code chính
│   ├── config/             # Cấu hình (DB, Settings)
│   ├── models/             # Data models
│   ├── repositories/       # Data access layer (SQL)
│   ├── services/           # Business logic (Analytics)
│   ├── reports/            # Report generation
│   └── utils/              # Utilities
├── docs/                    # Documentation
│   ├── USAGE_GUIDE.md      # CLI usage guide
│   ├── ARCHITECTURE.md     # Architecture design
│   └── NICEGUI_GUIDE.md    # ⭐ Web UI guide
├── app.py                   # ⭐ NiceGUI Web UI (NEW!)
├── main.py                  # CLI entry point
├── notebook.ipynb           # Jupyter demo
├── .env                     # Environment variables
└── requirements.txt         # Dependencies
```

## 2. Hướng dẫn Khởi động Nhanh

### 2.1. Phương án 1: Giao diện Web (Khuyên dùng)

```powershell
# Bước 1: Kích hoạt môi trường ảo
.\student_env\Scripts\activate

# Bước 2: Chạy ứng dụng NiceGUI
python app.py

# Bước 3: Mở trình duyệt tại: http://localhost:8080
```

**Các tính năng chính:**
- Điều chỉnh tham số tương tác (IQR slider)
- Biểu đồ và phân tích real-time
- Xuất dữ liệu một chạm
- Giao diện chuyên nghiệp

**Chi tiết**: Xem [NICEGUI_GUIDE.md](NICEGUI_GUIDE.md)

### 2.2. Phương án 2: Giao diện Dòng lệnh (CLI)

```powershell
# Bước 1: Kích hoạt môi trường ảo
.\student_env\Scripts\activate

# Bước 2: Chạy quy trình xử lý
python main.py

# Kết quả: student_report.csv + student_analysis.log
```

### 2.3. Phương án 3: Jupyter Notebook

```powershell
# Bước 1: Kích hoạt môi trường ảo
.\student_env\Scripts\activate

# Bước 2: Khởi động Jupyter
jupyter notebook notebook.ipynb
```

## 3. Hướng dẫn Sử dụng các Module

### 3.1. Tầng Cấu hình (Config Layer)

```python
from src.config.database import DatabaseConfig

# Load config từ .env
config = DatabaseConfig.from_env()
print(config)  # Hiển thị config (ẩn password)

# Lấy connection string
conn_str = config.get_connection_string()
```

### Repository Layer

```python
from src.repositories.mysql_client import MySQLClient
from src.repositories.student_repository import StudentRepository

# Tạo MySQL client
client = MySQLClient(config)
client.test_connection()

# Tạo repository
repo = StudentRepository(client)

# Truy vấn dữ liệu
all_students = repo.fetch_all()
dseb_students = repo.fetch_by_major("Data Science")
high_gpa = repo.fetch_by_gpa_range(3.5, 4.0)
search_results = repo.search_by_name("Nguyen")
```

### 3.3. Dịch vụ Phân tích (Analytics Service)

```python
from src.services.analytics_service import StudentAnalyticsService

# Khởi tạo với DataFrame (tách biệt khỏi Database)
analytics = StudentAnalyticsService(df)

# Hỗ trợ method chaining
analytics.impute_missing()          # Điền giá trị thiếu theo nhóm major
analytics.add_bmi()                 # Tính BMI (vectorized)
analytics.add_age()                 # Tính tuổi
analytics.add_zscores()             # Chuẩn hóa Z-score

# Tính năng chính: Phát hiện ngoại lệ với tham số linh hoạt
outliers_strict = analytics.detect_outliers_iqr('bmi', multiplier=1.5)  # Nghiêm ngặt
outliers_relaxed = analytics.detect_outliers_iqr('bmi', multiplier=3.0) # Linh hoạt

# Thống kê tổng hợp
summary = analytics.get_summary_by_major()

# Lấy dữ liệu đã xử lý
processed_df = analytics.get_data()
```

**Điểm nổi bật của thiết kế:**
- Nhận DataFrame đầu vào (không phụ thuộc repository)
- Phương thức tham số hóa (threshold, reference_date)
- Thao tác bất biến (trả về dữ liệu mới)
- Tích hợp hoàn hảo với giao diện người dùng

### Report Generator

```python
from src.reports.report_generator import StudentReportGenerator

# Tạo report generator
generator = StudentReportGenerator(repository)

# Chạy pipeline hoàn chỉnh
df = generator.generate_full_report(
    output_file='student_report.csv',
    detect_outliers=True,
    top_k=3
)

# Lấy các thống kê
summary = generator.get_summary_by_major()
top_students = generator.get_top_students(k=5)
outliers = generator.get_outliers('bmi')
```

## 📊 Ví dụ workflow hoàn chỉnh

```python
# 1. Setup
from src.config.database import DatabaseConfig
from src.repositories.mysql_client import MySQLClient
from src.repositories.student_repository import StudentRepository
from src.reports.report_generator import StudentReportGenerator

# 2. Connect
config = DatabaseConfig.from_env()
client = MySQLClient(config)
repo = StudentRepository(client)

# 3. Generate report
generator = StudentReportGenerator(repo)
df = generator.generate_full_report()

# 4. Analyze
print(generator.get_summary_by_major())
print(generator.get_top_students(k=3))

# 5. Cleanup
client.close()
```

## 4. Các Chức năng Chính

### 4.1. Xử lý Dữ liệu Thiếu (Missing Values)

- Chiến lược: **Median theo nhóm** (thay vì mean toàn bộ)
- Các trường `height_cm`, `weight_kg`: Median theo `gender`
- Trường `gpa`: Median theo `major`

### 4.2. Tạo Đặc trưng (Feature Engineering)

- **BMI**: Tính toán vectorized với NumPy
- **Age**: Tính từ ngày sinh (date of birth)
- **Z-scores**: Chuẩn hóa các cột số

### 4.3. Phát hiện Ngoại lệ (Outlier Detection)

- Phương pháp: **IQR** với khoảng [Q1 - 1.5×IQR, Q3 + 1.5×IQR]
- Áp dụng cho các trường: BMI, GPA

### 4.4. Thống kê

- Tổng hợp theo từng ngành (major)
- Top K sinh viên xuất sắc mỗi ngành
- Xếp hạng theo GPA, tiếp theo là credits

## 5. Xử lý Sự cố

### 5.1. Lỗi kết nối cơ sở dữ liệu

```python
# Kiểm tra config
config = DatabaseConfig.from_env()
print(config)

# Test connection
client = MySQLClient(config)
if client.test_connection():
    print("OK")
```

### Lỗi import module

```python
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd()))
```

### Lỗi missing values

```python
# Kiểm tra missing
print(df.isna().sum())

# Impute manually
analytics = StudentAnalyticsService(df)
analytics.impute_missing()
```

## 6. Nguyên tắc Thực hành Tốt

1. **Đóng kết nối**: Luôn gọi `client.close()` sau khi hoàn tất
2. **Sử dụng logging**: Theo dõi log trong file `student_analysis.log`
3. **Kiểm tra dữ liệu**: Sử dụng `DataValidator` trước khi xử lý
4. **Sao lưu dữ liệu**: Lưu file CSV trước khi thực hiện xử lý

## 7. Tài liệu Tham khảo

Để hiểu rõ hơn về hệ thống:

- Nghiên cứu mã nguồn trong từng file module
- Đọc docstrings của các function để hiểu đầy đủ tham số
- Chạy notebook theo từng cell để nắm bắt quy trình
- Thử nghiệm với các tham số khác nhau để quan sát sự thay đổi
