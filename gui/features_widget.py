from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QScrollArea, QWidget
from PyQt6.QtCore import Qt

class FeaturesWidget(QFrame):
    def __init__(self):
        super().__init__()
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        
        main_layout = QVBoxLayout(self)
        
        # 1. Section Title
        title_label = QLabel("FEATURES & TRAITS")
        font = title_label.font()
        font.setBold(True)
        font.setPointSize(12)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(title_label)
        
        # 2. The Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # Ensures the inner widget stretches to fit
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # 3. The Inner Container (Holds the actual feature items)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Stack from top to bottom
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
    def add_feature(self, feature_name, source=""):
        """Adds a new formatted feature to the scrollable list."""
        # Using basic HTML to make the name bold and source italicized
        text = f"• <b>{feature_name}</b>"
        if source:
            text += f" <i>({source})</i>"
            
        feature_label = QLabel(text)
        feature_label.setWordWrap(True) # Wraps long text so it doesn't break the layout
        
        self.scroll_layout.addWidget(feature_label)
        
    def clear_features(self):
        """Clears all features from the list (useful for refreshing the UI)."""
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()