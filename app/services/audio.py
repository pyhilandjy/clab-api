import io
import json
import logging
import os
import re
import shutil
import subprocess
from datetime import datetime
from io import BytesIO

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from loguru import logger
from pydub import AudioSegment

from app.config import settings
from app.db.query import (INSERT_AUDIO_META_DATA, INSERT_STT_DATA,
                          SELECT_AUDIO_FILES, SELECT_FILES,
                          UPDATE_AUDIO_STATUS, UPDATE_RECORD_TIME, SELECT_AUDIO_FILE)
from app.db.worker import execute_insert_update_query, execute_select_query
from app.services.clova import ClovaApiClient

logger = logging.getLogger(__name__)

session = boto3.Session(
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

bucket_name = settings.bucket_name

s3 = session.client("s3")


def create_file_name(user_name):
    """파일 이름 생성"""
    return datetime.now().strftime("%y%m%d%H%M%S") + "_" + user_name


def create_file_path(user_id):
    """파일 경로 생성"""
    return f"./app/audio/{datetime.now().strftime("%y%m%d%H%M%S")}_{user_id}.webm"


def save_audio(file: UploadFile, file_path: str):
    """m4a 파일 저장"""
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        convert_to_m4a(file_path)
    except Exception as e:
        raise e


async def download_and_process_file():
    """S3에서 파일 다운로드 및 처리"""
    try:
        logger.info("Starting download_and_process_file task")
        ready_files = select_audio_ready()
        for file_record in ready_files:
            file_path = file_record.file_path
            local_path = f"./{file_path}"
            audio_files_id = str(file_record.id)
            # S3에서 파일 다운로드
            s3.download_file(settings.bucket_name, file_path, local_path)
            m4a_path = await convert_file_update_record_time(local_path, audio_files_id)
            await process_stt(audio_files_id, m4a_path)
            await delete_file(m4a_path)
        logger.info("Completed download_and_process_file task")
    except Exception as e:
        logger.error(f"Error during file processing: {e}")
        raise e


def select_audio_ready():
    results = execute_select_query(query=SELECT_AUDIO_FILES)
    return results


async def convert_file_update_record_time(local_path: str, audio_files_id):
    """오디오 파일 메타데이터 처리"""
    try:
        with open(local_path, "rb") as f:
            file_bytes = f.read()
        m4a_path = convert_to_m4a(file_bytes, local_path)
        record_time = get_record_time(m4a_path)
        insert_record_time(record_time, audio_files_id)
        logger.info(f"Audio file metadata inserted: {m4a_path}")
        return m4a_path
    except Exception as e:
        update_audio_status(audio_files_id, "convert_error")
        logger.error(f"Error processing metadata: {e}")
        raise e


def insert_record_time(record_time, audio_files_id):
    """record_time update"""
    execute_insert_update_query(
        query=UPDATE_RECORD_TIME,
        params={"record_time": record_time, "audio_files_id": audio_files_id},
    )


def get_record_time(m4a_path: str):
    """M4A 파일의 재생 시간을 가져옴"""
    try:
        audio = AudioSegment.from_file(m4a_path, format="m4a")
        duration_seconds = len(audio) / 1000.0
        return round(duration_seconds)
    except Exception as e:
        logger.error(f"Error getting record time: {e}")
        raise Exception("Failed to get record time")


def create_audio_metadata(user_id: str, file_name: str, file_path: str):
    """오디오 파일 메타데이터 생성"""
    return {
        "user_id": user_id,
        "file_name": file_name,
        "file_path": file_path,
    }


def insert_audio_metadata(metadata: dict):
    """오디오 파일 메타데이터 db적재"""
    return execute_insert_update_query(
        query=INSERT_AUDIO_META_DATA,
        params=metadata,
    )


def update_audio_status(audio_files_id, status):
    execute_insert_update_query(
        query=UPDATE_AUDIO_STATUS, params={"audio_files_id": audio_files_id, "status": status}
    )


async def process_stt(audio_files_id, m4a_path):
    """음성파일 STT"""
    try:
        segments = get_stt_results(m4a_path)
        if not segments:
            logger.error(f"No segments found for file: {audio_files_id}")
            update_audio_status(audio_files_id, "stt_error")
            delete_file(m4a_path)
            return

        rename_segments = rename_keys(segments)
        explode_segments = explode(rename_segments, "textEdited")
        insert_stt_segments(explode_segments, audio_files_id)
        update_audio_status(audio_files_id, "done")
    except Exception as e:
        update_audio_status(audio_files_id, "stt_error")
        delete_file(m4a_path)
        raise e
    else:
        logger.info(f"STT segments inserted: {audio_files_id}")


async def upload_to_s3(audio: UploadFile, file_path):
    """m4a 파일을 S3에 저장"""
    try:
        audio_content = await audio.read()
        audio_stream = BytesIO(audio_content)

        # S3에 업로드
        s3.upload_fileobj(audio_stream, settings.bucket_name, file_path)
    except NoCredentialsError:
        return {"error": "Credentials not available"}
    except ClientError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
    else:
        logger.info(f"File uploaded to S3: {file_path}")
        return {"message": "File uploaded successfully"}


def convert_to_m4a(file_bytes: bytes, input_path: str):
    """WebM 파일을 M4A로 변환"""
    output_path = input_path.replace(".webm", ".m4a")
    with open(input_path, "wb") as buffer:
        buffer.write(file_bytes)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-acodec",
        "aac",
        "-b:a",
        "192k",
        output_path,
    ]
    try:
        subprocess.run(command, check=True)
        os.remove(input_path)  # Remove the original webm file after conversion
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion error: {e}")
        raise Exception("Failed to convert file to M4A")


def insert_audio_file_metadata(metadata: dict):
    """오디오 파일 메타데이터 db적재"""
    execute_insert_update_query(query=INSERT_AUDIO_META_DATA, params=metadata)


def insert_stt_data(data_list):
    """stt 결과값 db 적재"""
    execute_insert_update_query(query=INSERT_STT_DATA, params=data_list)


def get_stt_results(file_path):
    """클로바에서 나온 stt 세그먼츠 return"""
    clova_api_client = ClovaApiClient()
    response = clova_api_client.request_stt(file_path=file_path)

    clova_output = response.text
    data = json.loads(clova_output)
    data["segments"]

    return data["segments"]


def insert_stt_segments(segments, audio_files_id):
    """stt결과값 필요 세그먼츠 추출 밑 적재"""
    data_list = []
    for text_order, segment in enumerate(segments, start=1):
        segment_data = {
            "audio_files_id": audio_files_id,
            "text_order": text_order,
            "start_time": segment["start_time"],
            "end_time": segment["end_time"],
            "text": segment["text"],
            "confidence": segment["confidence"],
            "speaker": segment["speaker"]["label"],
            "text_edited": segment["textEdited"],
        }
        data_list.append(segment_data)
        insert_stt_data(segment_data)
    return data_list


def splitter(text_list, punct):
    """
    :param text_list: 리스트로 감싸진 문장들
    :param punct: 처리할 특수문자
    """
    output_list = []

    # input으로 받은 문장 리스트에 대해 (리스트 원소가 하나라도 동일하게 작업 됨)
    for sentence in text_list:
        sentence = sentence.strip()

        # 특수문자가 문장에 있다면
        if punct in sentence:
            texts = []
            temp_sent = ""

            # 띄어쓰기로 단어별 문장 split
            for word in sentence.split():

                # 임시 문장에 단어와 띄어쓰기 추가
                temp_sent += word + " "

                # 주어진 특수문자가 단어에 있다면
                if punct in word:
                    # 문장 양 끝의 공백 제거 후 texts 리스트에 추가
                    texts.append(temp_sent.strip())
                    # 임시 문장 초기화
                    temp_sent = ""

            # 문장의 마지막이 주어진 특수문자가 아닐 때, 최종 저장된 임시문장을 texts 리스트에 추가
            # 이걸 안해주면 특수문자 없는 마지막 문장이 최종 결과물에 포함되지 않음
            if temp_sent != texts[-1]:
                if temp_sent.strip() != "":
                    texts.append(temp_sent.strip())

            # texts의 문장들을 최종 output 리스트에 추가
            for text in texts:
                output_list.append(text)

        # 문장에 특수문자가 없다면 그냥 문장 그대로 최종 output 리스트에 추가
        else:
            output_list.append(sentence)
    return output_list


def explode(segments: list, target_col: str):
    """
    :params segments : 줄바꿈을 해야할 DataFrame
    :params target_col : 대상이 될 Column

    :return : 줄바꿈이 완료된 DataFrame
    """

    # 작업할 특수문자들 / 특수 문자 추가 필요시 여기에 그냥 추가하면 됨
    puncts = ".?!"

    return_list = []
    # 매 row 별로 데이터 작업
    for index in range(len(segments)):
        target_text = [segments[index][target_col]]

        # 매 특수문자 별 splitter 실행
        for punct in puncts:
            target_text = splitter(target_text, punct)

        # splitter의 output의 text별로 col_datas의 컬럼별 리스트에 추가 (DF Row 추가하는 작업)
        for text in target_text:
            col_data = {}
            # 컬럼별로 작업
            for col in segments[index].keys():
                # target column에 나누어진 text 추가
                if col == target_col:
                    col_data[target_col] = text

                # 나머지 컬럼은 원래 컬럼 내용과 동일하게 추가
                else:
                    col_data[col] = segments[index][col]

            return_list.append(col_data)
    return return_list


def rename_keys(segments):
    segment = segments[0]
    segment_names = {}
    time = []
    for key, value in segment.items():
        if type(value) == int:
            time.append([key, value])
        elif type(value) == str:
            if "edited" in key.lower():
                segment_names[key] = "textEdited"
            else:
                segment_names[key] = "text"
        elif type(value) == float:
            segment_names[key] = "confidence"
        elif type(value) == dict:
            if "name" in value.keys():
                segment_names[key] = "speaker"
            else:
                segment_names[key] = "diarization"
        elif type(value) == list:
            segment_names[key] = "words"
        else:
            logger.error(f"Unknown type: {type(value)}")

    if time[0][1] > time[1][1]:
        segment_names[time[0][0]] = "end_time"
        segment_names[time[1][0]] = "start_time"
    else:
        segment_names[time[0][0]] = "start_time"
        segment_names[time[1][0]] = "end_time"

    output = []
    for segment in segments:
        output.append({segment_names.get(k, k): v for k, v in segment.items()})
    return output


async def delete_file(m4a_path):
    try:
        if os.path.exists(m4a_path):
            os.remove(m4a_path)
    except Exception as e:
        logger.error(f"An error occurred while trying to delete the file: {str(e)}")
    else:
        logger.info(f"File deleted: {m4a_path}")


def get_files_by_user_id(user_id):
    return execute_select_query(query=SELECT_FILES, params={"user_id": user_id})


def sum_record_times(record_time):
    total_time = 0
    for record in record_time:
        if record["record_time"] is not None:
            total_time += record["record_time"]
    return total_time


def recordtime_to_min_sec(record_time):
    # 전체 초에서 분과 초를 분리
    minutes = int(record_time // 60)
    seconds = round(record_time % 60)
    return {"분": minutes, "초": round(seconds, 3)}


async def select_audio_file(id, range_header):
    audio_file = execute_select_query(query=SELECT_AUDIO_FILE, params={"id": id})
    file_path = audio_file[0].file_path
    return await get_audio(file_path, range_header)



async def get_audio(file_path: str, range_header: str = None):
    try:
        # S3에서 오디오 파일 불러오기
        s3_response = s3.get_object(Bucket=bucket_name, Key=file_path)
        audio_content = s3_response["Body"].read()
        file_name = file_path.split("/")[-1]
        content_length = len(audio_content)

        start, end = 0, content_length - 1
        if range_header:
            match = re.match(r"bytes=(\d+)-(\d*)", range_header)
            if match:
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else content_length - 1

        # 오디오 내용을 BytesIO 객체에 쓰기
        buffer = io.BytesIO(audio_content[start:end+1])

        headers = {
            "Content-Disposition": f"inline; filename={file_name}",
            "Content-Range": f"bytes {start}-{end}/{content_length}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1)
        }

        # BytesIO 객체의 시작 위치를 0으로 되돌립니다.
        buffer.seek(0)

        # 오디오 파일을 StreamingResponse로 반환
        return StreamingResponse(
            content=buffer, headers=headers, media_type="audio/webm",
            status_code=206 if range_header else 200
        )
    except Exception as e:
        logger.error(f"Error processing audio file: {e}")



async def select_audio_info(id: str):
    """audio_files_id 별 audio_files 정보 가져오는 앤드포인트"""
    audio_file = execute_select_query(query=SELECT_AUDIO_FILE, params={"id": id})
    record_time = audio_file[0].record_time
    return record_time
