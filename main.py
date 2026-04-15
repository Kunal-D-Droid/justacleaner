import sys
import os
import threading
import ctypes
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QRadioButton, QScrollArea,
    QLineEdit, QCheckBox, QFrame, QSizePolicy, QMainWindow,
    QGraphicsDropShadowEffect, QStackedWidget, QDialog
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QPainterPath, QLinearGradient, QFont, QColorConstants, QPolygonF
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSlot

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

from cleaner import run_clean
from scheduler import schedule_hours, enable_startup, enable_resume

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")
        self._position = 21.0
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.setDuration(150)
        
        self.stateChanged.connect(self.setup_animation)

    def hitButton(self, pos):
        return self.rect().contains(pos)

    @pyqtProperty(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()

    def setup_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(float(self.width() - 19))
        else:
            self.animation.setEndValue(3.0)
        self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor("#00E5FF") if self.isChecked() else QColor("#22262E")
        p.setBrush(bg_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), self.height() / 2.0, self.height() / 2.0)
        
        circle_color = QColorConstants.White
        p.setBrush(circle_color)
        circle_radius = self.height() - 6.0
        p.drawEllipse(QRectF(self._position, 3.0, circle_radius, circle_radius))
        p.end()

class CustomRadioButton(QRadioButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(30)
        self.setMinimumWidth(120)
        self.setStyleSheet("background: transparent; border: none; color: white;")
        font = self.font()
        font.setFamily('Segoe UI')
        font.setPointSize(10)
        self.setFont(font)

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        p.setPen(QPen(QColor("#00E5FF") if self.isChecked() else QColor("#555555"), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(2, (self.height() - 16) // 2, 16, 16)
        
        if self.isChecked():
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#00E5FF"))
            p.drawEllipse(6, (self.height() - 8) // 2, 8, 8)
            
        p.setPen(QPen(QColorConstants.White))
        p.setFont(self.font())
        p.drawText(28, 0, self.width() - 28, self.height(), Qt.AlignmentFlag.AlignVCenter, self.text())
        p.end()

class GradientButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        self.setStyleSheet("background: transparent; border: none;")
        font = self.font()
        font.setBold(True)
        font.setPointSize(11)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        self.setFont(font)
        self._is_pressed = False
        
    def mousePressEvent(self, event):
        self._is_pressed = True
        self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        gradient = QLinearGradient(0, 0, self.width(), 0)
        if self._is_pressed:
            gradient.setColorAt(0, QColor("#00B3CC"))
            gradient.setColorAt(1, QColor("#663399"))
        else:
            gradient.setColorAt(0, QColor("#00E5FF"))
            gradient.setColorAt(1, QColor("#994CFF"))
            
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 8, 8)
        
        p.fillPath(path, QBrush(gradient))
        
        pen = QPen(QColor("#00E5FF"))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        p.drawPath(path)
        
        p.setPen(QColor("#0c1117"))
        p.setFont(self.font())
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        p.end()

class ModuleCard(QFrame):
    def __init__(self, title, description, parent=None):
        super().__init__(parent)
        self.setStyleSheet("ModuleCard { background-color: #1A1C21; border-radius: 8px; }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        
        self.toggle = ToggleSwitch()
        self.toggle.setChecked(True)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 13px; font-family: 'Segoe UI';")
        
        self.desc_lbl = QLabel(description)
        self.desc_lbl.setStyleSheet("color: #8B949E; font-size: 11px; font-family: 'Segoe UI';")
        self.desc_lbl.setWordWrap(True)
        
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.desc_lbl)
        text_layout.addStretch()
        
        layout.addWidget(self.toggle, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(text_layout)

class InfoDialog(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("QDialog { background-color: #1A1C21; border: 1px solid #00E5FF; border-radius: 8px; }")
        self.setFixedSize(260, 130)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #D1D5DB; font-family: 'Segoe UI'; font-size: 11px;")
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn = QPushButton("CLOSE")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(30)
        btn.setStyleSheet("QPushButton { background-color: #22262E; color: #00E5FF; border: 1px solid #00E5FF; border-radius: 4px; font-weight: bold; font-size: 10px; letter-spacing: 1px; } QPushButton:hover { background: #00E5FF; color: black; }")
        btn.clicked.connect(self.accept)
        
        layout.addWidget(lbl)
        layout.addWidget(btn)

class ProgressSquare(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self._progress = 0
        
        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(4000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        
    @pyqtProperty(int)
    def progress(self):
        return self._progress
        
    @progress.setter
    def progress(self, val):
        self._progress = val
        self.update()
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(bg_rect, 10, 10)
        
        p.setClipPath(path)
        p.fillPath(path, QBrush(QColor("#15232d")))
        
        if self.progress > 0:
            offset_y = self.height() - (self.progress / 100) * self.height() * 1.5
            poly = QPolygonF([
                QPointF(-50, self.height() + 50),
                QPointF(self.width() + 50, self.height() + 50),
                QPointF(self.width() + 50, offset_y),
                QPointF(-50, offset_y + self.height() * 0.6)
            ])
            p.setBrush(QBrush(QColor("#1C4B59")))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawPolygon(poly)
            
        p.setPen(QPen(QColorConstants.White))
        font = self.font()
        font.setFamily('Segoe UI')
        font.setPointSize(34)
        font.setBold(True)
        p.setFont(font)
        
        text_y_offset = -10
        p.drawText(bg_rect.adjusted(0, text_y_offset, 0, text_y_offset), Qt.AlignmentFlag.AlignCenter, f"{self.progress}%")
        
        p.setPen(QPen(QColor("#00E5FF")))
        font.setPointSize(9)
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        p.setFont(font)
        p.drawText(bg_rect.adjusted(0, 35, 0, 0), Qt.AlignmentFlag.AlignCenter, "SCANNING...")
        p.end()


class DiagnosticRow(QFrame):
    def __init__(self, title, initial_status, parent=None):
        super().__init__(parent)
        self.setStyleSheet("DiagnosticRow { background-color: #1A1C21; border-radius: 6px; }")
        self.setFixedHeight(45)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.dot = QLabel("●")
        self.dot.setStyleSheet("color: #555; font-size: 14px;")
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #8B949E; font-weight: bold; font-family: 'Segoe UI'; font-size: 11px;")
        
        self.lbl_status = QLabel(initial_status)
        self.lbl_status.setStyleSheet("color: #555; font-weight: bold; font-family: 'Segoe UI'; font-size: 9px; letter-spacing: 1px;")
        
        layout.addWidget(self.dot)
        layout.addWidget(self.lbl_title)
        layout.addStretch()
        layout.addWidget(self.lbl_status)
        
    def set_active(self):
        self.dot.setStyleSheet("color: #00E5FF; font-size: 14px;")
        self.setStyleSheet("DiagnosticRow { background-color: #22262E; border-radius: 6px; }")
        self.lbl_title.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; font-size: 11px;")
        self.lbl_status.setStyleSheet("color: #00E5FF; font-weight: bold; font-family: 'Segoe UI'; font-size: 9px; letter-spacing: 1px;")
        self.lbl_status.setText("SCANNING...")
        
    def set_done(self, done_text="DONE"):
        self.dot.setStyleSheet("color: #994CFF; font-size: 14px;")
        self.setStyleSheet("DiagnosticRow { background-color: #1A1C21; border-radius: 6px; }")
        self.lbl_title.setStyleSheet("color: #8B949E; font-weight: bold; font-family: 'Segoe UI'; font-size: 11px;")
        self.lbl_status.setStyleSheet("color: #00E5FF; font-weight: bold; font-family: 'Segoe UI'; font-size: 9px; letter-spacing: 1px;")
        self.lbl_status.setText(done_text)

class ProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.square = ProgressSquare()
        
        sq_layout = QHBoxLayout()
        sq_layout.addStretch()
        sq_layout.addWidget(self.square)
        sq_layout.addStretch()
        
        layout.addLayout(sq_layout)
        layout.addSpacing(25)
        
        header_lay = QHBoxLayout()
        diag_lbl = QLabel("ACTIVE DIAGNOSTICS")
        diag_lbl.setStyleSheet("color: #00E5FF; font-weight: bold; letter-spacing: 1px; font-size: 10px; font-family: 'Segoe UI';")
        sys_lbl = QLabel("SYSTEM LIVE")
        sys_lbl.setStyleSheet("color: #00E5FF; font-weight: bold; letter-spacing: 1px; font-size: 10px; font-family: 'Segoe UI';")
        header_lay.addWidget(diag_lbl)
        header_lay.addStretch()
        header_lay.addWidget(sys_lbl)
        layout.addLayout(header_lay)
        layout.addSpacing(5)
        
        self.row_temp = DiagnosticRow("Clearing Temp Files...", "WAITING")
        self.row_dns = DiagnosticRow("Flushing DNS Cache...", "PENDING")
        self.row_logs = DiagnosticRow("Wiping Event Logs...", "PENDING")
        
        layout.addWidget(self.row_temp)
        layout.addWidget(self.row_dns)
        layout.addWidget(self.row_logs)
        layout.addStretch()
        
        self.cancel_btn = QPushButton("CANCEL SCAN")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.setStyleSheet("""
            QPushButton { background-color: #22262E; color: white; font-weight: bold; font-family: 'Segoe UI'; font-size: 11px; letter-spacing: 2px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #2D333B; }
        """)
        layout.addWidget(self.cancel_btn)
        
        self.square.animation.valueChanged.connect(self.on_progress)
        self.square.animation.finished.connect(self.on_finished)
        
    def start_scan(self):
        self.square.progress = 0
        self.cancel_btn.setText("CANCEL SCAN")
        
        self.row_temp.lbl_status.setText("WAITING")
        self.row_temp.dot.setStyleSheet("color: #555;")
        self.row_temp.setStyleSheet("DiagnosticRow { background-color: #1A1C21; border-radius: 6px; }")
        self.row_temp.lbl_title.setStyleSheet("color: #8B949E; font-weight: bold; font-family: 'Segoe UI'; font-size: 11px;")
        
        self.row_dns.lbl_status.setText("PENDING")
        self.row_dns.dot.setStyleSheet("color: #555;")
        self.row_dns.setStyleSheet("DiagnosticRow { background-color: #1A1C21; border-radius: 6px; }")
        self.row_dns.lbl_title.setStyleSheet("color: #8B949E; font-weight: bold; font-family: 'Segoe UI'; font-size: 11px;")
        
        self.row_logs.lbl_status.setText("PENDING")
        self.row_logs.dot.setStyleSheet("color: #555;")
        self.row_logs.setStyleSheet("DiagnosticRow { background-color: #1A1C21; border-radius: 6px; }")
        self.row_logs.lbl_title.setStyleSheet("color: #8B949E; font-weight: bold; font-family: 'Segoe UI'; font-size: 11px;")
        
        self.square.animation.start()
        
    def on_progress(self, val):
        if val == 5:
            self.row_temp.set_active()
        elif val == 35:
            self.row_temp.set_done("CLEARED")
            self.row_dns.set_active()
        elif val == 65:
            self.row_dns.set_done("CLEARED")
            self.row_logs.set_active()
            
    def on_finished(self):
        self.row_logs.set_done("COMPLETED")
        self.cancel_btn.setText("RETURN")

class MainWidget(QWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#0b1015"))
        gradient.setColorAt(1, QColor("#111a22"))
        p.fillRect(self.rect(), gradient)

class CleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Just a Cleaner")
        self.setWindowIcon(QIcon(resource_path('cleanerlogo.png')))
        self.setFixedSize(380, 680)

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 20, 20, 10)
        
        header_logo = QLabel()
        pixmap = QPixmap(resource_path('cleanerlogo.png'))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            header_logo.setPixmap(pixmap)
        
        header_title = QLabel("Just a <font color='#994CFF'>Cleaner</font>")
        header_title.setStyleSheet("color: #00E5FF; font-size: 18px; font-weight: bold; font-family: 'Segoe UI';")
        
        header_layout.addWidget(header_logo)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        credits_lbl = QLabel("<a href='https://www.kunaldas.tech' style='color: #8295d2; text-decoration: none;'>Open Source by Kunal</a>")
        credits_lbl.setOpenExternalLinks(True)
        credits_lbl.setStyleSheet("font-size: 10px; font-family: 'Segoe UI'; font-weight: bold;")
        header_layout.addWidget(credits_lbl)
        
        self.main_layout.addWidget(header_widget)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout(self.settings_page)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; } QScrollBar:vertical { width: 8px; background: transparent; } QScrollBar::handle:vertical { background: #333; border-radius: 4px; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 10, 20, 20)
        scroll_layout.setSpacing(10)
        
        mod_lbl = QLabel("OPTIMIZATION MODULES")
        mod_lbl.setStyleSheet("color: #8B949E; font-size: 10px; font-weight: bold; letter-spacing: 1.5px; font-family: 'Segoe UI';")
        mod_lbl.setContentsMargins(0, 10, 0, 5)
        scroll_layout.addWidget(mod_lbl)
        
        self.mod_sys = ModuleCard("System Cleaning", "Clears Temp files, Prefetch, Recent Items, and Recycle Bin.")
        self.mod_dl = ModuleCard("Downloads Cleanup", "Wipes all files inside the local Downloads folder.")
        self.mod_vpn = ModuleCard("VPN Removal", "Uninstalls common VPNs and eradicates leftover AppData.")
        self.mod_outlook = ModuleCard("Outlook Cleanup", "Removes Outlook saved credentials.")
        self.mod_deep = ModuleCard("Deep Privacy Clean", "Flushes DNS, nullifies clipboard, wipes Windows Event Logs, and erases File Explorer history.")
        
        scroll_layout.addWidget(self.mod_sys)
        scroll_layout.addWidget(self.mod_dl)
        scroll_layout.addWidget(self.mod_vpn)
        scroll_layout.addWidget(self.mod_outlook)
        scroll_layout.addWidget(self.mod_deep)
        
        def create_info_icon(tooltip_text):
            btn = QPushButton("i")
            btn.setFixedSize(20, 20)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("QPushButton { color: #00E5FF; border: 1px solid #00E5FF; border-radius: 10px; font-weight: bold; font-size: 11px; font-family: 'Segoe UI'; background: transparent; } QPushButton:hover { background: #00E5FF; color: black; }")
            btn.clicked.connect(lambda checked, t=tooltip_text: self.show_info_dialog(t))
            return btn

        schedule_frame = QFrame()
        schedule_frame.setStyleSheet("background-color: #1A1C21; border-radius: 8px;")
        s_layout = QVBoxLayout(schedule_frame)
        s_layout.setContentsMargins(15, 15, 15, 15)
        s_layout.setSpacing(12)
        
        auto_title = QLabel("Automate the Cleaning")
        auto_title.setStyleSheet("color: white; font-weight: bold; font-size: 13px; font-family: 'Segoe UI'; letter-spacing: 0.5px;")
        s_layout.addWidget(auto_title)
        
        int_layout = QHBoxLayout()
        self.radio_hours = CustomRadioButton("Interval")
        self.radio_hours.setChecked(True)
        
        hrs_frame = QFrame()
        hrs_frame.setStyleSheet("background-color: #22262E; border-radius: 4px;")
        hrs_layout = QHBoxLayout(hrs_frame)
        hrs_layout.setContentsMargins(10, 2, 10, 2)
        hrs_layout.setSpacing(5)
        lbl_every = QLabel("EVERY")
        lbl_every.setStyleSheet("color: #8B949E; font-size: 10px; font-weight: bold;")
        self.hours_input = QLineEdit()
        self.hours_input.setStyleSheet("background: transparent; color: #00E5FF; font-weight: bold; font-size: 14px; border: none;")
        self.hours_input.setFixedWidth(24)
        self.hours_input.setText("6")
        self.hours_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_hrs = QLabel("HRS")
        lbl_hrs.setStyleSheet("color: #8B949E; font-size: 10px; font-weight: bold;")
        hrs_layout.addWidget(lbl_every)
        hrs_layout.addWidget(self.hours_input)
        hrs_layout.addWidget(lbl_hrs)
        
        int_layout.addWidget(self.radio_hours)
        int_layout.addWidget(create_info_icon("Runs the cleaner repeatedly in the background every X hours."))
        int_layout.addStretch()
        int_layout.addWidget(hrs_frame)
        s_layout.addLayout(int_layout)
        
        s_startup_layout = QHBoxLayout()
        self.radio_startup = CustomRadioButton("On Startup")
        s_startup_layout.addWidget(self.radio_startup)
        s_startup_layout.addWidget(create_info_icon("Automatically runs the cleaner safely in the background exactly once when your computer turns on."))
        s_startup_layout.addStretch()
        s_layout.addLayout(s_startup_layout)
        
        s_resume_layout = QHBoxLayout()
        self.radio_resume = CustomRadioButton("On Resume")
        s_resume_layout.addWidget(self.radio_resume)
        s_resume_layout.addWidget(create_info_icon("Runs the cleaner immediately whenever you wake your computer from sleep or hibernation."))
        s_resume_layout.addStretch()
        s_layout.addLayout(s_resume_layout)
        
        self.save_btn = QPushButton("SAVE SCHEDULE")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedHeight(35)
        self.save_btn.setStyleSheet("QPushButton { background-color: transparent; border: 1px solid #2A2E35; border-radius: 4px; color: #00E5FF; font-weight: bold; font-size: 11px; letter-spacing: 1px; } QPushButton:hover { background-color: rgba(0, 229, 255, 0.05); border: 1px solid #00E5FF; } QPushButton:pressed { background-color: rgba(0, 229, 255, 0.1); }")
        self.save_btn.clicked.connect(self.save_schedule)
        s_layout.addWidget(self.save_btn)
        
        scroll_layout.addWidget(schedule_frame)
        scroll_area.setWidget(scroll_content)
        
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: #0d1218; border-top: 1px solid #1a2028;")
        bottom_layout_inner = QVBoxLayout(bottom_widget)
        bottom_layout_inner.setContentsMargins(20, 15, 20, 20)
        bottom_layout_inner.setSpacing(15)
        
        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #555;")
        self.status_lbl = QLabel("STATUS: IDLE")
        self.status_lbl.setStyleSheet("color: #8B949E; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        version_lbl = QLabel("V0.1.4 ACTIVE")
        version_lbl.setStyleSheet("color: #555; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_lbl)
        status_row.addStretch()
        status_row.addWidget(version_lbl)
        
        self.clean_btn = GradientButton("CLEAN NOW")
        self.clean_btn.clicked.connect(self.start_clean)
        
        bottom_layout_inner.addLayout(status_row)
        bottom_layout_inner.addWidget(self.clean_btn)
        
        settings_layout.addWidget(scroll_area)
        settings_layout.addWidget(bottom_widget)
        self.stacked_widget.addWidget(self.settings_page)
        
        self.progress_page = ProgressView()
        self.progress_page.cancel_btn.clicked.connect(self.return_to_settings)
        self.stacked_widget.addWidget(self.progress_page)

    def show_info_dialog(self, text):
        dlg = InfoDialog(text, self)
        dlg.exec()

    def start_clean(self):
        self.stacked_widget.setCurrentIndex(1)
        self.progress_page.start_scan()
        
        do_sys = self.mod_sys.toggle.isChecked()
        do_dl = self.mod_dl.toggle.isChecked()
        do_vpn = self.mod_vpn.toggle.isChecked()
        do_outlook = self.mod_outlook.toggle.isChecked()
        do_deep = self.mod_deep.toggle.isChecked()
        
        threading.Thread(target=self.clean_task, args=(do_sys, do_dl, do_vpn, do_outlook, do_deep), daemon=True).start()

    def return_to_settings(self):
        if self.progress_page.square.animation.state() == QPropertyAnimation.State.Running:
            self.progress_page.square.animation.stop()
        self.stacked_widget.setCurrentIndex(0)
        self.status_lbl.setText("STATUS: DONE")
        self.status_dot.setStyleSheet("color: #994CFF;")

    def clean_task(self, do_sys, do_dl, do_vpn, do_outlook, do_deep):
        run_clean(do_system=do_sys, do_downloads=do_dl, do_vpn=do_vpn, do_outlook=do_outlook, do_deep=do_deep)

    def save_schedule(self):
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0])

        config_path = os.path.join(os.path.dirname(exe_path), "config.json")
        try:
            config = {
                "do_system": self.mod_sys.toggle.isChecked(),
                "do_downloads": self.mod_dl.toggle.isChecked(),
                "do_vpn": self.mod_vpn.toggle.isChecked(),
                "do_outlook": self.mod_outlook.toggle.isChecked(),
                "do_deep": self.mod_deep.toggle.isChecked()
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
                self.status_lbl.setText(f"STATUS: SCHEDULED {hours}H")
            except:
                self.status_lbl.setText("STATUS: ERROR (INVALID HRS)")

        elif self.radio_startup.isChecked():
            enable_startup(exe_path)
            self.status_lbl.setText("STATUS: STARTUP ENABLED")

        elif self.radio_resume.isChecked():
            enable_resume(exe_path)
            self.status_lbl.setText("STATUS: RESUME ENABLED")

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