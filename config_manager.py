import os
import configparser


CONFIG_FILE = "config.ini"

DEFAULTS = {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": "587",
    "sender_email": "",
    "app_password": "",
    "recipient": "",
}


def load_config():
    """Load email config from config.ini next to the executable."""
    # Support running from PyInstaller bundle
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, CONFIG_FILE)

    cfg = configparser.ConfigParser()
    cfg.read(config_path)

    result = dict(DEFAULTS)
    if cfg.has_section("EMAIL"):
        for key in DEFAULTS:
            if cfg.has_option("EMAIL", key):
                result[key] = cfg.get("EMAIL", key).strip()

    return result


def save_config(values: dict):
    """Save updated config back to config.ini, preserving other sections."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, CONFIG_FILE)

    cfg = configparser.ConfigParser()
    cfg.read(config_path)          # preserve existing sections
    cfg["EMAIL"] = values
    with open(config_path, "w") as f:
        cfg.write(f)


def is_configured(config: dict) -> bool:
    required = ["sender_email", "app_password", "recipient"]
    return all(config.get(k) for k in required)