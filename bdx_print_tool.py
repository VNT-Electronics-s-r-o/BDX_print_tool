import platform
import sys
from datetime import datetime

from PyQt6.QtCore import (
    QObject,
    QRunnable,
    QSize,
    Qt,
    QThreadPool,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from zebra import Zebra  # pip install Zebra

from data_saver import DataSaver, DataViewer
from settings import DEVICE_MAP, ICONS_PATH, PRINTER, ROLE, SAVE_PATH
from styles import AppStyles


def apply_light_palette(app: QApplication) -> None:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)


class Signals(QObject):
    result = pyqtSignal(object)  # Changed to object to handle various return types
    progress = pyqtSignal(str, str)  # For progress updates (message, color)
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


class MainWindow(QMainWindow):
    log_signal = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BD/BDX - TISK ŠTÍTKU')
        self.setWindowIcon(QIcon(ICONS_PATH + 'print.png'))
        
        # Initialize current printer
        self.current_printer = PRINTER
        self.role = ROLE

        # Threading
        self.thread_pool = QThreadPool()

        # Current operation state variables for worker threads
        self.current_device_num = None
        self.current_device_data = None
        self.device_type = None
        self.device_name = None
        self.board_num = None
        self.mac = None
        self.ble_name = None
        self.ble_pin = None
        self.ble_mac = None

        main_container = QWidget()
        main_container.setStyleSheet(AppStyles.get_container_style())

        heading = QLabel('BD/BDX - TISK ŠTÍTKU')
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet(AppStyles.get_heading_style())

        # Status indicator
        self.status_indicator = QLabel('Připraveno k tisku')
        self.status_indicator.setStyleSheet('font-size: 14px; color: #27ae60; font-weight: bold;')

        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_frame.setStyleSheet(AppStyles.get_input_frame_style())

        info_layout = QVBoxLayout()
        info_label = QLabel('Info:')
        info_label.setStyleSheet(AppStyles.get_info_label_style())

        self.log = QTextEdit()
        
        self.log.setReadOnly(True)
        self.log.setFont(QFont('Segoe UI', 13))
        #self.log.setStyleSheet(AppStyles.get_text_edit_style())
        self.log.setFixedHeight(100)

        self.label_preview = QTextEdit()
        self.label_preview.setReadOnly(True)
        self.label_preview.setFont(QFont('Segoe UI', 16))
        self.label_preview.setMinimumHeight(300)
        self.label_preview.setStyleSheet(AppStyles.get_text_edit_style())

        info_layout.addWidget(info_label)
        info_layout.addWidget(self.log)
        info_layout.addWidget(self.label_preview)
        info_layout.addWidget(self.status_indicator)

        info_frame.setLayout(info_layout)

        # Input fields section
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        #input_frame.setMaximumWidth(800)  # Match the button width
        input_frame.setStyleSheet(AppStyles.get_input_frame_style())

        device_num_label = QLabel('Číslo výrobku: ')
        device_num_label.setStyleSheet(AppStyles.get_form_label_style())

        self.device_num_input = QLineEdit()
        self.device_num_input.setStyleSheet(AppStyles.get_line_edit_style())
        self.device_num_input.setReadOnly(True)
        self.device_num_input.setPlaceholderText('Výrobní číslo se zobrazí zde...')


        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.addRow(device_num_label, self.device_num_input)
        
        input_frame.setLayout(form_layout)

        # Action button section
        button_frame = QFrame()
        button_frame.setStyleSheet(AppStyles.get_input_frame_style())
        button_layout = QHBoxLayout()

        self.print_btn = QPushButton(' ZAHÁJIT TISK')
        self.print_btn.setFixedHeight(90)
        self.print_btn.setIcon(QIcon(ICONS_PATH + 'print.png'))
        self.print_btn.setIconSize(QSize(30, 30))
        self.print_btn.setStyleSheet(AppStyles.get_primary_button_style())

        button_layout.addWidget(self.print_btn)
        button_frame.setLayout(button_layout)

        # Printer status label
        self.printer_status = QLabel()
        self.printer_status.setStyleSheet('''
            QLabel {
                font-size: 14px; 
                color: #2c3e50; 
                padding: 8px;
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                font-weight: bold;
            }
        ''')
        self.printer_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- TOOLBAR ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet(AppStyles.get_toolbar_style())

        database_action = QAction('Databáze', self)
        database_action.setIcon(QIcon(ICONS_PATH + 'database.png'))
        database_action.setToolTip('Otevřít databázi pro prohlížení záznamů')


        printer_action = QAction('Vybrat tiskárnu', self)
        printer_action.setIcon(QIcon(ICONS_PATH + 'print.png'))
        printer_action.setToolTip("Vyberte si tiskárnu")

        close_action = QAction('Zavřít', self)
        close_action.setIcon(QIcon(ICONS_PATH + 'exit.png'))
        close_action.setToolTip('Zavřít aplikaci')

        spacer_1 = QWidget()
        spacer_1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        toolbar.addAction(database_action)
        toolbar.addAction(printer_action)
        toolbar.addWidget(spacer_1)
        toolbar.addAction(close_action)

        # Main content layout
        
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)

        content_layout.addWidget(heading)
        content_layout.addWidget(input_frame)
        content_layout.addWidget(button_frame)
        content_layout.addWidget(info_frame)

        content_layout.addStretch(1)

        left_right_layout = QHBoxLayout()
        left_right_layout.addStretch()
        left_right_layout.addLayout(content_layout)
        left_right_layout.addStretch()

        # Set up the main container
        main_container.setLayout(left_right_layout)
        self.setCentralWidget(main_container)
        self.addToolBar(toolbar)

        self.print_btn.clicked.connect(self.start_printing_process)
        database_action.triggered.connect(self.emit_open_db)
        printer_action.triggered.connect(self.select_printer)
        close_action.triggered.connect(self.emit_close_app)
        self.log_signal.connect(self.log_msg)

        self.update_printer_status()
        self.log_signal.emit(f'Aktuální tiskárna: {self.current_printer}', 'I')

        # Initialize status
        self.update_status('Připraveno k tisku', '#27ae60')

    def update_status(self, message, color='#27ae60'):
        """
        Update the status indicator with a message and color
        """
        self.status_indicator.setText(message)
        self.status_indicator.setStyleSheet(f'font-size: 14px; color: {color}; font-weight: bold;')

    def update_printer_status(self):
        """
        Update printer status display
        """
        self.printer_status.setText(f'Aktuální tiskárna: {self.current_printer}')

    def detect_device_type(self, device_num):
        """
        Detect device type (BD or BDX) based on device number prefix
        BD devices: 1610, 1620, 1630, 1650 (prefixes)
        BDX devices: 2611, 2621, 2631, 2651 (prefixes)
        """
        try:
            device_num = device_num.removeprefix('07')
            print(device_num)
            # Check if device number starts with any of the known prefixes
            for device_name, prefix in DEVICE_MAP.items():
                if device_num.startswith(prefix):
                    # Return BD or BDX based on device name
                    if device_name.startswith('BD') and not device_name.startswith('BDX'):
                        return 'BD'
                    elif device_name.startswith('BDX'):
                        return 'BDX'
            
            # Fallback: check by prefix pattern if DEVICE_MAP doesn't match
            if len(device_num) >= 4:
                device_code = device_num[:4]
                
                # Check if it's a BD device (16xx pattern)
                if device_code.startswith('16'):
                    return 'BD'
                # Check if it's a BDX device (26xx pattern)
                elif device_code.startswith('26'):
                    return 'BDX'
            
            return None
        except Exception as e:
            print(f'Error detecting device type: {e}')
            return None

    def format_device_number(self, device_num):
        """
        Format device number as prefix-rest
        Example: 2651000001 -> 2651-000001
        """
        try:
            # Find the matching prefix
            for prefix in DEVICE_MAP.values():
                if device_num.startswith(prefix):
                    rest = device_num[len(prefix):]
                    return f"{prefix}-{rest}"
            
            # Fallback: use first 4 digits as prefix
            if len(device_num) >= 4:
                prefix = device_num[:4]
                rest = device_num[4:]
                return f"{prefix}-{rest}"
            
            return device_num
        except Exception as e:
            print(f'Error formatting device number: {e}')
            return device_num

    def get_available_printers(self):
        """
        Get list of available printers on the system
        """
        try:
            z = Zebra()
            printers = z.getqueues()
            print(f'Available printers: {printers}')
            return printers
        except Exception as e:
            print(f'Error getting available printers: {e}')
            return []

    def select_printer(self):
        """
        Allow user to select a printer from available printers
        """
        try:
            available_printers = self.get_available_printers()
            
            if not available_printers:
                alert_dialog('Chyba', 'Žádné tiskárny nebyly nalezeny v systému!')
                return False
            
            # Create selection dialog
            printer_dialog = QDialog(self)
            printer_dialog.setWindowTitle('Vybrat tiskárnu')
            printer_dialog.setWindowIcon(QIcon(ICONS_PATH + 'print.png'))
            printer_dialog.resize(450, 350)
            printer_dialog.setStyleSheet('''
                QDialog {
                    background-color: #f8f9fa;
                }
            ''')
            
            layout = QVBoxLayout()
            
            label = QLabel('Vyberte tiskárnu:')
            label.setStyleSheet('font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;')
            layout.addWidget(label)
            
            # Create list widget for printers
            printer_list = QListWidget()
            printer_list.setStyleSheet('''
                QListWidget {
                    font-size: 14px;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    padding: 8px;
                    background-color: white;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #ecf0f1;
                }
                QListWidget::item:selected {
                    background-color: #135e75;
                    color: white;
                }
            ''')
            
            for printer in available_printers:
                item = QListWidgetItem(f'🖨️ {printer}')
                printer_list.addItem(item)
                # Select current printer if it exists in the list
                if printer == self.current_printer:
                    item.setSelected(True)
            
            layout.addWidget(printer_list)
            
            # Current printer info
            current_label = QLabel(f'Aktuální tiskárna: {self.current_printer}')
            current_label.setStyleSheet('font-size: 12px; color: #135e75; font-weight: bold; margin: 10px;')
            layout.addWidget(current_label)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            select_btn = QPushButton('Vybrat')
            select_btn.setStyleSheet('''
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #219a52;
                }
            ''')
            
            test_btn = QPushButton('Test tisku')
            test_btn.setStyleSheet('''
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            ''')
            
            cancel_btn = QPushButton('Zrušit')
            cancel_btn.setStyleSheet('''
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            ''')
            
            button_layout.addWidget(select_btn)
            button_layout.addWidget(test_btn)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            printer_dialog.setLayout(layout)
            
            # Connect signals
            def on_select():
                selected_items = printer_list.selectedItems()
                if selected_items:
                    selected_printer = selected_items[0].text().replace('🖨️ ', '')
                    self.current_printer = selected_printer
                    self.update_printer_status()
                    self.log_signal.emit(f'Tiskárna změněna na: {selected_printer}', 'O')
                    printer_dialog.accept()
                else:
                    alert_dialog('Chyba', 'Prosím vyberte tiskárnu!')
            
            def on_test():
                selected_items = printer_list.selectedItems()
                if selected_items:
                    test_printer = selected_items[0].text().replace('🖨️ ', '')
                    self.test_printer(test_printer)
                else:
                    alert_dialog('Chyba', 'Prosím vyberte tiskárnu pro test!')
            
            def on_cancel():
                printer_dialog.reject()
            
            select_btn.clicked.connect(on_select)
            test_btn.clicked.connect(on_test)
            cancel_btn.clicked.connect(on_cancel)
            
            # Double click to select
            printer_list.itemDoubleClicked.connect(on_select)
            
            printer_dialog.exec()
            
        except Exception as e:
            print(f'Error in select_printer: {e}')
            alert_dialog('Chyba', f'Chyba při výběru tiskárny: {e}')
            return False

    def test_printer(self, printer_name):
        """
        Test the selected printer with a simple test label
        """
        try:
            self.update_status('Testování tiskárny...', '#f39c12')
            
            # Use worker for test printing
            worker = Worker(self.worker_test_printer, printer_name)
            worker.signals.result.connect(self.on_test_print_completed)
            self.thread_pool.start(worker)
            
        except Exception as e:
            print(f'Error in test_printer: {e}')
            self.update_status('Chyba při testu', '#e74c3c')
            alert_dialog('Chyba', f'Chyba při testování tiskárny: {e}')

    def worker_test_printer(self, printer_name):
        """
        Worker function to test printer
        """
        try:
            z = Zebra()
            z.setqueue(printer_name)
            
            # Create simple test label
            test_zpl = "^XA"
            test_zpl += "^LH0,0"
            test_zpl += "^FO50,50^A0N,30,30^FH^FD TEST TISKU ^FS"
            test_zpl += f"^FO50,100^A0N,25,25^FH^FD Tiskarna: {printer_name}^FS"
            test_zpl += "^FO50,140^A0N,20,20^FH^FD Datum: {}^FS".format(datetime.now().strftime('%d.%m.%Y %H:%M'))
            test_zpl += "^XZ"
            
            z.output(test_zpl)
            return {'success': True, 'printer': printer_name}
            
        except Exception as e:
            print(f'Error in worker_test_printer: {e}')
            return {'success': False, 'error': str(e), 'printer': printer_name}

    def on_test_print_completed(self, result):
        """
        Handle result of test print operation
        """
        if result['success']:
            self.update_status('Test úspěšný', '#27ae60')
            self.log_signal.emit(f'Test tisku na {result["printer"]} byl úspěšný', 'O')
            alert_dialog('Úspěch', f'Test tisku na tiskárně {result["printer"]} byl úspěšný!')
        else:
            self.update_status('Test se nezdařil', '#e74c3c')
            self.log_signal.emit(f'Test tisku na {result["printer"]} se nezdařil: {result["error"]}', 'E')
            alert_dialog('Chyba', f'Test tisku na tiskárně {result["printer"]} se nezdařil:\n{result["error"]}')

    def worker_save_label_operations(self, device_data, original_sn):
        """
        Worker function to save label and update database
        """
        try:
            # Save to text file, because the pin is not generated in here, we can save only to txt
            txt_result = self.save_label_txt()
            if not txt_result:
                return {'success': False, 'error': 'Failed to save to text file'}

            return {'success': True, 'device_data': device_data}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def worker_print_label(self, label_data):
        """
        Worker function to print label
        """
        try:
            success_count = 0
            for i in range(3):  # Print 3 copies
                if self.send_to_printer(label_data):
                    success_count += 1
                else:
                    break
            
            return {'success': success_count == 3, 'printed_count': success_count}
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'printed_count': 0}

    def start_printing_process(self):
        """
        Start the printing process - now uses worker threads for database operations
        """
        try:
            self.update_status('Načítání čísla výrobku...', '#f39c12')
            
            device_num = input_dialog('Číslo výrobku', 'Načtěte číslo <b>výrobku</b>: ')
            if not device_num:
                self.log_signal.emit('Číslo nebylo zadáno', 'W')
                self.update_status('Číslo výrobku nebylo zadáno', '#e74c3c')
                return

            # Remove "07" prefix if present
            device_num = device_num.removeprefix('07')

            self.update_status('🔍 Detekce typu zařízení...', '#f39c12')
            
            # Detect device type
            self.device_type = self.detect_device_type(device_num)
            if not self.device_type:
                self.log_signal.emit('Neznámý typ zařízení! Zkontrolujte číslo výrobku.', 'E')
                self.update_status('Neznámý typ zařízení', '#e74c3c')
                alert_dialog('Chyba', 'Neznámý typ zařízení! Zkontrolujte číslo výrobku.')
                return

            self.log_signal.emit(f'Detekován typ zařízení: {self.device_type}', 'I')
            self.update_status(f'Detekován: {self.device_type}', '#27ae60')

            # Store current operation data
            self.current_device_num = device_num
            self.device_num_input.setText(device_num)

            # Start database check with worker
            self.check_device_with_worker()

        except Exception as e:
            print('Error while starting printing process: ', e)
            self.log_signal.emit(f'Vyskytla se chyba: {e}', 'E')
            self.update_status('Systémová chyba', '#e74c3c')
            return

    def check_device_with_worker(self):
        """
        Check device in database using worker thread
        """
        self.update_status('🔍 Hledání v databázi...', '#f39c12')
        worker = Worker(self.check_device_in_db, self.current_device_num)
        worker.signals.result.connect(self.on_device_check_completed)
        self.thread_pool.start(worker)

    def on_device_check_completed(self, device_data):
        """
        Handle result of device database check
        """
        if not device_data:
            self.log_signal.emit('Výrobek nebyl nalezen v databázi!', 'E')
            self.update_status('Výrobek nenalezen', '#e74c3c')
            alert_dialog('CHYBA', 'Výrobek nebyl nalezen v databázi! Ujistěte se, že je výrobek spárován.')
            return

        # Store device data
        self.current_device_data = device_data
        self.device_name = device_data.get("Device")
        self.board_num = device_data.get("BoardNumber")
        self.mac = device_data.get("BoardMAC")
        self.ble_name = device_data.get("BleName")
        self.ble_pin = device_data.get("BlePin")
        self.ble_mac = device_data.get("BleMAC")

        # Generate and show label preview
        label_data = self.generate_label(device_data)
        if not label_data:
            self.update_status('Chyba při generování štítku', '#e74c3c')
            return

        # Show preview
        self.show_label_preview(label_data)
        self.update_status('Připraveno k tisku', '#27ae60')

        # Ask for confirmation
        if confirmation_msg('Potvrzení', f'Chcete vytisknout štítek pro výrobek <b>{self.current_device_num}</b>?'):
            # Start save and print operations
            self.save_and_print_with_worker(label_data)
        else:
            self.update_status('Zrušeno uživatelem', '#f39c12')

    def show_label_preview(self, label_data):
        """
        Show label preview in the text area
        """
        try:
            heading, device_num, device_mac, ble_pin = label_data
            formatted_sn = self.format_device_number(device_num)

            preview_text = "\n".join((
                "NÁHLED ŠTÍTKU",
                "────────────────────────",
                heading,
                "",
                f"S/N: {formatted_sn}",
                f"MAC: {device_mac}",
                f"PIN: {ble_pin}",
                "────────────────────────",
                f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            ))

            self.label_preview.setPlainText(preview_text)

        except Exception as e:
            print(f'Error showing label preview: {e}')
            self.label_preview.setPlainText('Chyba při zobrazení náhledu štítku')

    def save_and_print_with_worker(self, label_data):
        """
        Save label data and print using worker thread
        """
        self.update_status('💾 Ukládání a tisk...', '#135e75')
        worker = Worker(self.worker_save_label_operations, self.current_device_data, self.current_device_num)
        worker.signals.result.connect(lambda result: self.on_save_completed(result, label_data))
        self.thread_pool.start(worker)

    def on_save_completed(self, save_result, label_data):
        """
        Handle result of save operation and proceed with printing
        """
        if not save_result['success']:
            self.log_signal.emit(f'Chyba při ukládání: {save_result["error"]}', 'E')
            self.update_status('Chyba při ukládání', '#e74c3c')
            alert_dialog('CHYBA', f'Nepodařilo se uložit data: {save_result["error"]}')
            return

        # Proceed with printing
        self.print_label_with_worker(label_data)

    def print_label_with_worker(self, label_data):
        """
        Print label using worker thread
        """
        self.update_status('🖨️ Tiskne se...', '#135e75')
        worker = Worker(self.worker_print_label, label_data)
        worker.signals.result.connect(self.on_print_completed)
        self.thread_pool.start(worker)

    def on_print_completed(self, print_result):
        """
        Handle result of print operation
        """
        if print_result['success']:
            self.log_signal.emit(f'Štítek byl úspěšně vytištěn ({print_result["printed_count"]}x)', 'O')
            self.update_status('Tisk dokončen!', '#27ae60')
        else:
            error_msg = print_result.get('error', 'Neznámá chyba')
            self.log_signal.emit(f'Nepodařilo se vytisknout štítek: {error_msg}', 'E')
            self.update_status('Chyba při tisku', '#e74c3c')
            alert_dialog('CHYBA', f'Nepodařilo se vytisknout štítek!\nChyba: {error_msg}\nUjistěte se, že je tiskárna zapnutá.')

        # Reset current operation data
        self.reset_current_operation()

    def reset_current_operation(self):
        """
        Reset current operation state variables
        """
        self.current_device_num = None
        self.current_device_data = None
        self.device_type = None
        self.device_name = None
        self.board_num = None
        self.mac = None
        self.ble_name = None
        self.ble_pin = None
        self.ble_mac = None

    # Old print_label method has been replaced with start_printing_process()
    # which uses worker threads for better performance and UI responsiveness

#071630000001
#5611-000002


    def generate_label(self, data):
        try:
            print('Data: ', data)
            heading = f'{data.get("BleName")}'  # Use BLE name as heading
            device_num = self.current_device_num
            device_mac = f'{data.get("BoardMAC")}'  # BoardMAC
            ble_pin = f'{data.get("BlePin")}'

            return (heading, device_num, device_mac, ble_pin)
        except Exception as e:
            print('Failed to generate label: ', e)
            return False

    def send_to_printer(self, label):
        try:
            print(f'Sending to printer: {self.current_printer}')

            heading = label[0]

            device_num = label[1]
            formatted_sn = self.format_device_number(device_num)

            mac = label[2]  # BoardMAC
            pin = label[3]

            z = Zebra()
            z.setqueue(self.current_printer)  # Use the selected printer

            zpl_label = "^XA"
            zpl_label += "^LH0,0"

            zpl_label += f"^FO15,30^A0N,36,36^FH^FD {heading}^FS"
            zpl_label += f"^FO15,120^A0N,36,36^FH^FD S/N: {formatted_sn}^FS"
            zpl_label += f"^FO15,170^A0N,36,36^FH^FD MAC: {mac}^FS"
            zpl_label += f"^FO15,220^A0N,36,36^FH^FD PIN: {pin}^FS"
            zpl_label += "^XZ"  # End of ZPL

            z.output(zpl_label)
            return True

        except Exception as e:
            print('Error while printing label: ', e)
            return False

    def save_label_txt(self):
        try:
            date = datetime.now().strftime('%Y.%m.%d %H:%M')

            with open(f'{SAVE_PATH}\\labels.txt', 'a', encoding='utf-8') as f:
                f.write(f'Datum a čas: {date}\n')
                f.write(f'DeviceNumber: {self.current_device_num}\n')
                f.write(f'{self.ble_name}\n')
                f.write(f'{self.ble_pin}\n')
                f.write('\n\n')
            return True

        except Exception as e:
            print('Error while saving label to TXT!', e)
            return False

    def check_device_in_db(self, device_num):
        try:
            '''
            SQLite database structure:
            Device, BoardNumber, BoardMAC, DeviceNumber, BleName, BlePin, BleMAC, Date
            '''
            
            # Use the already detected device type
            if not self.device_type:
                self.device_type = self.detect_device_type(device_num)
                if not self.device_type:
                    return False
                
            data_saver = DataSaver()
            device_data = data_saver.check_box_in_db(self.device_type, device_num)

            if device_data:
                return device_data
            else:
                print(f'Device {device_num} not found in SQLite database')
                return False
            
        except Exception as e:
            print('Error while checking device in SQLite db!', e)
            self.log_signal.emit(f'Vyskytla se chyba během hledání výrobku v databázi: {e}', 'E')
            return False

    def emit_open_db(self):
        # Create a selection dialog for database type
        db_selector = DatabaseSelector(self)
        if db_selector.exec() == QDialog.DialogCode.Accepted:
            selected_device = db_selector.get_selected_device()
            if selected_device:
                db_viewer = DataViewer(database = selected_device, role = self.role)
                db_viewer.exec()

    def log_msg(self, msg: str, msg_type: str = 'I') -> None:
        """
        Display a log message in the log widget with appropriate formatting.
        
        Args:
            msg: Message to display
            msg_type: Message type ('I'=info, 'O'=okay, 'W'=warning, 'E'=error, 'D'=debug)
        """
        try:
            self.log.clear()
            color_map = {
                'I': '#3498db',    # info - blue
                'O': '#27ae60',    # okay - green
                'W': '#f39c12',    # warning - orange
                'E': '#e74c3c',    # error - red
                'D': '#9b59b6',    # debug - purple
                '': '#2c3e50',     # default color
                'empty': 'none'
            }

            timestamp = self.get_timestamp()
            color = color_map.get(msg_type, '#2c3e50')

            match msg_type:
                case 'I':
                    self.log.append(f'<span style="color: {color}; font-weight: bold;">[INFO]</span> <span style="color: #7f8c8d; font-size: 13px;">{timestamp} | </span> <span style="color: #2c3e50;">{msg}</span>')
                case 'W':
                    self.log.append(f'<span style="color: {color}; font-weight: bold;">[WARN]</span> <span style="color: #7f8c8d; font-size: 13px;">{timestamp} | </span> <span style="color: {color};">{msg}</span>')
                case 'E':
                    self.log.append(f'<span style="color: {color}; font-weight: bold;">[ERR]</span> <span style="color: #7f8c8d; font-size: 13px;">{timestamp} | </span> <span style="color: {color}; font-weight: bold;">{msg}</span>')
                case 'D':
                    self.log.append(f'<span style="color: {color}; font-weight: bold;">[DEBUG]</span> <span style="color: #7f8c8d; font-size: 13px;">{timestamp} | </span> <span style="color: {color};">{msg}</span>')
                case 'O':
                    self.log.append(f'<span style="color: {color}; font-weight: bold;">[OK]</span> <span style="color: #7f8c8d; font-size: 13px;">{timestamp} | </span> <span style="color: {color}; font-weight: bold;">{msg}</span>')
                case '':
                    self.log.append(f'<span style="color: {color}; font-weight: bold;">[INFO]</span> <span style="color: #7f8c8d; font-size: 13px;">{timestamp} | </span> <span style="color: #2c3e50;">{msg}</span>')
                case 'empty':
                    self.log.append('')
                    
            # Auto-scroll to bottom
            self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

        except Exception as e:
            print(f'Error in log_msg: {e}')
    
    def get_timestamp(self):
        return datetime.now().strftime('%d.%m.%Y %H:%M')

    def emit_close_app(self):
        self.close()

    def closeEvent(self, event):
        if confirmation_msg('Ukončit', 'Opravdu chcete aplikaci ukončit?'):
            print('The app will be closed shortly')
            QApplication.quit()
        else:
            print('User does not want to close the app')
            event.ignore()


class DatabaseSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Vybrat databázi')
        self.setWindowIcon(QIcon(ICONS_PATH + 'database.png'))
        self.resize(350, 200)
        self.selected_device = None
        
        # Set up the layout
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Vyberte typ databáze:')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Device selection buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        self.bd_btn = QPushButton('🔧 BD Databáze')
        self.bd_btn.setStyleSheet('''
            QPushButton {
                border: 1px solid grey;
                border-radius: 8px;
                padding: 12px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        ''')
        
        self.bdx_btn = QPushButton('⚡ BDX Databáze')
        self.bdx_btn.setStyleSheet('''
            QPushButton {
                border: 1px solid grey;
                border-radius: 8px;
                padding: 12px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        ''')
        
        # Info label
        info_label = QLabel('BD: Základní verze | BDX: Rozšířená verze')
        info_label.setStyleSheet('font-size: 12px; color: #7f8c8d; margin-top: 10px;')
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        button_layout.addWidget(self.bd_btn)
        button_layout.addWidget(self.bdx_btn)
        layout.addLayout(button_layout)
        layout.addWidget(info_label)
        
        # Cancel button
        cancel_layout = QHBoxLayout()
        cancel_btn = QPushButton('Zrušit')
        cancel_btn.setStyleSheet('''
            QPushButton {
                border: 1px solid grey;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        ''')
        cancel_layout.addStretch()
        cancel_layout.addWidget(cancel_btn)
        cancel_layout.addStretch()
        
        layout.addLayout(cancel_layout)
        self.setLayout(layout)
        
        # Connect signals
        self.bd_btn.clicked.connect(lambda: self.select_device('BD'))
        self.bdx_btn.clicked.connect(lambda: self.select_device('BDX'))
        cancel_btn.clicked.connect(self.reject)
    
    def select_device(self, device_type):
        self.selected_device = device_type
        self.accept()
    
    def get_selected_device(self):
        return self.selected_device

# ------------------ OUTSIDE FUNCTIONS ------------------

def confirmation_msg(title: str, msg: str) -> bool:

    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setTextFormat(Qt.TextFormat.RichText)
    msg_box.setWindowIcon(QIcon(ICONS_PATH + 'question.png'))

    font = QFont()
    font.setPointSize(16)
    msg_box.setFont(font)

    yes_btn = msg_box.addButton('Ano', QMessageBox.ButtonRole.YesRole)
    msg_box.addButton('Ne', QMessageBox.ButtonRole.NoRole)

    msg_box.setStyleSheet(AppStyles.get_confirmation_msg_style())

    msg_box.exec()
    if msg_box.clickedButton() == yes_btn:
        print('User clicked Yes')
        return True
    else:
        print('User clicked No')
        return False


def input_dialog(label: str, text: str) -> str | None:
    """
    Display an input dialog for user text entry.
    
    Args:
        label: Dialog window title
        text: Prompt text to display
        
    Returns:
        str: User input text, None if empty, False if cancelled
    """
    dialog = QInputDialog()
    dialog.setWindowTitle(label)
    dialog.setLabelText(text)
    dialog.setWindowIcon(QIcon(ICONS_PATH + 'input.png'))

    font = QFont()
    font.setPointSize(16)

    dialog.setFont(font)

    # Force consistent dialog size
    dialog.resize(500, 300)
    # Set Czech button labels
    dialog.setOkButtonText('Potvrdit')
    dialog.setCancelButtonText('Zrušit')

    dialog.setStyleSheet(AppStyles.get_input_dialog_style())

    ok = dialog.exec()
    print(f'Dialog result: {ok}')
    
    if ok == 1:  # QDialog.Accepted
        if dialog.textValue() == '':
            print('Empty input')
            return None
        return dialog.textValue()
    else:
        return False


def alert_dialog(label: str, text: str) -> None:
    """
    Display an alert/warning dialog.
    
    Args:
        label: Dialog window title
        text: Message to display
    """
    msg = QMessageBox()
    msg.setWindowTitle(label)
    msg.setText(text)
    msg.setTextFormat(Qt.TextFormat.RichText)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowIcon(QIcon(ICONS_PATH + 'alert-active.png'))  

    font = QFont()
    font.setPointSize(16)
    msg.setFont(font)

    # Force consistent dialog size
    msg.resize(500, 300)

    msg.setStyleSheet(AppStyles.get_alert_dialog_style())

    msg.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    if platform.system() == "Windows":
        app.setStyle("windowsvista")
    else:
        app.setStyle("Fusion")

    apply_light_palette(app)

    window = MainWindow()
    window.setStyleSheet(
    '''
        font-family: Calibri;
        font-size: 18px;
    ''')

    window.showMaximized()

    sys.exit(app.exec())