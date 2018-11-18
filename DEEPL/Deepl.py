
# coding: utf-8

import requests
import time
from random import randint


def timestamp():
    return int(round(time.time() * 1000))


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


class Deepl():
    def __init__(self):
        self.headers = {
            'Origin': 'https://www.deepl.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'text/plain',
            'Accept': '*/*',
            'Referer': 'https://www.deepl.com/translator',
            'Connection': 'keep-alive',
        }
    def translate(self, sentence, target_lang, lang="auto"):
        data = {"jsonrpc":"2.0",
            "method": "LMT_handle_jobs",
            "params":{"jobs":[
                {"kind":"default",
                 "raw_en_sentence":sentence,
                 "raw_en_context_before":[],
                 "raw_en_context_after":[],
                 "quality":"fast"}
            ],"lang":{"user_preferred_langs":["DE", "EN", "FR"],
                      "source_lang_user_selected": lang,
                      "target_lang": target_lang},
                      "priority":-1,
                      "timestamp":timestamp()},
            "id":random_with_N_digits(8)}
        response = requests.post(url, headers=headers, json=data)
        js = response.json()
        translation_js = js['result']['translations'][0]['beams']
        translation = [i['postprocessed_sentence'] for i in translation_js]
        log_proba   = [i['totalLogProb'] for i in translation_js]
        return translation[0]
