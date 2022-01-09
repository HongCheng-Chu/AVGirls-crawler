from S1 import s1_crawler
from FALENO import faleno_crawler
from IDEAPOCKET import ideapocket_crawler
import savefiles


if __name__ == '__main__':

    sql_password = input('Enter a MySQL password: ')

    s1_crawler.main(sql_password)
    faleno_crawler.main(sql_password)
    ideapocket_crawler.main(sql_password)