from sqlalchemy import text

INSERT_AUDIO_META_DATA = text(
    """
    INSERT INTO audio_files (user_id, file_name, file_path, user_mission_ids, created_at) VALUES 
    (
        :user_id,
        :file_name,
        :file_path,
        :user_mission_ids,
        current_timestamp
    )
    """
)

UPDATE_AUDIO_STATUS = text(
    """
    UPDATE audio_files
    SET status = :status
    WHERE id = :audio_files_id
    """
)

UPDATE_RECORD_TIME = text(
    """
    UPDATE audio_files
    SET record_time = :record_time
    WHERE id = :audio_files_id
    """
)

SELECT_AUDIO_FILES = text(
    """
    SELECT * FROM audio_files
    WHERE audio_files.status = 'ready'
"""
)

SELECT_AUDIO_FILE = text(
    """
    SELECT * FROM audio_files
    WHERE audio_files.id = :id
"""
)

INSERT_IMAGE_FILES_META_DATA = text(
    """
INSERT INTO image_files (id, speaker, user_id, start_date, end_date, image_path, type) VALUES 
(
    :image_id, 
    :speaker,
    :user_id,
    :start_date,
    :end_date,
    :image_path,
    :type)
    """
)

SELECT_USERS = text(
    """
SELECT id, *
FROM users
    """
)

SELECT_FILES = text(
    """
SELECT id, file_name, status
FROM audio_files f
WHERE f.user_id = :user_id
ORDER BY file_name DESC
"""
)


INSERT_STT_DATA = text(
    """
INSERT INTO stt_data (audio_files_id, text_order, start_time, end_time, text, confidence, speaker, text_edited, created_at) VALUES 
(
    :audio_files_id, 
    :text_order,
    :start_time,
    :end_time,
    :text,
    :confidence,
    :speaker,
    :text_edited,
    current_timestamp)
    """
)

SELECT_STT_DATA = text(
    """
SELECT *
FROM stt_data sr
WHERE sr.audio_files_id = :audio_files_id
ORDER BY sr.text_order asc
    """
)

SELECT_TEXT_EDITED_DATA = text(
    """
SELECT text_edited, id
FROM stt_data sr
WHERE sr.audio_files_id = :audio_files_id
ORDER BY sr.text_order asc
    """
)

SELECT_LLM_DATA = text(
    """
SELECT text_edited, id, speaker
FROM stt_data sr
WHERE sr.audio_files_id = :audio_files_id
ORDER BY sr.text_order asc
    """
)

SELECT_STT_DATA_BETWEEN_DATE = text(
    """
    SELECT *
    FROM stt_data sd
    JOIN audio_files af ON sd.audio_files_id = af.id
    WHERE af.user_id = :user_id
        AND sd.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
    ORDER BY sd.created_at ASC, sd.text_order ASC

    """
)

SELECT_AUDIO_FILES_BETWEEN_DATE = text(
    """
    SELECT file_name, id
    FROM  audio_files
    WHERE user_id = :user_id
        AND created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
    ORDER BY created_at ASC
    """
)


SELECT_IMAGE_FILES = text(
    """
SELECT image_path
FROM image_files imf
WHERE imf.user_id = :user_id 
  AND imf.start_date = :start_date
  AND imf.end_date = :end_date
  AND imf.type = :type;
"""
)

SELECT_IMAGE_TYPE = text(
    """
SELECT DISTINCT type
FROM image_files
WHERE user_id = :user_id
  AND start_date = :start_date
  AND end_date = :end_date;
"""
)

UPDATE_REPLACE_TEXT_EDITED = text(
    """
    UPDATE stt_data
    SET text_edited = REPLACE(text_edited, :old_text, :new_text)
    WHERE audio_files_id = :audio_files_id
"""
)
UPDATE_REPLACE_SPEAKER = text(
    """
    UPDATE stt_data
    SET speaker = REPLACE(speaker, :old_speaker, :new_speaker)
    WHERE audio_files_id = :audio_files_id
"""
)

UPDATE_TEXT_EDITED = text(
    """
    UPDATE stt_data
    SET text_edited = :new_text, speaker = :new_speaker
    WHERE audio_files_id = :audio_files_id AND id = :id;
    """
)

UPDATE_INCREASE_TEXT_ORDER = text(
    """
UPDATE stt_data
SET text_order = text_order + 1
WHERE audio_files_id = :audio_files_id AND text_order > :selected_text_order
"""
)


INSERT_COPIED_DATA = text(
    """
INSERT INTO stt_data (
    audio_files_id, 
    text_order, 
    start_time, 
    end_time, 
    text, 
    confidence, 
    speaker, 
    text_edited, 
    created_at
)
SELECT
    audio_files_id, 
    :selected_text_order + 1 as text_order,
    start_time, 
    end_time, 
    text, 
    confidence, 
    speaker, 
    text_edited, 
    created_at
FROM
    stt_data
WHERE
    audio_files_id = :audio_files_id AND
    text_order = :selected_text_order;
"""
)


DELETE_ROW = text(
    """
    DELETE FROM stt_data
    WHERE audio_files_id = :audio_files_id AND text_order = :selected_text_order;
    """
)


UPDATE_DECREASE_TEXT_ORDER = text(
    """
    UPDATE stt_data
    SET text_order = text_order - 1
    WHERE audio_files_id = :audio_files_id AND text_order > :selected_text_order;
    """
)

SELECT_SPEECH_ACTS = text(
    """
SELECT act_name, *
FROM speech_acts
    """
)

SELECT_ACT_TYPES = text(
    """
    SELECT *
    FROM act_types
    """
)

SELECT_TALK_MORE = text(
    """
SELECT talk_more, *
FROM talk_more
    """
)

UPDATE_SPEECH_ACT = text(
    """
UPDATE stt_data
SET act_id = :act_id
WHERE id = :id;
"""
)

UPDATE_TALK_MORE = text(
    """
UPDATE stt_data
SET talk_more_id = :talk_more_id
WHERE id = :id;
"""
)

UPDATE_SPEECHACT_TYPE = text(
    """
    UPDATE stt_data
    SET act_id = :act_id, act_types_id = :act_types_id
    WHERE id = :id
    """
)

UPDATE_ACT_TYPE = text(
    """
    UPDATE stt_data
    SET act_types_id = :act_types_id
    WHERE id = :id
    """
)

COUNT_ACT_ID = text(
    """
WITH all_acts AS (
    SELECT act_name, id as act_id FROM speech_acts ORDER BY id
),
all_speakers AS (
    SELECT DISTINCT speaker
    FROM stt_data sd
    JOIN audio_files f ON sd.audio_files_id = f.id
    WHERE f.user_id = :user_id
    AND sd.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
),
all_combinations AS (
    SELECT
        a.act_name,
        a.act_id,
        s.speaker
    FROM
        all_acts a
    CROSS JOIN
        all_speakers s
)
SELECT
    ac.act_name,
    ac.speaker,
    COALESCE(cnt.count, 0) AS count
FROM
    all_combinations ac
LEFT JOIN (
    SELECT
        sa.act_name,
        sd.speaker,
        COUNT(sd.act_id) AS count
    FROM
        stt_data sd
    JOIN
        speech_acts sa ON sd.act_id = sa.id
    JOIN
        audio_files f ON sd.audio_files_id = f.id
    WHERE
        f.user_id = :user_id
        AND sd.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
    GROUP BY
        sa.act_name,
        sd.speaker
) cnt ON ac.act_name = cnt.act_name AND ac.speaker = cnt.speaker
ORDER BY
    ac.act_id,
    ac.speaker;

"""
)


COUNT_TALK_MORE_ID = text(
    """
WITH all_talk_mores AS (
    SELECT talk_more, id as talk_more_id FROM talk_more ORDER BY id
),
all_speakers AS (
    SELECT DISTINCT speaker
    FROM stt_data sd
    JOIN audio_files f ON sd.audio_files_id = f.id
    WHERE f.user_id = :user_id
    AND sd.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
),
all_combinations AS (
    SELECT
        tm.talk_more,
        tm.talk_more_id,
        s.speaker
    FROM
        all_talk_mores tm
    CROSS JOIN
        all_speakers s
)
SELECT
    ac.talk_more,
    ac.speaker,
    COALESCE(cnt.count, 0) AS count
FROM
    all_combinations ac
LEFT JOIN (
    SELECT
        tm.talk_more,
        sd.speaker,
        COUNT(sd.talk_more_id) AS count
    FROM
        stt_data sd
    JOIN
        talk_more tm ON sd.talk_more_id = tm.id
    JOIN
        audio_files f ON sd.audio_files_id = f.id
    WHERE
        f.user_id = :user_id
        AND sd.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
    GROUP BY
        tm.talk_more,
        sd.speaker
) cnt ON ac.talk_more = cnt.talk_more AND ac.speaker = cnt.speaker
ORDER BY
    ac.talk_more_id,
    ac.speaker;
"""
)


# LOGIN = text(
#     """
#     SELECT id, pw, role_id
#     FROM users
#     WHERE id = :id
#     """
# )


SELECT_SENTENCE_LEN = text(
    """
    SELECT 
        sd.speaker,
        MAX(LENGTH(sd.text_edited)) as max_length,
        ROUND(AVG(LENGTH(sd.text_edited))) as avg_length
    FROM stt_data sd
    JOIN audio_files af ON sd.audio_files_id = af.id
    WHERE af.user_id = :user_id
        AND sd.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
    GROUP BY sd.speaker
    """
)

SELECT_RECORD_TIME = text(
    """
    SELECT record_time
    FROM audio_files
    WHERE audio_files.user_id = :user_id
        AND audio_files.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
    """
)


SELECT_USERS = text(
    """
    SELECT DISTINCT user_id
    FROM audio_files;
    """
)

INSERT_REPORT_META_DATA = text(
    """
    INSERT INTO report_files (user_id, title, file_path) VALUES 
    (
        :user_id,
        :title,
        :file_path
    ) RETURNING id
    """
)

UPDATE_REPORTS_ID = text(
    """
    UPDATE audio_files
    SET reports_id = :new_reports_id
    WHERE user_id = :user_id
    AND created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day';
    """
)

SELECT_REPORT_METADATA = text(
    """
    SELECT id, title, created_at
    FROM report_files
    WHERE user_id = :user_id;
    """
)

SELECT_REPORT_FILE_PATH = text(
    """
    SELECT file_path
    FROM report_files
    where id = :id
    """
)


INSERT_FILE_PATH_REPORTS_ID = text(
    """
    UPDATE report_files
    SET file_path = :file_path
    WHERE id = :id
    """
)

SELECT_PLANS = text(
    """
    SELECT * FROM plans
    ORDER BY created_at DESC
    """
)

SELECT_PLAN = text(
    """
    SELECT * FROM plans
    WHERE id = :plans_id
    """
)

SELECT_MISSION = text(
    """
    SELECT * FROM missions
    WHERE plans_id = :plans_id
    ORDER BY day ASC;
    """
)

INSERT_MISSION = text(
    """
    INSERT INTO missions (plans_id, title, day, message, summation)
    VALUES (:plans_id, :title, :day, :message, :summation)
    """
)

UPDATE_MISSION = text(
    """
    UPDATE missions
    SET title = :title,
        day = :day,
        message = :message,
        summation = :summation
    WHERE id = :id
    """
)


DELETE_MISSION_MESSAGE = text(
    """
    DELETE FROM missions_message
    WHERE mission_id = :mission_id
    """
)

DELETE_PLAN = text(
    """
    DELETE FROM plans
    WHERE id = :plans_id
    """
)

DELETE_MISSION = text(
    """
    DELETE FROM missions
    WHERE id = :mission_id
    """
)

INSERT_PLANS = text(
    """
    INSERT INTO plans (plan_name, price, day, start_age_month, end_age_month, description, type, tags, category_id)
    VALUES (:plan_name, :price, :day, :start_age_month, :end_age_month, :description, :type, :tags, :category_id)
    """
)

UPDATE_PLANS = text(
    """
    UPDATE plans
    SET
        plan_name = :plan_name,
        price = :price,
        day = :day,
        start_age_month = :start_age_month,
        end_age_month = :end_age_month,
        description = :description,
        type = :type,
        tags = :tags,
        category_id = :category_id
    WHERE
        id = :id
    """
)

UPDATE_PLAN_STATUS = text(
    """
    UPDATE plans
    SET
        status = :status
    WHERE
        id = :id
    """
)

UPDATE_MISSION_STATUS = text(
    """
    UPDATE missions
    SET
        status = :status
    WHERE
        id = :id
    """
)

SELECT_PLAN = text(
    """
    SELECT * FROM plans
    WHERE id = :plans_id
    """
)

SELECT_PLANS_USER = text(
    """
    SELECT * FROM user_plan
    WHERE user_id = :user_id
    """
)

INSERT_USER_PLAN = text(
    """
    INSERT INTO user_plan (plans_id, user_id, start_at, end_at)
    VALUES (:plans_id, :user_id, :start_at, :end_at)
    """
)

SELECT_SUB_CATEGORY = text(
    """
    select * from category
    where parents_id = :parents_id
"""
)

SELECT_MAIN_CATEGORY = text(
    """
    select * from category
    where parents_id is null
"""
)

SELECT_ALL_CATEGORIES = text(
    """
    select * from category
"""
)

SELECT_REPORTS = text(
    """
    SELECT * FROM reports
    WHERE plans_id = :plans_id
    """
)

SELECT_MISSIONS_TITLE = text(
    """
SELECT id, title from missions
WHERE reports_id = :reports_id
"""
)

DELETE_REPORT = text(
    """
    DELETE FROM reports
    WHERE id = :report_id
    """
)

UPDATE_REPORT = text(
    """
    UPDATE reports
    SET title = :title,
        wordcloud = :wordcloud,
        sentence_length = :sentence_length,
        pos_ratio = :pos_ratio,
        speech_act = :speech_act,
        insight = :insight
    WHERE id = :id
    """
)


INSERT_REPORT = text(
    """
    INSERT INTO reports (plans_id, title, wordcloud, sentence_length, pos_ratio, speech_act, insight)
    VALUES (:plans_id, :title, :wordcloud, :sentence_length, :pos_ratio, :speech_act, :insight)
    RETURNING id
    """
)

SELECT_USER_REPORTS = text(
    """
    SELECT * FROM user_reports
    """
)

UPDATE_IS_TURN = text(
    """
    UPDATE stt_data
    SET is_turn = :is_turn
    WHERE id = :id
    """
)
SELECT_PROMPT = text(
    """
    SELECT prompt FROM prompts
    """
)

INSERT_QURITATIVE_DATA = text(
    """
    INSERT INTO user_report_quritative_data (alternative, description, expectation, mood, stt_data_id) VALUES 
    (
        :alternative,
        :description,
        :expectation,
        :mood,
        :stt_data_id
    )
    """
)


UPDATE_REAPORTS_ID_MISSIONS = text(
    """
    UPDATE missions
    SET reports_id = :reports_id
    WHERE id = :missions_id
"""
)

DELETE_REAPORTS_ID_MISSIONS = text(
    """
    UPDATE missions
    SET reports_id = null
    WHERE id = :missions_id
"""
)
