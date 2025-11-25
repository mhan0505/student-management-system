# 🎓 Student Management System - "Top 0.1% Edition"

Hệ thống quản lý và phân tích dữ liệu sinh viên với **Interactive Web UI (NiceGUI)** và **CLI**, sử dụng Python, MySQL, Pandas và NumPy.

## ⭐ NEW: NiceGUI Web Interface
- 🎨 Modern, responsive UI with Quasar Framework
- 🎛️ **Interactive parameter tuning** (IQR threshold slider)
- 📊 Real-time analytics với Plotly charts
- 🔄 Before/After data comparison
- 💾 One-click CSV export
- 🏗️ Clean Architecture (UI ← Service ← Repository)
- 🛠️ **Full CRUD Operations** (Add, Update, Delete, Filter)
- ↩️ **Backup/Undo System** (Automatic backup on delete, restore last 10)

**📚 Documentation:**
- [docs/NICEGUI_GUIDE.md](docs/NICEGUI_GUIDE.md) - Complete Web UI guide
- [CRUD_FEATURES.md](CRUD_FEATURES.md) - CRUD Operations & Backup System
- [NICEGUI_SUMMARY.md](NICEGUI_SUMMARY.md) - Implementation summary

---

## 📋 Mô tả

Project này xây dựng một pipeline hoàn chỉnh để:
- Kết nối và truy vấn dữ liệu từ MySQL
- Xử lý dữ liệu thiếu (missing data imputation by major)
- Tạo các đặc trưng mới (BMI, Age, Z-scores)
- Phát hiện ngoại lệ (outlier detection với **custom IQR threshold**)
- Tạo báo cáo thống kê theo ngành học
- Xuất kết quả ra file CSV
- **✨ Interactive web UI cho parameter exploration**

## 🏗️ Cấu trúc Project

```
student_management_system/
├── src/
│   ├── config/              # Cấu hình database và settings
│   │   ├── __init__.py
│   │   ├── database.py      # DatabaseConfig class
│   │   └── settings.py      # Application settings
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   └── student.py       # Student model
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── mysql_client.py  # MySQL client
│   │   └── student_repository.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   └── analytics_service.py
│   ├── reports/             # Report generation
│   │   ├── __init__.py
│   │   └── report_generator.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── validators.py
│       └── formatters.py
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md      # System architecture
│   ├── USAGE_GUIDE.md       # CLI usage guide
│   └── NICEGUI_GUIDE.md     # ⭐ Web UI guide
├── tests/                   # Unit tests
├── scripts/                 # Utility scripts
├── app.py                   # ⭐ NiceGUI Web UI entry point
├── main.py                  # CLI entry point
├── notebook.ipynb           # Jupyter notebook demo
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment file
├── .gitignore
├── requirements.txt
└── README.md
```

## 🎯 Key Features

### 📊 Analytics Pipeline
- Missing data imputation (by major)
- Feature engineering (BMI, Age, Z-scores)
- Outlier detection with custom IQR threshold
- Statistical reports by major

### 🛠️ Data Management (CRUD)
- **Create**: Add new students with 14-field validation
- **Read**: Load and view data with AG Grid pagination
- **Update**: Modify student information (13 editable fields)
- **Delete**: Remove students with automatic backup
- **Filter**: Query students by GPA threshold

### 🔒 Safety Features
- **Automatic Backup**: Every deletion creates a backup
- **Undo Delete**: Restore last 10 deleted students
- **FIFO Queue**: Maintains max 10 backups in memory
- **Full Record Preservation**: All 14 fields + timestamp saved

## 🚀 Quick Start

### ⭐ Option 1: Web UI (NiceGUI) - RECOMMENDED ⭐

```powershell
# 1. Activate environment
.\student_env\Scripts\Activate.ps1

# 2. Install dependencies (nếu chưa)
pip install -r requirements.txt

# 3. Configure .env file
# Đảm bảo có: MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB

# 4. Run NiceGUI app
python app.py
```

**🌐 Server starts at:** `http://localhost:8080`

**✨ Top 0.1% Features:**
- 🎛️ **Interactive IQR Threshold Slider** (1.0 - 3.0) - Parameter tuning!
- 📊 **Real-time Plotly Charts** - Interactive visualizations
- 📋 **AgGrid Data Table** - Sortable, filterable, paginated (20/50/100/200/500 rows)
- 🎯 **Outlier Detection** - Visual feedback with student details
- 💾 **One-click CSV Export** - Instant download to Downloads folder
- 🔄 **Before/After Comparison** - See data transformation
- 🎨 **Modern UI** - Sidebar, tabs, notification system
- ➕ **CRUD Operations** - Add, Update, Delete students with full validation
- ↩️ **Backup/Undo System** - Automatic backup on delete, restore last 10 deletions
- 🔍 **Filter by GPA** - Query students above GPA threshold

**👉 See [docs/NICEGUI_GUIDE.md](docs/NICEGUI_GUIDE.md) for complete guide**

---

### Option 2: CLI (Command Line)

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone <your-repo-url>
cd student_management_system
```

### 2. Tạo virtual environment

```powershell
python -m venv student_env
.\student_env\Scripts\activate
```

### 3. Cài đặt dependencies

```powershell
pip install -r requirements.txt
```

### 4. Cấu hình database

Tạo file `.env` từ `.env.example`:

```bash
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=university
```

## 💻 Sử dụng

### Chạy pipeline hoàn chỉnh

```powershell
python main.py
```

**Lưu ý:** Mỗi lần chạy sẽ tự động tạo backup của dữ liệu gốc vào thư mục `backups/`

### Quản lý Backup

```powershell
# Xem danh sách backups
python scripts/backup_manager.py list

# Restore từ backup
python scripts/backup_manager.py restore raw_data_20251120_225453.csv

# Dọn dẹp backups cũ (giữ lại 5 bản mới nhất)
python scripts/backup_manager.py cleanup 5

# So sánh 2 backups
python scripts/backup_manager.py compare backup1.csv backup2.csv
```

### Chạy Jupyter Notebook

```powershell
jupyter notebook notebook.ipynb
```

### Import và sử dụng trong code

```python
from src.config.database import DatabaseConfig
from src.repositories.mysql_client import MySQLClient
from src.repositories.student_repository import StudentRepository
from src.reports.report_generator import StudentReportGenerator

# Load config
config = DatabaseConfig.from_env()

# Initialize components
client = MySQLClient(config)
repository = StudentRepository(client)

# Generate report
generator = StudentReportGenerator(repository)
df = generator.generate_full_report()
```

## 📊 Chức năng chính

### 1. Data Access Layer
- `MySQLClient`: Kết nối MySQL và thực thi queries
- `StudentRepository`: Truy vấn dữ liệu sinh viên

### 2. Analytics Service
- `impute_missing()`: Xử lý dữ liệu thiếu
- `add_bmi()`: Tính chỉ số BMI
- `add_age()`: Tính tuổi từ ngày sinh
- `add_zscores()`: Chuẩn hóa Z-score
- `detect_outliers_iqr()`: Phát hiện ngoại lệ
- `summary_by_major()`: Thống kê theo ngành
- `top_k_per_major()`: Xếp hạng top sinh viên

### 3. Report Generator
- `generate_full_report()`: Tạo báo cáo hoàn chỉnh
- `export_csv()`: Xuất dữ liệu ra CSV

## 📈 Pipeline xử lý dữ liệu

```
1. Fetch data from MySQL
   ↓
2. Impute missing values (median by group)
   ↓
3. Calculate BMI (vectorized NumPy)
   ↓
4. Calculate Age from DOB
   ↓
5. Calculate Z-scores
   ↓
6. Detect outliers (IQR method)
   ↓
7. Generate statistics by major
   ↓
8. Export to CSV
```

## 🧪 Testing

```powershell
pytest tests/
```

## 📝 Yêu cầu

- Python 3.10+
- MySQL 5.7+
- Dependencies xem trong `requirements.txt`

## 🎓 Tác giả

- Sinh viên: [Lại Minh An]
- Lớp: DSEB
- Môn học: Data Science with Python

## 📄 License

Educational project for university coursework.
