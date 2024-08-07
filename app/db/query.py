from sqlalchemy import text

INSERT_AUDIO_META_DATA = text(
    """
    INSERT INTO audio_files (user_id, file_name, file_path, created_at) VALUES 
    (
        :user_id,
        :file_name,
        :file_path,
        current_timestamp
    )
    """
)

UPDATE_AUDIO_STATUS = text(
    """
    UPDATE audio_files
    SET status = :status
    WHERE id = :file_id
    """
)

UPDATE_RECORD_TIME = text(
    """
    UPDATE audio_files
    SET record_time = :record_time
    WHERE id = :file_id
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
INSERT INTO stt_data (file_id, text_order, start_time, end_time, text, confidence, speaker, text_edited, created_at) VALUES 
(
    :file_id, 
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
WHERE sr.file_id = :file_id
ORDER BY sr.text_order asc
    """
)


SELECT_STT_DATA_BETWEEN_DATE = text(
    """
    SELECT *
    FROM stt_data sd
    JOIN audio_files af ON sd.file_id = af.id
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
    WHERE file_id = :file_id
"""
)
UPDATE_REPLACE_SPEAKER = text(
    """
    UPDATE stt_data
    SET speaker = REPLACE(speaker, :old_speaker, :new_speaker)
    WHERE file_id = :file_id
"""
)

UPDATE_TEXT_EDITED = text(
    """
    UPDATE stt_data
    SET text_edited = :new_text, speaker = :new_speaker
    WHERE file_id = :file_id AND id = :id;
    """
)

UPDATE_INCREASE_TEXT_ORDER = text(
    """
UPDATE stt_data
SET text_order = text_order + 1
WHERE file_id = :file_id AND text_order > :selected_text_order
"""
)


INSERT_COPIED_DATA = text(
    """
INSERT INTO stt_data (
    file_id, 
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
    file_id, 
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
    file_id = :file_id AND
    text_order = :selected_text_order;
"""
)


DELETE_ROW = text(
    """
    DELETE FROM stt_data
    WHERE file_id = :file_id AND text_order = :selected_text_order;
    """
)


UPDATE_DECREASE_TEXT_ORDER = text(
    """
    UPDATE stt_data
    SET text_order = text_order - 1
    WHERE file_id = :file_id AND text_order > :selected_text_order;
    """
)

SELECT_SPEECH_ACTS = text(
    """
SELECT act_name, *
FROM speech_acts
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


COUNT_ACT_ID = text(
    """
WITH all_acts AS (
    SELECT act_name, id as act_id FROM speech_acts ORDER BY id
),
all_speakers AS (
    SELECT DISTINCT speaker
    FROM stt_data sd
    JOIN audio_files f ON sd.file_id = f.id
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
        audio_files f ON sd.file_id = f.id
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
    JOIN audio_files f ON sd.file_id = f.id
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
        audio_files f ON sd.file_id = f.id
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
    JOIN audio_files af ON sd.file_id = af.id
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

UPDATE_REPORT_ID = text(
    """
    UPDATE audio_files
    SET report_id = :new_report_id
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


INSERT_FILE_PATH_REPORT_ID = text(
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

SELECT_MISSION = text(
    """
    SELECT * FROM missions
    WHERE plan_id = :plan_id
    """
)
