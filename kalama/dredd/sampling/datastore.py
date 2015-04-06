import pymysql
import config

db = pymysql.connect(**config.db)
