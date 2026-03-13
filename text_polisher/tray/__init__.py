import platform


def create_tray(config, on_language_change, on_tone_change, on_quit):
    """Create the platform-appropriate tray icon."""
    if platform.system() == "Darwin":
        try:
            from text_polisher.tray.macos_tray import MacOSTray
            return MacOSTray(config, on_language_change, on_tone_change, on_quit)
        except ImportError:
            return None
    else:
        try:
            from text_polisher.tray.linux_tray import LinuxTray
            return LinuxTray(config, on_language_change, on_tone_change, on_quit)
        except ImportError:
            return None
