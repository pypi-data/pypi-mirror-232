from adelin import Readwrite as RW


class Tools:
    def __init__(self) -> None:
        self.rw_file = RW.RW_File()

    def del_with_id(self, folder_name: str, file_name: str, id_to_delete: str):
        temp_db = self.rw_file.read_with_encrypt(file_name, folder_name) 
        new_temp_db = {}
        for key, value in temp_db.items():
            new_value = []
            for item in value:
                if "Id" in item and item["Id"] == id_to_delete:                    
                    continue
                new_value.append(item)            
            if new_value:                
                new_temp_db[key] = new_value
        self.rw_file.save_with_encrypt(file_name, folder_name, new_temp_db)

    def fetchdata(self, folder_name: str, file_name: str, column: str, *args) -> list:
        temp_db = self.rw_file.read_with_encrypt(file_name, folder_name)
        temp_list = []

        for key, value in temp_db.items():
            if key.isupper():
                key = key.upper()
                column = column.upper()
            if key == column:                
                for item in value:
                    if all(arg in item for arg in args):
                        temp_list.extend(item[arg] for arg in args)

        return temp_list

        

   