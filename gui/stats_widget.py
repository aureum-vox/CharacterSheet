from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal

class ClickableLabel(QLabel):
    """A custom label that emits its key/name when clicked."""
    clicked = pyqtSignal(str)
    
    def __init__(self, key, text=""):
        super().__init__(text)
        self.key = key
        # Change the mouse cursor to a pointing hand on hover
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.key)
        super().mousePressEvent(event)

class StatsWidget(QFrame):
    # Signals that tell the main window when a label is clicked
    save_toggled = pyqtSignal(str)
    skill_toggled = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        main_layout = QVBoxLayout(self)
        
        # --- 1. CORE STATS ---
        title_label = QLabel("CORE STATS")
        font = title_label.font()
        font.setBold(True)
        font.setPointSize(10)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        grid_layout = QGridLayout()
        self.stat_labels = {}
        stats = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        
        for i, stat in enumerate(stats):
            box = QWidget()
            box_layout = QVBoxLayout(box)
            name_lbl = QLabel(stat)
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl = QLabel("+0\n(10)")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            box_layout.addWidget(name_lbl)
            box_layout.addWidget(val_lbl)
            grid_layout.addWidget(box, 0, i)
            self.stat_labels[stat] = val_lbl
            
        main_layout.addLayout(grid_layout)
        main_layout.addSpacing(15)
        
        # --- 2. SAVING THROWS ---
        saves_label = QLabel("SAVING THROWS")
        saves_label.setFont(font)
        main_layout.addWidget(saves_label)
        
        saves_layout = QGridLayout()
        self.save_labels = {}
        for i, stat in enumerate(stats):
            lbl = ClickableLabel(stat, f"○ +0  {stat}")
            lbl.clicked.connect(self.save_toggled.emit) # Hook up the click!
            saves_layout.addWidget(lbl, i // 3, i % 3)
            self.save_labels[stat] = lbl
            
        main_layout.addLayout(saves_layout)
        main_layout.addSpacing(15)
        
        # --- 3. SKILLS ---
        skills_label = QLabel("SKILLS")
        skills_label.setFont(font)
        main_layout.addWidget(skills_label)
        
        skills_layout = QGridLayout()
        self.skill_labels = {}
        skills = [
            "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", 
            "History", "Insight", "Intimidation", "Investigation", "Medicine", 
            "Nature", "Perception", "Performance", "Persuasion", "Religion", 
            "Sleight of Hand", "Stealth", "Survival"
        ]
        
        for i, skill in enumerate(skills):
            lbl = ClickableLabel(skill, f"○ +0  {skill}")
            lbl.clicked.connect(self.skill_toggled.emit) # Hook up the click!
            skills_layout.addWidget(lbl, i // 2, i % 2)
            self.skill_labels[skill] = lbl
            
        main_layout.addLayout(skills_layout)
        main_layout.addStretch()

    def sync_data(self, character):
        # 1. Sync Core Stats
        for stat, label in self.stat_labels.items():
            score = character.abilities.get(stat, 10)
            mod = character.get_modifier(stat)
            mod_str = f"+{mod}" if mod >= 0 else str(mod)
            label.setText(f"<b>{mod_str}</b><br>({score})")
            
        # 2. Sync Saving Throws
        for stat, label in self.save_labels.items():
            mod = character.get_save_modifier(stat)
            mod_str = f"+{mod}" if mod >= 0 else str(mod)
            prof_marker = "●" if stat in character.saving_throw_proficiencies else "○"
            label.setText(f"{prof_marker} <b>{mod_str}</b>  {stat}")
            
        # 3. Sync Skills
        for skill, label in self.skill_labels.items():
            mod = character.get_skill_modifier(skill)
            mod_str = f"+{mod}" if mod >= 0 else str(mod)
            prof_marker = "●" if skill in character.skill_proficiencies else "○"
            label.setText(f"{prof_marker} <b>{mod_str}</b>  {skill}")