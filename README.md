# 🎓 Hệ thống Quản lý Sinh viên

Đây là project cuối kỳ môn Python - Xây dựng hệ thống quản lý và phân tích dữ liệu sinh viên với giao diện web tương tác (NiceGUI), MySQL database, và các công cụ phân tích dữ liệu như Pandas/NumPy.

## ✨ Tính năng chính

### 🌐 Giao diện Web (NiceGUI)
- Thiết kế responsive với Quasar Framework
- Điều chỉnh tham số phân tích trực tiếp trên giao diện (IQR threshold slider)
- Biểu đồ tương tác real-time với Plotly
- So sánh dữ liệu trước/sau xử lý
- Export CSV chỉ với một click
- Kiến trúc phân tầng rõ ràng (UI ← Service ← Repository)
- Đầy đủ chức năng CRUD (Thêm, Sửa, Xóa, Lọc)
- Hệ thống backup tự động khi xóa + khôi phục lại 10 lần xóa gần nhất

**📖 Tài liệu chi tiết:**
- [docs/NICEGUI_GUIDE.md](docs/NICEGUI_GUIDE.md) - Hướng dẫn sử dụng giao diện web
- [CRUD_FEATURES.md](CRUD_FEATURES.md) - Chi tiết các chức năng CRUD & Backup
- [NICEGUI_SUMMARY.md](NICEGUI_SUMMARY.md) - Tóm tắt implementation

---

## 📋 Giới thiệu

Project này xây dựng một quy trình xử lý dữ liệu hoàn chỉnh bao gồm:
- Kết nối và truy vấn dữ liệu từ MySQL database
- Xử lý dữ liệu thiếu (tự động điền theo nhóm major)
- Tính toán các chỉ số mới (BMI, tuổi, Z-scores)
- Phát hiện ngoại lệ với ngưỡng IQR có thể tùy chỉnh
- Tạo báo cáo thống kê theo từng ngành học
- Xuất kết quả ra file CSV
- Giao diện web để thử nghiệm các tham số phân tích

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

## 🎯 Các tính năng chính

### 📊 Phân tích dữ liệu
- Tự động xử lý dữ liệu bị thiếu (theo từng nhóm major)
- Tính toán các chỉ số mới (BMI, tuổi, Z-scores)
- Phát hiện ngoại lệ với ngưỡng IQR tùy chỉnh được
- Tạo báo cáo thống kê theo ngành học

### 🛠️ Quản lý dữ liệu (CRUD)
- **Thêm mới**: Thêm sinh viên với validation 14 trường thông tin
- **Xem**: Hiển thị dữ liệu với bảng phân trang (20/50/100/200/500 dòng)
- **Sửa**: Chỉnh sửa thông tin sinh viên (13 trường có thể sửa)
- **Xóa**: Xóa sinh viên kèm backup tự động
- **Lọc**: Tìm kiếm sinh viên theo ngưỡng GPA

### 🔒 Bảo vệ dữ liệu
- **Backup tự động**: Mỗi lần xóa đều tạo bản sao lưu
- **Hoàn tác**: Khôi phục lại 10 lần xóa gần nhất
- **Hàng đợi FIFO**: Giữ tối đa 10 bản backup trong bộ nhớ
- **Lưu đầy đủ**: Cả 14 trường dữ liệu + timestamp

## 🚀 Hướng dẫn chạy nhanh

### ⭐ Cách 1: Giao diện Web (NiceGUI) - Khuyên dùng ⭐

```powershell
# Bước 1: Kích hoạt môi trường ảo
.\student_env\Scripts\Activate.ps1

# Bước 2: Cài đặt thư viện (nếu chưa có)
pip install -r requirements.txt

# Bước 3: Cấu hình file .env
# Cần có: MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB

# Bước 4: Chạy ứng dụng
python app.py
```

**🌐 Mở trình duyệt tại:** `http://localhost:8080`

**✨ Những tính năng nổi bật:**
- 🎛️ **Thanh trượt điều chỉnh IQR** (1.0 - 3.0) - Thử nghiệm các ngưỡng khác nhau!
- 📊 **Biểu đồ Plotly tương tác** - Khám phá dữ liệu trực quan
- 📋 **Bảng dữ liệu AgGrid** - Sắp xếp, lọc, phân trang (20/50/100/200/500 dòng)
- 🎯 **Phát hiện ngoại lệ** - Hiển thị chi tiết các điểm bất thường
- 💾 **Export CSV một chạm** - Tải xuống ngay vào thư mục Downloads
- 🔄 **So sánh trước/sau** - Xem dữ liệu thay đổi như thế nào
- 🎨 **Giao diện hiện đại** - Sidebar, tabs, hệ thống thông báo
- ➕ **Quản lý CRUD đầy đủ** - Thêm, sửa, xóa sinh viên với validation
- ↩️ **Hệ thống Backup/Undo** - Tự động backup khi xóa, khôi phục 10 lần gần nhất
- 🔍 **Lọc theo GPA** - Tìm sinh viên đạt ngưỡng điểm

**👉 Xem chi tiết tại [docs/NICEGUI_GUIDE.md](docs/NICEGUI_GUIDE.md)**

---

### Cách 2: Dòng lệnh (CLI)

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

## 💻 Cách sử dụng

### Chạy toàn bộ quy trình phân tích

```powershell
python main.py
```

**Lưu ý:** Mỗi lần chạy hệ thống sẽ tự động tạo bản backup dữ liệu gốc vào folder `backups/`

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

## 📊 Các chức năng chính

### 1. Lớp truy xuất dữ liệu
- `MySQLClient`: Quản lý kết nối MySQL và chạy các câu lệnh query
- `StudentRepository`: Lấy dữ liệu sinh viên từ database

### 2. Dịch vụ phân tích
- `impute_missing()`: Tự động điền các ô dữ liệu bị thiếu
- `add_bmi()`: Tính chỉ số BMI (cân nặng/chiều cao)
- `add_age()`: Tính tuổi dựa vào ngày sinh
- `add_zscores()`: Chuẩn hóa dữ liệu về dạng Z-score
- `detect_outliers_iqr()`: Tìm các điểm dữ liệu bất thường
- `summary_by_major()`: Tạo bảng thống kê theo từng ngành
- `top_k_per_major()`: Xếp hạng sinh viên giỏi nhất mỗi ngành

### 3. Tạo báo cáo
- `generate_full_report()`: Tạo báo cáo phân tích đầy đủ
- `export_csv()`: Xuất kết quả ra file CSV

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

## 🎓 Thông tin

- Sinh viên: Lại Minh An
- Lớp: DSEB 66A
- Môn học: Python for Data Science

## 📄 License

Educational project for university coursework.
