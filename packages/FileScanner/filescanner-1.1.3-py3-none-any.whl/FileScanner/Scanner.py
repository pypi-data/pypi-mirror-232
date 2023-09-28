import pandas as pd
from pathlib import Path


class FileScanner:
    def __init__(self):
        self.file_array = []

    def scan(self, path, file_type_array, recursive=True):
        if recursive:
            p = Path(path).rglob('*.*')
        else:
            p = Path(path).glob('*.*')

        only_files = [x for x in p if x.is_file()]

        for file in only_files:
            file_type = file.suffix[1:]
            file_name = file.name
            file_path = file.parent
            file = fr"{file_path}\{file_name}"

            if file_type in file_type_array:
                x = (file,file_name, file_type, file_path)
                self.file_array.append(x)

        df = pd.DataFrame(data=self.file_array, columns=['file', 'file_name', 'file_type', 'file_path'])
        return df

fss = FileScanner()
def scan(path='',file_type_array=[],recursive_file_scan=False):
    return fss.scan(path,file_type_array,recursive_file_scan)  # scans for all files
