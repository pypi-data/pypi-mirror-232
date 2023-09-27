import hashlib
import json
import logging
import os
import time
import uuid
from typing import Optional

import requests
from requests.models import Response

from common_packages.translate_utils import SentenceInfo, Translate, WordInfo


class YoudaoTranslate(Translate):
    def __init__(self, **kwargs) -> None:
        if not {"YOUDAO_URL", "APP_KEY", "APP_SECRET"}.issubset(kwargs.keys()):
            raise Exception("you need to set YOUDAO_URL,APP_KEY,APP_SECRET")
        self.YOUDAO_URL = kwargs["YOUDAO_URL"]
        self.APP_KEY = kwargs["APP_KEY"]
        self.APP_SECRET = kwargs["APP_SECRET"]

    def _encrypt(self, salt, current_time, word):
        signStr = (
            self.APP_KEY + self._truncate(word) + salt + current_time + self.APP_SECRET
        )
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode("utf-8"))
        return hash_algorithm.hexdigest()

    def _truncate(self, q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10 : size]

    def _send_request(self, word: str) -> dict:
        current_time = str(int(time.time()))
        salt = str(uuid.uuid1())
        sign = self._encrypt(salt=salt, current_time=current_time, word=word)
        data = {
            "from": "en",
            "to": "zh-CHS",
            "signType": "v3",
            "curtime": current_time,
            "sign": sign,
            "appKey": self.APP_KEY,
            "salt": salt,
            "q": word
            # 'vocabId':"您的用户词表ID"
        }

        try:
            response: Response = requests.post(
                self.YOUDAO_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except Exception as e:
            raise ValueError(f"youdao translate connect error: {e}")
        if response.status_code != 200:
            raise ValueError(f"youdao translate status error: {response.status_code}")
        return response.json()

    def translate(self, word: str) -> dict:
        response: dict = self._send_request(word=word)
        if response["errorCode"] != "0":
            raise ValueError(f"youdao translate error: {word} {response['errorCode']=}")
        return response

    @classmethod
    def format_word_response(cls, response: dict) -> WordInfo:
        # only word
        basic_direction: dict = response["basic"]

        word: str = response["query"]

        translation_no_class: list[str] = response["translation"]
        translation_have_class: list[str] = basic_direction["explains"]
        translation = {
            "no_class": translation_no_class,
            "have_class": translation_have_class,
        }

        translation_speak_url: str = response["tSpeakUrl"]
        source_speak_url: str = response["speakUrl"]
        source_speech_uk: str = basic_direction["uk-speech"]
        source_speech_us: str = basic_direction["us-speech"]
        speakUrl = {
            "translation_speak_url": translation_speak_url,
            "source_speak_url": source_speak_url,
            "source_speech_uk": source_speech_uk,
            "source_speech_us": source_speech_us,
        }

        phonetic_us: str = basic_direction["us-phonetic"]
        phonetic: str = basic_direction["phonetic"]
        phonetic_uk: str = basic_direction["uk-phonetic"]
        phonetic = {"us": phonetic_us, "uk": phonetic_uk, "default": phonetic}

        word_type: list[str] = basic_direction.get("exam_type")

        grammar_info: list[dict] = basic_direction.get("wfs")

        extended_info: list[dict[str, list[str]]] | None = response.get("web")

        format_response: WordInfo = {
            "word": word,
            "translation": translation,
            "speak_url": speakUrl,
            "phonetic": phonetic,
            "word_type": word_type,
            "grammar_info": grammar_info,
            "extended_info": extended_info,
        }
        # import json
        # print(json.dumps(res,indent=2,ensure_ascii=False))
        return format_response

    @classmethod
    def format_sentence_response(cls, response: dict) -> SentenceInfo:
        sentence: str = response["query"]
        translation: list[str] = response["translation"]

        source_speak_url: str = response["speakUrl"]
        translation_speak_url: str = response["tSpeakUrl"]

        response = {
            "sentence": sentence,
            "translation": translation,
            "source_speak_url": source_speak_url,
            "translation_speak_url": translation_speak_url,
        }

        return response

    @classmethod
    def download_audio_file(self, url: str) -> bytes:
        try:
            response = requests.get(url=url)
        except Exception as e:
            raise ValueError(f"youdao translate download audio file error: {e}")
        if response.status_code != 200:
            raise ValueError("download audio file,status code error")
        return response.content
