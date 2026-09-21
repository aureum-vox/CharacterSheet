from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QListWidget
from PyQt6.QtCore import Qt

class LevelUpDialog(QDialog):
    def __init__(self, parent=None, is_first_level=False, hero=None):
        super().__init__(parent)
        
        self.setWindowTitle("Level Up")
        
        # --- Make the window taller at Level 1 to fit the skill list and species ---
        self.setFixedSize(300, 520 if is_first_level else 150)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout(self)
        self.is_first_level = is_first_level
        self.hero = hero
        
        # --- 1. Level 1 Setup (Name, Species & Skills) ---
        if self.is_first_level:
            name_label = QLabel("Enter Character Name:")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(name_label)
            
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("e.g. Drizzt Do'Urden")
            layout.addWidget(self.name_input)
            layout.addSpacing(10)
            
            # --- NEW: Species Selector ---
            species_label = QLabel("Select Species:")
            species_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(species_label)
            
            self.species_combo = QComboBox()
            # The 10 core Species in the 2024 Player's Handbook
            self.species_combo.addItems([
                "Aasimar", "Dragonborn", "Dwarf", "Elf", "Gnome", 
                "Goliath", "Halfling", "Human", "Orc", "Tiefling"
            ])
            layout.addWidget(self.species_combo)
            layout.addSpacing(10)
            # -----------------------------
            
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

        self.subclass_label = QLabel("Select Subclass:")
        self.subclass_dropdown = QComboBox()
        self.subclass_label.hide()
        self.subclass_dropdown.hide()
        
        # Assuming you have a form layout or main layout, add these widgets:
        layout.addWidget(self.subclass_label)
        layout.addWidget(self.subclass_dropdown)
        
        # Connect the class dropdown to check if we hit Level 3
        # (Make sure self.class_dropdown is the name of your class QComboBox!)
        self.class_dropdown.currentTextChanged.connect(self.check_subclass_eligibility)
        
        # --- 3. Buttons ---
        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("Confirm")
        self.cancel_btn = QPushButton("Cancel")
        
        self.confirm_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(btn_layout)
        self.check_subclass_eligibility()
        
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

    def get_selected_species(self):
            """Returns the chosen species if it was selected, otherwise None."""
            if hasattr(self, 'species_combo'):
                return self.species_combo.currentText()
            return None

    def check_subclass_eligibility(self):
        """Checks if the chosen class is hitting Level 3 and reveals the subclass dropdown."""
        if not self.hero:
            return
            
        selected_class = self.class_dropdown.currentText().strip()
        current_level = self.hero.classes.get(selected_class, 0)
        projected_level = current_level + 1

        # In 2024 rules, all subclasses unlock at Level 3
        if projected_level == 3:
            self.subclass_label.show()
            self.subclass_dropdown.show()
            self.subclass_dropdown.clear()
            
            subclasses = self._get_2024_subclasses(selected_class)
            self.subclass_dropdown.addItems(subclasses)
        else:
            self.subclass_label.hide()
            self.subclass_dropdown.hide()

    def _get_2024_subclasses(self, class_name):
        """Returns the PHB 2024 subclasses for the given class."""
        subclass_map = {
            "Barbarian": ["Path of the Berserker", "Path of the Wild Heart", "Path of the World Tree", "Path of the Zealot"],
            "Bard": ["College of Dance", "College of Glamour", "College of Lore", "College of Valor"],
            "Cleric": ["Life Domain", "Light Domain", "Trickery Domain", "War Domain"],
            "Druid": ["Circle of the Land", "Circle of the Moon", "Circle of the Sea", "Circle of the Stars"],
            "Fighter": ["Battle Master", "Champion", "Eldritch Knight", "Psi Warrior"],
            "Monk": ["Warrior of Mercy", "Warrior of Shadow", "Warrior of the Elements", "Warrior of the Open Hand"],
            "Paladin": ["Oath of Devotion", "Oath of Glory", "Oath of the Ancients", "Oath of Vengeance"],
            "Ranger": ["Beast Master", "Fey Wanderer", "Gloom Stalker", "Hunter"],
            "Rogue": ["Arcane Trickster", "Assassin", "Soulknife", "Thief"],
            "Sorcerer": ["Aberrant Sorcery", "Clockwork Sorcery", "Draconic Sorcery", "Wild Magic Sorcery"],
            "Warlock": ["Archfey Patron", "Celestial Patron", "Fiend Patron", "Great Old One Patron"],
            "Wizard": ["Abjurer", "Diviner", "Evoker", "Illusionist"]
        }
        return subclass_map.get(class_name, ["Standard Subclass"])

    def get_selected_subclass(self):
        """Returns the subclass if the dropdown is visible, otherwise None."""
        if self.subclass_dropdown.isVisible():
            return self.subclass_dropdown.currentText()
        return None

class SubclassDialog(QDialog):
    """Pops up when a character reaches Level 3 in a class."""
    
    SUBCLASSES_2024 = {
        "Barbarian": ["Path of the Berserker", "Path of the Wild Heart", "Path of the World Tree", "Path of the Zealot"],
        "Bard": ["College of Dance", "College of Glamour", "College of Lore", "College of Valor"],
        "Cleric": ["Life Domain", "Light Domain", "Trickery Domain", "War Domain"],
        "Druid": ["Circle of the Land", "Circle of the Moon", "Circle of the Sea", "Circle of the Stars"],
        "Fighter": ["Battle Master", "Champion", "Eldritch Knight", "Psi Warrior"],
        "Monk": ["Warrior of Mercy", "Warrior of Shadow", "Warrior of the Elements", "Warrior of the Open Hand"],
        "Paladin": ["Oath of Devotion", "Oath of Glory", "Oath of the Ancients", "Oath of Vengeance"],
        "Ranger": ["Beast Master", "Fey Wanderer", "Gloom Stalker", "Hunter"],
        "Rogue": ["Arcane Trickster", "Assassin", "Soulknife", "Thief"],
        "Sorcerer": ["Aberrant Sorcery", "Clockwork Sorcery", "Draconic Sorcery", "Wild Magic Sorcery"],
        "Warlock": ["Archfey Patron", "Celestial Patron", "Fiend Patron", "Great Old One Patron"],
        "Wizard": ["Abjurer", "Diviner", "Evoker", "Illusionist"]
    }

    def __init__(self, class_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{class_name} Subclass")
        self.setFixedSize(300, 150)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout(self)
        
        lbl = QLabel(f"Level 3 Reached!\nChoose your {class_name} subclass:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        
        self.dropdown = QComboBox()
        subclasses = self.SUBCLASSES_2024.get(class_name, ["Default Subclass"])
        self.dropdown.addItems(subclasses)
        layout.addWidget(self.dropdown)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Confirm")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)

    def get_subclass(self):
        return self.dropdown.currentText()

class BackgroundDialog(QDialog):
    """Pops up during Level 1 character creation to fully customize the background."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Background Setup")
        self.setFixedSize(350, 250)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout(self)
        
        # 1. Background Name
        layout.addWidget(QLabel("Background Name (e.g. Mercenary, Chef):"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Custom Background")
        layout.addWidget(self.name_input)
        
        layout.addSpacing(10)
        
        # 2. Origin Feat
        layout.addWidget(QLabel("Select Origin Feat:"))
        self.feat_combo = QComboBox()
        self.feat_combo.addItems([
            "Alert", "Crafter", "Healer", "Lucky", "Magic Initiate", 
            "Musician", "Savage Attacker", "Skilled", "Tavern Brawler", "Tough"
        ])
        layout.addWidget(self.feat_combo)
        
        layout.addSpacing(10)
        
        # 3. Ability Score Increases
        layout.addWidget(QLabel("Ability Score Increases:"))
        asi_layout = QHBoxLayout()
        
        self.plus2_combo = QComboBox()
        self.plus1_combo = QComboBox()
        stats = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        
        self.plus2_combo.addItems(stats)
        self.plus1_combo.addItems(stats)
        self.plus1_combo.setCurrentIndex(1) # Default to DEX so they start different
        
        asi_layout.addWidget(QLabel("+2 to:"))
        asi_layout.addWidget(self.plus2_combo)
        asi_layout.addStretch()
        asi_layout.addWidget(QLabel("+1 to:"))
        asi_layout.addWidget(self.plus1_combo)
        
        layout.addLayout(asi_layout)
        layout.addSpacing(15)
        
        # 4. Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Confirm Background")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)

    def get_background_data(self):
        """Returns a dictionary of the user's custom background choices."""
        bg_name = self.name_input.text().strip()
        if not bg_name:
            bg_name = "Custom Background"
            
        return {
            "name": bg_name,
            "feat": self.feat_combo.currentText(),
            "plus_2": self.plus2_combo.currentText(),
            "plus_1": self.plus1_combo.currentText()
        }
    