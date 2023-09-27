import logging
from typing import BinaryIO

import requests

from common_packages.file_storage_utils import Storage
from common_packages.utils.tencent_utils import generate_tencent_key

# TODO sdk方式封装

class TencentCos(Storage):
    def __init__(self,root_dir: str,**kwargs) -> None:
        self.bucket = root_dir
        if not set(["region","secret_key","secret_id"]).issubset(kwargs):
            raise ValueError("region,key,secret_key,secret_id must be provided")
        self.region = kwargs["region"]
        self.secret_key = kwargs["secret_key"]
        self.secret_id = kwargs["secret_id"]
        
    # api 注明
    def save(self, filename: str, content: BinaryIO) -> tuple[bool, str]:
        url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{filename}"
        authorization: str = generate_tencent_key(secret_id=self.secret_id,secret_key=self.secret_key,key=filename,method="put")
        try:
            s = requests.put(
                url=url,
                headers={
                    "Authorization": authorization,
                    "Content-Type":"image/jpeg"
                },
                data=content,

            )
        except Exception as e:
            print(e)
            return False, e
        logging.info(f"tencent cos save file {filename} success. {s.status_code=} {s.content=}")
        return True, filename
    
    def load(self, filename: str) -> tuple[bool, bytes]:
        self.key = filename
        url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{self.key}"
        authorization: str = generate_tencent_key(secret_id=self.secret_id,secret_key=self.secret_key,key=self.key)
        try:
            s = requests.get(
                url=url,
                headers={
                    "Authorization": authorization,
                },
            )
        except Exception as e:
            logging.error(f"tencent cos read failed {e}")
            return False, b""
        
        logging.info(f"tencent cos save file {self.key} success. {s.status_code}")
        return True, s.content