"""
🎓 STUDENT MANAGEMENT SYSTEM - NICEGUI WEB APPLICATION
=======================================================
Interactive data analytics platform with real-time parameter tuning.
Built with Clean Architecture principles - "Top 0.1% Mindset"

Author: DSEB Team
Date: November 2025
Architecture: UI Layer (NiceGUI) → Service Layer (Analytics) → Repository Layer (Data Access)
"""

# CRITICAL: Load environment variables FIRST before any imports
from dotenv import load_dotenv
load_dotenv()  # Load .env file

from nicegui import ui
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.database import DatabaseConfig
from src.repositories.mysql_client import MySQLClient
from src.repositories.student_repository import StudentRepository
from src.services.analytics_service import StudentAnalyticsService
from src.reports.report_generator import StudentReportGenerator

# ============================================================================
# GLOBAL STATE MANAGEMENT (Separation of Concerns)
# ============================================================================

class AppState:
    """Centralized state management for the application"""
    def __init__(self):
        self.db_config = None
        self.mysql_client = None
        self.repository = None
        self.analytics_service = None
        self.report_generator = None
        
        # Data state
        self.df_raw = pd.DataFrame()
        self.df_processed = pd.DataFrame()
        self.current_threshold = 1.5
        
        # Backup/Undo state
        self.deleted_students = []  # Stack for undo delete
        self.max_backup_size = 10   # Keep last 10 deletions
        
        # UI components (will be initialized in main page)
        self.grid = None
        self.chart_container = None
        self.stats_container = None
        self.outlier_container = None
        self.undo_container = None
        self.imputation_container = None
        
    def initialize_database(self):
        """Initialize database connections and repositories"""
        try:
            self.db_config = DatabaseConfig.from_env()
            self.mysql_client = MySQLClient(self.db_config)
            self.repository = StudentRepository(self.mysql_client)
            self.report_generator = StudentReportGenerator(self.repository)
            return True
        except Exception as e:
            ui.notify(f'❌ Database initialization failed: {str(e)}', type='negative')
            return False

# Global state instance
app_state = AppState()

# ============================================================================
# PAGINATION HELPER FUNCTIONS
# ============================================================================

def get_filtered_data(df: pd.DataFrame, search_query: str = '') -> pd.DataFrame:
    """Filter dataframe based on search query"""
    if not search_query or df.empty:
        return df
    
    # Search across all string columns
    mask = df.astype(str).apply(
        lambda row: row.str.contains(search_query, case=False, na=False).any(),
        axis=1
    )
    return df[mask]

def get_paginated_data(df: pd.DataFrame, page: int, rows_per_page: int) -> pd.DataFrame:
    """Get data for specific page"""
    if rows_per_page == -1:  # Show all
        return df
    
    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    return df.iloc[start_idx:end_idx]

def get_total_pages(total_rows: int, rows_per_page: int) -> int:
    """Calculate total number of pages"""
    if rows_per_page == -1:
        return 1
    return max(1, (total_rows + rows_per_page - 1) // rows_per_page)

# ============================================================================
# UI EVENT HANDLERS
# ============================================================================

def handle_search(query: str):
    """Handle search input changes"""
    app_state.search_query = query.strip()
    app_state.current_page = 1  # Reset to first page
    
    # Refresh the grid with current data
    current_df = app_state.df_processed if not app_state.df_processed.empty else app_state.df_raw
    if not current_df.empty:
        update_data_grid(current_df)

def handle_rows_per_page_change(new_value: int):
    """Handle rows per page selection change"""
    print(f"[DEBUG] Changing rows per page from {app_state.rows_per_page} to {new_value}")
    app_state.rows_per_page = new_value
    app_state.current_page = 1  # Reset to first page
    
    # Refresh the grid
    current_df = app_state.df_processed if not app_state.df_processed.empty else app_state.df_raw
    if not current_df.empty:
        print(f"[DEBUG] Updating grid with {len(current_df)} total rows, showing {new_value} per page")
        update_data_grid(current_df)
    else:
        print("[DEBUG] No data to display")
        ui.notify('⚠️ Please load data first!', type='warning')

def handle_page_change(direction: int):
    """Handle page navigation (direction: -1 for previous, +1 for next)"""
    current_df = app_state.df_processed if not app_state.df_processed.empty else app_state.df_raw
    if current_df.empty:
        return
    
    # Apply search filter to get total count
    filtered_df = get_filtered_data(current_df, app_state.search_query)
    total_pages = get_total_pages(len(filtered_df), app_state.rows_per_page)
    
    # Update page number
    new_page = app_state.current_page + direction
    if 1 <= new_page <= total_pages:
        app_state.current_page = new_page
        update_data_grid(current_df)

# ============================================================================
# CONTROLLER FUNCTIONS (Business Logic Orchestration)
# ============================================================================

def load_data_from_db():
    """Load raw data from MySQL database"""
    ui.notify('🔄 Loading data from MySQL database...', type='info')
    
    try:
        # Fetch all students
        app_state.df_raw = app_state.repository.fetch_all()
        
        if app_state.df_raw.empty:
            ui.notify('⚠️ No data found in database!', type='warning')
            return
        
        # Update grid with raw data
        update_data_grid(app_state.df_raw)
        
        # Update statistics
        update_statistics_panel(app_state.df_raw, is_processed=False)
        
        ui.notify(f'✅ Loaded {len(app_state.df_raw)} students successfully!', type='positive')
        
    except Exception as e:
        ui.notify(f'❌ Error loading data: {str(e)}', type='negative')
        import traceback
        print(traceback.format_exc())


def run_analytics_pipeline(iqr_threshold: float):
    """Run complete analytics pipeline with custom threshold"""
    
    if app_state.df_raw.empty:
        ui.notify('⚠️ Please load data first!', type='warning')
        return
    
    ui.notify(f'🔬 Running analytics pipeline (IQR threshold = {iqr_threshold})...', type='info')
    
    try:
        # Step 1: Initialize analytics service with raw data
        app_state.analytics_service = StudentAnalyticsService(app_state.df_raw.copy())
        
        # Step 2: Impute missing values
        ui.notify('📊 Step 1/5: Imputing missing values...', type='info')
        app_state.analytics_service.impute_missing()
        
        # Step 3: Calculate BMI
        ui.notify('⚖️ Step 2/5: Calculating BMI...', type='info')
        app_state.analytics_service.add_bmi()
        
        # Step 4: Calculate Age
        ui.notify('📅 Step 3/5: Calculating age...', type='info')
        app_state.analytics_service.add_age()
        
        # Step 5: Calculate Z-scores
        ui.notify('📈 Step 4/5: Calculating z-scores...', type='info')
        app_state.analytics_service.add_zscores()
        
        # Step 6: Detect outliers with custom threshold
        ui.notify(f'🎯 Step 5/5: Detecting outliers (threshold={iqr_threshold})...', type='info')
        
        # Get processed data
        app_state.df_processed = app_state.analytics_service.get_data()
        app_state.current_threshold = iqr_threshold
        
        # Detect outliers
        bmi_outliers = app_state.analytics_service.detect_outliers_iqr('bmi', multiplier=iqr_threshold)
        gpa_outliers = app_state.analytics_service.detect_outliers_iqr('gpa', multiplier=iqr_threshold)
        
        # Update UI
        update_data_grid(app_state.df_processed)
        update_statistics_panel(app_state.df_processed, is_processed=True)
        update_charts(app_state.df_processed)
        update_outlier_panel(bmi_outliers, gpa_outliers, iqr_threshold)
        update_imputation_panel(app_state.analytics_service.imputation_stats)
        
        ui.notify('✅ Analytics pipeline completed successfully!', type='positive')
        
    except Exception as e:
        ui.notify(f'❌ Pipeline error: {str(e)}', type='negative')
        import traceback
        print(traceback.format_exc())


def export_to_csv():
    """Export processed data to CSV file"""
    
    if app_state.df_processed.empty:
        ui.notify('⚠️ No processed data to export! Run analytics first.', type='warning')
        return
    
    try:
        # Use Downloads folder or current directory
        downloads_path = Path.home() / 'Downloads'
        if downloads_path.exists():
            export_dir = downloads_path
        else:
            export_dir = Path(__file__).parent / 'exports'
            export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'student_report_{timestamp}.csv'
        filepath = export_dir / filename
        
        # Try to export
        app_state.df_processed.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        ui.notify(f'✅ Exported {len(app_state.df_processed)} records to:\n{filepath}', type='positive', close_button=True, timeout=5000)
        print(f'[EXPORT] Success: {filepath}')
        
    except PermissionError as e:
        ui.notify(f'❌ Permission denied. Close the file if it\'s open in Excel.\nTried: {filepath}', type='negative', close_button=True)
        print(f'[EXPORT] Permission error: {e}')
    except Exception as e:
        ui.notify(f'❌ Export failed: {str(e)}', type='negative')
        print(f'[EXPORT] Error: {e}')


# ============================================================================
# UI UPDATE FUNCTIONS (View Layer)
# ============================================================================

def update_data_grid(df: pd.DataFrame):
    """Update AG Grid with all data (AG Grid handles pagination)"""
    if app_state.grid is None or df.empty:
        return
    
    try:
        # Convert DataFrame to AG Grid format
        columns = [{'field': col, 'headerName': col, 'sortable': True, 'filter': True} for col in df.columns]
        rows = df.to_dict('records')
        
        # Update grid
        app_state.grid.options['columnDefs'] = columns
        app_state.grid.options['rowData'] = rows
        app_state.grid.update()
    except Exception as e:
        print(f'[ERROR] Failed to update grid: {e}')
        # Grid might be stale, ignore the error


def update_statistics_panel(df: pd.DataFrame, is_processed: bool):
    """Update statistics panel with key metrics"""
    if app_state.stats_container is None:
        return
    
    try:
        app_state.stats_container.clear()
        
        with app_state.stats_container:
            with ui.row().classes('w-full gap-4'):
                # Card 1: Total Students
                with ui.card().classes('flex-1'):
                    ui.label('👥 Total Students').classes('text-lg font-bold text-gray-700')
                    ui.label(str(len(df))).classes('text-3xl font-bold text-blue-600')
                
                # Card 2: Average GPA
                with ui.card().classes('flex-1'):
                    ui.label('📚 Average GPA').classes('text-lg font-bold text-gray-700')
                    ui.label(f"{df['gpa'].mean():.2f}").classes('text-3xl font-bold text-green-600')
                
                # Card 3: Average Credits
                with ui.card().classes('flex-1'):
                    ui.label('🎯 Average Credits').classes('text-lg font-bold text-gray-700')
                    ui.label(f"{df['credits'].mean():.0f}").classes('text-3xl font-bold text-purple-600')
                
                # Card 4: Missing Values
                missing_count = df.isnull().sum().sum()
                with ui.card().classes('flex-1'):
                    ui.label('⚠️ Missing Values').classes('text-lg font-bold text-gray-700')
                    color = 'text-red-600' if missing_count > 0 else 'text-green-600'
                    ui.label(str(missing_count)).classes(f'text-3xl font-bold {color}')
            
            # Additional stats for processed data
            if is_processed and 'bmi' in df.columns:
                with ui.row().classes('w-full gap-4 mt-4'):
                    with ui.card().classes('flex-1'):
                        ui.label('⚖️ Average BMI').classes('text-lg font-bold text-gray-700')
                        ui.label(f"{df['bmi'].mean():.2f}").classes('text-3xl font-bold text-orange-600')
                    
                    with ui.card().classes('flex-1'):
                        ui.label('👤 Average Age').classes('text-lg font-bold text-gray-700')
                        ui.label(f"{df['age'].mean():.1f}").classes('text-3xl font-bold text-indigo-600')
                    
                    with ui.card().classes('flex-1'):
                        ui.label('🎓 Majors').classes('text-lg font-bold text-gray-700')
                        ui.label(str(df['major'].nunique())).classes('text-3xl font-bold text-pink-600')
    except Exception as e:
        print(f'[ERROR] Failed to update statistics panel: {e}')


def update_charts(df: pd.DataFrame):
    """Update interactive charts"""
    if app_state.chart_container is None:
        return
    
    app_state.chart_container.clear()
    
    with app_state.chart_container:
        with ui.row().classes('w-full gap-4'):
            # Chart 1: GPA Distribution by Major
            with ui.card().classes('flex-1'):
                fig = px.box(
                    df, 
                    x='major', 
                    y='gpa',
                    title='📊 GPA Distribution by Major',
                    color='major',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig.update_layout(showlegend=False, height=400)
                ui.plotly(fig).classes('w-full')
            
            # Chart 2: BMI vs Weight Scatter
            with ui.card().classes('flex-1'):
                fig = px.scatter(
                    df,
                    x='weight_kg',
                    y='bmi',
                    color='major',
                    title='⚖️ BMI vs Weight by Major',
                    hover_data=['full_name', 'height_cm'],
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(height=400)
                ui.plotly(fig).classes('w-full')
        
        # Chart 3: Summary by Major (Full width)
        with ui.card().classes('w-full mt-4'):
            summary = df.groupby('major').agg({
                'student_id': 'count',
                'gpa': 'mean',
                'credits': 'mean',
                'bmi': 'mean'
            }).round(2)
            summary.columns = ['Count', 'Avg GPA', 'Avg Credits', 'Avg BMI']
            summary = summary.reset_index()
            
            fig = px.bar(
                summary,
                x='major',
                y=['Avg GPA', 'Avg Credits', 'Avg BMI'],
                title='📈 Comparison Across Majors',
                barmode='group',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_layout(height=400, xaxis_title='Major', yaxis_title='Average Value')
            ui.plotly(fig).classes('w-full')


def update_outlier_panel(bmi_outliers: pd.DataFrame, gpa_outliers: pd.DataFrame, threshold: float):
    """Update outlier detection panel"""
    if app_state.outlier_container is None:
        return
    
    app_state.outlier_container.clear()
    
    with app_state.outlier_container:
        ui.label(f'🎯 Outlier Detection Results (IQR Multiplier = {threshold})').classes('text-2xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-4'):
            # BMI Outliers
            with ui.card().classes('flex-1'):
                ui.label('⚖️ BMI Outliers').classes('text-xl font-bold text-orange-600')
                ui.label(f'Found: {len(bmi_outliers)} students').classes('text-lg mt-2')
                
                if not bmi_outliers.empty:
                    with ui.scroll_area().classes('h-64 mt-4'):
                        for idx, row in bmi_outliers.iterrows():
                            with ui.card().classes('mb-2 bg-orange-50'):
                                ui.label(f"🆔 {row['student_id']}: {row['full_name']}").classes('font-bold')
                                ui.label(f"BMI: {row['bmi']:.2f} | Major: {row['major']}").classes('text-sm text-gray-600')
                else:
                    ui.label('✅ No BMI outliers detected').classes('text-green-600 mt-4')
            
            # GPA Outliers
            with ui.card().classes('flex-1'):
                ui.label('📚 GPA Outliers').classes('text-xl font-bold text-blue-600')
                ui.label(f'Found: {len(gpa_outliers)} students').classes('text-lg mt-2')
                
                if not gpa_outliers.empty:
                    with ui.scroll_area().classes('h-64 mt-4'):
                        for idx, row in gpa_outliers.iterrows():
                            with ui.card().classes('mb-2 bg-blue-50'):
                                ui.label(f"🆔 {row['student_id']}: {row['full_name']}").classes('font-bold')
                                ui.label(f"GPA: {row['gpa']:.2f} | Major: {row['major']}").classes('text-sm text-gray-600')
                else:
                    ui.label('✅ No GPA outliers detected').classes('text-green-600 mt-4')


def update_imputation_panel(stats: dict):
    """Update imputation statistics panel"""
    if app_state.imputation_container is None:
        return
    
    app_state.imputation_container.clear()
    
    with app_state.imputation_container:
        ui.label('🧩 Missing Value Imputation Report').classes('text-2xl font-bold mb-4')
        
        with ui.card().classes('w-full bg-indigo-50 p-4'):
            ui.label('Imputation Strategy Used:').classes('font-bold text-indigo-800 mb-2')
            ui.markdown("""
            - **Height & Weight**: Imputed using **Median by Gender**
            - **GPA & Credits**: Imputed using **Median by Major**
            """).classes('text-sm text-gray-700 mb-4')
            
            if not stats:
                ui.label('✅ No missing values found in original data.').classes('text-green-600 font-bold')
            else:
                ui.label('Values Imputed:').classes('font-bold mb-2')
                with ui.row().classes('w-full gap-4'):
                    for col, count in stats.items():
                        with ui.card().classes('flex-1 items-center'):
                            ui.label(col.replace('_', ' ').title()).classes('text-gray-600 text-sm')
                            color = 'text-orange-600' if count > 0 else 'text-green-600'
                            ui.label(f'{count}').classes(f'text-2xl font-bold {color}')
                            ui.label('values filled').classes('text-xs text-gray-400')


# ============================================================================
# MAIN UI PAGE (Presentation Layer)
# ============================================================================

@ui.page('/')
def main_page():
    """Main application page with interactive controls"""
    
    # Initialize database on first load
    if app_state.db_config is None:
        if not app_state.initialize_database():
            ui.label('❌ Failed to initialize database. Check .env configuration.').classes('text-red-600 text-xl p-8')
            return
    
    # ========== HEADER ==========
    with ui.header().classes('bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg'):
        with ui.row().classes('w-full items-center justify-between px-4'):
            ui.label('🎓 STUDENT MANAGEMENT SYSTEM').classes('text-2xl font-bold')
            ui.label('Powered by MHAN').classes('text-sm opacity-80')
    
    # ========== SIDEBAR (CONTROL PANEL) ==========
    with ui.left_drawer(value=True, fixed=True).classes('bg-gray-50 p-4').style('width: 320px'):
        ui.label('🎛️ Control Panel').classes('text-2xl font-bold text-gray-800 mb-6')
        
        # Section 1: Data Loading
        with ui.card().classes('mb-4'):
            ui.label('1️⃣ Data Loading').classes('text-lg font-bold mb-3')
            ui.button(
                '📥 Load Data from MySQL',
                on_click=load_data_from_db,
                icon='database'
            ).classes('w-full').props('color=blue')
        
        ui.separator().classes('my-4')
        
        # Section 2: Pipeline Configuration
        with ui.card().classes('mb-4'):
            ui.label('2️⃣ Analytics Pipeline').classes('text-lg font-bold mb-3')
            
            ui.label('IQR Threshold (Outlier Sensitivity)').classes('text-sm text-gray-600 mb-2')
            ui.label('Lower = More Strict, Higher = More Relaxed').classes('text-xs text-gray-500 mb-2')
            
            # Interactive Slider (Key Feature for Top 0.1%!)
            iqr_slider = ui.slider(
                min=1.0,
                max=3.0,
                value=1.5,
                step=0.1
            ).props('label-always color=green').classes('mb-4')
            
            # Display current value
            slider_label = ui.label(f'Current: {iqr_slider.value}').classes('text-center font-bold text-green-600')
            iqr_slider.on('update:model-value', lambda e: slider_label.set_text(f'Current: {e.args:.1f}'))
            
            ui.button(
                '🔬 Run Analytics Pipeline',
                on_click=lambda: run_analytics_pipeline(iqr_slider.value),
                icon='analytics'
            ).classes('w-full mt-4').props('color=green')
        
        ui.separator().classes('my-4')
        
        # Section 3: Export
        with ui.card().classes('mb-4'):
            ui.label('3️⃣ Export Results').classes('text-lg font-bold mb-3')
            ui.button(
                '💾 Export to CSV',
                on_click=export_to_csv,
                icon='download'
            ).classes('w-full').props('color=orange')
        
        # Info Section
        ui.separator().classes('my-4')
        with ui.card().classes('bg-blue-50'):
            ui.label('💡 Quick Tips').classes('font-bold mb-2')
            ui.markdown("""
- **Step 1**: Load data from database
- **Step 2**: Adjust IQR threshold
- **Step 3**: Run analytics
- **Step 4**: Review results & export
            """).classes('text-xs')
    
    # ========== MAIN CONTENT AREA ==========
    with ui.column().classes('w-full p-6'):
        
        # Statistics Panel (KPIs)
        app_state.stats_container = ui.row().classes('w-full gap-4 mb-6')
        
        # Tabs for different views
        with ui.tabs().classes('w-full') as tabs:
            tab_data = ui.tab('📊 Data View', icon='table_chart')
            tab_charts = ui.tab('📈 Analytics Charts', icon='bar_chart')
            tab_outliers = ui.tab('🎯 Outlier Detection', icon='warning')
            tab_crud = ui.tab('📝 Data Management', icon='edit')
        
        with ui.tab_panels(tabs, value=tab_data).classes('w-full'):
            
            # TAB 1: Data Table
            with ui.tab_panel(tab_data):
                with ui.card().classes('w-full'):
                    # Header
                    with ui.row().classes('w-full items-center justify-between mb-4'):
                        ui.label('📋 Student Data Table').classes('text-2xl font-bold')
                        
                        # Page size selector
                        with ui.row().classes('items-center gap-2'):
                            ui.label('Rows per page:').classes('text-sm')
                            page_size_selector = ui.select(
                                options={20: '20', 50: '50', 100: '100', 200: '200', 500: 'All'},
                                value=100
                            ).props('dense outlined').classes('w-28')
                            
                            def update_page_size():
                                if app_state.grid:
                                    app_state.grid.options['paginationPageSize'] = page_size_selector.value
                                    app_state.grid.update()
                            
                            page_size_selector.on_value_change(update_page_size)
                    
                    # Data grid with built-in pagination
                    app_state.grid = ui.aggrid({
                        'columnDefs': [],
                        'rowData': [],
                        'defaultColDef': {
                            'resizable': True,
                            'sortable': True,
                            'filter': True
                        },
                        'pagination': True,
                        'paginationPageSize': 100,
                        'paginationPageSizeSelector': [20, 50, 100, 200, 500]
                    }).classes('h-[600px] w-full')
            
            # TAB 2: Charts
            with ui.tab_panel(tab_charts):
                ui.label('📊 Visual Analytics').classes('text-2xl font-bold mb-4')
                app_state.imputation_container = ui.column().classes('w-full mb-6')
                app_state.chart_container = ui.column().classes('w-full')
            
            # TAB 3: Outliers
            with ui.tab_panel(tab_outliers):
                app_state.outlier_container = ui.column().classes('w-full')
                with app_state.outlier_container:
                    ui.label('⚠️ Run analytics pipeline to detect outliers').classes('text-gray-500 text-center mt-8')
            
            # TAB 4: Data Management (CRUD)
            with ui.tab_panel(tab_crud):
                with ui.card().classes('w-full'):
                    ui.label('📝 Data Management - CRUD Operations').classes('text-2xl font-bold mb-4')
                    
                    with ui.row().classes('w-full gap-4'):
                        # LEFT COLUMN: Add/Update/Delete
                        with ui.column().classes('flex-1'):
                            # ADD STUDENT
                            with ui.expansion('➕ Add New Student', icon='person_add').classes('w-full mb-4'):
                                with ui.card().classes('bg-green-50 p-4'):
                                    ui.label('Enter student information (* = required):').classes('font-bold mb-3')
                                    
                                    with ui.row().classes('w-full gap-2'):
                                        add_id = ui.input('Student ID *').props('outlined dense').classes('flex-1')
                                        add_name = ui.input('Full Name *').props('outlined dense').classes('flex-1')
                                    
                                    with ui.row().classes('w-full gap-2 mt-2'):
                                        add_dob = ui.input('Date of Birth (YYYY-MM-DD)').props('outlined dense type=date').classes('flex-1')
                                        add_gender = ui.select({'M': 'Male', 'F': 'Female'}, label='Gender').props('outlined dense').classes('flex-1')
                                    
                                    with ui.row().classes('w-full gap-2 mt-2'):
                                        add_major = ui.input('Major').props('outlined dense').classes('flex-1')
                                        add_class = ui.input('Class ID').props('outlined dense').classes('flex-1')
                                    
                                    with ui.row().classes('w-full gap-2 mt-2'):
                                        add_email = ui.input('Email').props('outlined dense type=email').classes('flex-1')
                                        add_phone = ui.input('Phone').props('outlined dense').classes('flex-1')
                                    
                                    with ui.row().classes('w-full gap-2 mt-2'):
                                        add_gpa = ui.number('GPA', min=0, max=4, step=0.01, value=0).props('outlined dense').classes('flex-1')
                                        add_credits = ui.number('Credits', min=0, step=1, value=0).props('outlined dense').classes('flex-1')
                                    
                                    with ui.row().classes('w-full gap-2 mt-2'):
                                        add_height = ui.number('Height (cm)', min=0, step=0.1).props('outlined dense').classes('flex-1')
                                        add_weight = ui.number('Weight (kg)', min=0, step=0.1).props('outlined dense').classes('flex-1')
                                    
                                    with ui.row().classes('w-full gap-2 mt-2'):
                                        add_province = ui.input('Province').props('outlined dense').classes('flex-1')
                                        add_enrollment = ui.input('Enrollment Date (YYYY-MM-DD)').props('outlined dense type=date').classes('flex-1')
                                    
                                    def add_student():
                                        if not add_id.value or not add_name.value:
                                            ui.notify('❌ Student ID and Name are required!', type='negative')
                                            return
                                        
                                        student_data = {
                                            'student_id': add_id.value,
                                            'full_name': add_name.value,
                                            'date_of_birth': add_dob.value if add_dob.value else None,
                                            'gender': add_gender.value if add_gender.value else None,
                                            'major': add_major.value if add_major.value else None,
                                            'class': add_class.value if add_class.value else None,
                                            'email': add_email.value if add_email.value else None,
                                            'phone_number': add_phone.value if add_phone.value else None,
                                            'gpa': add_gpa.value if add_gpa.value else 0,
                                            'credits': int(add_credits.value) if add_credits.value else 0,
                                            'height_cm': add_height.value if add_height.value else None,
                                            'weight_kg': add_weight.value if add_weight.value else None,
                                            'province': add_province.value if add_province.value else None,
                                            'enrollment_date': add_enrollment.value if add_enrollment.value else None
                                        }
                                        
                                        if app_state.repository.insert_student(student_data):
                                            ui.notify(f'✅ Added student: {add_id.value}', type='positive')
                                            # Clear form
                                            for field in [add_id, add_name, add_dob, add_major, add_class, add_email, add_phone, add_province, add_enrollment]:
                                                field.value = ''
                                            add_gender.value = None
                                            add_gpa.value = 0
                                            add_credits.value = 0
                                            add_height.value = None
                                            add_weight.value = None
                                            load_data_from_db()
                                        else:
                                            ui.notify('❌ Failed to add student (may already exist)', type='negative')
                                    
                                    ui.button('➕ Add Student', on_click=add_student, icon='add').props('color=green').classes('w-full mt-3')
                            
                            # UPDATE STUDENT
                            with ui.expansion('✏️ Update Student', icon='edit').classes('w-full mb-4'):
                                with ui.card().classes('bg-blue-50 p-4'):
                                    ui.label('Update existing student:').classes('font-bold mb-3')
                                    
                                    upd_id = ui.input('Student ID to Update *').props('outlined dense').classes('w-full mb-2')
                                    upd_field = ui.select(
                                        options={
                                            'full_name': 'Full Name',
                                            'date_of_birth': 'Date of Birth',
                                            'gender': 'Gender',
                                            'major': 'Major',
                                            'class': 'Class ID',
                                            'email': 'Email',
                                            'phone_number': 'Phone',
                                            'gpa': 'GPA',
                                            'credits': 'Credits',
                                            'height_cm': 'Height (cm)',
                                            'weight_kg': 'Weight (kg)',
                                            'province': 'Province',
                                            'enrollment_date': 'Enrollment Date'
                                        },
                                        label='Field to Update'
                                    ).props('outlined dense').classes('w-full mb-2')
                                    upd_value = ui.input('New Value *').props('outlined dense').classes('w-full mb-2')
                                    ui.label('💡 Tip: For dates use YYYY-MM-DD, for gender use M or F').classes('text-xs text-gray-600 mb-2')
                                    
                                    def update_student():
                                        if not upd_id.value or not upd_field.value or not upd_value.value:
                                            ui.notify('❌ All fields are required!', type='negative')
                                            return
                                        
                                        value = upd_value.value
                                        # Convert value for numeric fields
                                        if upd_field.value in ['gpa', 'height_cm', 'weight_kg']:
                                            try:
                                                value = float(value)
                                            except ValueError:
                                                ui.notify('❌ Invalid numeric value!', type='negative')
                                                return
                                        elif upd_field.value == 'credits':
                                            try:
                                                value = int(value)
                                            except ValueError:
                                                ui.notify('❌ Invalid integer value!', type='negative')
                                                return
                                        
                                        update_data = {upd_field.value: value}
                                        
                                        if app_state.repository.update_student(upd_id.value, update_data):
                                            ui.notify(f'✅ Updated student {upd_id.value}: {upd_field.value} = {value}', type='positive')
                                            upd_id.value = ''
                                            upd_value.value = ''
                                            load_data_from_db()
                                        else:
                                            ui.notify('❌ Student not found or update failed', type='negative')
                                    
                                    ui.button('✏️ Update Student', on_click=update_student, icon='save').props('color=blue').classes('w-full')
                            
                            # DELETE STUDENT
                            with ui.expansion('🗑️ Delete Student', icon='delete').classes('w-full mb-4'):
                                with ui.card().classes('bg-red-50 p-4'):
                                    ui.label('⚠️ Deleted students will be backed up (can undo)').classes('text-orange-600 font-bold mb-2')
                                    
                                    del_id = ui.input('Student ID to Delete *').props('outlined dense').classes('w-full mb-2')
                                    
                                    def delete_student_with_backup():
                                        if not del_id.value:
                                            ui.notify('❌ Student ID is required!', type='negative')
                                            return
                                        
                                        student_id = del_id.value
                                        
                                        # Get student data directly from database (for backup)
                                        try:
                                            from sqlalchemy import text
                                            query = f"SELECT * FROM {app_state.repository.table_name} WHERE student_id = :student_id"
                                            
                                            with app_state.repository.client.engine.connect() as conn:
                                                result = conn.execute(text(query), {"student_id": student_id})
                                                columns = result.keys()
                                                row = result.fetchone()
                                                
                                                if not row:
                                                    ui.notify(f'❌ Student {student_id} not found!', type='negative')
                                                    return
                                                
                                                # Convert row to dictionary
                                                student_data = dict(zip(columns, row))
                                        except Exception as e:
                                            ui.notify(f'❌ Database error: {e}', type='negative')
                                            return
                                        
                                        with ui.dialog() as dialog, ui.card():
                                            student_name = student_data.get('full_name', 'Unknown')
                                            ui.label(f'Delete student {student_id}: {student_name}?').classes('text-lg font-bold mb-2')
                                            ui.label('✅ A backup will be created for undo').classes('text-sm text-green-600 mb-4')
                                            
                                            with ui.row().classes('w-full gap-2'):
                                                ui.button('Cancel', on_click=dialog.close).props('flat')
                                                
                                                def do_delete():
                                                    # Backup student data with timestamp
                                                    backup_data = student_data.copy()
                                                    backup_data['deleted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    
                                                    # Delete from database
                                                    if app_state.repository.delete_student(student_id):
                                                        # Add to backup stack
                                                        app_state.deleted_students.append(backup_data)
                                                        
                                                        # Keep only last N deletions
                                                        if len(app_state.deleted_students) > app_state.max_backup_size:
                                                            app_state.deleted_students.pop(0)
                                                        
                                                        ui.notify(f'✅ Deleted student: {student_id} (backup created)', type='positive')
                                                        del_id.value = ''
                                                        load_data_from_db()
                                                        update_undo_list()
                                                    else:
                                                        ui.notify('❌ Delete failed', type='negative')
                                                    dialog.close()
                                                
                                                ui.button('Delete & Backup', on_click=do_delete, color='red')
                                        
                                        dialog.open()
                                    
                                    ui.button('🗑️ Delete Student', on_click=delete_student_with_backup, icon='delete').props('color=red').classes('w-full')
                        
                        # RIGHT COLUMN: Filter by GPA & Undo Delete
                        with ui.column().classes('flex-1'):
                            # GPA Filter
                            with ui.card().classes('bg-purple-50 p-4 mb-4'):
                                ui.label('🔍 Filter Students by GPA').classes('text-xl font-bold mb-4')
                                
                                gpa_threshold = ui.number('Minimum GPA Threshold', value=3.0, min=0, max=4, step=0.1).props('outlined').classes('w-full mb-4')
                                
                                filter_result = ui.column().classes('w-full')
                                
                                def filter_by_gpa():
                                    filter_result.clear()
                                    
                                    with filter_result:
                                        try:
                                            df_filtered = app_state.repository.get_students_by_gpa(gpa_threshold.value)
                                            
                                            if df_filtered.empty:
                                                ui.label(f'❌ No students found with GPA > {gpa_threshold.value}').classes('text-gray-600 mt-4')
                                            else:
                                                ui.label(f'✅ Found {len(df_filtered)} students with GPA > {gpa_threshold.value}:').classes('font-bold text-green-600 mb-2')
                                                
                                                with ui.scroll_area().classes('h-64 w-full'):
                                                    for idx, row in df_filtered.iterrows():
                                                        with ui.card().classes('mb-2 bg-white'):
                                                            ui.label(f"🆔 {row['student_id']}: {row['full_name']}").classes('font-bold')
                                                            ui.label(f"GPA: {row['gpa']:.2f} | Major: {row.get('major', 'N/A')} | Credits: {row.get('credits', 0)}").classes('text-sm text-gray-600')
                                        except Exception as e:
                                            ui.label(f'❌ Error: {str(e)}').classes('text-red-600')
                                
                                ui.button('🔍 Filter by GPA', on_click=filter_by_gpa, icon='search').props('color=purple').classes('w-full')
                            
                            # Undo Delete Section
                            with ui.card().classes('bg-yellow-50 p-4'):
                                ui.label('↩️ Undo Delete (Backup Recovery)').classes('text-xl font-bold mb-4')
                                ui.label(f'Last {app_state.max_backup_size} deleted students can be restored').classes('text-sm text-gray-600 mb-4')
                                
                                app_state.undo_container = ui.column().classes('w-full')
                                
                                def update_undo_list():
                                    """Update the undo list display"""
                                    if app_state.undo_container is None:
                                        return
                                    
                                    app_state.undo_container.clear()
                                    
                                    with app_state.undo_container:
                                        if not app_state.deleted_students:
                                            ui.label('No deleted students in backup').classes('text-gray-500 text-center py-4')
                                        else:
                                            with ui.scroll_area().classes('h-64 w-full'):
                                                for backup in reversed(app_state.deleted_students):  # Show newest first
                                                    with ui.card().classes('mb-2 bg-white'):
                                                        ui.label(f"🆔 {backup['student_id']}: {backup['full_name']}").classes('font-bold')
                                                        ui.label(f"Deleted at: {backup['deleted_at']}").classes('text-xs text-gray-500')
                                                        
                                                        def create_undo_handler(backup_data):
                                                            def undo_delete():
                                                                # Remove backup metadata
                                                                restore_data = {k: v for k, v in backup_data.items() if k != 'deleted_at'}
                                                                
                                                                # Re-insert into database
                                                                if app_state.repository.insert_student(restore_data):
                                                                    ui.notify(f"✅ Restored student: {restore_data['student_id']}", type='positive')
                                                                    
                                                                    # Remove from backup list
                                                                    app_state.deleted_students.remove(backup_data)
                                                                    
                                                                    load_data_from_db()
                                                                    update_undo_list()
                                                                else:
                                                                    ui.notify(f"❌ Failed to restore (may already exist)", type='negative')
                                                            return undo_delete
                                                        
                                                        ui.button('↩️ Undo Delete', 
                                                                on_click=create_undo_handler(backup),
                                                                icon='undo'
                                                        ).props('size=sm color=orange').classes('mt-2')
                                
                                # Initial update
                                update_undo_list()
    
    # ========== FOOTER ==========
    with ui.footer().classes('bg-gray-800 text-white'):
        with ui.row().classes('w-full items-center justify-between px-4'):
            ui.label('© 2025 [DSEB] - Student Management System').classes('text-sm')
            ui.label(f'Connected to: {app_state.db_config.database}@{app_state.db_config.host}').classes('text-xs opacity-70')


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='🎓 Student Management System',
        favicon='🎓',
        reload=False,  # Important: Disable auto-reload to prevent DB connection issues
        port=8080,
        show=True
    )
