class AdminStatement:
    GET_GROUPS = """
        SELECT DISTINCT g.id, g.name
        FROM groups g
        JOIN results r ON g.id = r.group_id
        ORDER BY g.name
    """
    GET_TESTS = """
        SELECT DISTINCT t.id, t.name
        FROM tests t
        JOIN results r ON t.id = r.test_id
        WHERE r.group_id = $1
        ORDER BY t.name
    """
    GET_RESULTS = """
        SELECT DISTINCT ON (s.name, r.user_id) s.name, r.user_id, r.full_name, r.answers, r.points
        FROM students s
        LEFT JOIN results r ON s.id = r.student_id AND r.test_id = $2
        WHERE s.group_id = $1
        ORDER BY s.name, r.user_id, r.points DESC, r.finished_at DESC
    """


class UserStatement:
    GET_GROUPS = "SELECT * FROM groups ORDER BY name"
    GET_STUDENTS = "SELECT id, name FROM students WHERE group_id = $1 ORDER BY name"
    GET_TESTS = "SELECT * FROM tests ORDER BY name"
    GET_TASKS = """
        SELECT id, question, option1, option2, option3, option4
        FROM tasks
        WHERE test_id = $1
        ORDER BY RANDOM()
        LIMIT 30
    """
    ADD_RESULT = """
        INSERT INTO results (
            user_id,
            full_name,
            group_id,
            student_id,
            test_id,
            finished_at,
            answers,
            points,
            feedback
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    """
    GET_SUMMARY = """
        WITH answers AS (
            SELECT
                split_part(a.payload, '-', 1)::INTEGER AS id,
                split_part(a.payload, '-', 2) AS value
            FROM unnest($1::text[]) AS a(payload)
        )
        SELECT
            t.question,
            CASE a.value
                WHEN '1' THEN t.option1
                WHEN '2' THEN t.option2
                WHEN '3' THEN t.option3
                WHEN '4' THEN t.option4
            END AS answer
        FROM answers a
        JOIN tasks t ON t.id = a.id
    """
