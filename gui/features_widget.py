from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget, QCheckBox, QComboBox, QSizePolicy
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
        self.scroll_area.setWidgetResizable(True) 
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # 3. Inner Container
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
    def add_feature(self, feature_name, source="", description="", uses=0, choices=None):
        """Adds a new feature container with a header row and an inline description block."""
        
        # --- MAIN CONTAINER (Vertical) ---
        feature_container = QWidget()
        container_layout = QVBoxLayout(feature_container)
        container_layout.setContentsMargins(0, 0, 0, 15) # Adds breathing room between features
        
        # --- 1. HEADER ROW (Horizontal) ---
        header_row = QWidget()
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Name Label
        text = f"• <b>{feature_name}</b>"
            
        feature_label = QLabel(text)
        feature_label.setMinimumWidth(150)
        header_layout.addWidget(feature_label)
        
        # Selectable Dropdown (QComboBox)
        if choices:
            dropdown = QComboBox()
            dropdown.addItems(choices)
            dropdown.insertItem(0, f"Select a {feature_name}...") 
            dropdown.setCurrentIndex(0)
            header_layout.addWidget(dropdown)
        
        header_layout.addStretch()
        
        # Uses Checkboxes
        if uses > 0:
            for _ in range(uses):
                checkbox = QCheckBox()
                checkbox.setText("") 
                header_layout.addWidget(checkbox)
                
        # Add the header row to the main container
        container_layout.addWidget(header_row)
        
        # --- 2. DESCRIPTION BLOCK ---
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            # Indent the text slightly so it visually nests under the bullet point
            desc_label.setContentsMargins(15, 5, 0, 0)
            # Optional: Make the font slightly smaller or distinct if you prefer
            # font = desc_label.font()
            # font.setPointSize(9)
            # desc_label.setFont(font)
            
            container_layout.addWidget(desc_label)
            
        # Finally, add the completed feature block to the scrollable area
        self.scroll_layout.addWidget(feature_container)
        
    def clear_features(self):
        """Clears all features from the list."""
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()