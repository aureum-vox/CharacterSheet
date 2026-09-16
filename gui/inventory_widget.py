from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

class InventoryWidget(QFrame):
    def __init__(self):
        super().__init__()
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        main_layout = QVBoxLayout(self)
        
        # 1. Section Title
        title_label = QLabel("INVENTORY & EQUIPMENT")
        font = title_label.font()
        font.setBold(True)
        font.setPointSize(12)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 2. Currency Tracker Layout (CP, SP, EP, GP, PP)
        currency_frame = QWidget()
        currency_layout = QHBoxLayout(currency_frame)
        currency_layout.setContentsMargins(0, 0, 0, 10)
        
        self.coins = {}
        coin_types = ["CP", "SP", "EP", "GP", "PP"]
        
        for coin in coin_types:
            box_layout = QVBoxLayout()
            label = QLabel(coin)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            input_field = QLineEdit("0")
            input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
            input_field.setMaximumWidth(50)
            
            box_layout.addWidget(label)
            box_layout.addWidget(input_field)
            currency_layout.addLayout(box_layout)
            
            self.coins[coin] = input_field
            
        main_layout.addWidget(currency_frame)
        
        # 3. Item Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Item Name", "Qty", "Weight (lbs)", "Total Wt"])
        
        # Stretch columns nicely
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        main_layout.addWidget(self.table)
        
        # 4. Add Item & Weight Summary Row
        bottom_layout = QHBoxLayout()
        
        self.add_item_btn = QPushButton("Add Custom Item")
        bottom_layout.addWidget(self.add_item_btn)
        
        bottom_layout.addStretch()
        
        self.weight_label = QLabel("Total Weight: 0.0 lbs")
        font_wt = self.weight_label.font()
        font_wt.setBold(True)
        self.weight_label.setFont(font_wt)
        bottom_layout.addWidget(self.weight_label)
        
        main_layout.addLayout(bottom_layout)
        
        # Placeholder rows to demonstrate layout
        self.load_placeholder_data()
        
    def load_placeholder_data(self):
        """Loads sample inventory items for layout testing."""
        sample_items = [
            ("Quarterstaff", 1, 4.0),
            ("Explorer's Pack", 1, 59.0),
            ("Darts", 10, 0.25)
        ]
        
        self.table.setRowCount(len(sample_items))
        for row, (name, qty, wt) in enumerate(sample_items):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(str(qty)))
            self.table.setItem(row, 2, QTableWidgetItem(str(wt)))
            self.table.setItem(row, 3, QTableWidgetItem(str(qty * wt)))
            
        self.update_total_weight()
        
    def update_total_weight(self):
        """Calculates total weight of all inventory items."""
        total = 0.0
        for row in range(self.table.rowCount()):
            try:
                qty = float(self.table.item(row, 1).text() or 0)
                wt = float(self.table.item(row, 2).text() or 0)
                total += qty * wt
                # Update total weight column cell automatically
                self.table.setItem(row, 3, QTableWidgetItem(str(qty * wt)))
            except ValueError:
                continue
        self.weight_label.setText(f"Total Weight: {total:.1f} lbs")