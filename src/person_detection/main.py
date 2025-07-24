"""Main entry point for the Person Detection application."""

import sys
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Initialize models when actually needed by UI
    from .core.models import model_manager
    print("Initializing models...")
    model_manager.initialize()
    
    # Create and run the application
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())