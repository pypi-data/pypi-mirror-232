from abc import ABC, abstractmethod
from typing import BinaryIO

# from common_packages.file_storage_utils.local import LocalStorage


class Storage(ABC):
    @abstractmethod
    def __init__(self,root_dir: str) -> None:
        ...
        
    @abstractmethod
    def save(self,filename: str,content: BinaryIO) -> tuple[bool,str]:
        ...
    
    @abstractmethod
    def load(self,filename: str) -> tuple[bool,bytes]:
        ...
    