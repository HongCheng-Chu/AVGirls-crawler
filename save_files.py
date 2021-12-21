import json
import os
import pymysql
from pymysql import cursors
from datetime import datetime


def create_girls_list():

    with open("./s1_GirlsData.json", 'r') as f:
        girls_dict = json.load(f)

    return girls_dict


def create_sql_database(sql_password):

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

    sql = "create database if not exists avgirls"

    cursor.execute(sql)

    print('Create avgirls database success')

    connection.close()

    return 'avgirls'


def create_sql_girls_list(connection, girls_dict, sql_password, sql_database):

    cursor = connection.cursor()

    try:
        sql = "create table if not exists girls_list(\
               jpname varchar(10) not null,\
               enname varchar(30) not null,\
               chname varchar(10),\
               birth varchar(15),\
               company varchar(15),\
               body varchar(30),\
               cup varchar(10),\
               twitter varchar(100),\
               ig varchar(100),\
               primary key (jpname, enname)\
               )engine=InnoDB DEFAULT CHARSET=utf8;"

        cursor.execute(sql)

        connection.commit()

        print('Create girls_list success')
    except:
        connection.rollback()
        print('Already have girls_list')


    for edge in girls_dict['data']['edges']:
        
        sql = "insert into girls_list (jpname, enname, chname, birth, company, body, cup, twitter, ig) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        val = (edge['jpname'], edge['enname'], edge['chname'], edge['birth'], edge['company'], edge['body'], edge['cup'], edge['twitter'], edge['ig'])

        try:
            cursor.execute(sql, val)

            connection.commit()

            print('{0} save success in girls list'.format(edge['jpname']))
        except:
            connection.rollback()

            print('{0} already save in girls list'.format(edge['jpname']))


def sql_saved(videos):

    sql_password = input('sql password : ')

    sql_database = create_sql_database(sql_password)

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

    #girls_dict = create_girls_list()

    #create_sql_girls_list(connection ,girls_dict, sql_password, sql_database)

    cursor = connection.cursor()

    try:
        sql = "create table if not exists videos_list(\
               day varchar(50),\
               number varchar(50) not null,\
               name varchar(50),\
               title varchar(250),\
               img varchar(250),\
               primary key (number)\
               )engine=InnoDB DEFAULT CHARSET=utf8;"

        cursor.execute(sql)

        connection.commit()

        print('Create vidoes_list success')
    except:
        connection.rollback()
        print('Already have vidoes_list')

    for video in videos:  

        sql = "insert into videos_list (day, number, name, title, img) VALUES (%s, %s, %s, %s, %s)"

        val = (video['day'], video['number'], video['name'], video['title'], video['image'])
        
        try:
            # 執行sql
            cursor.execute(sql, val)

            # 提交到數據庫
            connection.commit()

            print('{0} save success in vidoes list'.format(video['name']))
        except:
            # 發生錯誤跳回
            connection.rollback()

            print('{0} already save in vidoes list'.format(video['name']))

    connection.close()


def create_json_by_sql():

    sql_password = input('sql password : ')

    sql_database = create_sql_database(sql_password)

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

    sql = "select * from girls_list"

    cursor.execute(sql)

    profs = cursor.fetchall()

    girls_dict = {'data': {'edges': []}}

    for prof in profs:

        node = {}

        node['jpname'] = prof['jpname']
        node['enname'] = prof['enname']
        node['chname'] = prof['chname']
        node['birth'] = prof['birth']
        node['company'] = prof['company']
        node['body'] = prof['body']
        node['cup'] = prof['cup']
        node['twitter'] = prof['twitter']
        node['ig'] = prof['ig']

        girls_dict['data']['edges'].append(node)

    sql = "select * from videos_list"

    cursor.execute(sql)
        
    videos = cursor.fetchall()
    
    for video in videos:

        node = {}

        edges = girls_dict['data']['edges']

        IsNumberExist = False

        for edge in edges:
            if video['name'] == edge['jpname']:
                edge['videos'] = []
                for item in edge['videos']:
                    if video['number']  == item['number']:
                        IsNumberExist = True
                        break
                if IsNumberExist == False:
                    edge['videos'].append({'day': video['day'], 'number': video['number'], 'title': video['title'], 'img': video['img']})
                    break;
    
    with open("./s1_GirlsData.json", 'w') as f:
        json.dump(girls_dict, f)