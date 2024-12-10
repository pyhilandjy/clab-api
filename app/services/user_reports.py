import json
import os
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
from matplotlib import font_manager
from wordcloud import WordCloud

from app.db.query import (
    DELETE_WORDCLOUD_DATA,
    INSERT_WORDCLOUD_DATA,
    SELECT_STT_DATA_USER_REPORTS,
    SELECT_WORDCLOUD_DATA,
    UPDATE_WORDCLOUD_DATA,
)
from app.db.worker import execute_insert_update_query, execute_select_query

FONT_PATH = os.path.abspath("./NanumFontSetup_TTF_GOTHIC/NanumGothic.ttf")
font_prop = font_manager.FontProperties(fname=FONT_PATH)

font_manager.fontManager.addfont(FONT_PATH)
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

POS_TAG_TO_KOREAN = {
    "NNP": "고유명사",
    "NNG": "명사",
    "NP": "대명사",
    "VV": "동사",
    "VA": "형용사",
    "MAG": "부사",
}

# 워드클라우드

from kiwipiepy import Kiwi


def create_wordcloud_data(user_reports_id):
    """
    주어진 사용자 보고서에 대한 워드 클라우드 데이터를 생성합니다.
    이 함수는 지정된 사용자 보고서에 대한 음성-텍스트(STT) 데이터를 검색하고,
    텍스트를 토큰화하여 명사를 추출하고 각 화자의 명사 발생 빈도를 계산합니다.
    결과는 화자와 해당 단어 빈도를 포함하는 사전 목록입니다.
    """
    stt_data = execute_select_query(
        query=SELECT_STT_DATA_USER_REPORTS, params={"user_reports_id": user_reports_id}
    )
    kiwi = Kiwi()

    stt_result = [dict(result) for result in stt_data]

    speaker_texts = defaultdict(str)
    for result in stt_result:
        speaker_texts[result["speaker"]] += " " + result["text_edited"]

    speaker_noun_counts = {}
    for speaker, text in speaker_texts.items():
        tokens = kiwi.tokenize(text)
        nouns = [token.form for token in tokens if token.tag.startswith("NN")]
        noun_counts = Counter(nouns)
        speaker_noun_counts[speaker] = dict(noun_counts)

    result = [
        {"speaker": speaker, "word_counts": word_counts}
        for speaker, word_counts in speaker_noun_counts.items()
    ]

    return result


def save_wordcloud_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 워드클라우드 데이터를 생성하고 저장합니다.
    """
    # user_reports_id의 데이터가 존재한다면 기존 데이터를 삭제 추가
    data = execute_select_query(
        query=SELECT_WORDCLOUD_DATA, params={"user_reports_id": user_reports_id}
    )
    if data:
        execute_insert_update_query(
            query=DELETE_WORDCLOUD_DATA,
            params={"user_reports_id": user_reports_id},
        )
    wordcloud_data = create_wordcloud_data(user_reports_id)
    data = json.dumps(wordcloud_data)
    execute_insert_update_query(
        query=INSERT_WORDCLOUD_DATA,
        params={"user_reports_id": user_reports_id, "data": data},
    )
    return {"message": "Wordcloud data saved successfully"}


def select_wordcloud_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 워드클라우드 데이터를 검색합니다.
    """
    results = execute_select_query(
        query=SELECT_WORDCLOUD_DATA, params={"user_reports_id": user_reports_id}
    )
    if results:
        return results[0]["data"]
    else:
        return []


def update_wordcloud_data(wordcloud_data, user_reports_id):
    """
    주어진 user_reports_id에 대한 워드클라우드 데이터를 업데이트합니다.
    """
    data = json.dumps(wordcloud_data)
    execute_insert_update_query(
        query=UPDATE_WORDCLOUD_DATA,
        params={"user_reports_id": user_reports_id, "data": data},
    )
    return {"message": "Wordcloud data updated successfully"}
