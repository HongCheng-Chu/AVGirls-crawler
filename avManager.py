import pymysql
from pymysql import cursors

class avManager(object):
    """description of class"""
    def __init__(self):
        self.company = None
        self.cookie = None
        self.sql_password = None
        self.lastUpdateDay = None
        self.actress = None


    def _create_db(self):

        db_name = 'avgirls'

        conn = pymysql.connect(host='localhost',
                               user='root',
                               password= self.sql_password)

        cursor = conn.cursor()

        sql = "create database if not exists {}".format(db_name)

        cursor.execute(sql)

        conn.close()

        return db_name


    def save_video(self, videos):

        db_name = self._create_db()

        conn = pymysql.connect(host='localhost',
                               user='root',
                               password= self.sql_password,
                               database= db_name,
                               cursorclass=pymysql.cursors.DictCursor, # 以字典的形式返回操作結果
                               charset='utf8')

        cursor = conn.cursor()

        try:
            create_tabel = "create table if not exists {0}(\
                   day varchar(50),\
                   number varchar(50),\
                   name varchar(50),\
                   title varchar(250),\
                   cover varchar(250),\
                   company varchar(50)\
                   )engine=InnoDB DEFAULT CHARSET=utf8;".format(self.company)

            cursor.execute(create_tabel)
            conn.commit()

        except:
            conn.rollback()

        for video in videos:

            isVideoExist = self._check_video(cursor, video)

            if isVideoExist:

                continue
            
            else:

                video_sql = "insert into {} (day, number, name, title, cover, company) values (%s, %s, %s, %s, %s, %s)".format(self.company)

                video_data = (video['day'], video['number'], video['name'], video['title'], video['cover'], video['company'])

                try:
                    cursor.execute(video_sql, video_data)
                    conn.commit()

                except:
                    conn.rollback()
        
        conn.close()


    def _check_video(self, cursor, video):

        select_video = """select * from {} where name= '{}' and number= '{}' """.format(video['company'], video['name'], video['number'])

        cursor.execute(select_video)

        isVideoExist = cursor.fetchone()

        return isVideoExist


    def get_day(self, girl_name):

        db_name = self._create_db()

        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password= self.sql_password,
                                     database= db_name,
                                     cursorclass=pymysql.cursors.DictCursor,
                                     charset='utf8')

        cursor = connection.cursor()

        try:
            select_girl = "select day from {0} where name = '{1}' order by day desc".format(self.company, girl_name)

            cursor.execute(select_girl)

            last_video_issue_day = cursor.fetchone()

        except:

            last_video_issue_day = ''

            print('Can not find {0} table or get recent update day'.format(self.company))

        connection.close()

        return last_video_issue_day


    def save_actress(self, girls):

        db_name = self._create_db()

        conn = pymysql.connect(host='localhost',
                               user='root',
                               password= self.sql_password,
                               database= db_name,
                               cursorclass=pymysql.cursors.DictCursor,
                               charset='utf8')

        cursor = conn.cursor()

        try:
            actress_table = "create table if not exists actresslist(\
                             headshot varchar(300),\
                             jp varchar(10),\
                             en varchar(20),\
                             ch varchar(10),\
                             birth varchar(20),\
                             company varchar(20),\
                             body varchar(20),\
                             primary key (jp)\
                             )engine=InnoDB DEFAULT CHARSET=utf8;"

            cursor.execute(actress_table)
            conn.commit()

        except:
            conn.rollback()

        for girl in girls:

            girlData = "select jp from actresslist where jp = '{0}'".format(girl['jp'])
            girlProfile = cursor.execute(girlData)

            if girlProfile:

                updateData = "update actresslist set headshot=(%s), en=(%s), ch=(%s), birth=(%s), company=(%s), body=(%s) where jp = '{0}'".format(girl['jp'])

                newProfile = (girl['headshot'], girl['en'], girl['ch'], girl['birth'], girl['company'], girl['body'])

                cursor.execute(updateData, newProfile)
                conn.commit()

            else:
                insertData = "insert into actresslist (headshot, jp, en, ch, birth, company, body) values (%s, %s, %s, %s, %s, %s, %s)"

                newProfile = (girl['headshot'], girl['jp'], girl['en'], girl['ch'], girl['birth'], girl['company'], girl['body'])

                cursor.execute(insertData, newProfile)
                conn.commit()

        conn.close()


