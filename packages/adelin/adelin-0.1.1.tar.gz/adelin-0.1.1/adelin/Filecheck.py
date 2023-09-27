import os

class ADLFileChecker:
    """
    The ADLFileChecker class provides methods to check the existence of .adl files in the current directory.

    Attributes:
        directory (str): The current working directory as the default directory for file checks.

    Methods:
        is_exist(file_name): Checks if a specified .adl file exists in the current directory.
    """
    def __init__(self) -> None:
        """
        Initializes an instance of the ADLFileChecker class.

        Args:
            None
        """
        self.directory = os.getcwd()
        
    def is_exist(self, file_name: str) -> bool:
        """
        Checks if a specified .adl file exists in the current directory.

        Args:
            file_name (str): The name of the .adl file to be checked (with or without the .adl extension).

        Returns:
            bool: True if the file exists; otherwise, False.
        """
        if not file_name.endswith(".adl"):
            file_name = file_name + ".adl"        
        for root, dirs, files in os.walk(self.directory):
            if f"{file_name}" in files:
                return True
        return False

