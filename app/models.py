#coding:utf8
import pymysql
from .config import mysql_option
from random import choice
from hashlib import md5
import random
import copy
import datetime

conn = pymysql.connect(**mysql_option)
cursor = conn.cursor()


def random_salt():

    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    salt = ''
    for i in range(16):
        salt += choice(chars)
    return salt


def check_password(password, salt):
    md5_o = md5()
    md5_o.update(password.encode() + salt.encode())
    return md5_o.hexdigest()


def check_user(user_name):
    conn.ping()
    try:
        cursor.execute("select * from qp.mng_manager_user where name = %s ;",[user_name])
        result = cursor.fetchall()[0]
    except Exception as e:
        print(e)
        return None
    return result


def get_user(user_name):
    conn.ping()
    try:
        cursor.execute("select * from qp.mng_manager_user where muid = %s ;", [user_name])
        result = cursor.fetchall()[0]
    except Exception as e:
        print(e)
        return None
    return result


def change_user(user_id, nick=None, pwd=None):
    conn.ping()
    try:
        if pwd:
            salt = random_salt()
            h_pw = check_password(pwd, salt)
            cursor.execute("update qp.mng_manager_user set password = %s ,salt=%s WHERE muid = %s",[h_pw,salt,user_id])
            conn.commit()
        if nick:
            cursor.execute("update qp.mng_manager_user set nick_name = %s WHERE muid = %s",[nick,user_id])
            conn.commit()
    except Exception as e:
        print(e)
        return False
    return True


def select_user_info(id, type=2):
    conn.ping()
    cursor.execute("select * from qp.mng_manager_user WHERE muid = %s;",[id])
    self_info = cursor.fetchall()

    cursor.execute("select * from qp.med_plat_account where user_id = %s ;", [id])
    account_info = cursor.fetchall()
    cursor.execute("select * from qp.med_flow WHERE user_id = %s ORDER by add_time Desc limit 10;", [id])
    video_info = cursor.fetchall()
    if type == 1:
        # 这里账户是超级管理员
        cursor.execute("select * from qp.mng_manager_user ;")
        qp_user_info = cursor.fetchall()
        self_info[0]['is_admin'] = 1
        return {
            "account_info": account_info,
            "video_info": video_info,
            "qp_user_info": qp_user_info,
            "self_info": self_info,
        }
    self_info[0]['is_admin'] = 0
    return {
        "account_info": account_info,
        "video_info": video_info,
        "self_info":self_info,
    }


def register_user(name, password, nickname, phone=" ",real_name="",mrid=2,user_limit='23,29,30,32,33,34,39'):
    conn.ping()
    salt = random_salt()
    new_pw = check_password(password,salt)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("insert into qp.mng_manager_user(name,password,salt,nick_name,phone,mrid,user_limit,real_name,created_at)" +
                       "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",[name,new_pw,salt,nickname,phone,mrid,user_limit,real_name,date])
        conn.commit()
    except Exception as e:
        print(e)
        return False
    return True


def account():
    conn.ping()
    cursor.execute("select * from qp.mng_plat_info")
    result = cursor.fetchall()
    return {
        "plat_info":result
    }


def add_account(user_id, plat_id, account_name, plat_name=" ", account_login_name=" ", account_login_password=" ", data_url="no test",third_id="123",status=1):
    conn.ping()
    try:
        cursor.execute("replace into qp.med_plat_account" +
                       "(user_id,plat_id,account_name,plat_name,account_login_name,account_login_password,get_data_url,extend,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                       [user_id,plat_id,account_name,plat_name,account_login_name,account_login_password,data_url,third_id,status]
                       )
        conn.commit()
    except Exception as e:
        print(e)
        return False
    return True


def del_account(user_id, plat_id, account_login_name):
    conn.ping()
    account_login_names = str(account_login_name).split(";")
    plat_ids = plat_id.split(";")
    try:
        count = 0
        for i in account_login_names:
            cursor.execute("update qp.med_plat_account set status = 2 WHERE user_id = %s and plat_id = %s and account_login_name = %s; ",[user_id,plat_ids[count],i])
            count += 1
        conn.commit()
    except Exception as e:
        print(e)
        return False
    return True


def select_user_video(user_id=None, plat_id=None, account_name=None,
                      page_count=20, page_num=1,determined='add_time',
                      start=None,end=None,adv_id=None,
                      title=None,tag = None,audit_status=None):
    conn.ping()
    sql_string = "select * from qp.med_flow "
    sql_params = []
    if user_id:
        sql_string += " where user_id = %s"
        sql_params.append(user_id)
    if plat_id:
        if "where" in sql_string:
            sql_string += " and plat_id = %s "
            sql_params.append(plat_id)
        else:
            sql_string += " where plat_id = %s "
            sql_params.append(plat_id)
    if title:
        if "where" in sql_string:
            sql_string += " and title_name like %s "
            sql_params.append("%" + title + "%")
        else:
            sql_string += " where title_name like %s "
            sql_params.append("%" + title + '%')
    if account_name:
        if "where" in sql_string:
            sql_string += " and account_name = %s "
            sql_params.append(account_name)
        else:
            sql_string += " where account_name = %s "
            sql_params.append(account_name)
    if start:
        if "where" in sql_string:
            sql_string += " and add_time > %s "
        else:
            sql_string += " where add_time > %s "
        sql_params.append(start)
    if end:
        if "where" in sql_string:
            sql_string += " and add_time < %s "
        else:
            sql_string += " where add_time < %s "
        sql_params.append(end)
    if adv_id == "0" :
        if "where" in sql_string:
            sql_string += " and adv_id = 0  "
        else:
            sql_string += " where adv_id = 0 "
    if adv_id == "1":
        if "where" in sql_string:
            sql_string += " and adv_id = 1  "
        else:
            sql_string += " where adv_id = 1 "
    if tag:
        if "where" in sql_string:
            sql_string += " and tag = %s  "
        else:
            sql_string += " where tag = %s "
        sql_params.append(tag)
    if audit_status == '3':
        if "where" in sql_string:
            sql_string += " and audit_status = 3  "
        else:
            sql_string += " where audit_status = 3 "
    if audit_status == '1':
        if "where" in sql_string:
            sql_string += " and audit_status = 1  "
        else:
            sql_string += " where audit_status = 1 "
    if audit_status == '2':
        if "where" in sql_string:
            sql_string += " and audit_status = 2  "
        else:
            sql_string += " where audit_status = 2 "
    count_sql = sql_string.replace(r"*", r"sum(flow_count) as total,count(*) as title")
    sql_string += " ORDER BY {0} desc limit %s offset %s ;".format(determined)
    sql_params.append(page_count)

    count = (int(page_num) - 1) * page_count

    sql_params.append(count)
    cursor.execute(sql_string, sql_params)
    result = cursor.fetchall()
    cursor.execute(count_sql, sql_params[0:-2])

    total = cursor.fetchall()

    for i in result:
        try:
            now = i['add_time']
            #st = now - datetime.timedelta(hours=8)
            strft_ = st.strftime("%Y-%m-%d %H:%M:%S")
            i['add_time'] = strft_
        except Exception :
            i['add_time'] = i['add_time'].strftime("%Y-%m-%d %H:%M:%S")
    if total:
        return result, int(total[0]['total'] or 0),int(total[0]["title"] or 0)
    return result,0,0


def change_user_video(flow_id, tag=None, adv_id=None, audit_status=None, user_id=None):
    params = locals()

    try:
        for i in params:
            if params[i]:
                if user_id:
                    cursor.execute('UPDATE qp.med_flow set {0} = %s where user_id = %s and flow_id=%s;'.format(i),[params[i][0],user_id,flow_id[0]])

                else:
                    print(i)
                    print(cursor.mogrify('UPDATE qp.med_flow set {0} = %s where  flow_id=%s;'.format(i),[params[i][0],flow_id[0]]))
                    cursor.execute('UPDATE qp.med_flow set {0} = %s where  flow_id=%s;'.format(i),[params[i][0],flow_id[0]])
                conn.commit()
    except Exception as e:
        print(e)
        return 0
    return 1
    #
    # try:
    #     if user_id:
    #         cursor.execute('UPDATE `qp.med_flow` set tag = %s,adv_id=%s,audit_status=%s where user_id = %s and flow_id=%s;'
    #                        , [tag, adv_id, audit_status, user_id, flow_id])
    #     else:
    #         cursor.execute('UPDATE `qp.med_flow` set tag = %s,adv_id=%s,audit_status=%s where  flow_id=%s;'
    #                        , [tag, adv_id, audit_status, flow_id])
    # except Exception as e:
    #     print(e)
    #     return False
    # return True


def all_flow(user_id,plat_id= None,account_id=None,start=None,end=None,account_name=None,title_name=None):
    conn.ping()
    params = locals()
    sqls = "SELECT count(flow_count) as count_flow ,count(*) as count_title from qp.med_flow "
    sqlp = []
    for i in params:
        if params[i]:
            if i == "end":
                if "where" in sqls:
                    sqls += " and add_time < %s "
                else:
                    sqls += " where add_time < %s "
                sqlp.append(params[i])
            elif i == "start":
                if "where" in sqls:
                    sqls += " and add_time > %s "
                else:
                    sqls += " where add_time > %s "
                sqlp.append(params[i])
            else:
                if "where" in sqls:
                    sqls += " and {0} = %s ".format(i)
                    sqlp.append(params[i])
                else:
                    sqls += " where "
                    sqls += " {0} = %s ".format(i)
                    sqlp.append(params[i])
    cursor.execute(sqls,sqlp)
    return cursor.fetchall()
    # try:
    #     if plat_id:
    #         cursor.execute("SELECT count(flow_count) as count FROM `med_flow` where user_id = %s and plat_id = %s;",[user_id,plat_id])
    #         result = cursor.fetchall()
    #     else :
    #         cursor.execute("SELECT count(flow_count) as count FROM `med_flow` where user_id = %s and plat_id = %s;",[user_id])
    #         result = cursor.fetchall()
    #
    # except Exception as e:
    #     print(e)
    #     return False
    # return result


def all_title(user_id,plat_id=None):
    conn.ping()
    try:
        if plat_id:
            cursor.execute("SELECT count(*) as count FROM `med_flow` where user_id = %s and plat_id = %s;",[user_id,plat_id])
            result = cursor.fetchall()
        else :
            cursor.execute("SELECT count(*) as count FROM `med_flow` where user_id = %s and plat_id = %s;",[user_id])
            result = cursor.fetchall()

    except Exception as e:
        print(e)
        return False
    return result


def all_account(plat_id=None,page=1,count=20,determined=None,user_id=None,account_login_name=None):
    conn.ping()
    params = locals()
    sqls = 'select * from med_plat_account '
    sql_p = []
    for i in params:
        if i =='page' or i == 'count' or i == "determined":
            pass
        if params[i]:
            if "where" in sqls:
                sqls += "and {0} = %s".format(i)
                sql_p.append(params[i])
            else :
                sqls += " where"
                sqls += "{0} = %s".format(i)
                sql_p.append(params[i])
    sqls += "  limit %s offset %s;"
    sql_p.append(count)
    sql_p.append(count * page)
    cursor.execute(sqls,sql_p)
    return cursor.fetchall()


def all_tag():
    conn.ping()
    cursor.execute("select tag_name,tag_value from qp.tag_value")
    return cursor.fetchall()


def chioce(user_id):
    conn.ping()
    cursor.execute("select distinct account_name,plat_name,plat_id,user_id,mng_manager_user.`name` " +
                           "from qp.med_plat_account as a INNER  JOIN qp.mng_manager_user  on qp.mng_manager_user.muid = a.user_id and a.user_id = %s and a.plat_id is not null;",
                           [user_id])
    users = cursor.fetchall()
    return users


#

def plat_and_user():
    conn.ping()
    cursor.execute("select * from qp.mng_plat_info")
    plats = cursor.fetchall()
    cursor.execute("select * from qp.mng_manager_user  ")
    users = cursor.fetchall()
    return {
        "plat":plats,
        "user":users
    }


def select_account(user_id=None, plat_id=None):
    conn.ping()
    sqls = "select * from qp.med_plat_account  "
    sqlp = []
    if user_id:
        sqls += " where user_id = %s "
        sqlp.append(user_id)
    if plat_id:
        if "where" in sqls:
            sqls += " and plat_id = %s "
            sqlp.append(plat_id)
        else:
            sqls += " where plat_id = %s "
            sqlp.append(plat_id)
    if "where" in sqls:
        sqls += " and status in (0,1) "
    else:
        sqls += " where status in (0,1) "
    cursor.execute(sqls, sqlp)
    accounts = cursor.fetchall()
    return accounts


def plat_info():
    conn.ping()
    cursor.execute("select * from qp.mng_plat_info")
    plats = cursor.fetchall()
    return plats

def all_dates(start,end):
    delta =0
    arr1 = start.split("-")
    arr2 = end.split("-")
    arr1 = [int(i) for i in arr1]
    arr2 = [int(i) for i in arr2]

    d1 = datetime.datetime(arr1[0],arr1[1], arr1[2])
    d2 = datetime.datetime(arr2[0],arr2[1], arr2[2])
    delta = (d2- d1).days or 0
    if delta == 0:
        return [{"date":start,"total_play":0}],delta
    else:
        dates = []
        dates = [{"date":(d1+datetime.timedelta(days=(i))).strftime("%Y-%m-%d"),"total_play":0} for i in range(delta+1)]
        return dates,delta


def for_secret():
    conn.ping()
    cursor.execute("select * from qp.med_plat_account")
    result = cursor.fetchall()
    return result

def save_code(uid,value):
    try:
        cursor.execute("insert into qp.code_value(uid,value) VALUES(%s,%s)",[uid,value])
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_code(uid):
    cursor.execute("select value from qp.code_value where uid=%s",[uid])
    return cursor.fetchone()


def select_history_video(user_id, plat_id, account_name,
                                        start,end,adv_id, title,
                                        tag ,audit_status):
    conn.ping()

    # d1 = datetime.datetime(2005, 2, 16)
    # d2 = datetime.datetime(2004, 12, 31)
    sql_string = ('select DATE_FORMAT(add_time,"%Y-%m-%d") as date ,'
                    'sum(flow_count) as total_play  '
                    'from qp.med_flow where DATE_FORMAT(add_time,"%Y-%m-%d") >= "{0}" '
                    'and DATE_FORMAT(add_time,"%Y-%m-%d") <= "{1}" '
                    '||| '
                    'group by DATE_FORMAT(add_time,"%Y-%m-%d-> ")').format(start,end)
    sql_plat = ('select plat_name as name,'
                    'sum(flow_count) as value  '
                    'from qp.med_flow where DATE_FORMAT(add_time,"%Y-%m-%d") >= "{0}" '
                    'and DATE_FORMAT(add_time,"%Y-%m-%d") <= "{1}" '
                    'group by plat_name').format(start,end)
    sql_install = "select install_today,update_time from qp.app_count where update_time>= %s and  %s>=update_time order by update_time "

    sql = ''
    condition = ''
    if user_id:
        condition += " and user_id = {}".format(user_id)
    if plat_id:
        condition += " and plat_id = {}".format(plat_id)
    if title:
        condition += " and title_name like '{}'".format(title)
    if account_name:
       condition += " and account_name = '{}'".format(account_name)
    if adv_id :
       condition += " and adv_id = {}".format(adv_id)
    if tag:
       condition += " and tag = {}".format(tag)
    if audit_status :
       condition += " and audit_status = '{}'".format(audit_status)

    sql_string = sql_string.replace("|||",condition)
    dates,delta = all_dates(start,end)

    try:
        print(sql_string)
        cursor.execute(sql_string)
        result = cursor.fetchall()
        cursor.execute(sql_plat)
        plat_data = cursor.fetchall()
        cursor.execute(sql_install,[start,end])
        downloads = cursor.fetchall()
        
        for i in range(len(dates)):
            for j in  range(len(result)):
                if result[j]['date'] == dates[i]['date']:
                    dates[i]['total_play'] = int(result[j]['total_play'].to_eng_string())
            for x in range(len(downloads)):
                print()
                if downloads[x]['update_time'].strftime('%Y-%m-%d') == dates[i]['date']:
                     dates[i]['total_daownload'] = int(downloads[x]['install_today'])
        for plat_ in plat_data:
            plat_['value'] = str(plat_['value'])

        return dates,plat_data
    except Exception as e:
        print(e)
        result = []
        plat_data = []
        return result,plat_data

'''
def select_history_video(user_id, plat_id, account_name,
                                        start,end,adv_id, title,
                                        tag ,audit_status):
    conn.ping()
    print(start,end)

    sql_string = "select install_today,update_time from qp.app_count where update_time>= %s and  %s>=update_time"
    sql_plat = ('select plat_name as name,'
                'sum(flow_count) as value  '
                'from qp.med_flow where add_time>= %s '
                'and add_time<= %s '
                'group by plat_name')

    try:
        cursor.execute(sql_string,[start,end])
        result = cursor.fetchall()
        cursor.execute(sql_plat,[start,end])
        plat_data = cursor.fetchall()
        for i in range(len(plat_data)):
            plat_data[i]['value'] = int(plat_data[i]['value'])
        for j in range(len(result)):
            result[j]['update_time'] = result[j]['update_time'].strftime('%Y-%m-%d')

        return result,plat_data,'success'
    except Exception as e:
        result = []
        plat_data = []
        return result,plat_data,'failed'    
'''