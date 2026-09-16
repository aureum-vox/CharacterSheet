import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import CharacterSheetWindow
from data.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Initializing 5.5e Character Sheet Application...")
    
    # 1. Create the QApplication instance (required for any PyQt6 app)
    app = QApplication(sys.argv)
    
    # 2. Instantiate and show our main window
    window = CharacterSheetWindow()
    window.show()
    
    # 3. Start the application event loop
    logger.info("GUI event loop started.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()