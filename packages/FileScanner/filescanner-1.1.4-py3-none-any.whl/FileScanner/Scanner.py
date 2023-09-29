import pandas as pd
from pathlib import Path
import datetime


class FileScanner:
    def __init__(self):
        self.file_array = []
        self.columns = ['file',
                        'file_name',
                        'file_type',
                        'file_path',
                        'file_name_no_ext',
                        'file_size',
                        'file_accessed',
                        'file_modified',
                        'file_created']

    def scan(self, path, file_type_array, recursive=True):
        if recursive:
            p = Path(path).rglob('*.*')
        else:
            p = Path(path).glob('*.*')

        # creates array of file info
        only_files = [x for x in p if x.is_file()]

        # loops over array and create obj with file info
        for file in only_files:
            if file.suffix[1:] in file_type_array:  # only create obj if file type in array
                # creates tuple of values for appending
                array_values = fr"{file.parent}\{file.name}", \
                               file.name, \
                               file.suffix[1:], \
                               file.parent, \
                               file.stem, \
                               file.stat().st_size, \
                               datetime.datetime.fromtimestamp(file.stat().st_atime), \
                               datetime.datetime.fromtimestamp(file.stat().st_mtime), \
                               datetime.datetime.fromtimestamp(file.stat().st_ctime)
                # appends into file_array
                self.file_array.append(array_values)

        # creates df based on file_Array and columns defintion
        df = pd.DataFrame(data=self.file_array, columns=self.columns)
        return df


fss = FileScanner()


def scan(path='', file_type_array=[], recursive=False):
    if not Path.is_dir(Path(path)):
        raise Exception(fr"Path {path} is not a valid folder")

    if len(path) == 0:
        raise Exception("Path cannot be 0 length")

    if not isinstance(recursive, bool):
        raise Exception("recursive_file_scan flag must be of type bool")

    if not isinstance(file_type_array, list):
        raise Exception("File type must be in array format ['txt']")

    return fss.scan(path, file_type_array, recursive)  # scans for all files

