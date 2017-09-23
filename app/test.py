import pymysql
config = {
    "host":"114.215.176.190",
    "port":33069,
    "user":"root",
    "password":"huodao123",
    'cursorclass':pymysql.cursors.DictCursor,
    'charset':"utf-8"
}

conn = pymysql.connect(**config)
cur = conn.cursor()

cur.execute("insert into qp.mng_manager_user(name,password,salt,nick_name,phone,mrid,user_limit,real_name,created_at,updated_at,deleted_at)" +
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",["monster","ssasasasas","test_salt",'nickname',12345678,2,'23,29,30,32,33,34,39','xxxx','2017-8-11 10:14:12','0000-00-00 00:00:00','0000-00-00 00:00:00'])
