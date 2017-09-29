#coding:utf8
from flask import session,Blueprint,request,jsonify,make_response
from functools import wraps
from .. import lm
from .. import models
from flask_login import UserMixin,current_user,login_user,login_required,logout_user
from hashlib import md5
from .. import check_accounts
import threading
import time
v1 = Blueprint("v1", __name__)



def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        rst.headers['withCredentials'] = 'true'
        rst.headers['Access-Control-Allow-Credentials'] = 'true'
        return rst
    return wrapper_fun

'''
    redis 数据结构
    [
        flow_id | plat_id third_id account_id account_name plat_name user_id title_name flow_count add_time url tag adv_id audit_status

        '',
    ]


'''





def check_password(password,salt):
    md5_o = md5()
    md5_o.update(password.encode() + salt.encode())
    return md5_o.hexdigest()



class User(UserMixin):
    pass


@lm.user_loader
def user_loader(user_id):
    user_info = models.get_user(user_id)
    u = User()
    u.id = user_info['muid']
    u.mrid = user_info['mrid']
    u.user_limit = user_info['user_limit']
    u.name = user_info['name']
    return u


@v1.route("/index")
def index():
    return "v1 index"


@v1.route("/checkname", methods=['POST'])
@allow_cross_domain
def checkname():
    name = request.form.get("username")
    user_info = models.get_user(name)
    if user_info:
        return jsonify({
            "status":"success",
            "is_used":True
        })
    return jsonify({
        "status": "success",
        "is_used": False
    })


@v1.errorhandler(404)
def notfound():
    return jsonify({
        "status":"failed",
        "message":"url错误"
    })


@v1.route("/register", methods=['POST'])
@allow_cross_domain
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    nickname = request.form.get("nickname")
    phone = request.form.get("phone") or " "
    real_name = request.form.get("real_name") or " "

    if username and password and nickname:
        result = models.register_user(username,password,nickname,phone,real_name)
        if result:
            return jsonify({
                "status": "success",
                "message": "注册成功"
            })
        else :
            return jsonify({
                "status":"failed",
                "message":"注册失败"
            })
    else:
        return jsonify({
            "status":"failed",
            "message":"参数不全"
        })


@v1.route("/login", methods=['POST'])
@allow_cross_domain
def login():
    user = request.form.get("username")
    pw = request.form.get("password")
    remember_me = request.form.get("remember")
    pw_r = models.check_user(user)
    if pw_r:
        tmp = User()
        tmp.id = pw_r['muid']
        hash_pw = check_password(pw, pw_r['salt'])
        if hash_pw == pw_r['password']:
            user_type = pw_r["mrid"]
            user_info = models.select_user_info(pw_r['muid'],user_type)
            login_user(tmp,remember=remember_me)
            return jsonify({
                "status": "success",
                "user_info": user_info
            })
        else:
            return jsonify({
                "status": "failed",
                "message": "用户不存在或者密码错误"
            })
    return jsonify({
        "status": "failed",
        "message": "用户不存在或者密码错误"
    })


@v1.route("/logout",methods=['POST'])
@allow_cross_domain
def logout():
    logout_user()
    return jsonify({
        "status":"success",
        "message":"logged out"
    })


@lm.unauthorized_handler
def unauthorized():
    return jsonify({
        "status": "failed",
        "message": "out logged ,try login"
    })


@v1.route("/user/account")
@allow_cross_domain
def account():
    result = models.account()
    return jsonify({
        "status":"success",
        "data":result
    })


def handle_plat(plat_id,user_id):
    if plat_id == 6:
        #头条
        return user_id
    elif plat_id == 2:
        #B站
        return "http://space.bilibili.com/ajax/member/getSubmitVideos?mid=" + str(user_id)
    elif plat_id == 3:
        #内涵
        return 'http://lf.snssdk.com/2/essay/zone/user/posts/?user_id=' + str(user_id)
    elif plat_id == 10:
        #美拍
        return "http://www.meipai.com/users/user_timeline?page=1&count=8&category=0&id="  + str(user_id)
    elif plat_id == 12:
        #大鱼
        return str(user_id)
    else:
        return str(user_id)

    [{
        "plat_id":6,
        "plat_name":"今日头条",
        "need_login":"0"

    },
    ]


need_plat_id = []


@v1.route("/user/add_account", methods=['POST'])
@allow_cross_domain
@login_required
def add_account():
    if current_user.mrid == 1:
        user_id = request.form.get("user_id") or current_user.id
    else:
        user_id = current_user.id or request.form.get("user_id")
    #user_id =request.form.get("user_id")
    plat_id = request.form.get("plat_id")
    account_name = request.form.get("account_name")
    plat_name = request.form.get("plat_name")
    account_login_name = request.form.get("account_login_name") or ""
    account_login_password = request.form.get("account_login_password") or ""
    third_id = request.form.get("third_id") or '123'
    data_url = request.form.get("data_url") or 'no data url'
    d_url = handle_plat(plat_id, data_url)
    if plat_id and account_name:
        result = models.add_account(user_id,plat_id,account_name,plat_name,account_login_name,account_login_password, d_url, third_id)
        if result:

            #todo  这里新开一个线程 检测账户密码是否正确
            # thread
            return jsonify({
                "status":"success",
                "message":"成功添加账户"
            })
        return jsonify({
            "status":"failed",
            "message":"添加失败"
        })
    return jsonify({
        "status":"failed",
        "message":"参数不全"
    })


@v1.route("/person")
@allow_cross_domain
@login_required
def person():
    return jsonify({
        "status":"success",
        "message":"you are logged"
    })




# 这里开始是 /user


@v1.route("/user/info",methods=['POST','GET'])
@allow_cross_domain
@login_required
def info_u():
    if request.method == 'GET':
        user_type = current_user.mrid
        user_id = current_user.id
        user_info = models.select_user_info(user_id,user_type)
        return jsonify(user_info)
    else:
        # params  nickname 昵称  password 密码
        nick = request.form.get("nickname")
        pwd = request.form.get("password")
        user_id = request.form.get("user_id")
        if nick or pwd:
            if current_user.mrid == 1:
                user_id = user_id or current_user.id
            else:
                user_id = current_user.id
            status = models.change_user(user_id,nick,pwd)
            user_info = models.select_user_info(user_id)

            if status:
                return jsonify({
                    "status": "success",
                    "messgae": "修改成功",
                    "user_info":user_info
                })
            return jsonify({
                "status": "failed",
                "message": "数据库操作失败"
            })
        return jsonify({
            "status":"failed",
            "message":"参数不全"
        })

@v1.route("/user/del_account",methods=['POST'])
@allow_cross_domain
@login_required
def user_del_account():
    # params     普通用户 plat_id account_login_name  管理员  user_id plat_id  account_login_name  account_login_name之间用;隔开,多个plat_id之间用;隔开
    user_type = current_user.mrid
    params = request.form
    plat_id = params.get("plat_id")
    login_name = params.get("account_login_name")
    type = params.get("type")
    if user_type == 1:
        # 这里是 超级管理员
        user_id = params.get("user_id") or current_user.id
    else:
        user_id = current_user.id
    status = models.del_account(user_id, plat_id, login_name)
    if status:
        return jsonify({
            "status":"success"
        })
    else:
        return jsonify({
            "status":"failed",
            "message":"数据库操作失败"
        })


@v1.route("/user/video_info",methods=['POST','GET'])
@allow_cross_domain
@login_required
def video():
    # params  plat_id  account_login_name  page_count page_num 默认一页是 20条  管理员多一个 user_id start_time end_time
    form = request.form

    if current_user.mrid == 1:
        user_id = request.form.get("user_id") or current_user.id
    else:
        user_id = current_user.id
    adv_id = form.get("adv_id")
    title = form.get('title')
    plat_id = form.get("plat_id")
    account_name = form.get("account_name")
    page_count = form.get("page_count") or 20
    page_num = form.get("page_num") or 1
    start_time = form.get("start")
    end_time = form.get("end")
    determined = form.get("determined") or 'add_time'
    tag = form.get("tag")
    audit_status = form.get("audit_status")

    result, total,title = models.select_user_video(user_id=user_id,plat_id=plat_id,account_name = account_name,page_count=page_count,page_num = page_num,
                                                   start=start_time,end=end_time,title=title,determined=determined,adv_id=adv_id,
                                                   tag = tag,audit_status=audit_status)

    return jsonify({
        "status": "success",
        "data": result,
        "total": total,
        "title":title
    })



@v1.route("/user/change_video",methods=['POST'])
@allow_cross_domain
@login_required
def change_video():
    # todo
    # parmas  flow_id  tag adv_id audit_status user_id  超级管理员不需要user_id
    params = request.form
    if request.form.get("flow_id"):
        if current_user.mrid == 1:
            status = models.change_user_video(**params)
        else:
            status = models.change_user_video(**params)
        if status:
            return jsonify({
                "status": "修改成功"
            })
        else:
            return jsonify({
                "status": "修改成功",
                "message": "数据库操作失败"
            })
    return jsonify({
        "status":"failed",
        "message":"参数不足"
    })


@v1.route('/user/flow_count')
@allow_cross_domain
@login_required
def flow_count():
    user_id = request.args.get("user_id") or current_user.id
    plat_id = request.args.get("plat_id")
    result = models.all_flow(user_id,plat_id)
    if result:
        return jsonify({
            "status": "success",
            "data": result
        })
    return jsonify({
        "status": "failed",
        "message": "操作失败"
    })


@v1.route('/user/title_count')
@allow_cross_domain
@login_required
def title_count():
    user_id = request.args.get("user_id") or current_user.id
    plat_id = request.args.get("plat_id")
    result = models.all_flow(user_id, plat_id)
    if result:
        return jsonify({
            "status": "success",
            "data": result
        })
    return jsonify({
        "status": "failed",
        "message": "操作失败"
    })


@v1.route('/user/all_tag')
@allow_cross_domain
@login_required
def all_tag():
    result = models.all_tag()
    return jsonify({
        "status":"success",
        "data":result
    })


@v1.route("/user/choice",methods=['POST'])
@allow_cross_domain
@login_required
def choice():
    user_id = request.form.get('user_id') or current_user.id
    choices = models.chioce(user_id)
    print(user_id)
    print(choices)
    return jsonify({
        "status": "success",
        "data": choices
    })


@v1.route("/user/plat_and_user",methods=['GET','POST'])
@allow_cross_domain
@login_required
def p_and_a():
    user_type = current_user.mrid
    user_id = current_user.id
    result = models.plat_and_user()
    return jsonify({
        "status":"success",
        "data":result
    })



@v1.route("/user/select_account",methods=['POST'])
@allow_cross_domain
@login_required
def select_account():
    params = request.form

    #user_id = current_user.id
    user_id = request.form.get("user_id") or current_user.id
    plat_id = params.get("plat_id")
    results = models.select_account(plat_id = plat_id,user_id=user_id)

    return jsonify({
        "status":"success",
        "data":results
    })


@v1.route("/user/plat")
@allow_cross_domain
@login_required
def plat_():
    plats = models.plat_info()
    return jsonify({
        "status":"success",
        "data":plats
    })



class Myt(threading.Thread):
    def __init__(self,func,args):
        super(Myt,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


@v1.route("/user/check_account",methods=['GET'])
@allow_cross_domain
def check_account():
    '''
    :param  user
    :param  pwd
    :param  plat_id
    '''
    maps = [{"plat_id":7,"func":check_accounts.check_omqq},
            {'plat_id':14,"func":check_accounts.check_miaopai},
            {"plat_id":8,"func":check_accounts.check_renren},
            {'plat_id':9,"func":check_accounts.check_yidian}
            ]

    user = request.args.get('user')
    pwd = request.args.get('pwd')
    plat_id = int(request.args.get('plat_id'))
    if plat_id and user and pwd:
        for i in maps:
            if i['plat_id'] == plat_id:
                t = Myt(i['func'],args=(user,pwd))
                t.start()
                t.join()
                if t.get_result():
                    return jsonify({
                        "status":"success",
                        "can_login":True
                    })
                else:
                    return jsonify({
                        "status":"success",
                        "can_login":False
                    })
        return jsonify({
            "status":"success",
            "message":"该平台暂不支持"
        })
    else:
        return jsonify({
            "status":"failed",
            "message":"参数不全"
        })


@v1.route("/check_code")
@allow_cross_domain
def check_code():
    '''
        params:value
        params:phone_number
    '''
    verify_id = session.get("verify_id")
    value = request.args.get("value").upper()
    r_value = models.get_code(verify_id)
    print("====>",value)
    if r_value['value'] == value:
        #todo 调用短信接口
        return jsonify({
            "status":"success",
            "message":"短信发送成功"
        })
    return jsonify({
        "status":"failed",
        "message":"验证码错误"
    })

@v1.route("/register_mobile",methods =['POST'])
@allow_cross_domain
def mobile_register():
    '''
        :params phone_number
        :params phone_code
        :params password

    '''
    r_phone_code = session.get("phone_code") or '12345'
    phone_number = request.form.get("phone_number")
    phone_code = request.form.get("phone_code")
    password = request.form.get("password")
    if int(phone_code) == int(r_phone_code) :
        if models.register_user(name=phone_number,nickname=phone_number,password=password):
            return jsonify({
                "status":"success",
                "message":"注册成功"
            })
        else:
            return jsonify({
                "status":"failed",
                "message":"注册失败"
            })
    else:
        return jsonify({
            "status":"failed",
            "message":"验证码错误"
        })




@v1.route("/secret/plat_account")
@allow_cross_domain
def secret():
    key = request.args.get("key")
    if key == "@@@@@111":
        result = models.for_secret()
        return jsonify({
            "status":"success",
            "data":result
        })
    else:
        return ""

@v1.route("/history",methods=['POST'])
@allow_cross_domain
@login_required
def history():
    # params@ plat_id account_name adv_id  title  tag  audit_status  start  end
    # start  end 默认为当天日期
    user_type = current_user.mrid
    now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    params = request.form
    plat_id = params.get('plat_id')
    account_name = params.get('account_name')
    adv_id = params.get('adv_id')
    title = params.get('title')
    tag = params.get('tag')
    audit_status = params.get('audit_status')
    start = params.get('start') or now
    end = params.get('end') or now
    type = params.get("type")
    if user_type == 1:
        # 这里是 超级管理员
        user_id = params.get("user_id") or current_user.id

        data,plat_data = models.select_history_video(user_id, plat_id, account_name,
                                            start,end,adv_id, title,
                                            tag ,audit_status)
        if len(data)>0:
            return jsonify({
                "status":"success",
                "data":data,
                "plat":plat_data,

            })
        elif len(data) == 0:
            return jsonify({
                "data":data,
                "status":"success",
            })
        else:
            return jsonify({
                "status":"failed",
                "status":data
            })
    else: 
        return jsonify({
            "status":"failed",
            "message":"权限不够"
        })       

