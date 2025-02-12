from sqlalchemy import text

SELECT_USER_PLANS = text(
    """
    SELECT up.id AS user_plans_id, up.user_id, up.created_at AS plan_created_at, up.status, p.plan_name
    FROM user_plans up
    JOIN plans p ON up.plans_id = p.id
    """
)

DELETE_USER_PACKAGE = text(
    """
    DELETE FROM user_reports WHERE user_plans_id = :user_plans_id;
    DELETE FROM user_missions WHERE user_plans_id = :user_plans_id;
    DELETE FROM user_plans WHERE id = :user_plans_id;
    """
)
