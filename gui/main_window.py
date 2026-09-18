from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QTabWidget
from gui.ability_widget import AbilityWidget
from gui.header_widget import HeaderWidget
from gui.features_widget import FeaturesWidget
from gui.level_up_dialog import LevelUpDialog, SubclassDialog
from gui.inventory_widget import InventoryWidget, AddItemDialog
from gui.stats_widget import StatsWidget
from gui.spells_widget import SpellsWidget 
from gui.subspecies_dialog import SubspeciesDialog

import re

# Import our Data Layer
from data.character import Character
from data.fetcher import get_2024_class_data

def parse_5e_text(entry):
    """Recursively extracts text from 5etools nested JSON structures."""
    if isinstance(entry, str):
        return entry
        
    if isinstance(entry, list):
        return "\n\n".join(parse_5e_text(e) for e in entry if e)
        
    if isinstance(entry, dict):
        text = ""
        if "name" in entry:
            text += f"{entry['name']}: "
            
        if "entries" in entry:
            text += parse_5e_text(entry["entries"])
        elif "items" in entry:
            items_text = "\n".join(f"  • {parse_5e_text(i)}" for i in entry["items"])
            text += "\n" + items_text
            
        return text.strip()
        
    return ""

class CharacterSheetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("5.5e Dynamic Character Sheet")
        self.setMinimumSize(1024, 768)
        
        self.hero = Character(name="")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.setup_left_column()
        self.setup_right_column()
        
        self.header.level_up_btn.clicked.connect(self.level_up_character)
        
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
        
        self.tabs = QTabWidget()
        
        # --- Tab 1: Features & Traits ---
        self.features_area = FeaturesWidget()
        self.tabs.addTab(self.features_area, "Features & Traits")

        # --- Tab 2: Stats, Saves & Skills ---
        self.stats_area = StatsWidget()
        self.tabs.addTab(self.stats_area, "Saves & Skills")
        
        self.stats_area.save_toggled.connect(self.toggle_save)
        self.stats_area.skill_toggled.connect(self.toggle_skill)
        
        # --- Tab 3: Inventory ---
        self.inventory_area = InventoryWidget()
        self.tabs.addTab(self.inventory_area, "Inventory")
        self.inventory_area.add_item_btn.clicked.connect(self.prompt_add_item)

        # --- Tab 4: Spells ---
        self.spells_area = SpellsWidget()
        self.tabs.addTab(self.spells_area, "Spells")
        
        # Connect Spell UI signals to the backend
        self.spells_area.spell_prepared.connect(self.prepare_spell)
        self.spells_area.slot_toggled.connect(self.toggle_spell_slot)
        self.spells_area.spell_unprepared.connect(self.unprepare_spell)
        
        self.right_column.addWidget(self.tabs)
        
        self.main_layout.addLayout(self.right_column)
        self.main_layout.setStretch(0, 1) 
        self.main_layout.setStretch(1, 5)

    def level_up_character(self):
        total_level = sum(self.hero.classes.values())
        is_first_level = (total_level == 0)
        
        dialog = LevelUpDialog(self, is_first_level=is_first_level)
        
        if not dialog.exec():
            return 
            
        selected_class = dialog.get_selected_class()
        selected_skills = dialog.get_selected_skills()
        
        species_name = None
        subspecies_name = None
        if is_first_level:
            new_name = dialog.get_character_name()
            self.hero.name = new_name if new_name else "Unknown Hero"
            species_name = dialog.get_selected_species() 

        species_with_subtypes = ["Goliath", "Dragonborn", "Elf", "Gnome", "Tiefling", "Aasimar"]
        
        if species_name in species_with_subtypes:
                sub_dialog = SubspeciesDialog(species_name, self)
                if sub_dialog.exec():
                    subspecies_name = sub_dialog.get_subspecies()
        
        class_data, feature_data = get_2024_class_data(f"class/class-{selected_class}.json")
        if not class_data:
            QMessageBox.critical(self, "Network Error", f"Failed to fetch {selected_class.capitalize()} data!")
            return
            
        class_name_formatted = selected_class.capitalize()
        current_class_level = self.hero.classes.get(class_name_formatted, 0)
        new_class_level = current_class_level + 1
        
        subclass_name = None
        if new_class_level == 3:
            subclass_dialog = SubclassDialog(class_name_formatted, self)
            if subclass_dialog.exec():
                subclass_name = subclass_dialog.get_subclass()
                
        self.hero.level_up_class(
            class_name_formatted, 
            selected_skills=selected_skills, 
            subclass_name=subclass_name,
            species_name=species_name, 
            subspecies_name=subspecies_name
        )
        new_level = self.hero.classes[class_name_formatted]
        
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
                    desc = "Description not found."
                    
                    for real_feat in feature_data:
                        if real_feat.get("name") == feature_name and str(real_feat.get("level")) == str(new_level):
                            entries = real_feat.get("entries", [])
                            raw_desc = parse_5e_text(entries)
                            desc = re.sub(r'\{@[^\s]+\s([^}|]+)[^}]*\}', r'\1', raw_desc)
                            break
                    
                    uses = 2 if feature_name in ["Second Wind", "Channel Divinity"] else 0
                    
                    choices = None
                    if feature_name == "Fighting Style":
                        choices = ["Archery", "Defense", "Dueling", "Great Weapon Fighting", "Protection", "Two-Weapon Fighting"]
                    elif feature_name == "Weapon Mastery":
                        choices = ["Cleave", "Graze", "Nick", "Push", "Sap", "Slow", "Topple", "Vex"]
                    
                    self.hero.add_feature(feature_name, "XPHB", description=desc, uses=uses, choices=choices)
                    
        self.update_ui()

    def prompt_add_item(self):
        dialog = AddItemDialog(self)
        if dialog.exec():
            name, qty, wt = dialog.get_data()
            self.hero.add_item(name, qty, wt)
            self.update_ui() 
    
    def update_ui(self):
        if self.hero.name:
            self.header.name_input.setText(self.hero.name)
        else:
            self.header.name_input.clear()
            
        # Build the class string
        class_strings = []
        for c, l in self.hero.classes.items():
            sub = self.hero.subclasses.get(c)
            if sub:
                class_strings.append(f"{sub} {c} {l}")
            else:
                class_strings.append(f"{c} {l}")
                
        class_str = ", ".join(class_strings)
        
        # --- NEW: Prepend Species ---
        if self.hero.species:
            class_str = f"{self.hero.species} {class_str}"
            
        if not class_str:
            class_str = "Level 0 (Ready to Start)"
        self.header.class_level_display.setText(class_str)
        
        self.features_area.clear_features()
        for feat in self.hero.features:
            self.features_area.add_feature(
                feat["name"], 
                feat.get("source", ""),
                feat.get("description", ""),
                feat.get("uses", 0),
                feat.get("choices", [])
            )

        self.header.update_hp(self.hero.current_hp, self.hero.hp_max, self.hero.get_hit_dice_string())
        self.stats_area.sync_data(self.hero)
        self.inventory_area.sync_data(self.hero.coins, self.hero.inventory)
        
        # --- NEW: Sync Spellbook Tab ---
        self.spells_area.sync_spellbook(self.hero)

    # --- ACTION HANDLERS ---
    def toggle_save(self, stat):
        self.hero.toggle_save_proficiency(stat)
        self.update_ui()
        
    def toggle_skill(self, skill):
        self.hero.toggle_skill_proficiency(skill)
        self.update_ui()

    def prepare_spell(self, spell_dict):
        self.hero.prepare_spell(spell_dict)
        self.update_ui()

    def toggle_spell_slot(self, level, is_pact):
        self.hero.toggle_spell_slot(level, pact_magic=is_pact)
        self.update_ui()
        
    def unprepare_spell(self, spell_name, level):
        self.hero.unprepare_spell(spell_name, level)
        self.update_ui()