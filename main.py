import sys
import os
import threading
import ctypes
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QRadioButton,
    QLineEdit, QCheckBox, QSpinBox
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

from cleaner import run_clean
from scheduler import schedule_hours, enable_startup, enable_resume

class CleanerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Cleaner")
        self.setWindowIcon(QIcon(resource_path('cleanerlogo.png')))

        layout = QVBoxLayout()
        layout.setSpacing(8)

        # LOGO
        self.logo_label = QLabel()
        pixmap = QPixmap(resource_path('cleanerlogo.png'))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # CLEAN BUTTON
        self.clean_btn = QPushButton("Clean Now")
        self.clean_btn.clicked.connect(self.start_clean)

        # STATUS
        self.status = QLabel("Status: Idle")

        # CHECKBOXES
        self.chk_system = QCheckBox("System Cleaning")
        self.chk_system.setChecked(True)

        self.chk_downloads = QCheckBox("Downloads Cleanup")
        self.chk_downloads.setChecked(True)

        self.chk_vpn = QCheckBox("VPN Removal")
        self.chk_vpn.setChecked(True)

        self.chk_outlook = QCheckBox("Outlook Cleanup")
        self.chk_outlook.setChecked(True)

        self.chk_deep = QCheckBox("Deep Privacy Clean (Logs, History)")
        self.chk_deep.setChecked(True)

        # SCHEDULER OPTIONS
        self.radio_hours = QRadioButton("Every X hours")
        self.hours_input = QLineEdit()
        self.hours_input.setPlaceholderText("Enter hours")

        self.radio_startup = QRadioButton("On Startup")
        self.radio_resume = QRadioButton("On Resume")

        self.save_btn = QPushButton("Save Schedule")
        self.save_btn.clicked.connect(self.save_schedule)

        # ADD TO LAYOUT
        layout.addWidget(self.logo_label)
        layout.addWidget(self.clean_btn)
        layout.addWidget(self.status)
        layout.addWidget(self.chk_system)
        layout.addWidget(self.chk_downloads)
        layout.addWidget(self.chk_vpn)
        layout.addWidget(self.chk_outlook)
        layout.addWidget(self.chk_deep)
        layout.addWidget(self.radio_hours)
        layout.addWidget(self.hours_input)
        layout.addWidget(self.radio_startup)
        layout.addWidget(self.radio_resume)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)
        
        # Hug the contents tightly and lock the size
        self.setFixedWidth(350)
        self.adjustSize()
        self.setFixedSize(self.size())

    # ---------------- CLEAN ----------------

    def start_clean(self):
        self.status.setText("Running...")
        
        do_sys = self.chk_system.isChecked()
        do_dl = self.chk_downloads.isChecked()
        do_vpn = self.chk_vpn.isChecked()
        do_outlook = self.chk_outlook.isChecked()
        do_deep = self.chk_deep.isChecked()
        
        threading.Thread(target=self.clean_task, args=(do_sys, do_dl, do_vpn, do_outlook, do_deep)).start()

    def clean_task(self, do_sys, do_dl, do_vpn, do_outlook, do_deep):
        run_clean(do_system=do_sys, do_downloads=do_dl, do_vpn=do_vpn, do_outlook=do_outlook, do_deep=do_deep)
        self.status.setText("Done")

    # ---------------- SCHEDULER ----------------

    def save_schedule(self):
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0])

        config_path = os.path.join(os.path.dirname(exe_path), "config.json")
        try:
            config = {
                "do_system": self.chk_system.isChecked(),
                "do_downloads": self.chk_downloads.isChecked(),
                "do_vpn": self.chk_vpn.isChecked(),
                "do_outlook": self.chk_outlook.isChecked(),
                "do_deep": self.chk_deep.isChecked()
            }
            with open(config_path, "w") as f:
                json.dump(config, f)
        except:
            pass

        if self.radio_hours.isChecked():
            try:
                hours = int(self.hours_input.text())
                if hours <= 0:
                    raise ValueError
                schedule_hours(hours, exe_path)
                self.status.setText(f"Scheduled every {hours} hrs")
            except:
                self.status.setText("Invalid hours")

        elif self.radio_startup.isChecked():
            enable_startup(exe_path)
            self.status.setText("Startup enabled")

        elif self.radio_resume.isChecked():
            enable_resume(exe_path)
            self.status.setText("Resume trigger enabled")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == '__main__':
    if "--silent-clean" in sys.argv:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0])
            
        config_path = os.path.join(os.path.dirname(exe_path), "config.json")
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except:
            config = {}
            
        run_clean(
            do_system=config.get("do_system", True),
            do_downloads=config.get("do_downloads", False),
            do_vpn=config.get("do_vpn", False),
            do_outlook=config.get("do_outlook", False),
            do_deep=config.get("do_deep", False)
        )
        sys.exit(0)

    if not is_admin():
        script = sys.executable
        params = ' '.join([f'"{sys.argv[0]}"'] + sys.argv[1:]) if not getattr(sys, 'frozen', False) else ''
        ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
        sys.exit()

    app = QApplication(sys.argv)
    window = CleanerApp()
    window.show()
    sys.exit(app.exec())