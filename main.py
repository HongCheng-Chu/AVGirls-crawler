from company import s1_crawler
from company import faleno_crawler
from company import ideapocket_crawler
from company import moodyz_crawler


if __name__ == '__main__':

    sql_password = input('Enter a MySQL password: ')

    #s1_crawler.main(sql_password)
    #faleno_crawler.main(sql_password)
    #ideapocket_crawler.main(sql_password)
    moodyz_crawler.main(sql_password)



