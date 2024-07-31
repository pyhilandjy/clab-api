from numbers_parser import Document
import pandas as pd
from app.db.worker import execute_insert_update_query
from sqlalchemy import text

# Numbers 파일 열기
doc = Document("/Users/choi-junyong/Downloads/mission_message.numbers")

# 시트에 접근 (리스트 형식으로 반환되므로 메소드 호출이 아니라 속성 접근으로 해야 합니다)
sheets = doc.sheets

# 시트 내의 테이블에 접근
table = sheets[0].tables[0]

# 데이터를 pandas 데이터프레임으로 변환
data = table.rows(values_only=True)
df = pd.DataFrame(data[1:], columns=data[0])

# 데이터프레임 출력
print(df)


def insert_data_to_db(df: pd.DataFrame):
    for index, row in df.iterrows():
        query = text(
            """
        INSERT INTO missions_message (mission_id, message_type, message)
        VALUES (:mission_id, :message_type, :message)
        """
        )
        params = {
            "mission_id": row["mission_id"],
            "message_type": row["message_type"],
            "message": row["Message"],
        }
        execute_insert_update_query(query, params)


insert_data_to_db(df)
