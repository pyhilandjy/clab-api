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
    WHERE audio_files.status = 'READY'
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
SELECT text_edited, id
FROM stt_data
WHERE stt_data.audio_files_id = :audio_files_id
    """
)

SELECT_STT_DATA_BETWEEN_DATE = text(
    """
    SELECT 
        stt_data.*
    FROM 
        stt_data
    INNER JOIN audio_files ON stt_data.audio_files_id = audio_files.id
    INNER JOIN user_missions ON audio_files.user_missions_id = user_missions.id
    WHERE 
        user_missions.user_reports_id = :user_reports_id and audio_files.is_used= true;
"""
)


SELECT_STT_DATA_USER_REPORTS = text(
    """
    SELECT 
        stt_data.*
    FROM 
        stt_data
    INNER JOIN audio_files ON stt_data.audio_files_id = audio_files.id
    INNER JOIN user_missions ON audio_files.user_missions_id = user_missions.id
    WHERE 
        user_missions.user_reports_id = :user_reports_id and audio_files.is_used= true;
"""
)


# 새로운 reports

SELECT_USER_REPORTS_INFO = text(
    """
    SELECT DISTINCT
    ur.user_id,
    r.title,
    p.plan_name,
    c.first_name,
    c.birth_date
FROM user_reports ur
JOIN reports r ON ur.reports_id = r.id
JOIN plans p ON r.plans_id = p.id
JOIN user_missions um ON ur.id = um.user_reports_id
JOIN user_plans up ON um.user_plans_id = up.id
JOIN user_children c ON up.user_children_id = c.id
WHERE user_reports_id = :user_reports_id;
    """
)

# 표지
SELECT_COVER_DATA = text(
    """
WITH 
missions_data AS (
    SELECT 
        DISTINCT um.user_id,
        um.user_plans_id,
        um.id AS user_missions_id
    FROM user_missions um
    WHERE um.user_reports_id = :user_reports_id
),

audio_data AS (
    SELECT 
        md.user_id,
        MIN(af.created_at) AS record_start_date,
        MAX(af.created_at) AS record_end_date,
        SUM(af.record_time) AS record_time_sum
    FROM audio_files af
    INNER JOIN missions_data md
        ON af.user_missions_id = md.user_missions_id
    GROUP BY md.user_id
),

children_data AS (
    SELECT 
        DISTINCT uc.first_name,
        up.user_id
    FROM user_children uc
    INNER JOIN user_plans up
        ON uc.id = up.user_children_id
    INNER JOIN missions_data md
        ON up.id = md.user_plans_id
),

reports_data AS (
    SELECT 
        DISTINCT r.title AS reports_title,
        ur.id AS user_reports_id
    FROM reports r
    INNER JOIN user_reports ur
        ON r.id = ur.reports_id
    WHERE ur.id = :user_reports_id
)

SELECT DISTINCT
    md.user_id,
    cd.first_name AS user_children_first_name,
    ad.record_start_date,
    ad.record_end_date,
    ad.record_time_sum,
    rd.reports_title
FROM missions_data md
INNER JOIN audio_data ad
    ON md.user_id = ad.user_id
INNER JOIN children_data cd
    ON md.user_id = cd.user_id
INNER JOIN reports_data rd
    ON rd.user_reports_id = :user_reports_id;
    """
)

# Wordcloud
INSERT_WORDCLOUD_DATA = text(
    """
    INSERT INTO user_wordcloud (user_reports_id, data) VALUES 
    (
        :user_reports_id,
        :data
    )
    """
)

SELECT_WORDCLOUD_DATA = text(
    """
    SELECT data, insights FROM user_wordcloud
    WHERE user_reports_id = :user_reports_id
    """
)


UPDATE_WORDCLOUD_DATA = text(
    """
    UPDATE user_wordcloud 
    SET data = :data , insights = :insights
    WHERE user_reports_id = :user_reports_id
    """
)


DELETE_WORDCLOUD_DATA = text(
    """
    DELETE FROM user_wordcloud
    WHERE user_reports_id = :user_reports_id
    """
)

# violinplot


INSERT_SENTENCE_LENGTH_DATA = text(
    """
    INSERT INTO user_sentence_length (user_reports_id, data) VALUES 
    (
        :user_reports_id,
        :data
    )
    """
)


SELECT_SENTENCE_LENGTH_DATA = text(
    """
    SELECT data, insights FROM user_sentence_length
    WHERE user_reports_id = :user_reports_id
    """
)


UPDATE_SENTENCE_LENGTH_DATA = text(
    """
    UPDATE user_sentence_length
    SET insights = :insights
    WHERE user_reports_id = :user_reports_id
    """
)

DELETE_SENTENCE_LENGTH_DATA = text(
    """
    DELETE FROM user_sentence_length
    WHERE user_reports_id = :user_reports_id
    """
)


# 품사 분류
SELECT_POS_RATIO_DATA = text(
    """
    SELECT data, insights FROM user_pos_ratio
    WHERE user_reports_id = :user_reports_id
    """
)

INSERT_POS_RATIO_DATA = text(
    """
    INSERT INTO user_pos_ratio (user_reports_id, data) VALUES 
    (
        :user_reports_id,
        :data
    )
    """
)

UPDATE_POS_RATIO_DATA = text(
    """
    UPDATE user_pos_ratio
    SET insights = :insights
    WHERE user_reports_id = :user_reports_id
    """
)

DELETE_POS_RATIO_DATA = text(
    """
    DELETE FROM user_pos_ratio
    WHERE user_reports_id = :user_reports_id
    """
)


### 문장분류
SELECT_SPEECH_ACT_COUNT = text(
    """

WITH all_acts AS (
    SELECT act_name, mood, id as act_id 
    FROM speech_acts 
    ORDER BY id
),
relevant_audio_files AS (
    SELECT 
        af.id AS audio_files_id
    FROM 
        user_missions um
    JOIN 
        audio_files af ON af.user_missions_id = um.id
    WHERE 
        um.user_reports_id = :user_reports_id
),
all_speakers AS (
    SELECT DISTINCT 
        sd.speaker
    FROM 
        stt_data sd
    JOIN 
        relevant_audio_files raf ON sd.audio_files_id = raf.audio_files_id
),
all_combinations AS (
    SELECT
        a.act_name,
        a.mood,
        a.act_id,
        s.speaker
    FROM
        all_acts a
    CROSS JOIN
        all_speakers s
)
SELECT
    ac.act_name,
    ac.mood,
    ac.speaker,
    COALESCE(cnt.count, 0) AS count
FROM
    all_combinations ac
LEFT JOIN (
    SELECT
        sa.act_name,
        sa.mood,
        sd.speaker,
        COUNT(sd.act_id) AS count
    FROM
        stt_data sd
    JOIN 
        speech_acts sa ON sd.act_id = sa.id
    JOIN 
        relevant_audio_files raf ON sd.audio_files_id = raf.audio_files_id
    GROUP BY
        sa.act_name,
        sa.mood,
        sd.speaker
) cnt ON ac.act_name = cnt.act_name AND ac.speaker = cnt.speaker
ORDER BY
    ac.act_id,
    ac.speaker;

"""
)

SELECT_SPEECH_ACT_DATA = text(
    """
    SELECT data, insights FROM user_speech_act
    WHERE user_reports_id = :user_reports_id
    """
)

INSERT_SPEECH_ACT_DATA = text(
    """
    INSERT INTO user_speech_act (user_reports_id, data) VALUES 
    (
        :user_reports_id,
        :data
    )
    """
)

UPDATE_SPEECH_ACT_DATA = text(
    """
    UPDATE user_speech_act
    SET insights = :insights
    WHERE user_reports_id = :user_reports_id
    """
)

DELETE_SPEECH_ACT_DATA = text(
    """
    DELETE FROM user_speech_act
    WHERE user_reports_id = :user_reports_id
    """
)


# 인사이트

SELECT_INSIGHT_DATA = text(
    """
    SELECT * FROM user_insight
    WHERE user_reports_id = :user_reports_id
    ORDER BY reports_order ASC
    """
)


UPSERT_INSIGHT_DATA = text(
    """
    INSERT INTO user_insight (
        id,
        user_reports_id,
        reports_order,
        title,
        text,
        insight,
        example
    ) VALUES (
        COALESCE(:id, gen_random_uuid()),
        :user_reports_id,
        :reports_order,
        :title,
        :text,
        :insight,
        :example
    )
    ON CONFLICT (id) DO UPDATE 
    SET
        user_reports_id = EXCLUDED.user_reports_id,
        reports_order = EXCLUDED.reports_order,
        title = EXCLUDED.title,
        text = EXCLUDED.text,
        insight = EXCLUDED.insight,
        example = EXCLUDED.example
    RETURNING id;
    """
)


####
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
UPDATE_AUDIO_FILES_IS_EDIT = text(
    """
UPDATE audio_files
SET is_edited = :is_edited, edited_at= :edited_at
WHERE id = :audio_files_id;
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
SELECT act_name, id
FROM speech_acts
    """
)

SELECT_ACT_TYPES = text(
    """
    SELECT *
    FROM act_types
    """
)

# SELECT_TALK_MORE = text(
#     """
# SELECT talk_more, *
# FROM talk_more
#     """
# )

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

UPDATE_ACT_ID = text(
    """
    UPDATE stt_data
    SET act_id = :act_id
    WHERE id = :id
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
# report_files 관련 쿼리 삭제 예정
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
    INSERT INTO missions (plans_id, title, day, message, summary)
    VALUES (:plans_id, :title, :day, :message, :summary)
    """
)

UPDATE_MISSION = text(
    """
    UPDATE missions
    SET title = :title,
        day = :day,
        message = :message,
        summary = :summary
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
    INSERT INTO plans (
        plan_name, price, day, start_age_month, end_age_month,
        description, type, tags, category_id, summary, schedule
    ) VALUES (
        :plan_name, :price, :day, :start_age_month, :end_age_month,
        :description, :type, :tags, :category_id, :summary, :schedule
    )
    RETURNING id
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
        category_id = :category_id,
        summary = :summary,
        schedule = :schedule
    WHERE id = :id
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

UPDATE_PLAN_DESCRIPTION_IMAGE = text(
    """
    UPDATE plans
    SET description_image_name = :description_image_name, "description_image_id" = :description_image_id
    WHERE id = :plans_id
    """
)

UPDATE_PLAN_SCHEDULE_IMAGE = text(
    """
    UPDATE plans
    SET schedule_image_name = :schedule_image_name, "schedule_image_id" = :schedule_image_id
    WHERE id = :plans_id
    """
)

UPDATE_PLAN_THUMBNAIL_IMAGE = text(
    """
    UPDATE plans
    SET thumbnail_image_name = :thumbnail_image_name, "thumbnail_image_id" = :thumbnail_image_id
    WHERE id = :plans_id
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
    SELECT up.id, up.user_id, up.created_at, up.status, p.plan_name
    FROM user_plan up
    JOIN plans p ON up.plans_id = p.id
    WHERE up.user_id = :user_id
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
        insights = :insight
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
    SELECT system_prompt, user_prompt FROM prompts
    where purpose = :purpose
    """
)

UPDATE_PROMPT = text(
    """
    UPDATE prompts
    SET system_prompt = :system_prompt, user_prompt = :user_prompt
    WHERE purpose = :purpose
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


UPDATE_REPORTS_ID_MISSIONS = text(
    """
    UPDATE missions
    SET reports_id = :reports_id
    WHERE id = :missions_id
"""
)

DELETE_REPORTS_ID_MISSIONS = text(
    """
    UPDATE missions
    SET reports_id = null
    WHERE id = :missions_id
"""
)

# SELECT_REPORTS_PAGINATED = text(
#     """
# SELECT DISTINCT ON (user_reports.id)
#     user_reports.id AS user_reports_id,
#     user_reports.user_id AS user_id,
#     user_reports.send_at AS send_at,
#     user_reports.inspection AS inspection,
#     user_reports.inspector AS inspector,
#     user_reports.inspected_at AS inspected_at,
#     user_reports.status AS status,
#     NULL AS user_name,
#     user_children.first_name AS child_name,
#     reports.title AS report_title,
#     plans.plan_name AS plans_name,
#     (SELECT ARRAY_AGG(user_missions.status)
#      FROM user_missions
#      WHERE user_missions.user_reports_id = user_reports.id) AS mission_statuses,
#     (SELECT COUNT(audio_files.id)
#      FROM user_missions
#      JOIN audio_files ON audio_files.user_missions_id = user_missions.id
#      WHERE user_missions.user_reports_id = user_reports.id) AS audio_file_count,
#     (SELECT COALESCE(SUM(audio_files.record_time), 0)
#      FROM user_missions
#      JOIN audio_files ON audio_files.user_missions_id = user_missions.id
#      WHERE user_missions.user_reports_id = user_reports.id) AS total_record_time
# FROM
#     user_reports
# LEFT JOIN (
#     SELECT DISTINCT ON (user_reports_id) *
#     FROM user_missions
#     ORDER BY user_reports_id, created_at DESC
# ) user_missions ON user_missions.user_reports_id = user_reports.id
# LEFT JOIN user_plans ON user_missions.user_plans_id = user_plans.id
# LEFT JOIN plans ON user_plans.plans_id = plans.id
# LEFT JOIN user_children ON user_plans.user_children_id = user_children.id
# LEFT JOIN reports ON user_reports.reports_id = reports.id
# WHERE
#     {where_clause}
# ORDER BY user_reports.id, user_reports.send_at DESC
# LIMIT :limit OFFSET :offset;
# """
# )
SELECT_TOTAL_COUNT = text(
    """
SELECT COUNT(*) AS total_count FROM user_reports;
"""
)

SELECT_REPORTS_AUDIO_FILES = text(
    """
SELECT
    audio_files.id AS audio_file_id,
    audio_files.created_at AS record_date,
    audio_files.record_time AS record_time,
    missions.title AS mission_title,
    audio_files.is_used AS is_used,
    audio_files.is_edited AS is_edited,
    audio_files.edited_at AS edited_at
FROM
    audio_files
    JOIN user_missions ON audio_files.user_missions_id = user_missions.id
    JOIN missions ON user_missions.missions_id = missions.id
WHERE
    user_missions.user_reports_id = :user_reports_id
ORDER BY
    audio_files.created_at DESC;
"""
)

UPDATE_AUDIO_FILE_IS_USED = text(
    """
    UPDATE audio_files
    SET is_used = :is_used
    WHERE id = :audio_file_id
    """
)

UPDATE_USER_REPORTS_INSPECTION = text(
    """
    UPDATE user_reports
    SET inspection = :inspection,
        inspected_at = :inspected_at,
        status = :status
    WHERE id = :user_reports_id
    """
)

UPDATE_USER_REPORTS_INSPECTOR = text(
    """
    UPDATE user_reports
    SET inspector = :inspector
    WHERE id = :user_reports_id
    """
)

SELECT_AUDIO_INFO = text(
    """
    SELECT 
        af.record_time, 
        m.title AS mission_title,
        af.created_at,
        uc.first_name AS first_name,
        uc.birth_date
    FROM 
        audio_files af
    INNER JOIN 
        user_missions um 
        ON af.user_missions_id = um.id
    INNER JOIN 
        missions m 
        ON um.missions_id = m.id
    INNER JOIN 
        user_plans up
        ON um.user_plans_id = up.id
    INNER JOIN 
        user_children uc
        ON up.user_children_id = uc.id
    WHERE 
        af.id = :audio_files_id
    """
)

SELECT_TALK_MORE = text(
    """
WITH all_talk_mores AS (
    SELECT 
        talk_more, 
        id AS talk_more_id 
    FROM 
        talk_more 
    ORDER BY 
        id
)
SELECT 
    talk_more_id, 
    talk_more
FROM 
    all_talk_mores;
"""
)

UPDATE_AUDIO_FILE_PATH = text(
    """
    UPDATE audio_files
    SET file_path = :file_path
    WHERE id = :audio_files_id
    """
)
