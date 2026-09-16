from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

class HeaderWidget(QFrame):
    def __init__(self):
        super().__init__()
        
        # Give the header a subtle panel border
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        
        # Main horizontal layout for the header
        layout = QHBoxLayout(self)
        
        # --- 1. Character Name Section ---
        name_layout = QVBoxLayout()
        name_label = QLabel("CHARACTER NAME")
        
        # Make the sub-label small and bold
        small_bold = name_label.font()
        small_bold.setBold(True)
        small_bold.setPointSize(8)
        name_label.setFont(small_bold)
        
        # Editable text box for the name
        self.name_input = QLineEdit("Kael")
        name_font = self.name_input.font()
        name_font.setPointSize(14)
        name_font.setBold(True)
        self.name_input.setFont(name_font)
        
        name_layout.addWidget(self.name_input)
        name_layout.addWidget(name_label)
        
        # --- 2. Class & Level Section ---
        class_layout = QVBoxLayout()
        class_label = QLabel("CLASS & LEVEL")
        class_label.setFont(small_bold)
        
        # Read-only label for the class and level
        self.class_level_display = QLabel("Fighter 1")
        class_font = self.class_level_display.font()
        class_font.setPointSize(14)
        self.class_level_display.setFont(class_font)
        
        class_layout.addWidget(self.class_level_display)
        class_layout.addWidget(class_label)
        
        # --- 3. Level Up Button ---
        self.level_up_btn = QPushButton("Level Up")
        self.level_up_btn.setToolTip("Click to advance your character to the next level!")
        self.level_up_btn.setMinimumHeight(40) # Make it big and clickable
        # We will connect this button's click event to our Character class in Phase 4
        
        # --- Assembly ---
        layout.addLayout(name_layout)
        layout.addSpacing(20) # Add a little breathing room between sections
        layout.addLayout(class_layout)
        layout.addStretch() # Pushes the button all the way to the right
        layout.addWidget(self.level_up_btn)