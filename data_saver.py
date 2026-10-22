import datetime
import os
import time

import requests
from dotenv import load_dotenv
from PyQt6.QtCore import QObject, QRunnable, Qt, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from settings import ENV_PATH, ICONS_PATH

load_dotenv(ENV_PATH)

API_KEY = os.getenv("API_KEY", None)
API_URL = os.getenv("API_URL", "http://192.168.1.95:5569")

COLUMN_NAMES = "Device, BoardNumber, BoardMAC, DeviceNumber, BleName, BlePin, BleMAC, Date"
COLUMN_LIST = ['Device', 'BoardNumber', 'BoardMAC', 'DeviceNumber', 'BleName', 'BlePin', 'BleMAC', 'Date']
QUESTIONMARKS = "?, ?, ?, ?, ?, ?, ?, ?"
PRIMARY_KEY = "BoardNumber"
BOX_NAME = "DeviceNumber"
TABLE = "main_data"


class Signals(QObject):
    result = pyqtSignal(object)
    def __init__(self):
        super().__init__()


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Signals()

    @pyqtSlot()
    def run(self):
        fn_result = self.fn(*self.args, **self.kwargs)
        self.signals.result.emit(fn_result)

class DataViewer(QDialog):
    def __init__(self, database: str, api_url = API_URL, api_key = API_KEY, role ='admin'):
        super().__init__()
        self.setWindowTitle('Databáze')
        self.setWindowIcon(QIcon(ICONS_PATH + 'database.png'))
        self.resize(900, 600)
        
        self.role = role
        self.database = database
        self.api_url = api_url

        if not api_key:
            self.api_key = API_KEY
        else:
            self.api_key = api_key

        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

         # Set dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
        """)

        main_label = QLabel('DATABÁZE')
        main_label.setStyleSheet('''
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e1e8ed;
                margin-bottom: 10px;
            }
        ''')
        main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Button styling
        button_style = '''
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                color: #2c3e50;
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px 20px;
                margin: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #d5dbdb;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #adb5bd;
                border-color: #dee2e6;
            }
        '''

        self.update_btn = QPushButton('Načíst Data')
        self.update_btn.setStyleSheet(button_style)

        self.close_btn = QPushButton('Zavřít')
        self.close_btn.setStyleSheet(button_style)

        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
        self.table.setRowCount(0)
        self.table.setStyleSheet('''
            QTableWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                gridline-color: #e1e8ed;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e1e8ed;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: 1px solid #e1e8ed;
                font-weight: bold;
                color: #2c3e50;
            }
        ''')

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(main_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_layout.addWidget(self.update_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        self.close_btn.clicked.connect(self.close)
        self.update_btn.clicked.connect(self.load_data)

        time.sleep(1)
        self.load_data()

    def load_data(self):
        """Load data from database using API."""

        self.update_btn.setEnabled(False)
        self.update_btn.setText('Načítám...')

        worker = Worker(self._load_data_worker)
        worker.signals.result.connect(self._on_load_complete)
        QThreadPool.globalInstance().start(worker)

    def _load_data_worker(self):
        try:
            print('Loading data via API')
            
            url = f"{self.api_url}/query"
            payload = {
                "database": self.database,
                "query": f"SELECT * FROM {TABLE}"
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get("success") and result.get("data"):
                rows = result["data"]
                columns = result.get("columns", [])

                if rows:
                    return {'rows': rows, 'columns': columns}
                else:
                    print('No data found')
                    return None
            else:
                print(f"Error loading data: {result.get('error', 'Unknown error')}")
                return False
        
        except Exception as e:
            print('Error while loading data: ', e)
            return False

    def _on_load_complete(self, result: bool):
        """Handle completion of load operation"""
        self.update_btn.setEnabled(True)
        self.update_btn.setText('Aktualizovat')
        if result and isinstance(result, dict):
            rows = result['rows']
            columns = result['columns']
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            for i, row_dict in enumerate(rows):
                for j, col_name in enumerate(columns):
                    cell = row_dict.get(col_name, '')
                    item = QTableWidgetItem(str(cell))
                    self.table.setItem(i, j, item)



class DataSaver:
    def __init__(self, api_url = API_URL, api_key = API_KEY):
        print("Init of data saver")
        self.api_url = api_url
        if not api_key:
            self.api_key = API_KEY
        else:
            self.api_key = api_key
        
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _execute_query(self, database:str, query:str, params: str | None = None):
        """Execute a query using the API and return the response."""
        url = f"{self.api_url}/query"
        payload = {
            "database": database,
            "query": query,
            "params": params or []
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return {"success": False, "error": str(e)}

    def check_sn_in_db(self, database: str, sn: str):
        """
        Check if serial number exists in the database using API.
        
        Args:
            database: Database name (e.g., 'BD', 'BDX', ...)
            sn: Serial number to check
        
        Returns:
            Dictionary with row data if found, False otherwise
        """

        try:
            result = self._execute_query(
                database=database,
                query=f'SELECT * FROM {TABLE} WHERE {PRIMARY_KEY} = ?',
                params=[sn]
            )
            print("Result in check_sn_in_db: ", result)
            if result.get("success") and result.get("data"):
                sn_data = result["data"][0]
                return sn_data
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"Error Checking sn in db: {error_msg}")
                return False

        except Exception as e:
            print('Error while checking sn in db: ', e)
            return False
    
    def check_box_in_db(self, database: str, box: str):
        try:
            result = self._execute_query(
                database=database,
                query=f'SELECT * FROM {TABLE} WHERE {BOX_NAME} = ?',
                params=[box]
            )
            print("Result check_box_in_db", result)
            
            if result.get("success") and result.get("data"):
                box_data = result["data"][0]
                return box_data
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"Error Checking box in db: {error_msg}")
                return False

        except Exception as e:
            print('Error while checking box in db: ', e)
            return False

        
    def get_data_from_db(self, database: str, sn: str, box: str):
        try:
            result = self._execute_query(
                database=database,
                query=f'SELECT * FROM {TABLE} WHERE BoardNumber = ? AND DeviceNumber = ?',
                params=[sn, box]
            )
            
            if result.get("success") and result.get("data"):
                sn_data = result["data"][0]
                print('SN data found: ', sn_data)
                return sn_data
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"Error Checking sn in db: {error_msg}")
                return False

        except Exception as e:
            print('Error while checking sn in db: ', e)
            return False

    def check_device_num_in_db(self, database: str, device_num: str):
        """
        Check if a device number is assigned to any board in the database.
        
        Args:
            database: Database name (e.g., 'BD', 'BDX')
            device_num: Device number to check
        
        Returns:
            tuple: (True, board_number) if found, (False, None) if not found
            dict: {'error': message} if error occurred
        """
        try:
            result = self._execute_query(
                database=database,
                query=f'SELECT * FROM {TABLE} WHERE DeviceNumber = ?',
                params=[device_num]
            )
            print("Result: ", result)
            if result.get("success") and result.get("data"):
                device_data = result["data"][0]
                board_num = device_data.get('BoardNumber')
                print(f'Device {device_num} found assigned to board: {board_num}')
                return True, board_num
            else:
                # Check for error vs not found
                if result.get("error"):  # Check if error value is not None
                    error_msg = result.get("error", "Unknown error")
                    print(f"Error checking device in db: {error_msg}")
                    return {'error': f'Vyskytla se chyba během hledání výrobku v databázi: {error_msg}'}
                else:
                    print(f'Device {device_num} not found in database')
                    return False, None

        except Exception as e:
            print('Error while checking device in db!', e)
            return {'error': f'Vyskytla se chyba během hledání výrobku v databázi: {e}'}
    
    def save_data(self, database: str, board_num: str, device_data: dict, clear_conflicts: bool = True):
        """
        Save device data to database using API.
        Handles both INSERT and UPDATE operations based on whether the record exists.
        Optionally clears any conflicting assignments before saving.
        
        Args:
            database: Database name (e.g., 'BD', 'BDX')
            board_num: Board number (primary key)
            device_data: Dictionary containing device data with keys:
                - device_type: Device type
                - device_num: Device number
                - mac_vnt: Board MAC address
                - jmeno_ble: BLE name
                - ble_pin: BLE PIN
                - mac_ble: BLE MAC address
            clear_conflicts: If True, automatically clear conflicting assignments. Default True.
                            Set to False when just checking/comparing data.
        
        Returns:
            True if successful, dict with error key if failed
        """
        try:
            
            date = datetime.datetime.now().strftime('%Y.%m.%d %H:%M')
            
            # Only clear conflicts if explicitly requested (after user confirmation)
            if clear_conflicts:
                # First, clear any existing assignment of this device number to a different board
                clear_device_result = self._execute_query(
                    database=database,
                    query=f'SELECT {PRIMARY_KEY} FROM {TABLE} WHERE DeviceNumber = ? AND {PRIMARY_KEY} != ?',
                    params=[device_data['device_num'], board_num]
                )
                
                if clear_device_result.get("success") and clear_device_result.get("data"):
                    existing_board = clear_device_result["data"][0][PRIMARY_KEY]
                    print(f'Removing device {device_data["device_num"]} from {PRIMARY_KEY} {existing_board}')
                    self._execute_query(
                        database=database,
                        query=f'UPDATE {TABLE} SET DeviceNumber = NULL WHERE {PRIMARY_KEY} = ?',
                        params=[existing_board]
                    )
                
                # Clear any existing device assignment for this board
                clear_board_result = self._execute_query(
                    database=database,
                    query=f'SELECT DeviceNumber FROM {TABLE} WHERE {PRIMARY_KEY} = ? AND DeviceNumber IS NOT NULL',
                    params=[board_num]
                )
                
                if clear_board_result.get("success") and clear_board_result.get("data"):
                    existing_device = clear_board_result["data"][0]['DeviceNumber']
                    print(f'Removing existing device {existing_device} from board {board_num}')
                    self._execute_query(
                        database=database,
                        query=f'UPDATE {TABLE} SET DeviceNumber = NULL WHERE {PRIMARY_KEY} = ?',
                        params=[board_num]
                    )
            
            # Check if board record exists
            check_result = self._execute_query(
                database=database,
                query=f'SELECT * FROM {TABLE} WHERE {PRIMARY_KEY} = ?',
                params=[board_num]
            )
            
            if check_result.get("success") and check_result.get("data"):
                # Record exists - UPDATE
                query = f'''UPDATE {TABLE} SET 
                    Device = ?,
                    BoardMAC = ?,
                    DeviceNumber = ?,
                    BleName = ?,
                    BlePin = ?,
                    BleMAC = ?,
                    Date = ?
                    WHERE {PRIMARY_KEY} = ?'''
                
                params = [
                    device_data['device_type'],
                    device_data['mac_vnt'],
                    device_data['device_num'],
                    device_data['jmeno_ble'],
                    device_data['ble_pin'],
                    device_data['mac_ble'],
                    date,
                    board_num
                ]
            else:
                # Record doesn't exist - INSERT
                query = f'''INSERT INTO {TABLE} 
                    (Device, {PRIMARY_KEY}, BoardMAC, DeviceNumber, BleName, BlePin, BleMAC, Date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                
                params = [
                    device_data['device_type'],
                    board_num,
                    device_data['mac_vnt'],
                    device_data['device_num'],
                    device_data['jmeno_ble'],
                    device_data['ble_pin'],
                    device_data['mac_ble'],
                    date
                ]
            
            # Execute the save operation
            result = self._execute_query(
                database=database,
                query=query,
                params=params
            )
            
            if result.get("success"):
                print(f'Device data saved to {database} database')
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                print(f'Error saving device: {error_msg}')
                return {'error': f'Vyskytla se chyba během ukládání do databáze: {error_msg}'}
                
        except Exception as e:
            print('Error while saving device to database!', e)
            return {'error': f'Vyskytla se chyba během ukládání do databáze: {e}'}
