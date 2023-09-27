import os
from typing import BinaryIO

from common_packages.file_storage_utils import Storage


class LocalStorage(Storage):
    def __init__(self,root_dir: str) -> None:
        """
            1. try to create directory if not exist
        Args:
            root_dir (str): _description_

        Raises:
            ValueError: _description_
            ValueError: _description_
        """
        # 判断目录是否存在，不存在则创建
        if not os.path.exists(root_dir):
            try:
                os.mkdir(root_dir)
            except Exception as e:
                raise ValueError("root_dir does not exist and cannot be created")
        self.root_dir = root_dir

    def save(self, filename: str, content: BinaryIO) -> tuple[bool,str]:
        file_path: str = os.path.join(self.root_dir,filename)
        try:
            with open(file_path,"wb") as f:
                f.write(content)
        except Exception as e:
            return False,e
        else:
            return True,file_path
        
    def load(self, filename: str) -> tuple[bool,bytes]:
        try:
            with open(os.path.join(self.root_dir,filename),"rb") as f:
                content: bytes = f.read()
        except Exception as e:
            return False,e
        else:
            return True,content