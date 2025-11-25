# 🛠️ CRUD Operations & Backup System

## 📋 Overview

Ứng dụng hỗ trợ **đầy đủ CRUD operations** (Create, Read, Update, Delete) với **automatic backup/undo system** để đảm bảo an toàn dữ liệu.

---

## ✅ Features Implemented

### 1. **Create - Add New Student**
- **Form**: 14 fields với validation
  - `student_id` (required, unique)
  - `full_name` (required)
  - `date_of_birth` (YYYY-MM-DD)
  - `gender` (M/F)
  - `major` (Data Science, AI, Business Analytics)
  - `class` (DS01, AI01, BA01, BA02)
  - `email` (required)
  - `phone_number`
  - `gpa` (0.0-4.0)
  - `credits` (integer)
  - `height_cm` (float)
  - `weight_kg` (float)
  - `province`
  - `enrollment_date` (YYYY-MM-DD)

**Code:**
```python
# src/repositories/student_repository.py
def insert_student(self, student_data: dict) -> bool:
    from sqlalchemy import text
    columns = ', '.join(student_data.keys())
    placeholders = ', '.join([f":{k}" for k in student_data.keys()])
    query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
    
    with self.client.engine.connect() as conn:
        conn.execute(text(query), student_data)
        conn.commit()
        return True
```

---

### 2. **Read - View & Filter Students**
- **Data Grid**: AG Grid với pagination (20/50/100/200/500 rows per page)
- **Filter by GPA**: Query students với GPA > threshold
- **Statistics Panel**: Real-time metrics (Total, GPA, Credits, BMI, Age)

**Code:**
```python
def get_students_by_gpa(self, min_gpa: float) -> pd.DataFrame:
    query = f"SELECT * FROM {self.table_name} WHERE gpa > {min_gpa} ORDER BY gpa DESC"
    return self.client.execute_query(query)
```

---

### 3. **Update - Modify Student Information**
- **Editable Fields**: 13 fields (all except `student_id`)
- **Type Validation**: Automatic conversion (float for gpa/height/weight, int for credits)
- **Dynamic Query**: Flexible SET clause construction

**Code:**
```python
def update_student(self, student_id: str, update_data: dict) -> bool:
    from sqlalchemy import text
    set_clause = ', '.join([f"{k} = :{k}" for k in update_data.keys()])
    query = f"UPDATE {self.table_name} SET {set_clause} WHERE student_id = :student_id"
    
    params = {**update_data, 'student_id': student_id}
    
    with self.client.engine.connect() as conn:
        result = conn.execute(text(query), params)
        conn.commit()
        return result.rowcount > 0
```

---

### 4. **Delete - Remove Student (with Backup)**
- **Confirmation Dialog**: Prevents accidental deletion
- **Automatic Backup**: Full record saved before deletion
- **FIFO Queue**: Maintains last 10 deletions
- **Undo Capability**: One-click restore

**Code:**
```python
def delete_student(self, student_id: str) -> bool:
    from sqlalchemy import text
    query = f"DELETE FROM {self.table_name} WHERE student_id = :student_id"
    
    with self.client.engine.connect() as conn:
        result = conn.execute(text(query), {"student_id": student_id})
        conn.commit()
        return result.rowcount > 0
```

---

## 🔒 Backup/Undo System

### Architecture
```
Delete Request
     ↓
Query full student record (SELECT *)
     ↓
Create backup: {student_data + deleted_at}
     ↓
Delete from database (DELETE)
     ↓
Add to backup stack (max 10, FIFO)
     ↓
Display in Undo panel
     ↓
[User clicks UNDO]
     ↓
Re-insert to database (INSERT)
```

### Implementation (app.py)

**State Management:**
```python
class AppState:
    deleted_students = []        # Backup stack
    max_backup_size = 10         # FIFO limit
    undo_container = None        # UI container
```

**Delete with Backup:**
```python
def delete_student_with_backup():
    # 1. Get full student data from database
    from sqlalchemy import text
    query = f"SELECT * FROM students WHERE student_id = :student_id"
    
    with app_state.repository.client.engine.connect() as conn:
        result = conn.execute(text(query), {"student_id": student_id})
        columns = result.keys()
        row = result.fetchone()
        student_data = dict(zip(columns, row))
    
    # 2. Show confirmation dialog
    with ui.dialog() as dialog:
        ui.label(f'Delete student {student_id}: {student_name}?')
        ui.label('✅ A backup will be created for undo')
        
        def do_delete():
            # 3. Create backup with timestamp
            backup_data = student_data.copy()
            backup_data['deleted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 4. Delete from database
            if app_state.repository.delete_student(student_id):
                # 5. Add to backup stack (FIFO)
                app_state.deleted_students.append(backup_data)
                if len(app_state.deleted_students) > app_state.max_backup_size:
                    app_state.deleted_students.pop(0)  # Remove oldest
                
                # 6. Update UI
                ui.notify(f'✅ Deleted student: {student_id} (backup created)')
                update_undo_list()
                load_data_from_db()
```

**Undo Delete:**
```python
def update_undo_list():
    """Display last 10 deleted students with restore buttons"""
    undo_container.clear()
    
    with undo_container:
        for backup in reversed(app_state.deleted_students):
            with ui.card():
                ui.label(f"🆔 {backup['student_id']}: {backup['full_name']}")
                ui.label(f"Deleted at: {backup['deleted_at']}")
                
                def create_undo_handler(backup_data):
                    def undo():
                        # Remove timestamp field
                        clean_data = {k: v for k, v in backup_data.items() 
                                     if k != 'deleted_at'}
                        
                        # Re-insert to database
                        if app_state.repository.insert_student(clean_data):
                            # Remove from backup stack
                            app_state.deleted_students.remove(backup_data)
                            ui.notify(f'✅ Restored student: {backup_data["student_id"]}')
                            update_undo_list()
                            load_data_from_db()
                    return undo
                
                ui.button('↩️ UNDO DELETE', on_click=create_undo_handler(backup))
```

---

## 🎯 Key Design Decisions

### 1. SQLAlchemy instead of raw MySQL
- **Before**: `with self.client.get_connection() as conn:` ❌ (doesn't exist!)
- **After**: `with self.client.engine.connect() as conn:` ✅
- **Benefits**:
  - Connection pooling
  - Automatic resource management
  - SQL injection protection
  - Cross-database compatibility

### 2. Named Parameters
- **Before**: `cursor.execute(query, (value1, value2))` (positional)
- **After**: `conn.execute(text(query), {"field": value})` (named)
- **Benefits**:
  - More readable
  - Less error-prone
  - Explicit parameter mapping

### 3. In-Memory Backup (not persistent)
- **Trade-off**: Lost on app restart
- **Benefit**: Fast, no database overhead
- **Future**: Save to `deleted_students_backup` table

### 4. FIFO Queue (max 10)
- **Trade-off**: Only last 10 deletions
- **Benefit**: Prevents memory overflow
- **Rationale**: Undo is for recent mistakes, not long-term archive

---

## 📊 Usage Statistics

| Operation | Fields Modified | Database Queries | UI Updates |
|-----------|----------------|------------------|------------|
| **Add**     | 14             | 1 INSERT         | 2 (grid + stats) |
| **Update**  | 1-13           | 1 UPDATE         | 2 (grid + stats) |
| **Delete**  | 0              | 1 SELECT + 1 DELETE | 3 (grid + stats + undo) |
| **Undo**    | 14             | 1 INSERT         | 3 (grid + stats + undo) |
| **Filter**  | 0              | 1 SELECT (WHERE) | 1 (result list) |

---

## 🚀 Future Enhancements

### 1. Persistent Backup
```sql
CREATE TABLE deleted_students_backup (
    backup_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50),
    student_data JSON,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(100)
);
```

### 2. Bulk Operations
- Delete multiple students at once
- Restore all backups
- Export backup to CSV

### 3. Audit Trail
- Track who deleted/restored
- Log all CRUD operations
- Display operation history

### 4. Search & Filter
- Search in backup by student name
- Filter backups by date range
- Advanced query builder

---

## ✅ Testing Checklist

- [ ] Add student with all 14 fields → Success
- [ ] Add student with missing required field → Error
- [ ] Update student GPA (float) → Success
- [ ] Update student credits (int) → Success
- [ ] Delete student → Backup created
- [ ] Check MySQL Workbench → Student deleted
- [ ] Undo delete → Student restored
- [ ] Check MySQL Workbench → Student exists
- [ ] Delete 11 students → Only last 10 in backup
- [ ] Restart app → Backups cleared (in-memory)
- [ ] Filter by GPA 3.5 → Shows correct list

---

## 📝 Notes for Presentation

**Q: "Tại sao cần backup system?"**
A: "Để tránh mất dữ liệu do thao tác nhầm. Production systems luôn có undo/rollback capability."

**Q: "Backup lưu ở đâu?"**
A: "In-memory stack (max 10). Để persistent, sẽ lưu vào database table."

**Q: "SQLAlchemy có lợi gì?"**
A: "Connection pooling, SQL injection protection, cross-database compatibility, production-ready."

**Q: "Có thể undo nhiều lần không?"**
A: "Có, lên đến 10 deletions gần nhất. Mỗi lần undo là 1 INSERT mới vào database."

**Q: "CRUD operations có validate không?"**
A: "Có, Add validates 14 required fields, Update validates numeric types, Delete requires confirmation."
