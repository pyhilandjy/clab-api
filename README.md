## installed

[poetry install local](https://python-poetry.org/docs/#installing-with-the-official-installer)

```bash
poetry install
```

or

```bash
poetry add fastapi
poetry add pydantic-settings
poetry add sqlalchemy
poetry add boto3
poetry add requests
poetry add pydub
poetry add psycopg2-binary
poetry add loguru
poetry add python-jose
poetry add passlib
poetry add pillow
poetry add matplotlib
poetry add pandas
poetry add seaborn
poetry add mecab-ko
poetry add wordcloud
poetry add xlsxwriter
poetry add supabase
poetry add pyjwt
poetry add apscheduler
```

## Getting Started

```bash
poetry run uvicorn app.main:app --reload --port 2456 --host 0.0.0.0
```

- Mecap설치가 되어있어야 localhost:2456/report/morphs-info/ 가 실행됩니다.
- 설치가 되어있으시다면 로컬에서 실행하시고 설치를 원치 않으시면 docker image build 하시면 됩니다.

## docker

```bash
docker build -t example .
docker run -d -p 2456:2456 --name fastapi_container example
```

## Database DDL

```bash
./app/db/DDL.SQL
```

## Fast-api Endpoint 구성 정리

1. POST (backendUrl + “/audio/”)

- 목적: user-page에서 녹음을 한 파일을 처리하기 위한 엔드포인트(for user)

- 요청 헤더:
  authorization (string, header) : 인증 토큰

- 요청 본문:
  audio (string, multipart/form-data): 오디오 파일 (binary 형식)

요청 예시:

```bash
POST /audio/
Content-Type: multipart/form-data
Authorization: Bearer < token >

{
  "audio": < binary data >
}
```

- 처리과정:

  - 오디오 파일 S3 적재
  - 메타데이터 DB 적재 (status = "ready")

- 스케쥴러(10Min):
  - S3 버킷에서 오디오 파일 불러와 webm to m4a 변환
  - 오류 발생 시 (status = "convert_error")
  - clova_stt에 요청하여 응답받은 segments를 DB에 저장
  - 오류 발생 시 (status = "stt_error")
  - 오디오 녹음시간 저장
  - 로컬 임시 오디오 파일 삭제

2. get(backendUrl + “/users/”)

- 목적: Supabase의 Authentication 유저 정보 반환(for admin)

- 요청 헤더: 없음

- 응답 예시:

```bash
[
  {
    "id": "user_id_1",
    "name": "User Name 1",
    "email": "user1@example.com"
  },
  {
    "id": "user_id_2",
    "name": "User Name 2",
    "email": "user2@example.com"
  }
]
```

3. get(backendUrl + “/audio/user/{user_id}/files/”)

- 목적: audio_files의 정보 전체를 반환하는 앤드포인트

- 응답 예시:

```bash
[
  {
    "id": "file_id_1",
    "file_name": "example1"
  },
  {
    "id": "file_id_2",
    "file_name": "example2"
  }
]
```

- 설명: 특정 사용자(user_id)의 모든 오디오 파일 정보를 반환합니다. 반환된 정보에는 파일 ID와 파일 이름이 포함됩니다. 이 정보를 사용하여 사용자의 오디오 파일의 STT데이터를 관리하기 위해 사용됩니다.

4. get(backendUrl + “/stt/data/{file_id}/”)

- 목적: file_id에 따른 stt_data를 반환하는 앤드포인트

- 응답 예시:

```bash
[
  {
    "id": "example_id1",
    "file_id": "example_file_id",
    "act_id": 1,
    "text_order": 1,
    "start_time": 17550,
    "end_time": 19480,
    "text": "Example text 1",
    "confidence": 0.9693,
    "speaker": "1",
    "text_edited": "Edited example text 1",
    "created_at": "2024-07-12T04:51:11.456054",
    "talk_more_id": 1
  },
  {
    "id": "example_id2",
    "file_id": "example_file_id",
    "act_id": 2,
    "text_order": 2,
    "start_time": 19500,
    "end_time": 21400,
    "text": "Example text 2",
    "confidence": 0.9775,
    "speaker": "2",
    "text_edited": "Edited example text 2",
    "created_at": "2024-07-12T04:51:12.456054",
    "talk_more_id": 2
  }
]
```

- 설명: 특정 파일 ID(file_id)에 대한 모든 STT 데이터를 반환합니다. 이 정보를 사용하여 파일의 STT 데이터를 관리할 수 있습니다.

5. patch(backendUrl + “/stt/data/edit-text/”)

- 목적: 특정 파일 ID에 따른 stt_data의 각 row 별로 text_edited를 수정하여 업데이트하는 엔드포인트

- 요청 예시:

```bash
PATCH /stt/data/edit-text/
Content-Type: application/json

{
  "id": "71f09f83-b126-46ff-b89e-6d6b6b90bc58",
  "file_id": "example_file_id",
  "new_text": "Updated example text",
  "new_speaker": "Updated speaker"
}
```

- 설명: 특정 파일 ID에 따른 stt_data의 각 row를 식별하는 ID를 사용하여 text_edited와 speaker를 수정합니다.

6. post(backendUrl + “/stt/data/add-row/”)

- 목적: 특정 파일 ID에 따른 stt_data에서 선택된 row의 text_order를 복제하여 row를 추가하는 엔드포인트

- 요청 예시:

```bash
POST /stt/data/add-row/
Content-Type: application/json

{
  "file_id": "example_file_id",
  "selected_text_order": 1
}
```

- 설명: 이 엔드포인트는 특정 파일 ID에 따른 stt_data에서 선택된 text_order를 복제하여 새로운 row를 추가합니다. 요청 본문에는 파일 ID와 복제할 text_order가 포함되어야 합니다. 이 엔드포인트의 처리 과정은 다음과 같습니다.
  - 선택된 row 이후의 text_order를 +1 증가
  - 선택된 row의 데이터를 복제하여 새로운 row를 추가 (새로운 text_order는 선택된 text_order +1)
- 오류 처리: 오류 발생 시 데이터베이스 롤백을 수행하여 데이터 일관성을 유지합니다.

7. post(backendUrl + “/stt/data/delete-row/”)

- 목적: file_id에 따른 stt_data에서 선택된 row의 데이터 삭제

- 요청 예시:

```bash
POST /stt/data/delete-row/
Content-Type: application/json

{
  "file_id": "example_file_id",
  "selected_text_order": 1
}
```

- 설명: 요청 본문에서 제공된 `file_id`와 `selected_text_order`를 기반으로 해당 row를 복제하고, 그 아래에 새로운 row를 추가합니다.
- 처리 과정:
  1. 선택된 row 이후의 text_order를 +1 증가시킴.
  2. 선택된 row의 데이터를 복제하여 새로운 row를 추가함 (새로운 text_order는 선택된 text_order +1).
  3. 새로운 row에 필요한 추가 정보를 업데이트할 수 있음.
- 오류 처리: 오류 발생 시 데이터베이스 롤백을 수행하여 데이터 일관성을 유지합니다.

8. patch(backendUrl + “/stt/data/replace-text/”)

- 목적: file_id에 따른 stt_data의 단어를 전체 수정

- 요청 예시:

```bash
PATCH /stt/data/replace-text/
Content-Type: application/json

{
  "file_id": "example_file_id",
  "old_text": "old example text",
  "new_text": "new example text"
}
```

- 설명:
  - 이 엔드포인트는 example_file_id로 지정된 파일 내의 old example text를 찾아 new example text로 대체합니다.
  - 모든 해당 텍스트 인스턴스가 새 텍스트로 바뀌며, 이러한 변경 사항은 stt_data 테이블에 저장됩니다.
  - 예를 들어, "Hello"라는 단어를 "Hi"로 바꾸는 경우, 파일에 포함된 모든 "Hello"가 "Hi"로 변경됩니다.

9. patch(backendUrl + “/stt/data/replace-speaker/”)

- 목적: file_id에 따른 stt_data의 발화자를 전체 수정

- 요청 예시:

```bash
PATCH /stt/data/replace-speaker/
Content-Type: application/json

{
  "file_id": "example_file_id",
  "old_speaker": "old speaker name",
  "new_speaker": "new speaker name"
}
```

- 설명:
  - 이 엔드포인트는 `example_file_id`로 지정된 파일 내의 `old speaker name`을 찾아 `new speaker name`으로 대체합니다.
  - 모든 해당 화자 이름이 새 이름으로 변경되며, 이러한 변경 사항은 stt_data 테이블에 저장됩니다.
  - 예를 들어, "John"이라는 화자를 "Jane"으로 바꾸는 경우, 파일에 포함된 모든 "John"이 "Jane"으로 변경됩니다.

10. get(backendUrl + “/stt/speech_acts/”)

- 목적: speech_acts(화행)의 정보 전체를 반환하는 앤드포인트

- 응답 예시:

```bash
[
  {
    "act_name": "example_act",
    "id": 1
  },
  {
    "act_name": "example_act",
    "id": 2
  }
]
```

11. patch(backendUrl + “/stt/data/edit-speech-act”)

- 목적: stt_data의 각 row(pk = id(UUID)) 별로 화행 act_id를 update

- 요청 예시:

```bash
PATCH /stt/data/edit-speech-act/
Content-Type: application/json

{
  "id": "example_id",
  "act_id": 1
}
```

- 설명:
  - 이 엔드포인트는 `example_id`로 지정된 특정 stt_data 행의 화행을 `act_id` 1로 업데이트합니다.
  - `id`는 데이터베이스에서 고유하게 식별되는 행의 ID이며, `act_id`는 새로운 화행을 지정하는 식별자입니다.

12. post(backendUrl + “/report/morphs_info”)
13. post(backendUrl + “/report/wordcloud/”)
14. post(backendUrl + “/report/violinplot/”)
15. post(backendUrl + “/report/images/{image_path}”)
16. post(backendUrl + “/report/data/”)
17. post(backendUrl + “/report/act_count/”)

- 목적: report에서 필요 내용을 생성하여 반환하는 앤드포인트

- 요청 예시:

```bash
POST /report/morphs_inf{request_url}
Content-Type: application/json

{
  "user_id": "example_user_id",
  "start_date": "2024-07-01",
  "end_date": "2024-07-29"
}
```

18. get(backendUrl + ”/reports/”)

- 목적: pdf 파일을 갖고오기위한 title 반환 앤드포인트

- 요청 예시:

```bash
GET /reports/
Authorization: Bearer <user_token>
```

- 응답 예시:

```bash
{
  "id": "example_id",
  "title": "Example Report Title",
  "created_at": "2024-07-29T10:00:00Z"
}
```

- 설명:

  - 이 엔드포인트는 사용자의 인증 토큰을 기반으로, 해당 사용자가 접근할 수 있는 보고서 메타데이터를 반환합니다.

- 작동 방식:
  1. `Authorization` 헤더에서 토큰을 추출하여 사용자 정보를 획득합니다.
  2. 토큰에서 추출된 사용자 ID (`user_id`)를 사용하여 사용자의 보고서 메타데이터를 가져옵니다.

19. get(backendUrl + ”/reports/{report}/”)

- 목적: 주어진 report_id에 해당하는 PDF 파일의 경로를 찾아 S3에서 해당 파일을 불러와 사용자가 User 페이지에서 확인할 수 있도록 하는 엔드포인트

- 요청 예시:

```bash
GET /reports/{report_id}/
```

- 설명:
  - 이 엔드포인트는 report_id를 기반으로 데이터베이스에서 해당 보고서의 메타데이터를 조회하여 PDF 파일의 경로(file_path)를 확인합니다.

20. post(backendUrl + ”/report/”)

- 목적: 관리자(Admin)가 사용자별로 특정 기간 동안 생성한 PDF 리포트를 업로드하고, 이를 S3에 저장하며, 해당 파일의 메타데이터를 기록하는 엔드포인트

- 요청 예시:

```bash
POST /report/
Content-Type: multipart/form-data

{
  "file": <PDF file>,
  "user_id": "example_user_id",
  "start_date": "2024-07-29",
  "end_date": "2024-07-29"
}
```

- 설명:

  - 이 엔드포인트는 관리자가 특정 사용자의 지정된 기간 동안의 데이터를 기반으로 생성한 PDF 파일을 업로드하는 데 사용됩니다.
  - 업로드된 파일의 이름(file.name)이 해당 보고서의 제목(title)이 됩니다.

- 처리 과정:
  1. 사용자 ID 및 기간 정보를 기반으로 임시 파일 경로를 생성하고, 이를 통해 파일 메타데이터를 생성합니다.
  2. 업로드된 PDF 파일을 S3에 저장합니다.
  3. 이후, 사용자는 User 페이지에서 해당 파일을 열람할 수 있습니다.

21. post(backendUrl + ”/report/csv/”)

- 목적: 특정 사용자(user_id)와 기간(start_date, end_date)에 대한 리포트 데이터를 기반으로 CSV 파일을 생성하고 다운로드할 수 있도록 하는 엔드포인트

- 요청 예시:

```bash
POST /report/csv/
Content-Type: application/json

{
  "user_id": "example_user_id",
  "start_date": "2024-07-29",
  "end_date": "2024-07-29"
}
```

- 설명:

  - 이 엔드포인트는 사용자가 지정한 기간 동안의 데이터를 기반으로 다양한 분석 데이터를 수집하고, 이를 CSV 파일로 생성하여 다운로드할 수 있게 합니다.

- 처리과정:

  1.  데이터베이스의 데이터로 다음 데이터를 수집합니다.

  - 형태소 분석 데이터
  - 화행 발생 횟수
  - 문장 길이 정보
  - 녹음된 시간 정보
  - 보고서 생성 날짜 정보
  - 추가 대화 발생 횟수

  2. 필요한 데이터 간 조인을 통해 최종 데이터를 구성합니다.
  3. 데이터는 엑셀 파일로 변환되어 다운로드 가능한 형태로 반환합니다.

22. post(backendUrl + ”/report/stt/data/between_date/”)

- 목적: 특정 사용자(user_id)와 지정된 기간(start_date, end_date) 동안의 stt_data 테이블 데이터를 수집하고, 각 파일의 이름을 시트 이름으로 하여 Excel 파일로 제공하는 엔드포인트

- 요청 예시

```bash
POST /report/stt/data/between_date/
Content-Type: application/json

{
  "user_id": "example_user_id",
  "start_date": "2024-07-29",
  "end_date": "2024-08-05"
}
```

- 설명:

  - 이 엔드포인트는 사용자의 지정된 기간 동안의 stt_data 테이블 데이터를 수집하여 Excel 파일로 생성합니다.

- 처리 과정:
  - user_id와 start_date, end_date를 사용하여 해당 기간 동안의 stt_data를 수집합니다.
  - 수집된 데이터는 각 파일의 이름을 시트 이름으로 하여 Excel 파일에 저장됩니다.

## MVP Issue

- [ ] 아무런 정보가 없는 user를 선택했을 때 데이터가 없는것이 아니라 이전 선택한 유저의 정보가 나옴
- [ ] 녹음을 실수한경우 stt_error가 나오는데 이를 admin에서 확인이 가능해야함
- [ ] report, edit 유동적으로 움직이게 하기
- [ ] 아이의 이름, 인식하지 못하는 단어 사전에 추가하는 기능 (아이의 이름은 db에서 불러와서 리스트로 사전에 넣는 방식으로)
- [ ] 워드클라우드의 생성시 기존 이미지에서 변경이 안될때가 있음 이유는 파일명이 동일해서 캐쉬데이터에서 이전 파일을 불러옴
- [ ] mission 변환시 변경되어야 하는 앤드포인트 정리
- [ ] mission note 테이블 정리
- [ ] turn_in check box
