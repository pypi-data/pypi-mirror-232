import json
from typing import Union
    
class MakeObj:
    """
    The MakeObj class is used for creating and processing JSON objects.
    
    Attributes:
        None
    
    Methods:
        dumps(obje): Serializes a JSON object to a string.
        loads(obje): Deserializes a JSON string to a Python dictionary or list.
    """
    def __init__(self) -> None:
        pass

    def dumps(self, obje) -> str:
        """
        Serializes the given JSON object to a string.
        
        Args:
            obje: The JSON object to be converted to a string.
        
        Returns:
            str: The JSON data serialized into a string.
        """        
        obj = json.dumps(obje,  indent=2) 
        return obj

    def loads(self, obje: Union[bytes, str]) -> dict:
        """
        Deserializes the given JSON string into a Python dictionary or list.
        
        Args:
            obje (Union[bytes, str]): The JSON string to be deserialized (bytes or str).
        
        Returns:
            dict: The Python dictionary or list deserialized from the JSON string.
        """        
        obj = json.loads(obje)
        return obj

