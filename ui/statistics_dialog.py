"""
Statistics Dialog for Neuro-Tracker Application
Shows analysis and correlations between food and symptoms
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
    QFrame, QScrollArea, QComboBox, QHeaderView, QSizePolicy,
    QSlider, QSpinBox, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from config import (
    SEVERITY_COLORS, COLOR_PRIMARY, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    STATS_MIN_DAYS, CORRELATION_THRESHOLD
)
from models.data_manager import DataManager
from utils.statistics import StatisticsCalculator


class StatCard(QFrame):
    """A card widget for displaying a single statistic"""

    def __init__(self, title: str, value: str, subtitle: str = "", highlight: bool = False, parent=None):
        super().__init__(parent)
        self.setup_ui(title, value, subtitle, highlight)

    def setup_ui(self, title: str, value: str, subtitle: str, highlight: bool):
        """Initialize the UI"""
        bg_color = "#E3F2FD" if highlight else "white"
        border_color = COLOR_PRIMARY if highlight else "#E0E0E0"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)


class StatisticsDialog(QDialog):
    """
    Dialog showing statistics and food correlations
    """

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.stats_calculator = StatisticsCalculator(data_manager)

        self.setWindowTitle("Statistiken & Analyse")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_statistics()

    def setup_ui(self):
        """Initialize the UI components"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Statistiken & Analyse")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")

        # Time range selector
        self.time_range = QComboBox()
        self.time_range.addItems([
            "Letzte 7 Tage",
            "Letzte 14 Tage",
            "Letzte 30 Tage",
            "Letzte 90 Tage",
            "Alle Daten"
        ])
        self.time_range.setCurrentIndex(2)  # Default to 30 days
        self.time_range.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                min-width: 150px;
            }
        """)
        self.time_range.currentIndexChanged.connect(self.load_statistics)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Zeitraum:"))
        header_layout.addWidget(self.time_range)

        layout.addLayout(header_layout)

        # Tab widget for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 4px;
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
        """)

        # Overview tab
        self.overview_tab = QWidget()
        self.setup_overview_tab()
        self.tabs.addTab(self.overview_tab, "Übersicht")

        # Trends tab with chart
        self.trends_tab = QWidget()
        self.setup_trends_tab()
        self.tabs.addTab(self.trends_tab, "Verlauf")

        # Pattern detection tab
        self.patterns_tab = QWidget()
        self.setup_patterns_tab()
        self.tabs.addTab(self.patterns_tab, "Muster-Erkennung")

        layout.addWidget(self.tabs)

        # Close button
        close_btn = QPushButton("Schließen")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 30px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """)
        close_btn.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def setup_overview_tab(self):
        """Setup the overview tab"""
        layout = QVBoxLayout(self.overview_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Stats cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.total_entries_card = StatCard("Einträge gesamt", "0", "")
        self.avg_severity_card = StatCard("Durchschnittliche Schwere", "0.0", "", highlight=True)
        self.good_days_card = StatCard("Gute Tage", "0", "Schwere 1-2")
        self.bad_days_card = StatCard("Schlechte Tage", "0", "Schwere 4-5")

        cards_layout.addWidget(self.total_entries_card)
        cards_layout.addWidget(self.avg_severity_card)
        cards_layout.addWidget(self.good_days_card)
        cards_layout.addWidget(self.bad_days_card)

        layout.addLayout(cards_layout)

        # Severity distribution
        severity_frame = QFrame()
        severity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        severity_layout = QVBoxLayout(severity_frame)
        severity_layout.setContentsMargins(16, 16, 16, 16)

        severity_title = QLabel("Verteilung der Hautzustände")
        severity_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        severity_layout.addWidget(severity_title)

        self.severity_bars_layout = QVBoxLayout()
        severity_layout.addLayout(self.severity_bars_layout)

        layout.addWidget(severity_frame)

        # Most common foods
        foods_frame = QFrame()
        foods_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        foods_layout = QVBoxLayout(foods_frame)
        foods_layout.setContentsMargins(16, 16, 16, 16)

        foods_title = QLabel("Häufigste Lebensmittel")
        foods_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        foods_layout.addWidget(foods_title)

        self.top_foods_layout = QVBoxLayout()
        foods_layout.addLayout(self.top_foods_layout)

        layout.addWidget(foods_frame)
        layout.addStretch()

    def setup_trends_tab(self):
        """Setup the trends tab with chart"""
        layout = QVBoxLayout(self.trends_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Chart frame
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(16, 16, 16, 16)

        chart_title = QLabel("Verlauf der Hautzustände")
        chart_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        chart_layout.addWidget(chart_title)

        # Chart container with scroll
        self.chart_container = QWidget()
        self.chart_layout = QHBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(0, 20, 0, 40)
        self.chart_layout.setSpacing(2)
        self.chart_layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        chart_scroll = QScrollArea()
        chart_scroll.setWidget(self.chart_container)
        chart_scroll.setWidgetResizable(True)
        chart_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        chart_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chart_scroll.setMinimumHeight(250)
        chart_scroll.setStyleSheet("QScrollArea { border: none; }")

        chart_layout.addWidget(chart_scroll)

        # Y-axis labels
        y_axis_frame = QFrame()
        y_axis_layout = QVBoxLayout(y_axis_frame)
        y_axis_layout.setContentsMargins(0, 0, 8, 40)
        y_axis_layout.setSpacing(0)
        for i in range(5, 0, -1):
            lbl = QLabel(str(i))
            lbl.setFixedHeight(32)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            y_axis_layout.addWidget(lbl)

        chart_with_axis = QHBoxLayout()
        chart_with_axis.addWidget(y_axis_frame)
        chart_with_axis.addWidget(chart_scroll, stretch=1)
        chart_layout.addLayout(chart_with_axis)

        layout.addWidget(chart_frame, stretch=1)

        # Day of week analysis
        dow_frame = QFrame()
        dow_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        dow_layout = QVBoxLayout(dow_frame)
        dow_layout.setContentsMargins(16, 16, 16, 16)

        dow_title = QLabel("Durchschnitt nach Wochentag")
        dow_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        dow_layout.addWidget(dow_title)

        self.dow_bars_layout = QVBoxLayout()
        dow_layout.addLayout(self.dow_bars_layout)

        layout.addWidget(dow_frame)

    def setup_patterns_tab(self):
        """Setup the pattern detection tab"""
        layout = QVBoxLayout(self.patterns_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Info text
        info_label = QLabel(
            "Die Muster-Erkennung analysiert, ob bestimmte Lebensmittel mit einer Verschlechterung "
            "des Hautzustands in den folgenden Tagen zusammenhängen. Je höher die Wahrscheinlichkeit, "
            "desto öfter folgte auf dieses Lebensmittel ein schlechter Tag."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; padding: 10px; background-color: #E8F5E9; border-radius: 4px;")
        layout.addWidget(info_label)

        # Settings frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(16, 12, 16, 12)

        # Delay days setting
        delay_label = QLabel("Zeitfenster (Tage nach Verzehr):")
        delay_label.setFont(QFont("Segoe UI", 11))

        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(1, 5)
        self.delay_spinbox.setValue(2)
        self.delay_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 6px 10px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                min-width: 60px;
            }
        """)
        self.delay_spinbox.valueChanged.connect(self.update_patterns)

        # Severity threshold
        threshold_label = QLabel("Schwellenwert (min. Schwere):")
        threshold_label.setFont(QFont("Segoe UI", 11))

        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(3, 5)
        self.threshold_spinbox.setValue(4)
        self.threshold_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 6px 10px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                min-width: 60px;
            }
        """)
        self.threshold_spinbox.valueChanged.connect(self.update_patterns)

        # Refresh button
        refresh_btn = QPushButton("Aktualisieren")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """)
        refresh_btn.clicked.connect(self.update_patterns)

        settings_layout.addWidget(delay_label)
        settings_layout.addWidget(self.delay_spinbox)
        settings_layout.addSpacing(20)
        settings_layout.addWidget(threshold_label)
        settings_layout.addWidget(self.threshold_spinbox)
        settings_layout.addSpacing(20)
        settings_layout.addWidget(refresh_btn)
        settings_layout.addStretch()

        layout.addWidget(settings_frame)

        # Patterns table
        patterns_frame = QFrame()
        patterns_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        patterns_layout = QVBoxLayout(patterns_frame)
        patterns_layout.setContentsMargins(16, 16, 16, 16)

        patterns_title = QLabel("Erkannte Muster")
        patterns_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        patterns_layout.addWidget(patterns_title)

        self.patterns_table = QTableWidget()
        self.patterns_table.setColumnCount(4)
        self.patterns_table.setHorizontalHeaderLabels([
            "Lebensmittel", "Vorkommen", "Reaktionen", "Wahrscheinlichkeit"
        ])
        self.patterns_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.patterns_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.patterns_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.patterns_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.patterns_table.setAlternatingRowColors(True)
        self.patterns_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #F5F5F5;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        self.patterns_table.verticalHeader().setVisible(False)
        self.patterns_table.setSelectionBehavior(QTableWidget.SelectRows)
        patterns_layout.addWidget(self.patterns_table)

        layout.addWidget(patterns_frame, stretch=1)

    def update_patterns(self):
        """Update the patterns table based on current settings"""
        delay_days = self.delay_spinbox.value()
        threshold = self.threshold_spinbox.value()

        patterns = self.stats_calculator.detect_patterns(delay_days, threshold)
        self.patterns_table.setRowCount(len(patterns))

        for row, data in enumerate(patterns):
            # Food name
            name_item = QTableWidgetItem(data['food'])
            self.patterns_table.setItem(row, 0, name_item)

            # Occurrences
            occ_item = QTableWidgetItem(str(data['total_occurrences']))
            occ_item.setTextAlignment(Qt.AlignCenter)
            self.patterns_table.setItem(row, 1, occ_item)

            # Reactions
            react_item = QTableWidgetItem(str(data['triggered_reactions']))
            react_item.setTextAlignment(Qt.AlignCenter)
            self.patterns_table.setItem(row, 2, react_item)

            # Probability with progress bar style
            prob = data['probability']
            prob_text = f"{prob}%"

            # Color based on probability
            if prob >= 50:
                color = COLOR_DANGER
                rating = f"⚠️ {prob_text}"
            elif prob >= 25:
                color = COLOR_WARNING
                rating = f"⚡ {prob_text}"
            else:
                color = COLOR_SUCCESS
                rating = f"✓ {prob_text}"

            prob_item = QTableWidgetItem(rating)
            prob_item.setForeground(QColor(color))
            prob_item.setTextAlignment(Qt.AlignCenter)
            self.patterns_table.setItem(row, 3, prob_item)

    def get_selected_days(self) -> int:
        """Get the number of days for the selected time range"""
        index = self.time_range.currentIndex()
        days_map = {0: 7, 1: 14, 2: 30, 3: 90, 4: None}
        return days_map.get(index)

    def load_statistics(self):
        """Load and display statistics"""
        days = self.get_selected_days()
        stats = self.stats_calculator.calculate_all(days)

        # Update overview cards
        self.total_entries_card.findChild(QLabel).setText(str(stats['total_entries']))

        avg_label = self.avg_severity_card.findChildren(QLabel)[1]
        avg_label.setText(f"{stats['average_severity']:.1f}")

        good_label = self.good_days_card.findChildren(QLabel)[1]
        good_label.setText(str(stats['good_days']))

        bad_label = self.bad_days_card.findChildren(QLabel)[1]
        bad_label.setText(str(stats['bad_days']))

        # Update severity distribution
        self._update_severity_bars(stats['severity_distribution'])

        # Update top foods
        self._update_top_foods(stats['top_foods'])

        # Update chart
        self._update_chart()

        # Update day of week analysis
        self._update_dow_bars(stats['day_of_week_averages'])

        # Update patterns
        self.update_patterns()

    def _update_severity_bars(self, distribution: Dict[int, int]):
        """Update the severity distribution bars"""
        # Clear existing
        while self.severity_bars_layout.count():
            item = self.severity_bars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear nested layout
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        total = sum(distribution.values()) or 1
        severity_labels = {
            1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "Sehr schlecht"
        }

        for severity in range(1, 6):
            count = distribution.get(severity, 0)
            percentage = (count / total) * 100

            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 2, 0, 2)

            label = QLabel(f"{severity} - {severity_labels[severity]}")
            label.setFixedWidth(130)
            label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px;")

            # Bar with background
            bar = QFrame()
            bar.setFixedHeight(20)
            bar.setFixedWidth(max(int(percentage * 2.5), 4))
            bar.setStyleSheet(f"background-color: {SEVERITY_COLORS[severity]}; border-radius: 3px;")

            count_label = QLabel(f"{count} ({percentage:.0f}%)")
            count_label.setFixedWidth(70)
            count_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")

            row.addWidget(label)
            row.addWidget(bar)
            row.addStretch()
            row.addWidget(count_label)

            self.severity_bars_layout.addWidget(row_widget)

    def _update_top_foods(self, top_foods: List[Tuple[str, int]]):
        """Update the top foods list"""
        # Clear existing
        while self.top_foods_layout.count():
            item = self.top_foods_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        if not top_foods:
            empty = QLabel("Keine Daten verfügbar")
            empty.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-style: italic;")
            self.top_foods_layout.addWidget(empty)
            return

        max_count = top_foods[0][1] if top_foods else 1

        for food, count in top_foods[:10]:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 2, 0, 2)

            name_label = QLabel(food)
            name_label.setFixedWidth(130)
            name_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px;")

            bar_width = max(int((count / max_count) * 150), 4)
            bar = QFrame()
            bar.setFixedSize(bar_width, 16)
            bar.setStyleSheet(f"background-color: {COLOR_PRIMARY}; border-radius: 3px;")

            count_label = QLabel(f"{count}x")
            count_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")

            row.addWidget(name_label)
            row.addWidget(bar)
            row.addSpacing(8)
            row.addWidget(count_label)
            row.addStretch()

            self.top_foods_layout.addWidget(row_widget)

    def _update_chart(self):
        """Update the severity chart with bars for each day"""
        # Clear existing chart
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        days = self.get_selected_days()
        if days is None:
            days = 90  # Max days for chart
        days = min(days, 60)  # Limit to 60 days for readability

        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        entries = self.data_manager.get_entries_in_range(start_date, end_date)
        entry_map = {date.fromisoformat(e.date): e for e in entries}

        bar_height_max = 160  # pixels for severity 5

        current = start_date
        while current <= end_date:
            entry = entry_map.get(current)

            # Bar container
            bar_widget = QWidget()
            bar_layout = QVBoxLayout(bar_widget)
            bar_layout.setContentsMargins(0, 0, 0, 0)
            bar_layout.setSpacing(2)
            bar_layout.setAlignment(Qt.AlignBottom)

            if entry:
                severity = entry.severity
                bar_height = int((severity / 5) * bar_height_max)
                color = SEVERITY_COLORS.get(severity, "#9E9E9E")

                bar = QFrame()
                bar.setFixedSize(12, bar_height)
                bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
                bar.setToolTip(f"{current.strftime('%d.%m')}: Schwere {severity}")
                bar_layout.addWidget(bar, alignment=Qt.AlignHCenter)
            else:
                # Empty placeholder
                empty = QFrame()
                empty.setFixedSize(12, 4)
                empty.setStyleSheet("background-color: #E0E0E0; border-radius: 2px;")
                bar_layout.addWidget(empty, alignment=Qt.AlignHCenter)

            # Date label (show every 7th day or first/last)
            if current == start_date or current == end_date or current.weekday() == 0:
                date_label = QLabel(current.strftime("%d.%m"))
                date_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 9px;")
                date_label.setAlignment(Qt.AlignCenter)
            else:
                date_label = QLabel("")
                date_label.setFixedHeight(14)

            bar_layout.addWidget(date_label)
            bar_widget.setFixedWidth(16)

            self.chart_layout.addWidget(bar_widget)
            current += timedelta(days=1)

        self.chart_layout.addStretch()

    def _update_dow_bars(self, dow_data: Dict[int, float]):
        """Update the day of week bars"""
        # Clear existing
        while self.dow_bars_layout.count():
            item = self.dow_bars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        day_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

        for day_num, name in enumerate(day_names):
            avg = dow_data.get(day_num, 0)

            row = QHBoxLayout()

            label = QLabel(name)
            label.setFixedWidth(100)

            # Bar
            bar_width = int(avg * 40)  # Scale factor

            # Determine color based on average
            if avg <= 2:
                color = COLOR_SUCCESS
            elif avg <= 3:
                color = COLOR_WARNING
            else:
                color = COLOR_DANGER

            bar = QFrame()
            bar.setFixedSize(bar_width, 20)
            bar.setStyleSheet(f"background-color: {color}; border-radius: 4px;")

            value_label = QLabel(f"{avg:.1f}" if avg > 0 else "-")
            value_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")

            row.addWidget(label)
            row.addWidget(bar)
            row.addWidget(value_label)
            row.addStretch()

            self.dow_bars_layout.addLayout(row)
