import io
import os
from collections import Counter, OrderedDict
from datetime import date

import boto3
import matplotlib.pyplot as plt
import mecab_ko as MeCab
import numpy as np
import pandas as pd
import seaborn as sns
from fastapi import Response
from matplotlib import font_manager
from wordcloud import WordCloud

from app.config import settings
from app.db.query import (COUNT_ACT_ID, COUNT_TALK_MORE_ID,
                          INSERT_FILE_PATH_REPORTS_ID,
                          INSERT_IMAGE_FILES_META_DATA,
                          INSERT_REPORT_META_DATA,
                          SELECT_AUDIO_FILES_BETWEEN_DATE, SELECT_RECORD_TIME,
                          SELECT_REPORT_FILE_PATH, SELECT_REPORT_METADATA,
                          SELECT_SENTENCE_LEN, SELECT_STT_DATA_BETWEEN_DATE,
                          UPDATE_REPORTS_ID)
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

session = boto3.Session(
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

bucket_name = settings.bucket_name

s3 = session.client("s3")


# 형태소 분석
def parse_text(text):
    """텍스트에 형태소분석 결과를 반환"""
    mecab = MeCab.Tagger()
    return mecab.parse(text)


def classify_words_by_pos(parsed_text):
    """파싱된 텍스트에서 품사별로 단어를 분류"""
    pos_lists = {korean: [] for korean in POS_TAG_TO_KOREAN.values()}
    pos_unique_lists = {korean: set() for korean in POS_TAG_TO_KOREAN.values()}

    for line in parsed_text.split("\n"):
        if "\t" not in line:
            continue
        word, tag_info = line.split("\t")
        tag = tag_info.split(",")[0]
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
        pos: f"{round(len(words) / total_words * 100, 1)}%, {len(words)}개"
        for pos, words in pos_lists.items()
    }
    summary["총단어 수"] = total_words
    summary = OrderedDict(
        [("총단어 수", summary.pop("총단어 수"))] + list(summary.items())
    )
    return summary


def analyze_text_with_mecab(text):
    """품사별로 단어를 분류"""
    parsed_text = parse_text(text)
    pos_lists, pos_unique_lists = classify_words_by_pos(parsed_text)
    return build_pos_summary(pos_lists, pos_unique_lists)


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


def analyze_speech_data(morphs_data):
    """형태소분석"""
    speaker_data = extract_speaker_data(morphs_data)
    a = {
        speaker: analyze_text_with_mecab(text) for speaker, text in speaker_data.items()
    }
    return a


def create_morphs_data(user_id, start_date, end_date):
    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    morphs_data = execute_select_query(
        query=SELECT_STT_DATA_BETWEEN_DATE, params=params
    )

    morps_data = analyze_speech_data(morphs_data)
    return morps_data


# 워드클라우드


def gen_image_audio_files_id(user_id: str, speaker: str, start_date: date, end_date: date, type: str) -> str:
    """이미지 파일 아이디 생성"""
    return f"{user_id}_{speaker}_{start_date}_{end_date}_{type}.png"


def gen_image_file_path(image_id):
    """이미지 파일경로 생성"""
    return f"./app/image/{image_id}"


def create_image_metadata(image_id: str, speaker: str, user_id: str, start_date: date, end_date: date, type: str, image_path: str):
    return {
        "image_id": image_id,
        "speaker": speaker,
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "type": type,
        "image_path": image_path,
    }


def insert_image_file_metadata(metadata: dict):
    execute_insert_update_query(query=INSERT_IMAGE_FILES_META_DATA, params=metadata)


def create_circle_mask():
    """mask 생성"""
    x, y = np.ogrid[:600, :600]
    center_x, center_y = 300, 300
    radius = 300

    circle = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2
    mask = 255 * np.ones((600, 600), dtype=np.uint8)
    mask[circle] = 0
    return mask


def extract_nouns_with_mecab(text):
    """형태소분석 명사 추출"""
    mecab = MeCab.Tagger()
    nouns = []
    for line in mecab.parse(text).split("\n"):
        if "\t" in line:
            word, tag_info = line.split("\t")
            tag = tag_info.split(",")[0]
            if tag in ["NNG", "NNP"]:
                nouns.append(word)
    # 특정 단어 수정
    nouns = [word if word != "박하" else "박하율" for word in nouns]
    return nouns


def count_words(nouns):
    """한 글자 명사 제거"""
    words = [word for word in nouns if len(word) > 1]
    return Counter(words)


def generate_wordcloud(word_counts, font_path, mask):
    """워드클라우드 기본 생성"""
    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        width=800,
        height=800,
        max_words=200,
        max_font_size=100,
        colormap="viridis",
        mask=mask,
    )
    wc.generate_from_frequencies(word_counts)
    return wc


def save_wordcloud(wordcloud, image_path, speaker, font_prop):
    """워드클라우드를 S3 및 로컬에 저장"""
    try:
        plt.figure(figsize=(10, 10))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.text(
            0.05,
            0,
            speaker,
            fontsize=24,
            fontproperties=font_prop,
            ha="left",
            va="top",
            transform=plt.gca().transAxes,
            bbox=dict(facecolor="white", alpha=0.5),
        )
        plt.savefig(image_path, format="PNG", bbox_inches="tight")
        plt.close()
    except Exception as e:
        return {"error": str(e)}


def create_wordcloud_path(stt_data, user_id, start_date, end_date):
    """워드클라우드 생성 및 파일로 저장"""
    font_path = os.path.abspath("./NanumFontSetup_TTF_GOTHIC/NanumGothic.ttf")
    type = "wordcloud"
    if not isinstance(stt_data, pd.DataFrame):
        stt_data = pd.DataFrame(stt_data)

    f_start_date = start_date.strftime("%Y-%m-%d")
    f_end_date = end_date.strftime("%Y-%m-%d")
    local_paths = []

    for speaker in stt_data["speaker"].unique():
        speaker_data = stt_data[stt_data["speaker"] == speaker]
        text = " ".join(speaker_data["text_edited"].astype(str))
        nouns = extract_nouns_with_mecab(text)
        
        if not nouns:
            continue
        
        word_counts = count_words(nouns)
        mask = create_circle_mask()
        wordcloud = generate_wordcloud(word_counts, font_path, mask)

        image_id = gen_image_audio_files_id(user_id, speaker, f_start_date, f_end_date, type)
        image_path = gen_image_file_path(image_id)

        # 워드클라우드 저장
        save_wordcloud(wordcloud, image_path, speaker, font_prop)
        local_paths.append(image_path)

    return local_paths


def create_wordcoud(user_id, start_date, end_date):
    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    stt_data = execute_select_query(query=SELECT_STT_DATA_BETWEEN_DATE, params=params)
    image_path = create_wordcloud_path(stt_data, user_id, start_date, end_date)
    return image_path


# 바이올린플롯


def violin_chart(
    stt_data,
    user_id,
    start_date,
    end_date,
):
    type = "violinplot"
    if not isinstance(stt_data, pd.DataFrame):
        stt_data = pd.DataFrame(stt_data)
    stt_data["char"] = stt_data["text_edited"].apply(len)
    f_start_date = start_date.strftime("%Y-%m-%d")
    f_end_date = end_date.strftime("%Y-%m-%d")
    speaker = stt_data["speaker"].unique()
    speaker = ",".join(speaker)

    image_id = gen_image_audio_files_id(user_id, speaker, f_start_date, f_end_date, type)

    image_path = gen_image_file_path(image_id)

    metadata = create_image_metadata(
        image_id=image_id,
        user_id=user_id,
        speaker=speaker,
        start_date=start_date,
        end_date=end_date,
        type=type,
        image_path=image_path,
    )
    insert_image_file_metadata(metadata)
    sns.set_theme(
        style="whitegrid", font="NanumGothic", rc={"axes.unicode_minus": False}
    )
    sns.set_palette(sns.color_palette("Set2", 2))
    save_violin_plot(stt_data, font_prop, image_path)
    return image_path


def save_violin_plot(stt_data, font_prop, image_path):
    """바이올린 플롯을 S3에 저장"""
    try:
        # 메모리에 바이올린 플롯 이미지 저장
        # img_data = io.BytesIO()
        plt.figure(figsize=(6, 6))
        plt.title("발화자별 문장 길이 분포", fontproperties=font_prop)
        plt.xlabel("speaker", fontproperties=font_prop)
        plt.ylabel("문장 길이", fontproperties=font_prop)

        sns.violinplot(
            data=stt_data,
            x="speaker",
            y="char",
            hue="speaker",
            split=True,
            inner="quart",
            palette=sns.color_palette("Set2"),
        )

        plt.tight_layout()
        # plt.savefig(img_data, format="PNG")
        plt.savefig(image_path, format="PNG")
        plt.close()
        # img_data.seek(0)

        return image_path
    except Exception as e:
        return {"error": str(e)}


def create_violinplot(user_id, start_date, end_date):
    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    stt_data = execute_select_query(query=SELECT_STT_DATA_BETWEEN_DATE, params=params)
    image_path = violin_chart(stt_data, user_id, start_date, end_date)
    return image_path


# 리포트 필요내용


def recordtime_to_min_sec(record_time):
    # 전체 초에서 분과 초를 분리
    minutes = int(record_time // 60)
    seconds = round(record_time % 60)
    return {"분": minutes, "초": round(seconds, 3)}


def record_time(record_time):
    total_time = 0
    for record in record_time:
        if record["record_time"] is not None:
            total_time += record["record_time"]
    sum_record_time = recordtime_to_min_sec(total_time)
    return f"{sum_record_time['분']}분 {sum_record_time['초']}초"


def create_sentence_len(user_id, start_date, end_date):
    """문장 길이 반환"""

    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    select__stt_results = execute_select_query(query=SELECT_SENTENCE_LEN, params=params)

    sentence_len = {}

    for result in select__stt_results:
        speaker = result["speaker"]
        sentence_len[speaker] = {
            "가장 긴 문장": result["max_length"],
            "평균 문장 길이": int(result["avg_length"]),
        }
    # return speech_data
    return sentence_len


def create_audio_record_time(user_id, start_date, end_date):
    """문장 길이 반환"""

    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    select_record_time = execute_select_query(query=SELECT_RECORD_TIME, params=params)
    record_time_report = record_time(select_record_time)

    r_time = {
        "녹음시간": record_time_report,
    }
    # return speech_data
    return r_time


def select_act_count(user_id, start_date, end_date):
    """화행 갯수 카운트"""

    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    count_act_name = execute_select_query(query=COUNT_ACT_ID, params=params)
    act_count_dict = process_act_count(count_act_name)
    return act_count_dict


def process_act_count(count_act_name):
    speaker_act_count_dict = {}
    for row in count_act_name:
        speaker = row["speaker"]
        act_name = row["act_name"]
        count = row["count"]

        if speaker not in speaker_act_count_dict:
            speaker_act_count_dict[speaker] = {}

        speaker_act_count_dict[speaker][act_name] = count

    return speaker_act_count_dict


def select_talk_more_count(user_id, start_date, end_date):
    """화행 갯수 카운트"""

    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    count_talk_more_name = execute_select_query(query=COUNT_TALK_MORE_ID, params=params)
    talk_more_count_dict = process_talk_more_count(count_talk_more_name)
    return talk_more_count_dict


def process_talk_more_count(count_talk_more):
    speaker_talk_more_count_dict = {}
    for row in count_talk_more:
        speaker = row["speaker"]
        talk_more = row["talk_more"]
        count = row["count"]

        if speaker not in speaker_talk_more_count_dict:
            speaker_talk_more_count_dict[speaker] = {}

        speaker_talk_more_count_dict[speaker][talk_more] = count

    return speaker_talk_more_count_dict


def create_report_date(user_id, start_date, end_date):
    """녹음 기간 반환"""
    # 수정필요함
    start_date_str = start_date.strftime("%Y/%m/%d")
    end_date_str = f"{end_date.strftime("%Y/%m/%d")}"  # MM/DD 형식으로 변환
    report_date = {"녹음기간": f"{start_date_str} ~ {end_date_str}"}
    return report_date


def create_tmp_file_path(user_id):
    """임시 경로 생성"""
    return f"app/report/{user_id}/temp.pdf"


def create_file_path(user_id, id):
    """S3 파일 경로 생성"""
    return f"app/report/{user_id}/{id}.pdf"


def update_file_path(id, file_path):
    return execute_insert_update_query(
        query=INSERT_FILE_PATH_REPORTS_ID,
        params={"id": id, "file_path": file_path},
    )


def gen_report_file_metadata(user_id: str, title: str, tmp_file_path: str):
    """리포트 파일 메타데이터 생성"""
    return {
        "user_id": user_id,
        "title": title,
        "file_path": tmp_file_path,
    }


def insert_report_metadata(metadata: dict):
    """오디오 파일 메타데이터 db적재"""
    return execute_insert_update_query(
        query=INSERT_REPORT_META_DATA,
        params=metadata,
        return_id=True,
    )


def update_report_files_id(id, user_id, start_date, end_date):
    """오디오 파일 메타데이터 db적재"""
    return execute_insert_update_query(
        query=UPDATE_REPORTS_ID,
        params={
            "new_reports_id": id,
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


def save_report_file_s3(file, file_path: str):
    """m4a 파일을 S3에 저장"""
    try:
        file.file.seek(0)
        s3.upload_fileobj(file.file, bucket_name, file_path)

        return {"message": "File uploaded successfully", "file_path": file_path}
    except Exception as e:
        return {"error": str(e)}


def get_report_metadata(user_id):
    report_metadata = execute_select_query(
        query=SELECT_REPORT_METADATA, params={"user_id": user_id}
    )
    return report_metadata


def get_report_file_path(report: str) -> str:
    result = execute_select_query(query=SELECT_REPORT_FILE_PATH, params={"id": report})
    if isinstance(result, list) and len(result) > 0 and "file_path" in result[0]:
        return result[0]["file_path"]
    else:
        print("e")


def get_report(file_path: str):
    try:
        # S3에서 PDF 파일 불러오기
        pdf_file = s3.get_object(Bucket=bucket_name, Key=file_path)
        pdf_content = pdf_file["Body"].read()
        file_name = file_path.split("/")[-1]

        # PDF 내용을 BytesIO 객체에 쓰기
        buffer = io.BytesIO(pdf_content)

        headers = {"Content-Disposition": f"inline; filename={file_name}"}

        # BytesIO 객체의 시작 위치를 0으로 되돌립니다.
        buffer.seek(0)

        # PDF 파일을 Response로 반환
        return Response(
            content=buffer.read(), headers=headers, media_type="application/pdf"
        )
    except Exception as e:
        raise e


def select_audio_id_stt_data(user_id, start_date, end_date):
    """audio_files_id별로 stt result를 가져오는 엔드포인트"""
    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
    }
    audio_files_id = execute_select_query(
        query=SELECT_AUDIO_FILES_BETWEEN_DATE, params=params
    )
    stt_data = execute_select_query(query=SELECT_STT_DATA_BETWEEN_DATE, params=params)
    return audio_files_id, stt_data


def group_stt_data_by_file_name(audio_files_id, stt_data):
    grouped_data = {}
    for file in audio_files_id:
        file_name = file["file_name"]
        grouped_data[file_name] = [
            data for data in stt_data if data["audio_files_id"] == file["id"]
        ]
    return grouped_data


def export_to_excel(grouped_data):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for file_name, data in grouped_data.items():
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=file_name, index=False)
    output.seek(0)
    return output
