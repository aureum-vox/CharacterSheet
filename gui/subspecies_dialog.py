from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class SubspeciesDialog(QDialog):
    """Pops up when a species with lineage/ancestry choices is selected at Level 1."""
    
    SUBSPECIES_2024 = {
        "Goliath": [
            "Cloud Giant Ancestry", "Fire Giant Ancestry", "Frost Giant Ancestry", 
            "Hill Giant Ancestry", "Stone Giant Ancestry", "Storm Giant Ancestry"
        ],
        "Dragonborn": [
            "Black Dragon", "Blue Dragon", "Brass Dragon", "Bronze Dragon", 
            "Copper Dragon", "Gold Dragon", "Green Dragon", "Red Dragon", 
            "Silver Dragon", "White Dragon"
        ],
        "Elf": [
            "Drow", "High Elf", "Wood Elf"
        ],
        "Gnome": [
            "Forest Gnome", "Rock Gnome"
        ],
        "Tiefling": [
            "Abyssal Tiefling", "Chthonic Tiefling", "Infernal Tiefling"
        ],
        "Aasimar": [
            "Celestial Aasimar" # Standardizes 2024 options
        ]
    }

    def __init__(self, species_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{species_name} Lineage / Ancestry")
        self.setFixedSize(320, 160)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout(self)
        
        lbl = QLabel(f"Choose your {species_name} Ancestry or Lineage:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        
        self.dropdown = QComboBox()
        options = self.SUBSPECIES_2024.get(species_name, ["Standard Lineage"])
        self.dropdown.addItems(options)
        layout.addWidget(self.dropdown)
        
        layout.addSpacing(10)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Confirm")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)

    def get_subspecies(self):
        return self.dropdown.currentText()