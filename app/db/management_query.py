from sqlalchemy import text

# user_reports_id로 해당 플랜의 mission을 가져오는 쿼리
USER_REPORT_MISSIONS = text(
    """
WITH mission_data AS (
    SELECT 
        um.user_plans_id
    FROM 
        user_missions um
    WHERE 
        um.user_reports_id = :user_reports_id
),
plan_data AS (
    SELECT 
        up.id AS user_plans_id,
        p.id AS plan_id
    FROM 
        user_plans up
    INNER JOIN 
        plans p
    ON 
        up.plans_id = p.id
    WHERE 
        up.id IN (SELECT user_plans_id FROM mission_data)
),
missions_data AS (
    SELECT 
        m.id AS mission_id,
        m.day,
        m.plans_id
    FROM 
        missions m
    WHERE 
        m.plans_id IN (SELECT plan_id FROM plan_data)
)
SELECT 
    md.mission_id,
    md.day
FROM 
    missions_data md
ORDER BY 
    md.day ASC;
"""
)
# user_reports_id로 해당 플랜의 report를 가져오는 쿼리
USER_REPORT_REPORT = text(
    """

WITH mission_data AS (
    SELECT 
        um.user_plans_id
    FROM 
        user_missions um
    WHERE 
        um.user_reports_id = :user_reports_id
),
plan_data AS (
    SELECT 
        up.id AS user_plans_id,
        p.id AS plan_id
    FROM 
        user_plans up
    INNER JOIN 
        plans p
    ON 
        up.plans_id = p.id
    WHERE 
        up.id IN (SELECT user_plans_id FROM mission_data)
),
reports_data AS (
    SELECT 
        r.id AS report_id,
        r.day,
        r.plans_id
    FROM 
        reports r
    WHERE 
        r.plans_id IN (SELECT plan_id FROM plan_data)
)
SELECT 
    rd.report_id,
    rd.day AS report_day
FROM 
    reports_data rd
ORDER BY 
    rd.day ASC;

"""
)

# user_reports_idfh report_id를 가져오는 쿼리
USER_REPORT_REPORT_ID = text(
    """
SELECT reports_id, user_plans_id
FROM user_reports
WHERE id = :user_reports_id;
"""
)

UPDATE_USER_MISSIONS_IS_OPEN = text(
    """
    UPDATE user_missions
SET is_open = TRUE
WHERE user_plans_id = :user_plans_id
  AND missions_id = :missions_id;
  """
)
