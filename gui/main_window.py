from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox
from gui.ability_widget import AbilityWidget
from gui.header_widget import HeaderWidget
from gui.features_widget import FeaturesWidget

# Import our Data Layer
from data.character import Character
from data.fetcher import get_2024_class_data

class CharacterSheetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("5.5e Dynamic Character Sheet")
        self.setMinimumSize(1024, 768)
        
        # 1. Initialize our Backend Character state
        self.hero = Character(name="Kael")
        self.current_class = "fighter" # We'll hardcode Fighter for testing
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.setup_left_column()
        self.setup_right_column()
        
        # 2. Wire up the button!
        self.header.level_up_btn.clicked.connect(self.level_up_character)
        
        # 3. Sync the UI to the character's initial state
        self.update_ui()

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
        self.header = HeaderWidget()
        self.right_column.addWidget(self.header)
        
        self.features_area = FeaturesWidget()
        self.right_column.addWidget(self.features_area)
        
        self.main_layout.addLayout(self.right_column)
        self.main_layout.setStretch(0, 1) 
        self.main_layout.setStretch(1, 5)

    def level_up_character(self):
        """Triggered when the Level Up button is clicked."""
        # Fetch data (this uses the cache if it already exists in temp/)
        class_data = get_2024_class_data(f"class/class-{self.current_class}.json")
        if not class_data:
            QMessageBox.critical(self, "Network Error", "Failed to fetch class data! Check your .env file.")
            return
            
        # Update character level internally
        class_name_formatted = self.current_class.capitalize()
        self.hero.level_up_class(class_name_formatted)
        new_level = self.hero.classes[class_name_formatted]
        
        # Extract features specifically for this new level
        class_features = class_data.get("classFeatures", [])
        for item in class_features:
            feature_ref = item.get("classFeature") if isinstance(item, dict) else item
            if isinstance(feature_ref, str):
                parts = feature_ref.split("|")
                if parts[0] == "classFeature":
                    feature_name = parts[1]
                    feature_level = parts[4] if len(parts) >= 5 else None
                else:
                    feature_name = parts[0]
                    feature_level = parts[3] if len(parts) >= 4 else None
                    
                if str(feature_level) == str(new_level):
                    self.hero.add_feature(feature_name, source="XPHB")
                    
        # Refresh the GUI to show the new features
        self.update_ui()

    def update_ui(self):
        """Syncs the visual GUI to match the internal character state."""
        # Update name
        self.header.name_input.setText(self.hero.name)
        
        # Update class & level display (e.g., "Fighter 1", "Fighter 2")
        class_str = ", ".join([f"{c} {l}" for c, l in self.hero.classes.items()])
        if not class_str:
            class_str = "Level 0 (Ready to Start)"
        self.header.class_level_display.setText(class_str)
        
        # Clear the visual features list and rebuild it from the character state
        self.features_area.clear_features()
        for feat in self.hero.features:
            self.features_area.add_feature(feat["name"], feat["source"])