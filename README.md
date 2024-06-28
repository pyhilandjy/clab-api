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
```

## Getting Started

```bash
poetry run uvicorn app.main:app --reload --port 2456 --host 0.0.0.0
```

- Mecap설치가 되어있어야 localhost:2456/report/morphs-info/ 가 실행됩니다.
- 설치가 되어있으시다면 로컬에서 실행하시고 설치를 원치 않으시면 docker image build 하시면 됩니다!

## docker

```bash
docker build -t example .
docker run -d -p 2456:2456 --name fastapi_container example
```

## Fast-api Endpoint 구성 정리

1. post(backendUrl + “/audio/upload/”)

- 목적 : user-page에서 녹음을 한 파일을 처리하기 위한 앤드포인트
- 처리과정
  - file_name(bucket에서 이름을 확인하기 위함) 생성
  - file_path(ec2 local, s3 bucket) 생성
  - 오디오 파일 저장 및 메타데이터 db적재
  - file_path로 오디오 파일 불러와 clova_stt에 request, segments db 적재
    - 파일을 던지려고 했는데 clova에서 파일을 받지 않음(backlog)
  - 오디오파일 s3 적재
  - 로컬 임시 오디오파일 삭제
- issue
  - [x] 오디오 파일 저장 후 return을 하는 백그라운드 테스크 적용 X 처리가 끝나고 그 데이터를 사용하여 처리를 하다보니 비동기처리가 안됨.

2. get(backendUrl + “/users/”)

- 목적 : user_id 반환하는 앤드포인트 (audio_files에서의 user_id)

3. get(backendUrl + “/audio/user/{user_id}/files/”)

- 목적 : audio_files의 정보 전체를 반환하는 앤드포인트

4. get(backendUrl + “/stt/data/{file_id}/”)

- 목적 : file_id에 따른 stt_data를 반환하는 앤드포인트

5. patch(backendUrl + “/stt/data/edit-text/”)

- 목적 : file_id에 따른 stt_data의 각 row(pk = id(UUID)) 별로 text_edited의 내용을 수정하여 update하는 앤드포인트

6. post(backendUrl + “/stt/data/add-row/”)

- 목적 : file_id에 따른 stt_data에서 선택된 row의 text_order 를 복제하여 row를 추가
- 처리과정
  - 선택된 row 이후의 text_order를 +1
  - 선택된 row의 데이터를 복제하여 붙여넣기 {selected_text_order +1}
  - except → db.rollback()

7. post(backendUrl + “/stt/data/delete-row/”)

- 목적 : file_id에 따른 stt_data에서 선택된 row의 데이터 삭제
- 처리과정
  - 선택된 row의 데이터 삭제
  - 선택된 row의 이후의 text_order -1
  - except → db.rollback()

8. patch(backendUrl + “/stt/data/replace-text/”)

- 목적 : file_id에 따른 stt_data의 단어를 전체 수정

9. patch(backendUrl + “/stt/data/replace-speaker/”)

- 목적 : file_id에 따른 stt_data의 발화자를 전체 수정

10. get(backendUrl + “/stt/speech_acts/”)

- 목적 : speech_acts(화행)의 정보 전체를 반환하는 앤드포인트

11. patch(backendUrl + “/stt/data/edit-speech-act”)

- 목적 : stt_data의 각 row(pk = id(UUID)) 별로 화행 act_id를 update

12. post(backendUrl + “/report/morphs_info”)
13. post(backendUrl + “/report/wordcloud/”)
14. post(backendUrl + “/report/violinplot/”)
15. post(backendUrl + “/report/images/{image_path}”)
16. post(backendUrl + “/report/data/”)
17. post(backendUrl + “/report/act_count/”)

- 목적 : report에서 필요 내용을 생성하여 반환하는 앤드포인트

18. get(backendUrl + ”/report/title/”)

- 목적 pdf 파일을 갖고오기위한 title 반환 앤드포인트

19. post(backendUrl + ”/report/pdf/”)

- title을 기준으로 file_path조회 후 s3버킷에서 pdf 반환

20. post(backendUrl + ”/report/upload/pdf/”)

- 리포트파일 업로드 앤드포인트(file_name이 한글이면 조회가 안됨 현재 title == 'test'만 가능)

21. post(backendUrl + ”/report/csv/”)

- 리포트 작성시 필요한 데이터 반환 csv
