import configparser
from pathlib import Path
from getpass import getpass
from cryptography.fernet import Fernet  # for secure password storage

CONFIG_FILE = Path("~/.alxconfig").expanduser()
KEY_FILE = Path("~/.alxkey").expanduser()

def load_config():
    """Load the configuration from the config file.

    Returns:
        configparser.ConfigParser: A ConfigParser object containing the loaded configuration.
    """
    config = configparser.ConfigParser()

    if not CONFIG_FILE.exists():
        config.add_section("user")

        with CONFIG_FILE.open("w", encoding="utf-8") as config_file:
            config.write(config_file)    
    
    config.read(CONFIG_FILE)
    return config

def save_config(config):
    """Save the configuration to the config file.

    Args:
        config (configparser.ConfigParser): The ConfigParser object containing the configuration to be saved.
    """
    with CONFIG_FILE.open("w", encoding="utf-8") as config_file:
        config.write(config_file)

def configure_email(config):
    """Configure the user's email in the configuration.

    Args:
        config (configparser.ConfigParser): The ConfigParser object to store the email configuration.
    """
    user_email: str = input("Email: ")

    config["user"]["email"] = user_email
    save_config(config)

def get_email() -> str:
    """Retrieve the user's email from the configuration.

    Returns:
        str: The user's email.
    """
    config = load_config()

    if config and "user" in config and "email" in config["user"]:
        user_email: str = config["user"]["email"]

    else:
        print("error occured while getting email")

    return user_email

def configure_password(config):
    """Configure the user's password in the configuration.

    Args:
        config (configparser.ConfigParser): The ConfigParser object to store the encrypted password.
    """
    key = Fernet.generate_key()
    fernet = Fernet(key)
    password = getpass()
    encrypted_password = fernet.encrypt(password.encode())
    config["user"]["password"] = encrypted_password.decode()
    
    with KEY_FILE.open("wb") as key_file:
        key_file.write(key)

    save_config(config)

def get_password() -> str:
    """Retrieve the user's password from the configuration.

    Returns:
        str: The user's password (decrypted).
    """
    if KEY_FILE.exists():
        with KEY_FILE.open("rb") as key_file:
            key = key_file.read()

        fernet = Fernet(key)
        config = load_config()

        if config and "user" in config and "password" in config["user"]:
            encrypted_password = config["user"]["password"]
            decrypted_password = fernet.decrypt(encrypted_password.encode())
            
            user_password = decrypted_password.decode()

    else:
        print("error occured while getting password")

    return user_password
