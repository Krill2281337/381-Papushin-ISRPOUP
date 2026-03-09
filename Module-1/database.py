import pymysql
from pymysql.err import ProgrammingError


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "repair_service",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def _fetch_one(sql, params=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()
    finally:
        connection.close()


def _fetch_all(sql, params=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
    finally:
        connection.close()


def _execute(sql, params=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.rowcount
    finally:
        connection.close()


def _column_exists(table_name: str, column_name: str) -> bool:
    row = _fetch_one(
        """
        SELECT COUNT(*) AS cnt
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table_name, column_name),
    )
    return bool(row and row["cnt"])


def get_user_by_login(login, password):
    return _fetch_one(
        "SELECT * FROM users WHERE login = %s AND password = %s",
        (login, password),
    )


def get_user_by_id(user_id: int):
    return _fetch_one("SELECT * FROM users WHERE userID = %s", (user_id,))



def get_client_by_id(client_id: int):
    return get_user_by_id(client_id)



def get_masters():
    return _fetch_all(
        "SELECT userID, fio FROM users WHERE type = 'Мастер' ORDER BY fio"
    )



def _base_request_query():
    return """
        SELECT
            rr.*, 
            c.fio AS clientFIO,
            c.login AS clientLogin,
            m.fio AS masterFIO
        FROM repair_requests rr
        LEFT JOIN users c ON c.userID = rr.clientID
        LEFT JOIN users m ON m.userID = rr.masterID
    """



def get_all_requests():
    return _fetch_all(_base_request_query() + " ORDER BY rr.requestID DESC")



def get_master_requests(master_id):
    return _fetch_all(
        _base_request_query() + " WHERE rr.masterID = %s ORDER BY rr.requestID DESC",
        (master_id,),
    )



def get_client_requests(client_id):
    return _fetch_all(
        _base_request_query() + " WHERE rr.clientID = %s ORDER BY rr.requestID DESC",
        (client_id,),
    )



def get_request_by_id(request_id: int):
    return _fetch_one(
        _base_request_query() + " WHERE rr.requestID = %s",
        (request_id,),
    )



def update_status(request_id, status):
    return _execute(
        "UPDATE repair_requests SET requestStatus = %s WHERE requestID = %s",
        (status, request_id),
    )



def update_parts(request_id, parts):
    return _execute(
        "UPDATE repair_requests SET repairParts = %s WHERE requestID = %s",
        (parts, request_id),
    )



def create_request(homeTechType, homeTechModel, problemDescription, clientID):
    return _execute(
        """
        INSERT INTO repair_requests
        (homeTechType, homeTechModel, problemDescription, clientID, requestStatus, startDate)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """,
        (homeTechType, homeTechModel, problemDescription, clientID, "Новая заявка"),
    )



def update_client_request(request_id: int, client_id: int, homeTechType: str, homeTechModel: str, problemDescription: str):
    return _execute(
        """
        UPDATE repair_requests
        SET homeTechType = %s,
            homeTechModel = %s,
            problemDescription = %s
        WHERE requestID = %s AND clientID = %s AND requestStatus = 'Новая заявка'
        """,
        (homeTechType, homeTechModel, problemDescription, request_id, client_id),
    )



def assign_master(request_id, master_id):
    return _execute(
        "UPDATE repair_requests SET masterID = %s WHERE requestID = %s",
        (master_id, request_id),
    )



def add_comment(request_id, master_id, comment):
    return _execute(
        "INSERT INTO comments (requestID, masterID, commentText) VALUES (%s, %s, %s)",
        (request_id, master_id, comment),
    )



def extend_deadline(request_id, new_deadline):
    column_name = "deadline" if _column_exists("repair_requests", "deadline") else None
    if not column_name and _column_exists("repair_requests", "completionDate"):
        column_name = "completionDate"
    if not column_name:
        return 0
    return _execute(
        f"UPDATE repair_requests SET {column_name} = %s WHERE requestID = %s",
        (new_deadline, request_id),
    )



def search_requests(number=None, status=None, search_text=None):
    sql = _base_request_query() + " WHERE 1=1"
    params = []

    if number:
        sql += " AND rr.requestID = %s"
        params.append(number)
    if status:
        sql += " AND rr.requestStatus = %s"
        params.append(status)
    if search_text:
        sql += " AND (rr.homeTechType LIKE %s OR rr.homeTechModel LIKE %s OR rr.problemDescription LIKE %s OR c.fio LIKE %s)"
        like_value = f"%{search_text}%"
        params.extend([like_value, like_value, like_value, like_value])

    sql += " ORDER BY rr.requestID DESC"
    return _fetch_all(sql, params)



def get_statistics():
    total_row = _fetch_one("SELECT COUNT(*) AS total FROM repair_requests")
    completed_row = _fetch_one(
        "SELECT COUNT(*) AS completed FROM repair_requests WHERE requestStatus = 'Готова к выдаче'"
    )

    fault_stats = _fetch_all(
        """
        SELECT problemDescription, COUNT(*) AS count
        FROM repair_requests
        GROUP BY problemDescription
        ORDER BY count DESC, problemDescription ASC
        LIMIT 10
        """
    )

    tech_stats = _fetch_all(
        """
        SELECT homeTechType, COUNT(*) AS count
        FROM repair_requests
        GROUP BY homeTechType
        ORDER BY count DESC, homeTechType ASC
        """
    )

    avg_days = None
    try:
        date_column = None
        if _column_exists("repair_requests", "deadline"):
            date_column = "deadline"
        elif _column_exists("repair_requests", "completionDate"):
            date_column = "completionDate"

        if date_column:
            avg_row = _fetch_one(
                f"""
                SELECT ROUND(AVG(DATEDIFF({date_column}, startDate)), 2) AS avg_days
                FROM repair_requests
                WHERE requestStatus = 'Готова к выдаче'
                  AND {date_column} IS NOT NULL
                  AND startDate IS NOT NULL
                """
            )
            avg_days = avg_row["avg_days"] if avg_row else None
    except ProgrammingError:
        avg_days = None

    return {
        "total": total_row["total"] if total_row else 0,
        "completed": completed_row["completed"] if completed_row else 0,
        "avg_days": avg_days,
        "fault_stats": fault_stats,
        "tech_stats": tech_stats,
    }



def get_all_users():
    return _fetch_all("SELECT userID, fio, login, type FROM users ORDER BY userID")



def get_all_comments():
    return _fetch_all(
        """
        SELECT c.commentID, c.requestID, c.masterID, c.message AS message
        FROM comments c
        ORDER BY c.commentID DESC
        """
    )



def manager_update_request(request_id, status, master_id, parts):
    return _execute(
        """
        UPDATE repair_requests
        SET requestStatus = %s,
            masterID = %s,
            repairParts = %s
        WHERE requestID = %s
        """,
        (status, master_id, parts, request_id),
    )



def delete_request(request_id: int):
    return _execute("DELETE FROM repair_requests WHERE requestID = %s", (request_id,))



def delete_comment(comment_id: int):
    return _execute("DELETE FROM comments WHERE commentID = %s", (comment_id,))
