from sqlalchemy import text

INSERT_AUDIO_META_DATA = text(
    """
    INSERT INTO audio_files (user_id, file_name, file_path, created_at, record_time) VALUES 
    (
        :user_id,
        :file_name,
        :file_path,
        current_timestamp,
        :record_time
    ) RETURNING id
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
SELECT id, file_name
FROM audio_files f
WHERE f.user_id = :user_id
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
    FROM stt_data sr
    JOIN audio_files af ON sr.file_id = af.id
    WHERE af.user_id = :user_id
        AND sr.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
    ORDER BY sr.created_at ASC, sr.text_order ASC

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
    SET text_edited = :new_text
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

UPDATE_SPEECH_ACT = text(
    """
UPDATE stt_data
SET act_id = :act_id
WHERE id = :id;
"""
)

COUNT_ACT_ID = text(
    """
SELECT
    speech_acts.act_name,
    stt_data.speaker,
    COUNT(stt_data.act_id) AS count
FROM
    stt_data
JOIN
    speech_acts ON stt_data.act_id = speech_acts.id
JOIN
    audio_files f ON stt_data.file_id = f.id
WHERE
    f.user_id = :user_id
    AND stt_data.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
GROUP BY
    speech_acts.act_name,
    stt_data.speaker;

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
