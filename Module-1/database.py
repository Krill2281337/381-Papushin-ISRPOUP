import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="repair_service",
        cursorclass=pymysql.cursors.DictCursor
    )


def get_user_by_login(login, password):
    connection = get_connection()

    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE login=%s AND password=%s"
        cursor.execute(sql, (login, password))
        user = cursor.fetchone()

    connection.close()
    return user


def get_requests():
    connection = get_connection()

    with connection.cursor() as cursor:
        sql = "SELECT * FROM repair_requests"
        cursor.execute(sql)
        data = cursor.fetchall()

    connection.close()
    return data
def update_status(request_id, status):
    connection = get_connection()

    with connection.cursor() as cursor:
        sql = "UPDATE repair_requests SET requestStatus=%s WHERE requestID=%s"
        cursor.execute(sql, (status, request_id))
        connection.commit()

    connection.close()


def update_parts(request_id, parts):
    connection = get_connection()

    with connection.cursor() as cursor:
        sql = "UPDATE repair_requests SET repairParts=%s WHERE requestID=%s"
        cursor.execute(sql, (parts, request_id))
        connection.commit()

    connection.close()