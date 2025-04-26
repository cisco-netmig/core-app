# __main__.py

import platform
import ctypes
import sys
import importlib
import os
import ui
import utils
import logging


def main():
    """
    Entry point of the application.

    This function sets up the runtime environment, initializes key directories and templates,
    registers core components, and launches the PyQt5 GUI application.
    """

    logging.info("Netmig application starting...")

    # Set application ID on Windows for proper taskbar grouping
    if platform.system() == 'Windows':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            f'cisco.netmig.{__file__}'
        )
        logging.debug("Set Windows AppUserModelID for taskbar grouping.")

    # Change working directory to script location
    os.chdir(os.path.dirname(__file__))
    logging.debug("Working directory set to script location.")

    # Register utils & ui modules globally via sys.modules
    sys.modules['utils'] = utils
    sys.modules['ui'] = ui
    logging.debug("Registered 'utils' and 'ui' modules in sys.modules.")

    # Initialize the custom QApplication subclass
    app = ui.Application(sys.argv)
    logging.debug("Initialized QApplication instance.")

    # Start telemetry agent
    app.start_telemetry_agent()

    # Attach registry to app instance
    app.registry = utils.Registry(utils.PATH_USER_DIR)
    logging.info("Registry initialized and attached to application.")

    # Register paths for settings, sessions, and cache data
    app.registry.register('settings')
    app.registry.register('sessions')
    app.registry.register('cache')
    logging.debug("Core paths registered in registry.")

    # Apply theme and UI styling
    app.set_styling()
    logging.info("Application styling applied.")

    # Load and display the splash screen
    app.load_splash()
    logging.info("Splash screen loaded.")

    # Load and display the main application window
    app.load_mainwindow()
    logging.debug("Main window loaded.")

    logging.debug("Starting Qt event loop.")
    # Start the event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
