class AppStyles:
    """
    Centralized styling system.
    
    This class provides modular, reusable style components that ensure
    consistent visual appearance across the entire application.
    """
    
    # Color palette
    COLORS = {
        'secondary': '#95a5a6',

        'success_light': '#d5f4e6',
        'success_pressed': '#a9e5c4',

        'warning_hover':"#e49630",
        'warning_pressed': "#db8615",
        'warning_dark':"#db7c00",
        
        'warning_light': "#f5c373",

        'info': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'debug': '#9b59b6',

        'light_blue': '#bee5eb',
        'blue': '#73b9c4',
        'darker_blue': '#48909b',
        'highlight': '#34737c',
        'greyish_blue': "#638094",

        'light_red': '#ee9595',
        'mid_red': '#dd7272',
        'darker_red': '#cc5c5c',
        'dark_red': '#aa3d3d',

        'dark': '#4a4a49',
        'dark_secondary': '#34495e',

        'light': '#ecf0f1',
        'light_secondary': '#bdc3c7',

        'white': '#ffffff',
        'background': '#f8f9fa',
        'text_muted': '#7f8c8d',

        'border': '#d0d0d0',
        'border_light': '#e0e0e0',

        'input_bg': '#f8f9fa',
        'input_disabled': '#ecf0f1',
        'log_bg': '#f8f9fa',

        'yellow': '#ffeed0',
        'yellow_hoover': '#ffe0aa',
        'yellow_pressed': '#ffd48b',
        'darker_yellow': '#fdc564'

    }

    # Typography
    FONTS = {
        'main': "'Segoe UI', Arial, sans-serif",
        'monospace': "'Segoe UI', monospace"
    }
    
    # Common measurements
    SIZES = {
        'xs': '5px',
        'sm': '8px',
        'md': '10px',
        'lg': '15px',
        'xl': '20px',
        'xxl': '30px'
    }
    
    BORDER_RADIUS = {
        'sm': '6px',
        'md': '8px',
        'lg': '10px'
    }

    @classmethod # this way you don't need to use self
    def get_toolbar_style(cls) -> str:
        """Get unified toolbar styling."""
        return f"""
            QToolBar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['light_blue']}, stop:1 {cls.COLORS['light_blue']});
                border: none;
                border-bottom: 1px solid {cls.COLORS['blue']};
                padding: {cls.SIZES['xs']};
                spacing: {cls.SIZES['md']};
            }}
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['sm']} 12px;
                font-weight: bold;
                color: {cls.COLORS['dark']};
            }}
            QToolButton:hover {{
                background-color: {cls.COLORS['blue']};
                border: 1px solid {cls.COLORS['darker_blue']};
            }}
            QToolButton:pressed {{
                background-color: {cls.COLORS['darker_blue']};
                border: 1px solid {cls.COLORS['highlight']};
            }}
        """

    @classmethod
    def get_main_window_style(cls) -> str:
        """Get main window styling."""
        return f"""
            QMainWindow {{
                background-color: {cls.COLORS['light']};
            }}
            QStatusBar {{
                background-color: {cls.COLORS['light_secondary']};
                border-top: 1px solid {cls.COLORS['secondary']};
                font-size: 12px;
                padding: 3px;
            }}
        """

    @classmethod
    def get_container_style(cls) -> str:
        """Get main container styling."""
        return f"""
            QWidget {{
                background-color: {cls.COLORS['background']};
                border-radius: {cls.BORDER_RADIUS['sm']};
            }}
        """ 

    @classmethod
    def get_input_frame_style(cls) -> str:
        """Get input section frame styling."""
        return f"""
            QFrame {{
                background-color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['sm']};
            }}
        """

    @classmethod
    def get_button_frame_style(cls) -> str:
        """Get button section frame styling."""
        return f"""
            QFrame {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {cls.BORDER_RADIUS['sm']};
            }}
        """

    @classmethod
    def get_heading_style(cls) -> str:
        """Get main heading styling."""
        return f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {cls.COLORS['dark']};
                background-color: {cls.COLORS['log_bg']};
                border: 1px solid {cls.COLORS['light_secondary']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['sm']};
            }}
        """

    @classmethod
    def get_info_label_style(cls) -> str:
        """Get info label styling."""
        return f"""
            QLabel {{
                font-weight: bold;
                color: {cls.COLORS['dark_secondary']};
                font-size: 16px;
                border: 0px;
            }}
        """

    @classmethod
    def get_form_label_style(cls) -> str:
        """Get form label styling."""
        return f"""
            QLabel {{
                font-size: 16px;
                padding: 5px {cls.SIZES['xs']};
                border: 1px solid {cls.COLORS['light_secondary']};
                border-radius: 6px;
                color: #000000;
                min-height: 30px;
                min-width: 150px;
            }}
        """

    @classmethod
    def get_line_edit_style(cls) -> str:
        """Get line edit input styling."""
        return f"""
            QLineEdit {{
                font-size: 16px;
                padding: 5px {cls.SIZES['xs']};
                border: 1px solid {cls.COLORS['light_secondary']};
                border-radius: 6px;
                background-color: {cls.COLORS['input_bg']};
                color: {cls.COLORS['dark']};
                min-height: 30px;
                min-width: 250px;
            }}
            QLineEdit:read-only {{
                background-color: {cls.COLORS['input_disabled']};
                color: {cls.COLORS['text_muted']};
            }}
        """

    @classmethod
    def get_text_edit_style(cls) -> str:
        """Get text edit (log) styling."""
        return f"""
            QTextEdit {{
                background-color: {cls.COLORS['log_bg']};
                border: 1px solid {cls.COLORS['light_secondary']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['sm']};
                font-family: {cls.FONTS['monospace']};
            }}
        """

    @classmethod
    def get_primary_button_style(cls) -> str:
        """Get primary button styling."""
        return f"""
            QPushButton {{
                background-color: {cls.COLORS['light_blue']};
                border: 1px solid {cls.COLORS['blue']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                color: {cls.COLORS['dark']};
                font-weight: bold;
                font-size: 25px;
            }}

            QPushButton:hover {{
                background-color: {cls.COLORS['blue']};
                border: 1px solid {cls.COLORS['darker_blue']};
            }}

            QPushButton:pressed {{
                background-color: {cls.COLORS['darker_blue']};
                border: 1px solid {cls.COLORS['highlight']};
            }}
        """
    
    @classmethod
    def get_secondary_button_style(cls) -> str:
        """ Get secondary button styling"""
        return f"""
            QPushButton {{
                background-color: {cls.COLORS['warning_light']};
                border: 1px solid {cls.COLORS['warning']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                color: {cls.COLORS['dark']};
                font-weight: bold;
                font-size: 16px;
                margin: {cls.SIZES['xs']};
                padding: {cls.SIZES['xs']};
                min-height: 30px;
            }}

            QPushButton:hover {{ 
                background: {cls.COLORS['warning_hover']};
                border: 1px solid {cls.COLORS['warning_pressed']};
            }}

            QPushButton:pressed {{
                background-color: {cls.COLORS['warning_pressed']};
                border: 1px solid {cls.COLORS['warning_dark']};
            }}
        """
    @classmethod
    def get_close_button_style(cls) -> str:
        return f"""
            QPushButton {{
                background-color: {cls.COLORS['yellow']};
                border: 1px solid {cls.COLORS['yellow_hoover']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                color: {cls.COLORS['dark']};
                font-weight: bold;
                font-size: 16px;
                margin: {cls.SIZES['xs']};
                padding: {cls.SIZES['xs']};
                min-height: 30px;
            }}

            QPushButton:hover {{ 
                background: {cls.COLORS['yellow_hoover']};
                border: 1px solid {cls.COLORS['yellow_pressed']};
            }}

            QPushButton:pressed {{
                background-color: {cls.COLORS['yellow_pressed']};
                border: 1px solid {cls.COLORS['darker_yellow']};
            }}
        """


    @classmethod
    def get_confirmation_msg_style(cls) -> str:
        """Get confirmation message box styling."""
        return f"""
            QMessageBox {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['dark']};
            }}
            QMessageBox QLineEdit {{
                background-color: {cls.COLORS['white']};
                border: 2px solid {cls.COLORS['light_secondary']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['md']};
                font-size: 16px;
            }}
            QMessageBox QLineEdit:focus {{
                border-color: {cls.COLORS['blue']};
            }}
            QMessageBox QPushButton {{
                background-color: {cls.COLORS['white']};
                border: 2px solid {cls.COLORS['light_secondary']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['md']} {cls.SIZES['xl']};
                margin: {cls.SIZES['xs']};
                font-weight: 600;
                font-size: 16px;
                min-width: 80px;
            }}
            QMessageBox QPushButton[text="Ano"] {{
                border-color: {cls.COLORS['success']};
            }}
            QMessageBox QPushButton[text="Ano"]:hover {{
                background-color: {cls.COLORS['success_light']};
                border-color: {cls.COLORS['success']};
                color: {cls.COLORS['success']};
            }}
            QMessageBox QPushButton[text="Ano"]:pressed {{
                background-color: {cls.COLORS['success_pressed']};
            }}
            QMessageBox QPushButton[text="Ne"] {{
                border-color: {cls.COLORS['danger']};
            }}
            QMessageBox QPushButton[text="Ne"]:hover {{
                background-color: {cls.COLORS['light_red']};
                border-color: {cls.COLORS['danger']};
                color: {cls.COLORS['danger']};
            }}
            QMessageBox QPushButton[text="Ne"]:pressed {{
                background-color: {cls.COLORS['mid_red']};
            }}
        """

    @classmethod
    def get_input_dialog_style(cls) -> str:
        """Get input dialog styling."""
        return f"""
            QInputDialog {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['dark']};
            }}

            QInputDialog QLabel {{
                color: {cls.COLORS['dark']};
                margin-bottom: {cls.SIZES['lg']}
                font-weight: bold;
                font-size: 20px; 
            }}

            QInputDialog QLineEdit {{
                border: 2px solid {cls.COLORS['light_secondary']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['sm']};
                font-size: 16px;
            }}

            QInputDialog QLineEdit:focus {{
                border-color: {cls.COLORS['highlight']};
            }}

            QInputDialog QComboBox {{
                border: 2px solid {cls.COLORS['light_secondary']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['sm']};
                font-size: 16px;
                min-height: 20px;
            }}

            QInputDialog QComboBox::focus {{
                border-color: {cls.COLORS['highlight']};
            }}

            QInputDialog QComboBox::down-arrow {{
                width: 13px;
                height: 13px;
            }}

            QInputDialog QPushButton {{
                background-color: {cls.COLORS['white']};
                border: 2px solid {cls.COLORS['light_secondary']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['md']} {cls.SIZES['xl']};
                margin: {cls.SIZES['xs']};
                font-weight: 600;
                font-size: 16px;
                min-width: 80px;
            }}

            QInputDialog QPushButton[text="Potvrdit"] {{
                border-color: {cls.COLORS['success']};
            }}
            QInputDialog QPushButton[text="Potvrdit"]:hover {{
                background-color: {cls.COLORS['success_light']};
                border-color: {cls.COLORS['success']};
                color: {cls.COLORS['success']};
            }}
            QInputDialog QPushButton[text="Potvrdit"]:pressed {{
                background-color: {cls.COLORS['success_pressed']};
            }}
            QInputDialog QPushButton[text="Zrušit"] {{
                border-color: {cls.COLORS['danger']};
            }}
            QInputDialog QPushButton[text="Zrušit"]:hover {{
                background-color: {cls.COLORS['light_red']};
                border-color: {cls.COLORS['danger']};
                color: {cls.COLORS['danger']};
            }}
            QInputDialog QPushButton[text="Zrušit"]:pressed {{
                background-color: {cls.COLORS['mid_red']};
            }}
        """
    
    @classmethod
    def get_ok_button_style(cls) -> str:
        return f"""
            QPushButton {{
                color: {cls.COLORS['dark']};
                background-color: {cls.COLORS['light_blue']};
                border: 1px solid {cls.COLORS['blue']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['md']} {cls.SIZES['xl']};
                margin: {cls.SIZES['xs']};
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS['blue']};
                border: 1px solid {cls.COLORS['darker_blue']};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS['darker_blue']};
                border: 1px solid {cls.COLORS['highlight']};
            }}
        """
    
    @classmethod
    def get_cancel_button_style(cls) -> str:
        return f"""
            QPushButton {{
                color: {cls.COLORS['dark']};
                background-color: {cls.COLORS['light_red']};
                border: 1px solid {cls.COLORS['mid_red']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['md']} {cls.SIZES['xl']};
                margin: {cls.SIZES['xs']};
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS['mid_red']};
                border: 1px solid {cls.COLORS['darker_red']};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS['darker_red']};
                border: 1px solid {cls.COLORS['dark_red']};
            }}
        """

    @classmethod
    def get_alert_dialog_style(cls) -> str:
        """Get alert dialog styling."""
        return f"""
            QMessageBox {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['dark']};
            }}
            QMessageBox QLabel {{
                color: {cls.COLORS['dark']};
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {cls.COLORS['light_red']};
                border: 1px solid {cls.COLORS['mid_red']};
                border-radius: {cls.BORDER_RADIUS['sm']};
                padding: {cls.SIZES['md']} {cls.SIZES['xl']};
                margin: {cls.SIZES['xs']};
                font-weight: bold;
                font-size: 16px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {cls.COLORS['mid_red']};
                border: 1px solid {cls.COLORS['darker_red']};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {cls.COLORS['darker_red']};
                border: 1px solid {cls.COLORS['dark_red']};
            }}
        """
    
    line_edit_style = '''
            QLineEdit {
                font-size: 18px;
                color: black;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                background-color: #ecf0f1;
            }
        '''