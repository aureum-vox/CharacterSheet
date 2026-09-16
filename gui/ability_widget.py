from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSpinBox
from PyQt6.QtCore import Qt

class AbilityWidget(QFrame):
    def __init__(self, name):
        super().__init__()
        
        # Give the widget a visible box border
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        # Stack elements vertically
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 1. Ability Name (e.g., "STR")
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.name_label.font()
        font.setBold(True)
        self.name_label.setFont(font)
        
        # 2. Modifier Display (Large Text)
        self.mod_label = QLabel("+0")
        self.mod_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mod_font = self.mod_label.font()
        mod_font.setPointSize(16)
        mod_font.setBold(True)
        self.mod_label.setFont(mod_font)
        
        # 3. Base Score Input (SpinBox allows clicking up/down arrows)
        self.score_spinbox = QSpinBox()
        self.score_spinbox.setRange(1, 30)
        self.score_spinbox.setValue(10)
        self.score_spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Connect the spinbox value change to our local update method
        self.score_spinbox.valueChanged.connect(self.update_modifier)
        
        # Add widgets to the layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.mod_label)
        layout.addWidget(self.score_spinbox)

    def update_modifier(self, score):
        """Mock logic: dynamically updates the modifier label when the score changes."""
        mod = (score - 10) // 2
        sign = "+" if mod >= 0 else ""
        self.mod_label.setText(f"{sign}{mod}")