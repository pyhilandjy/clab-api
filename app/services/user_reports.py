import json
import os
from collections import Counter, defaultdict, OrderedDict

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

from app.db.query import (
    DELETE_WORDCLOUD_DATA,
    INSERT_WORDCLOUD_DATA,
    SELECT_STT_DATA_USER_REPORTS,
    SELECT_WORDCLOUD_DATA,
    UPDATE_WORDCLOUD_DATA,
    SELECT_USER_REPORTS_INFO,
    SELECT_SENTENCE_LENGTH_DATA,
    INSERT_SENTENCE_LENGTH_DATA,
)
from app.db.worker import execute_insert_update_query, execute_select_query
from app.services.users import fetch_user_names

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
    "JKS": "전치사",
    "JC": "접속사",
    "IC": "감탄사",
}

# 워드클라우드

from kiwipiepy import Kiwi

async def select_user_reports_info(user_reports_id: str):
    """
    주어진 user_reports_id에 대한 사용자 보고서 정보를 검색합니다.
    """
    reports = execute_select_query(
        query=SELECT_USER_REPORTS_INFO, 
        params={"user_reports_id": user_reports_id}
    )
    
    if reports:
        reports = [dict(report) for report in reports]
        user_ids = [report["user_id"] for report in reports]
        user_data = await fetch_user_names(user_ids)
        for report in reports:
            user_id = report["user_id"]
            report["user_name"] = user_data.get(user_id, "")
        return reports    
    else:
        return []



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
        return {"message": "Wordcloud data already exists"}
    else:
        wordcloud_data = create_wordcloud_data(user_reports_id)
        data = json.dumps(wordcloud_data)
        execute_insert_update_query(
            query=INSERT_WORDCLOUD_DATA,
            params={"user_reports_id": user_reports_id, "data": data},
        )
        data = execute_select_query(
        query=SELECT_WORDCLOUD_DATA, params={"user_reports_id": user_reports_id}
    )
        if data:
            item = data[0]
        combined = {
            "data": item["data"],
            "insights": item["insights"]
        }
        return combined
    
    
def reset_wordcloud_data(user_reports_id):
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
        item = results[0]
        combined = {
            "data": item["data"],
            "insights": item["insights"]
        }
        return combined
    else:
        return []


def update_wordcloud_data(wordcloud_data, user_reports_id):
    """
    주어진 user_reports_id에 대한 워드클라우드 데이터를 업데이트합니다.
    """
    execute_insert_update_query(
        query=UPDATE_WORDCLOUD_DATA,
        params={
            "user_reports_id": user_reports_id,
            "data": wordcloud_data["data"],
            "insights": wordcloud_data["insights"]
        },
    )
    return {"message": "Wordcloud data updated successfully"}


#sentence_length(SENTENCE_LENGTH)

def create_sentence_length(user_reports_id):
    stt_data = execute_select_query(
        query=SELECT_STT_DATA_USER_REPORTS, params={"user_reports_id": user_reports_id}
    )
    sentence_length_data = {}

    for result in stt_data:
        char_length = len(result["text_edited"])
        
        speaker = result["speaker"]
        if speaker not in sentence_length_data:
            sentence_length_data[speaker] = []
        sentence_length_data[speaker].append(char_length)

    formatted_data = [
        {"speaker": speaker, "char_lengths": lengths}
        for speaker, lengths in sentence_length_data.items()
    ]

    return formatted_data

def save_sentence_length_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 바이올린플롯 데이터를 생성하고 저장합니다.
    """
    data = execute_select_query(
        query=SELECT_SENTENCE_LENGTH_DATA, params={"user_reports_id": user_reports_id}
    )
    if data:
        return {"message": "sentence_length data already exists"}
    else:
        sentence_length_data = create_sentence_length(user_reports_id)
        data = json.dumps(sentence_length_data)
        execute_insert_update_query(
            query=INSERT_SENTENCE_LENGTH_DATA,
            params={"user_reports_id": user_reports_id, "data": sentence_length_data},
        )
        data = execute_select_query(
            query=SELECT_SENTENCE_LENGTH_DATA, 
            params={"user_reports_id": user_reports_id})
        if data:
            item = data[0]
        combined = {
            "data": item["data"],
            "insights": item["insights"]
        }
        return combined
    
def select_sentence_length_data(user_reports_id):
    """
    주어진 user_reports_id에 대한 바이올린플롯 데이터를 생성하고 저장합니다.
    """
    data = execute_select_query(
        query=SELECT_SENTENCE_LENGTH_DATA, params={"user_reports_id": user_reports_id}
    )
    if data:
        item = data[0]
    combined = {
        "data": item["data"],
        "insights": item["insights"]
    }
    return combined
    
#tokenize data
def parse_text(text):
    kiwi = Kiwi()
    tokens = kiwi.tokenize(text)
    return tokens

def analyze_speech_data(morphs_data):
    """형태소분석"""
    speaker_data = extract_speaker_data(morphs_data)
    data= {
        speaker: analyze_text_with_kiwi(text) for speaker, text in speaker_data.items()
    }
    formatted_data = [
        {
            "speaker": speaker,
            "data": stats
        } for speaker, stats in data.items()
    ]

    return formatted_data

def extract_speaker_data(data):
    """발화자별로 텍스트를 추출하여 하나의 문자열로 결합"""
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    speaker_data = (
        data.groupby("speaker")["text_edited"]
        .apply(lambda texts: " ".join(texts.astype(str)))
        .to_dict()
    )
    return speaker_data

def analyze_text_with_kiwi(text):
    """품사별로 단어를 분류"""
    parsed_text = parse_text(text)
    pos_lists, pos_unique_lists = classify_words_by_pos(parsed_text)
    return build_pos_summary(pos_lists, pos_unique_lists)


def classify_words_by_pos(parsed_text):
    """파싱된 텍스트에서 품사별로 단어를 분류"""
    pos_lists = {korean: [] for korean in POS_TAG_TO_KOREAN.values()}
    pos_unique_lists = {korean: set() for korean in POS_TAG_TO_KOREAN.values()}

    for token in parsed_text:
        tag = token.tag
        word = token.form
        if tag in POS_TAG_TO_KOREAN:
            korean_pos = POS_TAG_TO_KOREAN[tag]
            pos_lists[korean_pos].append(word)
            pos_unique_lists[korean_pos].add(word)

    return pos_lists, pos_unique_lists


def build_pos_summary(
    pos_lists,
    pos_unique_lists,
):
    """품사별 단어 리스트와 고유 단어 세트에서 요약 정보를 구성하여 반환"""
    total_words = sum(len(words) for words in pos_lists.values())
    # total_unique_words = sum(
    #     len(unique_words) for unique_words in pos_unique_lists.values()
    # )
    summary = {
        pos: f"{round(len(words) / total_words * 100, 1)}%({len(words)})"
        for pos, words in pos_lists.items()
    }
    summary["총단어 수"] = total_words
    summary = OrderedDict(
        [("총단어 수", summary.pop("총단어 수"))] + list(summary.items())
    )
    return summary


def save_tokenized_data(user_reports_id):
    stt_data = execute_select_query(
        query=SELECT_STT_DATA_USER_REPORTS, params={"user_reports_id": user_reports_id}
    )

    morps_data = analyze_speech_data(stt_data)
    return morps_data