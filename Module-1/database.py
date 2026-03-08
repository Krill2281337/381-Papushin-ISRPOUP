import pymysql


# ---------------------------------
# Подключение к базе данных
# ---------------------------------

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="repair_service",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


# ---------------------------------
# Авторизация пользователя
# ---------------------------------

def get_user_by_login(login, password):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
            SELECT * FROM users
            WHERE login = %s AND password = %s
            """

            cursor.execute(sql, (login, password))
            user = cursor.fetchone()

        return user

    finally:
        connection.close()


# ---------------------------------
# Получить ВСЕ заявки
# ---------------------------------

def get_all_requests():
    connection = get_connection()

    with connection.cursor() as cursor:
        sql = "SELECT * FROM repair_requests"
        cursor.execute(sql)
        requests = cursor.fetchall()

    connection.close()
    return requests


# ---------------------------------
# Заявки конкретного мастера
# ---------------------------------

def get_master_requests(master_id):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
            SELECT * FROM repair_requests
            WHERE masterID = %s
            """

            cursor.execute(sql, (master_id,))
            requests = cursor.fetchall()

        return requests

    finally:
        connection.close()


# ---------------------------------
# Заявки конкретного клиента
# ---------------------------------

def get_client_requests(client_id):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
            SELECT * FROM repair_requests
            WHERE clientID = %s
            """

            cursor.execute(sql, (client_id,))
            requests = cursor.fetchall()

        return requests

    finally:
        connection.close()


# ---------------------------------
# Обновление статуса заявки
# ---------------------------------

def update_status(request_id, status):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
            UPDATE repair_requests
            SET requestStatus = %s
            WHERE requestID = %s
            """

            cursor.execute(sql, (status, request_id))

    finally:
        connection.close()


# ---------------------------------
# Добавление / изменение запчастей
# ---------------------------------

def update_parts(request_id, parts):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            sql = """
            UPDATE repair_requests
            SET repairParts = %s
            WHERE requestID = %s
            """

            cursor.execute(sql, (parts, request_id))

    finally:
        connection.close()

def create_request(homeTechType, homeTechModel, problemDescription, clientID):
            connection = get_connection()
            try:
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO repair_requests
                    (homeTechType, homeTechModel, problemDescription, clientID, requestStatus, startDate)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    """
                    cursor.execute(sql, (homeTechType, homeTechModel, problemDescription, clientID, "Новая"))
            finally:
                connection.close()