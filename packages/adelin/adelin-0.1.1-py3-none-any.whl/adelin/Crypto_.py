import base64
from adelin  import Object_ as OB 
class EncryptDecrypt:
    """
    The EncryptDecrypt class provides methods for encrypting and decrypting data using Base64 encoding.

    Attributes:
        make_obj (MakeObj): An instance of the MakeObj class for JSON object manipulation.

    Methods:
        encrypt(key): Encrypts a dictionary and returns the encrypted data as bytes.
        decrypt(obje): Decrypts encrypted data and returns the original dictionary.
    """
    def __init__(self) -> None:
        """
        Initializes an instance of the EncryptDecrypt class.

        Args:
            None
        """
        self.make_obj = OB.MakeObj()               

    def encrypt(self, key: dict) -> bytes:
        """
        Encrypts a dictionary and returns the encrypted data as bytes.

        Args:
            key (dict): The dictionary to be encrypted.

        Returns:
            bytes: The encrypted data represented as bytes.
        """
        obj = base64.b64encode(self.make_obj.dumps(key).encode("utf-8"))
        return obj

    def decrypt(self, obje: bytes) -> dict:
        """
        Decrypts encrypted data and returns the original dictionary.

        Args:
            obje (bytes): The encrypted data represented as bytes.

        Returns:
            dict: The original dictionary after decryption.
        """
        obj = base64.b64decode(obje.decode("utf-8"))        
        data = self.make_obj.loads(obj)
        return data
