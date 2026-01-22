"""
Entry Panel Widget for Neuro-Tracker Application
Left sidebar for entering/editing day data
"""

from datetime import date, datetime
from typing import List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QLineEdit, QTextEdit, QFrame, QScrollArea,
    QCompleter, QMessageBox, QSizePolicy, QGridLayout, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel, QTimer
from PyQt5.QtGui import QFont
import json

from config import (
    SEVERITY_COLORS, MIN_SEVERITY, MAX_SEVERITY,
    COLOR_PRIMARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_DANGER, COLOR_SUCCESS, ENTRY_PANEL_WIDTH, FOOD_SUGGESTIONS_FILE
)
from models.day_entry import DayEntry
from models.data_manager import DataManager
from models.food_manager import FoodManager




class EntryPanel(QWidget):
    """
    Panel for entering and editing day entries.
    Shows severity slider, food input, and notes.
    """

    entry_saved = pyqtSignal(date)  # Emitted when entry is saved
    entry_deleted = pyqtSignal(date)  # Emitted when entry is deleted

    def __init__(self, data_manager: DataManager, food_manager: FoodManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.food_manager = food_manager
        self.current_date: Optional[date] = None
        self.current_entry: Optional[DayEntry] = None

        self.setFixedWidth(ENTRY_PANEL_WIDTH)
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI components"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: white;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)

        # Date header
        self.date_label = QLabel("Datum auswählen")
        self.date_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.date_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        self.content_layout.addWidget(self.date_label)

        self.weekday_label = QLabel("")
        self.weekday_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 14px;")
        self.content_layout.addWidget(self.weekday_label)

        # Separator
        self.content_layout.addWidget(self._create_separator())

        # Severity section
        severity_section = QWidget()
        severity_layout = QVBoxLayout(severity_section)
        severity_layout.setContentsMargins(0, 0, 0, 0)
        severity_layout.setSpacing(12)

        severity_header = QLabel("Hautzustand")
        severity_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        severity_layout.addWidget(severity_header)

        # Severity buttons
        severity_buttons_layout = QHBoxLayout()
        severity_buttons_layout.setSpacing(8)

        self.severity_buttons = []
        severity_labels = ["1", "2", "3", "4", "5"]

        for i, label in enumerate(severity_labels, start=1):
            btn = QPushButton(label)
            btn.setFixedSize(48, 48)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("severity", i)
            btn.clicked.connect(lambda checked, s=i: self.set_severity(s))
            self.severity_buttons.append(btn)
            severity_buttons_layout.addWidget(btn)

        severity_buttons_layout.addStretch()
        severity_layout.addLayout(severity_buttons_layout)

        # Severity description
        self.severity_description = QLabel("Wähle den Hautzustand (1=sehr gut, 5=sehr schlecht)")
        self.severity_description.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        self.severity_description.setWordWrap(True)
        severity_layout.addWidget(self.severity_description)

        # Skin Notes directly under severity
        skin_notes_header = QLabel("Notizen Hautzustand")
        skin_notes_header.setFont(QFont("Segoe UI", 12))
        skin_notes_header.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; margin-top: 8px;")
        severity_layout.addWidget(skin_notes_header)

        self.skin_notes_input = QTextEdit()
        self.skin_notes_input.setPlaceholderText("z.B. Rötungen, Juckreiz, Stellen...")
        self.skin_notes_input.setMaximumHeight(60)
        self.skin_notes_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """)
        severity_layout.addWidget(self.skin_notes_input)

        self.content_layout.addWidget(severity_section)

        # Separator
        self.content_layout.addWidget(self._create_separator())

        # Food section with checkboxes
        food_section = QWidget()
        food_layout = QVBoxLayout(food_section)
        food_layout.setContentsMargins(0, 0, 0, 0)
        food_layout.setSpacing(8)

        food_header = QLabel("Lebensmittel")
        food_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        food_layout.addWidget(food_header)

        # Load fixed food suggestions
        self.fixed_foods = self._load_food_suggestions()
        self.food_checkboxes = {}

        # Create checkbox grid
        checkbox_container = QWidget()
        checkbox_grid = QGridLayout(checkbox_container)
        checkbox_grid.setContentsMargins(0, 0, 0, 0)
        checkbox_grid.setSpacing(4)

        for i, food in enumerate(self.fixed_foods):
            checkbox = QCheckBox(food)
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    font-size: 12px;
                    padding: 4px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {COLOR_PRIMARY};
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 3px;
                }}
                QCheckBox::indicator:unchecked {{
                    background-color: white;
                    border: 1px solid #BDBDBD;
                    border-radius: 3px;
                }}
            """)
            row = i // 2
            col = i % 2
            checkbox_grid.addWidget(checkbox, row, col)
            self.food_checkboxes[food] = checkbox

        food_layout.addWidget(checkbox_container)

        # Food Notes directly under food checkboxes
        food_notes_header = QLabel("Notizen Nahrung")
        food_notes_header.setFont(QFont("Segoe UI", 12))
        food_notes_header.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; margin-top: 8px;")
        food_layout.addWidget(food_notes_header)

        self.food_notes_input = QTextEdit()
        self.food_notes_input.setPlaceholderText("z.B. Menge, Zubereitung...")
        self.food_notes_input.setMaximumHeight(60)
        self.food_notes_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """)
        food_layout.addWidget(self.food_notes_input)

        self.content_layout.addWidget(food_section)

        # Keep legacy notes_input as hidden for backward compatibility
        self.notes_input = QTextEdit()
        self.notes_input.setVisible(False)

        # Stretch to push buttons to bottom
        self.content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Action buttons at bottom (smaller)
        button_container = QWidget()
        button_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top: 1px solid #E0E0E0;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(20, 10, 20, 10)
        button_layout.setSpacing(8)

        self.save_button = QPushButton("Speichern")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #388E3C;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
            }}
        """)
        self.save_button.clicked.connect(self.save_entry)

        self.delete_button = QPushButton("Löschen")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: {COLOR_DANGER};
                border: 1px solid {COLOR_DANGER};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #FFEBEE;
            }}
        """)
        self.delete_button.clicked.connect(self.delete_entry)
        self.delete_button.setVisible(False)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # Status message label (for save confirmation)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"""
            color: {COLOR_SUCCESS};
            font-size: 13px;
            font-weight: bold;
            padding: 5px;
        """)
        self.status_label.setVisible(False)
        button_layout.addWidget(self.status_label)

        main_layout.addWidget(button_container)

        # Initialize severity buttons style
        self.current_severity = None
        self.update_severity_buttons()

    def _create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #E0E0E0;")
        separator.setFixedHeight(1)
        return separator

    def _load_food_suggestions(self) -> list:
        """Load fixed food suggestions from JSON file"""
        try:
            with open(FOOD_SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return ["Milch", "Weizen", "Eier", "Nüsse", "Schokolade"]

    def get_selected_foods(self) -> list:
        """Get list of selected food checkboxes"""
        return [food for food, checkbox in self.food_checkboxes.items() if checkbox.isChecked()]

    def set_food_checkboxes(self, foods: list):
        """Set the food checkboxes based on a list of foods"""
        for food, checkbox in self.food_checkboxes.items():
            checkbox.setChecked(food in foods)

    def set_date(self, selected_date: date):
        """Set the date to edit"""
        self.current_date = selected_date
        self.current_entry = self.data_manager.get_entry(selected_date)

        # Update date display
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                 "Juli", "August", "September", "Oktober", "November", "Dezember"]

        self.date_label.setText(f"{selected_date.day}. {months[selected_date.month - 1]} {selected_date.year}")
        self.weekday_label.setText(weekdays[selected_date.weekday()])

        # Load entry data
        if self.current_entry:
            self.set_severity(self.current_entry.severity)
            self.set_food_checkboxes(self.current_entry.foods)
            self.skin_notes_input.setText(self.current_entry.skin_notes or "")
            self.food_notes_input.setText(self.current_entry.food_notes or "")
            self.delete_button.setVisible(True)
        else:
            self.current_severity = None
            self.set_food_checkboxes([])
            self.skin_notes_input.clear()
            self.food_notes_input.clear()
            self.delete_button.setVisible(False)

        self.update_severity_buttons()

    def set_severity(self, severity: int):
        """Set the current severity level"""
        self.current_severity = severity
        self.update_severity_buttons()

        severity_descriptions = {
            1: "Sehr gut - Haut ist klar und gesund",
            2: "Gut - Leichte Rötungen möglich",
            3: "Mittel - Moderate Symptome",
            4: "Schlecht - Deutliche Symptome",
            5: "Sehr schlecht - Starke Symptome"
        }
        self.severity_description.setText(severity_descriptions.get(severity, ""))

    def update_severity_buttons(self):
        """Update the style of severity buttons"""
        for btn in self.severity_buttons:
            severity = btn.property("severity")
            color = SEVERITY_COLORS.get(severity, "#9E9E9E")

            if severity == self.current_severity:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border: 2px solid {color};
                        border-radius: 24px;
                        font-weight: bold;
                        font-size: 16px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                        color: {color};
                        border: 2px solid {color};
                        border-radius: 24px;
                        font-weight: bold;
                        font-size: 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {color}20;
                    }}
                """)


    def save_entry(self):
        """Save the current entry"""
        if not self.current_date:
            return

        if self.current_severity is None:
            QMessageBox.warning(self, "Fehler", "Bitte wähle einen Hautzustand aus.")
            return

        entry = DayEntry(
            date=self.current_date.isoformat(),
            severity=self.current_severity,
            foods=self.get_selected_foods(),
            skin_notes=self.skin_notes_input.toPlainText().strip() or "",
            food_notes=self.food_notes_input.toPlainText().strip() or ""
        )

        self.data_manager.add_or_update_entry(entry)
        self.current_entry = entry
        self.delete_button.setVisible(True)

        self.entry_saved.emit(self.current_date)

        # Show status message instead of popup
        self.show_status_message("✓ Gespeichert")

    def delete_entry(self):
        """Delete the current entry"""
        if not self.current_date or not self.current_entry:
            return

        self.data_manager.delete_entry(self.current_date)
        self.current_entry = None
        self.current_severity = None
        self.set_food_checkboxes([])
        self.skin_notes_input.clear()
        self.food_notes_input.clear()
        self.delete_button.setVisible(False)

        self.update_severity_buttons()

        self.entry_deleted.emit(self.current_date)

        self.show_status_message("✓ Gelöscht")

    def show_status_message(self, message: str, duration: int = 2000):
        """Show a temporary status message at the bottom"""
        self.status_label.setText(message)
        self.status_label.setVisible(True)
        QTimer.singleShot(duration, lambda: self.status_label.setVisible(False))

    def clear(self):
        """Clear the panel"""
        self.current_date = None
        self.current_entry = None
        self.current_severity = None
        self.set_food_checkboxes([])

        self.date_label.setText("Datum auswählen")
        self.weekday_label.setText("")
        self.skin_notes_input.clear()
        self.food_notes_input.clear()
        self.delete_button.setVisible(False)

        self.update_severity_buttons()
