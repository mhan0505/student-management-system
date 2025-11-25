# Architecture Documentation - "Top 0.1% Design"

## System Overview

Hệ thống Student Management System được thiết kế theo **Clean Architecture** với **Layered Pattern**:

```
┌─────────────────────────────────────────┐
│   UI LAYER (app.py - NiceGUI)           │ ← NEW! Interactive Web UI
│   - User interactions                   │
│   - Event handlers                      │
│   - State management                    │
├─────────────────────────────────────────┤
│   Presentation Layer (main.py)          │ ← CLI interface
│   - Jupyter Notebook                    │
├─────────────────────────────────────────┤
│   Report Layer (report_generator.py)    │
│   - Pipeline Orchestration              │
│   - Backup management                   │
├─────────────────────────────────────────┤
│   Service Layer (analytics_service.py)  │
│   - Business Logic                      │
│   - Parameterized methods ⭐            │
├─────────────────────────────────────────┤
│   Repository Layer (student_repository) │
│   - Data Access (SQL queries)           │
├─────────────────────────────────────────┤
│   Infrastructure (mysql_client)         │
│   - Database Connection                 │
└─────────────────────────────────────────┘
```

## 🎯 "Top 0.1%" Design Principles

### 1. Separation of Concerns
- **UI Layer không chứa business logic**
- **Service Layer không biết về UI**
- **Repository Layer chỉ làm data access**

### 2. Dependency Inversion
```python
# UI depends on Service (abstraction)
# Service depends on DataFrame (not Repository)
class StudentAnalyticsService:
    def __init__(self, df: pd.DataFrame):  # ← Decoupled!
        self.df = df
```

### 3. Parameterization (Key for UI)
```python
# Before (fixed)
def detect_outliers(df):
    return df[df['bmi'] > threshold]  # threshold hard-coded

# After (parameterized) ⭐
def detect_outliers_iqr(df, multiplier=1.5):
    return df[df['bmi'] > Q3 + multiplier * IQR]  # UI can control!
```

## Layer Responsibilities

### 1. Config Layer (`src/config/`)

**Responsibility**: Quản lý cấu hình ứng dụng

- `database.py`: Database connection configuration
- `settings.py`: Application-wide settings và constants

**Principles**:
- Single source of truth cho config
- Environment-based configuration
- No hard-coded values

### 2. Model Layer (`src/models/`)

**Responsibility**: Define data structures

- `student.py`: Student data model với validation

**Principles**:
- Immutable data structures (dataclass)
- Built-in validation
- Type safety

### 3. Repository Layer (`src/repositories/`)

**Responsibility**: Data access và persistence

- `mysql_client.py`: Low-level database operations
- `student_repository.py`: Student-specific queries

**Principles**:
- Separation of data access từ business logic
- Return pandas DataFrames
- No business logic trong repository

### 4. Service Layer (`src/services/`)

**Responsibility**: Business logic và data processing

### 4. Service Layer (`src/services/`)

**Responsibility**: Business logic và data processing

- `analytics_service.py`: Data analysis với **parameterized methods**

**Principles**:
- Pure business logic
- No database dependencies
- **Accepts DataFrame (decoupled from Repository)** ⭐
- **Parameterized operations for UI integration** ⭐
- Immutable operations (returns new data)

**UI-Friendly Design:**
```python
class StudentAnalyticsService:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()  # Work on copy
    
    def detect_outliers_iqr(self, column: str, multiplier: float = 1.5):
        # multiplier can be controlled by UI slider!
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - multiplier * IQR
        upper = Q3 + multiplier * IQR
        return self.df[(self.df[column] < lower) | (self.df[column] > upper)]
```

### 5. Report Layer (`src/reports/`)

**Responsibility**: Orchestrate pipeline và generate reports

- `report_generator.py`: End-to-end pipeline với backup support

**Principles**:
- High-level orchestration
- Combine multiple services
- Export functionality
- **Automatic backup before processing** (safety net)

### 6. UI Layer (`app.py`) ⭐ NEW!

**Responsibility**: Interactive web interface

- `app.py`: NiceGUI application với **state management**

**Principles**:
- **NO business logic** (chỉ điều phối)
- **Calls Service methods**
- Real-time user feedback
- Parameter exploration support

**State Management:**
```python
class AppState:
    def __init__(self):
        self.df_raw = pd.DataFrame()         # Raw data
        self.df_processed = pd.DataFrame()   # Processed data
        self.current_threshold = 1.5         # UI parameter
        self.grid = None                     # UI components
        self.chart_container = None
```

### 7. Utils Layer (`src/utils/`)

**Responsibility**: Shared utilities

- `validators.py`: Data validation
- `formatters.py`: Data formatting

**Principles**:
- Reusable functions
- No business logic
- Pure functions

## Data Flow

### CLI Flow (main.py)
```
┌──────────┐
│  .env    │ → DatabaseConfig
└──────────┘
                ↓
         MySQLClient
                ↓
      StudentRepository.fetch_all()
                ↓
         pandas DataFrame
                ↓
    StudentAnalyticsService
                ↓
    1. impute_missing()
    2. add_bmi()
    3. add_age()
    4. add_zscores()
    5. detect_outliers()
    6. summary_by_major()
                ↓
      processed DataFrame
                ↓
      Save to CSV/Excel
```

### Web UI Flow (app.py) ⭐ NEW!
```
┌──────────┐
│ Browser  │ User visits localhost:8080
└──────────┘
      ↓
┌──────────────────┐
│   app.py         │ NiceGUI renders UI with 4 tabs
│   main_page()    │ (Data View, Charts, Outliers, CRUD)
└──────────────────┘
      ↓ [1. Load Data Button Click]
┌──────────────────────────┐
│ load_data_from_db()      │
│  - Read .env             │
│  - Connect MySQL         │
│  - StudentRepository     │
│  - Load to AppState      │
└──────────────────────────┘
      ↓
┌──────────────────┐
│ UI Updates       │ Show data grid (AG Grid), enable controls
└──────────────────┘
      ↓ [2. Slider Changed (1.5 → 2.0)]
┌──────────────────────────┐
│ run_analytics_pipeline() │
│  threshold = 2.0         │
└──────────────────────────┘
      ↓
┌──────────────────────────┐
│ StudentAnalyticsService  │
│  .detect_outliers_iqr(   │
│    multiplier=2.0)       │ ← Parameterized!
└──────────────────────────┘
      ↓
┌──────────────────┐
│ Plotly Charts    │ Interactive box plots update
└──────────────────┘
      ↓ [3. Export Button Click]
┌──────────────────┐
│ export_to_csv()  │ Save to Downloads folder
└──────────────────┘
```

### CRUD Operations Flow ⭐ NEW!
```
┌─────────────────────┐
│ Tab 4: CRUD Panel   │ User clicks Data Management tab
└─────────────────────┘
      ↓ [ADD Student]
┌────────────────────────────┐
│ Fill 14-field form         │ student_id, full_name, dob, gender,
│ Validate required fields   │ major, class, email, phone, gpa,
│ Convert numeric types      │ credits, height, weight, province,
│                            │ enrollment_date
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ repository.insert_student()│ INSERT INTO students (...)
│  - SQLAlchemy engine       │ VALUES (:student_id, :full_name, ...)
│  - Named parameters        │
│  - Commit transaction      │
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ load_data_from_db()        │ Refresh UI with new data
│ ui.notify('✅ Added...')   │
└────────────────────────────┘

      ↓ [UPDATE Student]
┌────────────────────────────┐
│ Enter: student_id, field,  │ e.g., student_id=1, field=gpa,
│        new_value            │      new_value=3.8
│ Validate types             │ (float for gpa/height/weight,
│                            │  int for credits)
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ repository.update_student()│ UPDATE students SET gpa = :gpa
│  - Dynamic SET clause      │ WHERE student_id = :student_id
│  - Type conversion         │
│  - Return rowcount         │
└────────────────────────────┘

      ↓ [DELETE Student]
┌────────────────────────────┐
│ Enter student_id to delete │
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ Query DB for full record   │ SELECT * WHERE student_id = :id
│  - Get all 14 fields       │
│  - Prepare backup data     │
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ Show confirmation dialog   │ "Delete student X: Name?"
│  "✅ Backup will be created"│
└────────────────────────────┘
      ↓ [User confirms]
┌────────────────────────────┐
│ Create backup              │ backup = {student_data +
│  - Add timestamp           │           deleted_at: timestamp}
│  - Add to FIFO queue       │ deleted_students.append(backup)
│  - Keep max 10             │ if len > 10: pop(0)
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ repository.delete_student()│ DELETE FROM students
│  - Execute DELETE          │ WHERE student_id = :student_id
│  - Commit transaction      │
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ update_undo_list()         │ Refresh backup UI panel
│ load_data_from_db()        │ Refresh main data grid
│ ui.notify('✅ Deleted')    │
└────────────────────────────┘

      ↓ [UNDO Delete]
┌────────────────────────────┐
│ Undo Delete panel          │ Shows last 10 deleted students
│  - Display: ID, Name, Time │ with "↩️ UNDO DELETE" buttons
└────────────────────────────┘
      ↓ [User clicks UNDO]
┌────────────────────────────┐
│ Remove timestamp field     │ clean_data = {k: v for k, v
│ Prepare for re-insertion   │   if k != 'deleted_at'}
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ repository.insert_student()│ Re-INSERT student to database
│  - Full record restoration │
└────────────────────────────┘
      ↓
┌────────────────────────────┐
│ Remove from backup stack   │ deleted_students.remove(backup)
│ update_undo_list()         │ Refresh UI
│ load_data_from_db()        │
│ ui.notify('✅ Restored')   │
└────────────────────────────┘
```

**Key Difference**: Web UI allows **real-time parameter tuning** + **full CRUD** without restarting!

## Design Patterns Used

### 1. Repository Pattern
```python
# Tách data access khỏi business logic
repository = StudentRepository(client)
df = repository.fetch_all()  # Data access

analytics = StudentAnalyticsService(df)
analytics.impute_missing()  # Business logic
```

### 2. Dependency Injection
```python
# Inject dependencies thay vì hard-code
class StudentAnalyticsService:
    def __init__(self, df: pd.DataFrame):
        self.df = df  # Injected DataFrame (decoupled!)
```

### 3. Factory Pattern
```python
# Factory method để create config
config = DatabaseConfig.from_env()
```

### 4. Service Layer Pattern
```python
# Business logic tập trung trong service
service = StudentAnalyticsService(df)
service.add_bmi()
service.add_age()
```

### 5. State Management Pattern ⭐ NEW!
```python
# Centralized state for UI components
class AppState:
    def __init__(self):
        self.df_raw = pd.DataFrame()
        self.df_processed = pd.DataFrame()
        self.current_threshold = 1.5
        self.deleted_students = []        # ⭐ Backup stack
        self.max_backup_size = 10         # ⭐ FIFO limit
        
state = AppState()  # Single source of truth
```

### 6. Command Pattern (CRUD Operations) ⭐ NEW!
```python
# Each CRUD operation is encapsulated
def add_student():
    validate_input()
    execute_command()  # repository.insert_student()
    refresh_ui()

def delete_with_backup():
    backup_data()      # Before delete
    execute_command()  # repository.delete_student()
    update_backup_ui()
```

### 7. Memento Pattern (Backup/Undo) ⭐ NEW!
```python
# Store state for undo capability
backup = {
    **student_data,           # Original state
    'deleted_at': timestamp   # Metadata
}
deleted_students.append(backup)  # Save memento

# Restore state
def undo_delete(backup):
    clean_data = {k: v for k, v in backup.items() if k != 'deleted_at'}
    repository.insert_student(clean_data)  # Restore
```

## Key Principles Applied

### 1. Single Responsibility Principle (SRP)
- Mỗi class chỉ có 1 lý do để thay đổi
- `MySQLClient`: Chỉ quản lý connection + SQLAlchemy engine
- `StudentRepository`: Chỉ truy vấn dữ liệu (SELECT, INSERT, UPDATE, DELETE)
- `StudentAnalyticsService`: Chỉ xử lý logic phân tích
- **`app.py`: Chỉ quản lý UI (NO business logic!)** ⭐

### 2. Dependency Inversion Principle (DIP)
- High-level modules không depend vào low-level modules
- `StudentReportGenerator` depends vào `StudentRepository` interface
- **`app.py` depends vào `StudentAnalyticsService` (không gọi DB trực tiếp!)** ⭐

### 3. Don't Repeat Yourself (DRY)
- Common logic trong `utils/`
- Configuration centralized trong `config/`

### 4. Separation of Concerns
- Database logic ≠ Business logic ≠ **Presentation logic** ⭐
- Mỗi layer có responsibility riêng
- **UI chỉ điều phối, không xử lý data** ⭐

### 5. Parameterization for Flexibility ⭐ NEW!
- Service methods accept parameters (not hardcoded)
- UI can pass different values dynamically
- Example: `detect_outliers_iqr(multiplier=2.0)` instead of fixed 1.5

## Error Handling Strategy

```python
# Config layer: Validate và raise meaningful errors
if not username:
    raise ValueError("MYSQL_USER required")

# Repository layer: Log và propagate errors
try:
    df = pd.read_sql(query, engine)
except Exception as e:
    logger.error(f"Query failed: {e}")
    raise

# Service layer: Handle business exceptions
if std == 0:
    logger.warning("Cannot calculate z-score")
    return df

# UI layer: User-friendly notifications ⭐ NEW!
try:
    run_analytics_pipeline(threshold)
except Exception as e:
    ui.notify(f"Error: {str(e)}", type='negative')
```

## Testing Strategy

```
tests/
├── test_config.py          # Config validation
├── test_repositories.py    # Data access tests
├── test_services.py        # Business logic tests
├── test_ui.py              # UI component tests ⭐ NEW!
└── test_utils.py           # Utility function tests
```

## Performance Optimizations

1. **NumPy Vectorization**: Thay vì loops
   ```python
   # ❌ Slow
   for i, row in df.iterrows():
       bmi = row['weight'] / (row['height']/100)**2
   
   # ✅ Fast
   bmi = weight / (height/100)**2
   ```

2. **Database Connection Pooling**
   ```python
   engine = create_engine(..., pool_pre_ping=True)
   ```

3. **Batch Operations**: Process toàn bộ DataFrame cùng lúc

4. **UI Reactive Updates** ⭐ NEW!
   ```python
   # NiceGUI auto-updates only changed components
   @ui.refreshable
   def chart_container():
       # Only re-renders when state changes
   ```

## Extensibility

### Thêm chức năng mới:

1. **Thêm query mới**: Extend `StudentRepository`
2. **Thêm analysis**: Extend `StudentAnalyticsService`
3. **Thêm validation**: Extend `DataValidator`
4. **Thêm format**: Extend `DataFormatter`
5. **Thêm UI tab** ⭐ NEW!:
   ```python
   with ui.tab_panel('new_feature'):
       # Add new visualization
       ui.plotly(create_new_chart())
   ```

---

## Summary: Why This Architecture?

✅ **Maintainable**: Clear separation of concerns  
✅ **Testable**: Each layer can be tested independently  
✅ **Extensible**: Easy to add new features  
✅ **Reusable**: Service layer works for both CLI and Web UI ⭐  
✅ **Professional**: Follows industry best practices  
✅ **Interactive**: Real-time parameter tuning with NiceGUI ⭐  

**Perfect for "Top 0.1%" demonstration!** 🎯

### Ví dụ:

```python
# Thêm query trong StudentRepository
def fetch_by_city(self, city: str) -> pd.DataFrame:
    query = f"SELECT * FROM {self.table_name} WHERE city = :city"
    return self.client.execute_query(query, {'city': city})

# Thêm analysis trong StudentAnalyticsService
def calculate_percentile_rank(self, column: str) -> pd.DataFrame:
    self.df[f'{column}_percentile'] = self.df[column].rank(pct=True)
    return self.df
```

## Maintenance Guidelines

1. **Logging**: Sử dụng logger thay vì print
2. **Type Hints**: Always use type annotations
3. **Docstrings**: Document tất cả public methods
4. **Constants**: Define trong `Settings`, không hard-code
5. **Validation**: Validate inputs ở entry points
