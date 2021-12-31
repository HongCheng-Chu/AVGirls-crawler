import json
import os
import pymysql
from pymysql import cursors
from datetime import datetime


def create_database(sql_password):

    try:
        connection = pymysql.connect(host='localhost',
                           user='root',
                           password= sql_password,
                           cursorclass=pymysql.cursors.DictCursor,
                           charset='utf8')
        if connection:
            print('Connect success')
    except:
        print('Connect fail')

    cursor = connection.cursor()

    try:
        sql = "create database if not exists avgirls"

        cursor.execute(sql)

        print('Create avgirls database success')

    except:
        print('Already has avgirls database')

    connection.close()

    return 'avgirls'


def sql_saved(videos, company):

    sql_password = input('sql password : ')

    sql_database = create_database(sql_password)

    try:
        # 建立Connection物件
        connection = pymysql.connect(host='localhost',
                               user='root',
                               password= sql_password,
                               database= sql_database,
                               cursorclass=pymysql.cursors.DictCursor, # 以字典的形式返回操作結果
                               charset='utf8')
        if connection:
            print('Connect success')
    except:
        print('Connect fail')

    cursor = connection.cursor()

    try:
        sql = "create table if not exists {0}(\
               day varchar(50),\
               number varchar(50) not null,\
               name varchar(50),\
               title varchar(250),\
               video varchar(250),\
               company varchar(50),\
               primary key (number)\
               )engine=InnoDB DEFAULT CHARSET=utf8;".format(company)

        cursor.execute(sql)

        connection.commit()

        print('Create vidoes_list success')
    except:
        connection.rollback()
        print('Already have vidoes_list')

    for video in videos:  

        sql = "insert into {0} (day, number, name, title, video, company) VALUES (%s, %s, %s, %s, %s, %s)".format(company)

        val = (video['day'], video['number'], video['name'], video['title'], video['video'], video['company'])
        
        try:
            # 執行sql
            cursor.execute(sql, val)

            # 提交到數據庫
            connection.commit()

            print('{0} save success in {1} list'.format(video['title'], company))
        except:
            # 發生錯誤跳回
            connection.rollback()

            print('{0} already save in {1} list'.format(video['title'], company))

    connection.close()


def check_day(name, company):

    sql_password = input('sql password : ')

    sql_database = create_database(sql_password)

    try:
        connection = pymysql.connect(host='localhost',
                               user='root',
                               password= sql_password,
                               database= sql_database,
                               cursorclass=pymysql.cursors.DictCursor,
                               charset='utf8')
        if connection:
            print('Connect success')
    except:
        print('Connect fail')

    cursor = connection.cursor()

    try:
        sql = "select day from {0} where name = '{1}' order by day desc".format(company, name)

        cursor.execute(sql)

        recent_day = cursor.fetchone()

        print('get recent update day success')

    except:
        connection.rollback()

        recent_day = ''

        print('Can not find {0} table or get recent update day'.format(company))

    return recent_day