from adelin  import Crypto_ as EN
import os

class RW_File:
    """
    The RW_File class provides methods for saving and reading encrypted data to/from files.

    Attributes:
        secretobj (EncryptDecrypt): An instance of the EncryptDecrypt class for data encryption and decryption.
        file_path (str): The current working directory as the default file path.

    Methods:
        save_with_encrypt(file_name, folder_name, keyx): Saves data with encryption to a file.
        read_with_encrypt(file_name, folder_name): Reads and decrypts data from a file.
    """
    def __init__(self) -> None:
        """
        Initializes an instance of the RW_File class.

        Args:
            None
        """
        self.secretobj = EN.EncryptDecrypt()
        self.file_path = os.getcwd()

    def save_with_encrypt(self, file_name: str, folder_name: str, keyx: dict) -> None:
        """
        Saves data with encryption to a file.

        Args:
            file_name (str): The name of the file to be saved (without extension).
            folder_name (str): The name of the folder where the file will be saved.
            keyx (dict): The data to be encrypted and saved.

        Returns:
            None
        """
        full_file_path = os.path.join(self.file_path, f"{folder_name}", file_name + ".adl")
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
        with open(full_file_path, "wb") as file:
            file.write(self.secretobj.encrypt(keyx))

    def read_with_encrypt(self, file_name: str, folder_name: str) -> dict:
        """
        Reads and decrypts data from a file.

        Args:
            file_name (str): The name of the file to be read (without extension).
            folder_name (str): The name of the folder where the file is located.

        Returns:
            dict: The decrypted data read from the file.
        """
        full_file_path = os.path.join(self.file_path, f"{folder_name}", file_name + ".adl")
        if os.path.exists(full_file_path):
            with open(full_file_path, "rb") as file:
                datareaded = self.secretobj.decrypt(file.read())
            return datareaded
