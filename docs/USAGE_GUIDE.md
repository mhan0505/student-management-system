# Hướng dẫn sử dụng Student Management System

## 📚 Cấu trúc Project (Top 0.1% Architecture)

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

## 🚀 Bắt đầu nhanh

### ⭐ Option 1: Web UI (RECOMMENDED)

```powershell
# 1. Activate environment
.\student_env\Scripts\activate

# 2. Run NiceGUI app
python app.py

# 3. Open browser: http://localhost:8080
```

**Features:**
- Interactive parameter tuning (IQR slider)
- Real-time charts & analytics
- One-click data export
- Professional UI/UX

👉 **See [NICEGUI_GUIDE.md](NICEGUI_GUIDE.md) for details**

---

### Option 2: CLI (Command Line)

```powershell
# 1. Activate environment
.\student_env\Scripts\activate

# 2. Run pipeline
python main.py

# Output: student_report.csv + student_analysis.log
```

---

### Option 3: Jupyter Notebook

```powershell
# 1. Activate environment
.\student_env\Scripts\activate

# 2. Start Jupyter
jupyter notebook notebook.ipynb
```

## 💡 Cách sử dụng từng module

### Config Layer

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

### Analytics Service (UI-Friendly Design)

```python
from src.services.analytics_service import StudentAnalyticsService

# Khởi tạo với DataFrame (decoupled from DB)
analytics = StudentAnalyticsService(df)

# Method chaining support
analytics.impute_missing()          # Điền missing values by major
analytics.add_bmi()                 # Tính BMI (vectorized)
analytics.add_age()                 # Tính tuổi
analytics.add_zscores()             # Z-score normalization

# ⭐ KEY FEATURE: Parameterized outlier detection
outliers_strict = analytics.detect_outliers_iqr('bmi', multiplier=1.5)  # Strict
outliers_relaxed = analytics.detect_outliers_iqr('bmi', multiplier=3.0) # Relaxed

# Summary statistics
summary = analytics.get_summary_by_major()

# Lấy processed data
processed_df = analytics.get_data()
```

**Design Highlights:**
- ✅ Accepts DataFrame (not tied to repository)
- ✅ Parameterized methods (threshold, reference_date)
- ✅ Immutable operations (returns new data)
- ✅ Perfect for UI integration

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

## 🎯 Các chức năng chính

### 1. Xử lý Missing Values

- **Median by group** thay vì mean toàn bộ
- `height_cm`, `weight_kg`: median theo `gender`
- `gpa`: median theo `major`

### 2. Feature Engineering

- **BMI**: Vectorized với NumPy
- **Age**: Tính từ date of birth
- **Z-scores**: Chuẩn hóa các cột số

### 3. Outlier Detection

- **IQR method**: [Q1 - 1.5×IQR, Q3 + 1.5×IQR]
- Áp dụng cho: BMI, GPA

### 4. Statistics

- Summary by major
- Top K students per major
- Ranked by GPA, then credits

## 🔧 Troubleshooting

### Lỗi kết nối database

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

## 📈 Best Practices

1. **Luôn close connection**: `client.close()`
2. **Sử dụng logging**: Xem log trong `student_analysis.log`
3. **Validate data**: Dùng `DataValidator` trước khi xử lý
4. **Backup data**: Lưu file CSV trước khi xử lý

## 🎓 Học thêm

- Xem code trong từng file để hiểu chi tiết
- Đọc docstrings của mỗi function
- Chạy notebook từng cell để hiểu flow
- Thử modify parameters để thấy sự khác biệt
