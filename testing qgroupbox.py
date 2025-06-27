#!/usr/bin/env python3

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Collapsible Hierarchical Checkbox List")
        self.resize(300, 250)

        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)  # Hide column headers

        # --- Reports Section ---Qt.ItemFlag.ItemIsTristate
        reports = QTreeWidgetItem(["Reports"])
        reports.setFlags(reports.flags() | Qt.ItemFlag.ItemIsUserCheckable)

        script1 = QTreeWidgetItem(["Script 1"])
        script1.setCheckState(0, Qt.CheckState.Unchecked)

        script2 = QTreeWidgetItem(["Script 2"])
        script2.setCheckState(0, Qt.CheckState.Unchecked)

        reports.addChildren([script1, script2])

        # --- Cleanup Section ---
        cleanup = QTreeWidgetItem(["Cleanup"])
        cleanup.setFlags(cleanup.flags() | Qt.ItemFlag.ItemIsUserCheckable)

        unused_computers = QTreeWidgetItem(["Unused Computers"])
        unused_computers.setCheckState(0, Qt.CheckState.Unchecked)

        unused_alerts = QTreeWidgetItem(["Unused Alerts"])
        unused_alerts.setCheckState(0, Qt.CheckState.Unchecked)

        cleanup.addChildren([unused_computers, unused_alerts])

        # Add sections to tree
        self.tree.addTopLevelItems([reports, cleanup])

        layout.addWidget(self.tree)
        self.setLayout(layout)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())