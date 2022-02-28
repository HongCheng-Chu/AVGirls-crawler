import pymysql
from pymysql import cursors


def create_database(sql_password):

    try:
        conn = pymysql.connect(host='localhost',
                           user='root',
                           password= sql_password,
                           cursorclass=pymysql.cursors.DictCursor,
                           charset='utf8')
    except:
        print('Connect fail')

    cursor = conn.cursor()

    sql = "create database if not exists avgirls"

    cursor.execute(sql)

    conn.close()

    return 'avgirls'


def save_data(videos, company, sql_password):

    sql_database = create_database(sql_password)

    try:
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password= sql_password,
                               database= sql_database,
                               cursorclass=pymysql.cursors.DictCursor, # 以字典的形式返回操作結果
                               charset='utf8')
    except:
        print('Connect fail')

    cursor = conn.cursor()

    try:
        sql = "create table if not exists {0}(\
               day varchar(50),\
               number varchar(50),\
               name varchar(50),\
               title varchar(250),\
               cover varchar(250),\
               company varchar(50)\
               )engine=InnoDB DEFAULT CHARSET=utf8;".format(company)

        cursor.execute(sql)
        conn.commit()

    except:
        conn.rollback()

    for video in videos:  

        sql = "insert into {0} (day, number, name, title, cover, company) values (%s, %s, %s, %s, %s, %s)".format(company)

        val = (video['day'], video['number'], video['name'], video['title'], video['cover'], video['company'])

        try:
            cursor.execute(sql, val)
            conn.commit()

        except:
            conn.rollback()
        
    conn.close()


def check_day(name, company, sql_password):

    sql_database = create_database(sql_password)

    try:
        connection = pymysql.connect(host='localhost',
                               user='root',
                               password= sql_password,
                               database= sql_database,
                               cursorclass=pymysql.cursors.DictCursor,
                               charset='utf8')
    except:
        print('Connect fail')

    cursor = connection.cursor()

    try:
        sql = "select day from {0} where name = '{1}' order by day desc".format(company, name)

        cursor.execute(sql)

        recent_day = cursor.fetchone()

    except:

        recent_day = ''

        print('Can not find {0} table or get recent update day'.format(company))

    connection.close()

    return recent_day


def save_actresslist(girls, sql_password):

    sql_database = create_database(sql_password)

    try:
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password= sql_password,
                               database= sql_database,
                               cursorclass=pymysql.cursors.DictCursor,
                               charset='utf8')
    except:
        print('Connect fail')

    cursor = conn.cursor()

    try:
        sql = "create table if not exists actresslist(\
               headshot varchar(300),\
               jp varchar(10),\
               en varchar(20),\
               ch varchar(10),\
               birth varchar(20),\
               company varchar(20),\
               body varchar(20),\
               primary key (jp)\
               )engine=InnoDB DEFAULT CHARSET=utf8;"

        cursor.execute(sql)
        conn.commit()

    except:
        conn.rollback()

    for girl in girls:

        sql = "select jp from actresslist where jp = '{0}'".format(girl['jp'])
        actress = cursor.execute(sql)

        if actress:
            sql = "update actresslist set headshot=%s, en=%s, ch=%s, birth=%s, company=%s, body=%s where jp = '{0}'".format(girl['jp'])

            val = (girl['headshot'], girl['en'], girl['ch'], girl['birth'], girl['company'], girl['body'])

            cursor.execute(sql, val)
            conn.commit()

        else:
            sql = "insert into actresslist (headshot, jp, en, ch, birth, company, body) values (%s, %s, %s, %s, %s, %s, %s)"

            val = (girl['headshot'], girl['jp'], girl['en'], girl['ch'], girl['birth'], girl['company'], girl['body'])

            cursor.execute(sql, val)
            conn.commit()

    conn.close()