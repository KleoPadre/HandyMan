import os
import sys

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLineEdit,
    QLabel,
    QProgressBar,
    QTextEdit,
    QFileDialog,
    QStatusBar,
    QFrame,
    QApplication,
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
from utils.file_operations import move_short_videos, move_screenshots


class WorkerThread(QThread):
    update_progress = pyqtSignal(int, int, int, str)
    update_log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, function, source, destination):
        super().__init__()
        self.function = function
        self.source = source
        self.destination = destination
        self.is_running = True

    def run(self):
        self.function(
            self.source,
            self.destination,
            self.update_log.emit,
            self.update_progress.emit,
            self.check_if_running,
        )
        self.finished.emit()

    def stop(self):
        self.is_running = False

    def check_if_running(self):
        return self.is_running


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HandyMan")  # Changed title
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Button style definition
        button_style = """
            QPushButton {
                background-color: #37474F;
                color: white;
                border: 1px solid #455A64;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
            QPushButton:pressed {
                background-color: #263238;
            }
        """

        # Set program icon
        if getattr(sys, "frozen", False):
            if hasattr(sys, "_MEIPASS"):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(application_path, "resources", "icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # Set dark theme
        self.set_dark_theme()

        # Main layout
        main_layout = QVBoxLayout()

        # Top panel
        title_bar = QFrame()
        title_bar.setStyleSheet(
            """
            background-color: #263238;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        """
        )
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 5, 10, 5)
        title_bar_layout.setSpacing(5)

        # Window control buttons
        close_button = QPushButton()
        close_button.setFixedSize(15, 15)
        close_button.setStyleSheet("background-color: #FF5F57; border-radius: 7px;")
        close_button.clicked.connect(self.close)

        minimize_button = QPushButton()
        minimize_button.setFixedSize(15, 15)
        minimize_button.setStyleSheet("background-color: #FFBD2E; border-radius: 7px;")
        minimize_button.clicked.connect(self.showMinimized)

        maximize_button = QPushButton()
        maximize_button.setFixedSize(15, 15)
        maximize_button.setStyleSheet("background-color: #28C940; border-radius: 7px;")
        maximize_button.clicked.connect(self.toggle_maximize)

        title_bar_layout.addWidget(close_button)
        title_bar_layout.addWidget(minimize_button)
        title_bar_layout.addWidget(maximize_button)

        # Add empty widget to create spacing
        spacer = QWidget()
        spacer.setFixedWidth(10)
        title_bar_layout.addWidget(spacer)

        # Title
        title_label = QLabel("HandyMan")  # Changed label
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()

        main_layout.addWidget(title_bar)

        # Container for main content
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #263238;")
        content_layout = QVBoxLayout(content_widget)

        # Source folder input and button
        source_layout = QHBoxLayout()
        self.source_input = QLineEdit(self)
        self.source_input.setPlaceholderText("Source Folder")
        self.select_source_button = QPushButton("Select", self)
        self.select_source_button.setStyleSheet(button_style)
        self.select_source_button.clicked.connect(self.select_source_folder)
        source_layout.addWidget(self.source_input)
        source_layout.addWidget(self.select_source_button)
        content_layout.addLayout(source_layout)

        # Destination folder input and button
        destination_layout = QHBoxLayout()
        self.destination_input = QLineEdit(self)
        self.destination_input.setPlaceholderText("Destination Folder")
        self.select_destination_button = QPushButton("Select", self)
        self.select_destination_button.setStyleSheet(button_style)
        self.select_destination_button.clicked.connect(self.select_destination_folder)
        destination_layout.addWidget(self.destination_input)
        destination_layout.addWidget(self.select_destination_button)
        content_layout.addLayout(destination_layout)

        # Action buttons in a row
        action_buttons_layout = QHBoxLayout()

        # 3 sec video button
        self.three_sec_button = QPushButton("3 sec video", self)
        self.three_sec_button.setStyleSheet(button_style)
        self.three_sec_button.clicked.connect(self.move_videos)
        action_buttons_layout.addWidget(self.three_sec_button)

        # Screenshots button
        self.screenshots_button = QPushButton("Screenshots", self)
        self.screenshots_button.setStyleSheet(button_style)
        self.screenshots_button.clicked.connect(self.move_screenshots)
        action_buttons_layout.addWidget(self.screenshots_button)

        content_layout.addLayout(action_buttons_layout)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setPointSize(10)
        self.progress_bar.setFont(font)

        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                text-align: center;
                padding: 1px;
                border: 1px solid #455A64;
                border-radius: 3px;
                background: #37474F;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 2px;
            }
            """
        )
        content_layout.addWidget(self.progress_bar)

        # Log output
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)  # Make console read-only
        content_layout.addWidget(self.log_output)

        # Cancel button
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setStyleSheet(button_style)
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setEnabled(False)  # Initially button is inactive
        content_layout.addWidget(self.cancel_button)

        main_layout.addWidget(content_widget)

        # Set main widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # For window dragging
        self.old_pos = None
        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent

        # Create status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(
            """
            QStatusBar {
                background-color: #263238;
                color: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """
        )
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Set margins for main layout
        main_layout.setContentsMargins(0, 0, 0, 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def set_dark_theme(self):
        # Create dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        # Apply palette to entire application
        self.setPalette(dark_palette)
        QApplication.setPalette(dark_palette)

        # The rest of the set_dark_theme method remains unchanged
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #263238;
                border-radius: 10px;
            }
            QWidget#centralWidget {
                background-color: #263238;
                border-radius: 10px;
            }
            QWidget {
                background-color: #263238;
                color: white;
            }
            QPushButton {
                background-color: #37474F;
                color: white;
                border: 1px solid #455A64;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
            QPushButton:pressed {
                background-color: #263238;
            }
            QLineEdit, QTextEdit {
                background-color: #37474F;
                color: #E0E0E0;
                border: 1px solid #455A64;
                padding: 3px;
                border-radius: 3px;
            }
            QLineEdit::placeholder {
                color: #78909C;
            }
            QLabel {
                color: white;
            }
            QStatusBar {
                background-color: #263238;
                color: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            """
        )

        # Set transparent background for main window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def update_status(self, message):
        self.status_bar.showMessage(message)

    def select_source_folder(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            folder = dialog.selectedFiles()[0]
            self.source_input.setText(folder)
            self.update_status("Source folder selected")

    def select_destination_folder(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            folder = dialog.selectedFiles()[0]
            self.destination_input.setText(folder)
            self.update_status("Destination folder selected")

    def reset_progress_bar(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0%")
        self.update_status("Ready")

    def move_videos(self):
        source_folder = self.source_input.text()
        destination_folder = self.destination_input.text()

        if not source_folder or not destination_folder:
            self.log_output.append("Please select both source and destination folders.")
            self.update_status("Error: Missing folders")
            return

        self.reset_progress_bar()
        self.update_status("Processing videos...")
        self.log_output.append("Moving videos...")

        self.worker = WorkerThread(move_short_videos, source_folder, destination_folder)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.update_log.connect(self.append_log)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

        self.cancel_button.setEnabled(True)  # Enable Cancel button

    def move_screenshots(self):
        source_folder = self.source_input.text()
        destination_folder = self.destination_input.text()

        if not source_folder or not destination_folder:
            self.log_output.append("Please select both source and destination folders.")
            self.update_status("Error: Folders not selected")
            return

        self.reset_progress_bar()
        self.update_status("Processing screenshots...")
        self.log_output.append("Starting search and moving of screenshots...")

        self.worker = WorkerThread(move_screenshots, source_folder, destination_folder)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.update_log.connect(self.append_log)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

        self.cancel_button.setEnabled(True)  # Enable Cancel button

    def cancel_operation(self):
        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()  # Wait for thread completion
            self.on_operation_finished()
            self.append_log("Operation cancelled by user.")

    def on_operation_finished(self):
        self.update_status("Done")
        self.log_output.append("Operation completed.")
        self.cancel_button.setEnabled(False)  # Disable Cancel button

    def update_progress(self, current, total, percentage, current_file=""):
        self.progress_bar.setValue(percentage)
        if current_file:
            self.progress_bar.setFormat(
                f"{current}/{total} {percentage}% - {current_file}"
            )
            self.update_status(f"Processing: {current_file}")
        else:
            self.progress_bar.setFormat(f"{current}/{total} {percentage}%")

    def append_log(self, message):
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

