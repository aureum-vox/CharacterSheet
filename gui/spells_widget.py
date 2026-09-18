from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLineEdit, QComboBox, QTextEdit, QPushButton, 
                             QLabel, QSplitter, QTabWidget, QScrollArea, QCheckBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
import re
from data.fetcher import get_spell_data

def clean_5e_text(entry):
    """Recursively extracts and formats text from 5etools JSON, stripping metadata tags."""
    if isinstance(entry, str):
        # Strip 5etools tags like {@spell fireball} -> fireball
        return re.sub(r'\{@[^\s]+\s([^}|]+)[^}]*\}', r'\1', entry)
    if isinstance(entry, list):
        return "\n\n".join(clean_5e_text(e) for e in entry if e)
    if isinstance(entry, dict):
        text = ""
        if "name" in entry: text += f"{entry['name']}: "
        if "entries" in entry: text += clean_5e_text(entry["entries"])
        elif "items" in entry:
            items_text = "\n".join(f"  • {clean_5e_text(i)}" for i in entry["items"])
            text += "\n" + items_text
        return text.strip()
    return ""

class SpellsWidget(QWidget):
    # Signals for the main window to intercept
    spell_prepared = pyqtSignal(dict)
    slot_toggled = pyqtSignal(int, bool) # level, is_pact
    spell_unprepared = pyqtSignal(str, int) # spell_name, level

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # --- Internal Tabs ---
        self.inner_tabs = QTabWidget()
        self.library_tab = QWidget()
        self.spellbook_tab = QWidget()
        
        self.inner_tabs.addTab(self.library_tab, "Spell Library")
        self.inner_tabs.addTab(self.spellbook_tab, "My Spellbook")
        layout.addWidget(self.inner_tabs)

        # Load spell data (Auto-downloads to temp/spells-xphb.json if missing)
        self.all_spells = get_spell_data("temp/spells-xphb.json")
        self.current_spell = None
        
        self.setup_library()
        self.setup_spellbook() # <-- Replaced placeholder with the real layout!

    def setup_library(self):
        layout = QHBoxLayout(self.library_tab)
        
        # --- LEFT: Search & List ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Filters
        filter_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search spells...")
        self.search_bar.textChanged.connect(self.filter_spells)
        
        self.class_filter = QComboBox()
        self.class_filter.addItems(["All Classes", "Bard", "Cleric", "Druid", "Paladin", "Ranger", "Sorcerer", "Warlock", "Wizard"])
        self.class_filter.currentTextChanged.connect(self.filter_spells)
        
        self.level_filter = QComboBox()
        self.level_filter.addItems(["All Levels", "Cantrip", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9"])
        self.level_filter.currentTextChanged.connect(self.filter_spells)
        
        filter_layout.addWidget(self.search_bar)
        filter_layout.addWidget(self.class_filter)
        filter_layout.addWidget(self.level_filter)
        left_layout.addLayout(filter_layout)
        
        # List
        self.spell_list = QListWidget()
        self.spell_list.itemSelectionChanged.connect(self.display_spell)
        left_layout.addWidget(self.spell_list)
        
        # --- RIGHT: Preview Pane ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.spell_title = QLabel("Select a spell to view")
        font = self.spell_title.font()
        font.setBold(True)
        font.setPointSize(14)
        self.spell_title.setFont(font)
        
        self.spell_meta = QLabel("Level • School • Casting Time • Range")
        self.spell_desc = QTextEdit()
        self.spell_desc.setReadOnly(True)
        
        self.prepare_btn = QPushButton("Learn / Prepare Spell")
        self.prepare_btn.setMinimumHeight(40)
        self.prepare_btn.setEnabled(False)
        self.prepare_btn.clicked.connect(self.emit_prepare)
        
        right_layout.addWidget(self.spell_title)
        right_layout.addWidget(self.spell_meta)
        right_layout.addWidget(self.spell_desc)
        right_layout.addWidget(self.prepare_btn)
        
        # Splitter allows user to resize the left/right columns
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 450])
        
        layout.addWidget(splitter)
        self.filter_spells() # Populate initially

    def setup_spellbook(self):
        """Builds the layout for tracking slots and prepared spells."""
        layout = QVBoxLayout(self.spellbook_tab)
        
        self.spellbook_scroll = QScrollArea()
        self.spellbook_scroll.setWidgetResizable(True)
        self.spellbook_content = QWidget()
        self.spellbook_layout = QVBoxLayout(self.spellbook_content)
        self.spellbook_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.spellbook_scroll.setWidget(self.spellbook_content)
        layout.addWidget(self.spellbook_scroll)

    def filter_spells(self):
        query = self.search_bar.text().lower().strip()
        cls_filter = self.class_filter.currentText().lower().strip() 
        lvl_filter = self.level_filter.currentText()
        
        self.spell_list.clear()
        
        for spell in self.all_spells:
            # Check Level
            if lvl_filter != "All Levels":
                if lvl_filter == "Cantrip" and spell["level"] != 0: continue
                if lvl_filter.startswith("Level ") and str(spell["level"]) != lvl_filter.split(" ")[1]: continue
            
            # Check Class (Safely strip all whitespace)
            if cls_filter != "all classes":
                safe_classes = [str(c).lower().strip() for c in spell.get("classes", [])]
                if cls_filter not in safe_classes: 
                    continue
            
            # Check Name
            if query and query not in spell["name"].lower(): continue
            
            self.spell_list.addItem(spell["name"])

    def display_spell(self):
        selected = self.spell_list.currentItem()
        if not selected: return
        
        spell_name = selected.text()
        spell = next((s for s in self.all_spells if s["name"] == spell_name), None)
        
        if spell:
            self.current_spell = spell
            self.spell_title.setText(spell["name"])
            
            lvl_text = "Cantrip" if spell["level"] == 0 else f"Level {spell['level']}"
            self.spell_meta.setText(f"<b>{lvl_text}</b> | {spell['school']} | {spell['casting_time']} | {spell['range']}")
            
            clean_desc = clean_5e_text(spell["entries"])
            self.spell_desc.setText(clean_desc)
            
            self.prepare_btn.setEnabled(True)

    def emit_prepare(self):
        if self.current_spell:
            self.spell_prepared.emit(self.current_spell)
            # Switch the UI over to the Spellbook tab automatically
            self.inner_tabs.setCurrentIndex(1)

    def sync_spellbook(self, character):
        """Clears and rebuilds the spellbook UI based on the character's backend state."""
        # 1. Clear existing UI elements
        for i in reversed(range(self.spellbook_layout.count())): 
            widget = self.spellbook_layout.itemAt(i).widget()
            if widget: 
                widget.setParent(None)
                widget.deleteLater()

        # 2. Render Warlock Pact Magic (if applicable)
        if character.pact_slots[0] > 0:
            self._build_slot_row("Pact Magic", character.pact_level, character.pact_slots, is_pact=True)

        # 3. Render Cantrips
        if character.spells.get(0):
            lbl = QLabel("<b>Cantrips</b>")
            self.spellbook_layout.addWidget(lbl)
            self._build_spell_list(0, character.spells[0])

        # 4. Render Standard Leveled Spells (1-9)
        for lvl in range(1, 10):
            has_slots = lvl in character.spell_slots and character.spell_slots[lvl][0] > 0
            has_spells = len(character.spells.get(lvl, [])) > 0
            
            if has_slots or has_spells:
                # Slot Tracker Row
                if has_slots:
                    self._build_slot_row(f"Level {lvl} Slots", lvl, character.spell_slots[lvl], is_pact=False)
                elif has_spells:
                    # If they have spells but no slots (e.g., racial spells), just show a header
                    lbl = QLabel(f"<b>Level {lvl} Spells</b>")
                    self.spellbook_layout.addWidget(lbl)
                    
                # Spells List
                if has_spells:
                    self._build_spell_list(lvl, character.spells[lvl])
                    
                # Add a divider line between levels for visual clarity
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Sunken)
                self.spellbook_layout.addWidget(line)

    def _build_slot_row(self, title, level, slot_data, is_pact):
        max_slots, current = slot_data
        row = QHBoxLayout()
        lbl = QLabel(f"<b>{title}:</b>")
        row.addWidget(lbl)
        
        # Build interactive checkboxes for slots
        for i in range(max_slots):
            cb = QCheckBox()
            # If current slots is 3, boxes 0, 1, 2 are checked
            cb.setChecked(i < current) 
            cb.clicked.connect(lambda checked, l=level, p=is_pact: self.slot_toggled.emit(l, p))
            row.addWidget(cb)
            
        row.addStretch()
        container = QWidget()
        container.setLayout(row)
        self.spellbook_layout.addWidget(container)

    def _build_spell_list(self, level, spells):
        for spell in spells:
            row = QHBoxLayout()
            row.setContentsMargins(15, 0, 0, 0) # Indent spells slightly
            
            # Base spell label
            label_text = f"• {spell['name']} <i>({spell['casting_time']})</i>"
            
            # Check for our backend locks!
            is_locked = spell.get("always_prepared", False)
            source = spell.get("source_feature", "")
            
            # If it's a domain/species spell, add a nice blue badge
            if is_locked and source:
                label_text += f" &nbsp;<span style='color: #2980b9; font-weight: bold;'>[{source}]</span>"
            elif is_locked:
                label_text += f" &nbsp;<span style='color: #2980b9; font-weight: bold;'>[Always Prepared]</span>"
                
            name_lbl = QLabel(label_text)
            name_lbl.setTextFormat(Qt.TextFormat.RichText) # Ensure HTML renders
            row.addWidget(name_lbl)
            
            # Only generate the Remove button if the spell IS NOT locked
            if not is_locked:
                remove_btn = QPushButton("X")
                remove_btn.setFixedSize(20, 20)
                remove_btn.setStyleSheet("color: red; font-weight: bold; border: none;")
                remove_btn.setToolTip("Unprepare Spell")
                remove_btn.clicked.connect(lambda checked, s=spell['name'], l=level: self.spell_unprepared.emit(s, l))
                row.addWidget(remove_btn)
                
            row.addStretch()
            
            container = QWidget()
            container.setLayout(row)
            self.spellbook_layout.addWidget(container)