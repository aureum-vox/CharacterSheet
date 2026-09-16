from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from gui.ability_widget import AbilityWidget
from gui.header_widget import HeaderWidget
from gui.features_widget import FeaturesWidget # <-- Import the new widget

class CharacterSheetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("5.5e Dynamic Character Sheet")
        self.setMinimumSize(1024, 768)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.setup_left_column()
        self.setup_right_column()

    def setup_left_column(self):
        self.left_column = QVBoxLayout()
        abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        for ability in abilities:
            widget = AbilityWidget(ability)
            self.left_column.addWidget(widget)
        self.left_column.addStretch() 
        self.main_layout.addLayout(self.left_column)

    def setup_right_column(self):
        self.right_column = QVBoxLayout()
        
        # 1. Header
        self.header = HeaderWidget()
        self.right_column.addWidget(self.header)
        
        # 2. Features Area
        self.features_area = FeaturesWidget()
        self.right_column.addWidget(self.features_area)
        
        # Let's add some mock data to test the layout
        mock_features = [
            "Second Wind", "Weapon Mastery", "Action Surge", 
            "Tactical Mind", "Indomitable", "Extra Attack"
        ]
        for i in range(3): # Loop a few times to guarantee a scrollbar appears
            for feat in mock_features:
                self.features_area.add_feature(feat, "XPHB")
        
        self.main_layout.addLayout(self.right_column)
        self.main_layout.setStretch(0, 1) 
        self.main_layout.setStretch(1, 5)