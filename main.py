from s1 import s1_crawler
from faleno import faleno_crawler
from ideapocket import ideapocket_crawler
from moodyz import moodyz_crawler


if __name__ == '__main__':

    sql_password = input('Enter a MySQL password: ')

    s1_crawler.main(sql_password)
    faleno_crawler.main(sql_password)
    ideapocket_crawler.main(sql_password)
    moodyz_crawler.main(sql_password)