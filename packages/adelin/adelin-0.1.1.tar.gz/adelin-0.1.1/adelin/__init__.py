
from datetime import datetime
import uuid
from adelin import Filecheck as FC
from adelin import Readwrite as RW
from adelin  import DB_Tools as DB



class InvalidInputError(Exception):
    """invalid input in the inherit Object."""
    pass

class MakeData:
    def __init__(self, *args, id = False, date = False, column_up = False) -> None:
        self.now = datetime.now()
        self.fileexist = FC.ADLFileChecker()
        self.rw_file = RW.RW_File()
        self.tools = DB.Tools()       
        self.row = args
        self.DB = {}
        self.id = id
        self.date = date
        self.column_up = column_up
        


    def  __call__(self, column:str ,*args) -> None:

        if self.id:
            if not "Id" in self.row:
                self.row += ("Id",) 
            args += (str(uuid.uuid1())[:8],)
            
        if self.date:
            if not "Date" in self.row:
                self.row += ("Date",)
            args += (self.now.strftime("%d/%m/%Y"),)

        if self.column_up:
            column = column.upper()  
        
        if len(self.row) == len(args):
            
            self.DB.setdefault(column,[])
            self.DB[column].append(dict(zip(self.row, args))) 
        else:
            error_msg = (f"*** invalid input in the inherit object. ***")
            raise InvalidInputError(error_msg)

   
    def save_db(self, folder_name:str, file_name:str) -> None:
        if self.fileexist.is_exist(file_name):
            temp_db = self.read_db(folder_name ,file_name)         
            for key in self.DB.keys():            
                if key in temp_db.keys():
                    for i in range(len(self.DB[key])):
                        temp_db[key].append(self.DB[key][i])            
                else:
                    for _ in range(len(self.DB[key])):
                        temp_db[key] = self.DB[key]
            self.rw_file.save_with_encrypt(file_name, folder_name, temp_db)
            self.DB.clear()
        else:        
            self.rw_file.save_with_encrypt(file_name, folder_name, self.DB)
            self.DB.clear()

    def read_db(self, folder_name:str, file_name:str) -> dict:        
        return self.rw_file.read_with_encrypt(file_name, folder_name)
    
    def del_with_id(self, folder_name:str, file_name:str, id_to_delete) -> None:
        self.tools.del_with_id(folder_name, file_name, id_to_delete)

    def fetchdata(self, folder_name:str, file_name:str,column, *args) -> list:
        result = self.tools.fetchdata(folder_name, file_name, column, *args)
        return result



