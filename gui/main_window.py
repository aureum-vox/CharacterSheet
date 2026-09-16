from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QTabWidget
from gui.ability_widget import AbilityWidget
from gui.header_widget import HeaderWidget
from gui.features_widget import FeaturesWidget
from gui.level_up_dialog import LevelUpDialog
from gui.inventory_widget import InventoryWidget
import re

# Import our Data Layer
from data.character import Character
from data.fetcher import get_2024_class_data

def parse_5e_text(entry):
    """Recursively extracts text from 5etools nested JSON structures."""
    if isinstance(entry, str):
        return entry
        
    if isinstance(entry, list):
        # Join lists with a double newline for paragraph spacing
        return "\n\n".join(parse_5e_text(e) for e in entry if e)
        
    if isinstance(entry, dict):
        text = ""
        # Sometimes nested objects have their own bolded headers
        if "name" in entry:
            text += f"{entry['name']}: "
            
        if "entries" in entry:
            text += parse_5e_text(entry["entries"])
        elif "items" in entry:
            # Format 5etools lists as bullet points
            items_text = "\n".join(f"  • {parse_5e_text(i)}" for i in entry["items"])
            text += "\n" + items_text
            
        return text.strip()
        
    return ""

class CharacterSheetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("5.5e Dynamic Character Sheet")
        self.setMinimumSize(1024, 768)
        
        # 1. Initialize our Backend Character state with no name
        self.hero = Character(name="")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.setup_left_column()
        self.setup_right_column()
        
        # === THE CRITICAL FIX FOR THE BUTTON ===
        self.header.level_up_btn.clicked.connect(self.level_up_character)
        
        # Sync UI to starting state
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
        
        # 1. Header (Stays permanently visible at the top)
        self.header = HeaderWidget()
        self.right_column.addWidget(self.header)
        
        # 2. The Tab System
        self.tabs = QTabWidget()
        
        # --- Tab 1: Features & Traits ---
        # We assign our existing FeaturesWidget to the first tab
        self.features_area = FeaturesWidget()
        self.tabs.addTab(self.features_area, "Features & Traits")
        
        # --- Tab 2: Spells (Placeholder) ---
        self.spells_area = QWidget()
        self.tabs.addTab(self.spells_area, "Spells")
        
        # --- Tab 3: Inventory ---
        self.inventory_area = InventoryWidget()
        self.tabs.addTab(self.inventory_area, "Inventory")
        
        # Add the tab system to the main column layout
        self.right_column.addWidget(self.tabs)
        
        self.main_layout.addLayout(self.right_column)
        self.main_layout.setStretch(0, 1) 
        self.main_layout.setStretch(1, 5)

    def level_up_character(self):
        """Triggered when the Level Up button is clicked."""
        
        # Calculate if this is the character's very first level
        total_level = sum(self.hero.classes.values())
        is_first_level = (total_level == 0)
        
        # 1. Launch the Pop-up Dialog
        dialog = LevelUpDialog(self, is_first_level=is_first_level)
        
        if not dialog.exec():
            return 
            
        # 2. Get the chosen class and optional name
        selected_class = dialog.get_selected_class()
        
        if is_first_level:
            new_name = dialog.get_character_name()
            # If they typed a name, save it. Otherwise, give a fallback.
            self.hero.name = new_name if new_name else "Unknown Hero"
        
        # 3. Fetch data for that specific class
        class_data, feature_data = get_2024_class_data(f"class/class-{selected_class}.json")
        if not class_data:
            QMessageBox.critical(self, "Network Error", f"Failed to fetch {selected_class.capitalize()} data!")
            return
            
        # 4. Level up the character internally
        class_name_formatted = selected_class.capitalize()
        self.hero.level_up_class(class_name_formatted)
        new_level = self.hero.classes[class_name_formatted]
        
        # 5. Safely extract features
        class_features = class_data.get("classFeatures", [])
        
        level_features = []
        if class_features and isinstance(class_features[0], list):
            if new_level - 1 < len(class_features):
                level_features = class_features[new_level - 1]
        else:
            level_features = class_features

        for item in level_features:
            feature_ref = item.get("classFeature") if isinstance(item, dict) else item
            
            if isinstance(feature_ref, str):
                parts = feature_ref.split("|")
                if parts[0] == "classFeature":
                    feature_name = parts[1]
                    feature_level = parts[4] if len(parts) >= 5 else "1"
                else:
                    feature_name = parts[0]
                    feature_level = parts[3] if len(parts) >= 4 else "1"
                    
                if str(feature_level) == str(new_level):
                    
                    # --- REAL DESCRIPTION EXTRACTION ---
                    desc = "Description not found."
                    
                    # 1. Search the actual "classFeature" array for the matching ability
                    for real_feat in feature_data:
                        if real_feat.get("name") == feature_name and str(real_feat.get("level")) == str(new_level):
                            entries = real_feat.get("entries", [])
                            
                            # 2. Recursively extract all text, including nested lists
                            raw_desc = parse_5e_text(entries)
                            
                            # 3. Clean up 5etools syntax tags
                            desc = re.sub(r'\{@[^\s]+\s([^}|]+)[^}]*\}', r'\1', raw_desc)
                            break
                    # -----------------------------------
                    
                    uses = 2 if feature_name in ["Second Wind", "Channel Divinity"] else 0
                    
                    choices = None
                    if feature_name == "Fighting Style":
                        choices = ["Archery", "Defense", "Dueling", "Great Weapon Fighting", "Protection", "Two-Weapon Fighting"]
                    elif feature_name == "Weapon Mastery":
                        choices = ["Cleave", "Graze", "Nick", "Push", "Sap", "Slow", "Topple", "Vex"]
                    
                    self.hero.add_feature(feature_name, "XPHB", description=desc, uses=uses, choices=choices)
                    
        self.update_ui()

    def update_ui(self):
        """Syncs the visual GUI to match the internal character state."""
        
        # Only set the text if the character actually has a name, 
        # otherwise clear it so the placeholder text is visible.
        if self.hero.name:
            self.header.name_input.setText(self.hero.name)
        else:
            self.header.name_input.clear()
            
        class_str = ", ".join([f"{c} {l}" for c, l in self.hero.classes.items()])
        if not class_str:
            class_str = "Level 0 (Ready to Start)"
        self.header.class_level_display.setText(class_str)
        
        self.features_area.clear_features()
        for feat in self.hero.features:
            # Pass all arguments, including choices, to the GUI
            self.features_area.add_feature(
                feat["name"], 
                feat.get("source", ""),
                feat.get("description", ""),
                feat.get("uses", 0),
                feat.get("choices", [])
            )