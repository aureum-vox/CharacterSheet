from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QListWidget
from PyQt6.QtCore import Qt

class LevelUpDialog(QDialog):
    def __init__(self, parent=None, is_first_level=False):
        super().__init__(parent)
        
        self.setWindowTitle("Level Up")
        
        # --- Make the window taller at Level 1 to fit the skill list ---
        self.setFixedSize(300, 450 if is_first_level else 150)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout(self)
        self.is_first_level = is_first_level
        
        # --- 1. Level 1 Setup (Name & Skills) ---
        if self.is_first_level:
            name_label = QLabel("Enter Character Name:")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(name_label)
            
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("e.g. Drizzt Do'Urden")
            layout.addWidget(self.name_input)
            layout.addSpacing(10)
            
            # Skill Selector
            skill_label = QLabel("Select Starting Skills:")
            skill_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(skill_label)
            
            self.skill_list = QListWidget()
            self.skill_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            skills = [
                "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", 
                "History", "Insight", "Intimidation", "Investigation", "Medicine", 
                "Nature", "Perception", "Performance", "Persuasion", "Religion", 
                "Sleight of Hand", "Stealth", "Survival"
            ]
            self.skill_list.addItems(skills)
            layout.addWidget(self.skill_list)
            layout.addSpacing(10)
        
        # --- 2. Class Selection ---
        prompt = QLabel("Select a class to level up:")
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(prompt)
        
        self.class_dropdown = QComboBox()
        core_classes = [
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter", 
            "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", 
            "Warlock", "Wizard"
        ]
        self.class_dropdown.addItems(core_classes)
        layout.addWidget(self.class_dropdown)
        
        layout.addSpacing(10)
        
        # --- 3. Buttons ---
        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("Confirm")
        self.cancel_btn = QPushButton("Cancel")
        
        self.confirm_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(btn_layout)
        
    def get_selected_class(self):
        return self.class_dropdown.currentText().lower()
        
    def get_character_name(self):
        """Returns the typed name, or None if the field wasn't generated."""
        if self.is_first_level:
            return self.name_input.text().strip()
        return None

    def get_selected_skills(self):
        """Returns a list of checked skills, or an empty list if not level 1."""
        if self.is_first_level:
            return [item.text() for item in self.skill_list.selectedItems()]
        return []