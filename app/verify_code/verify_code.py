from flask import Blueprint
from .random_code import ImageChar
from flask import current_app,send_from_directory,session,jsonify,make_response
import uuid
import os
from functools import wraps
from .. import models
try:
    import StringIO
except ImportError:
    from io import StringIO,BytesIO
code = Blueprint("code",__name__)


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        rst.headers['withCredentials'] = 'true'
        rst.headers['Access-Control-Allow-Credentials'] = 'true'
        rst.headers['Access-Control-Allow-Origin'] = '*'
        return rst
    return wrapper_fun


@code.route("/code")
@allow_cross_domain
def g_code():
    ic = ImageChar(fontColor=(100,211, 90))
    strs,code_img = ic.randChinese(4)
    #session[current_app.config.get('S_RECAPTCHA')]= strs

    #buf = StringIO()
    if 'verify_id' in session:
        print(session['verify_id'])
        session.pop('verify_id',None)
    tmp_p = os.path.join(os.getcwd() ,'./codes/',strs)
    print(tmp_p)
    try:
        buf = StringIO()
        code_img.save(tmp_p,'JPEG',quality=70)
    except:
        buf = BytesIO()
        code_img.save(tmp_p,'JPEG',quality=70)
    buf_str = buf.getvalue()
    print
    syr = str(code_img.tobytes())
    # buf_str = str(buf_str)
    # response = current_app.make_response(buf_str)
    # response.headers['']
    uis = str(uuid.uuid1())
    session['verify_id'] = uis
    models.save_code(uis,strs)
    return send_from_directory(os.path.join(os.getcwd() ,'./codes/'), strs,as_attachment=False)
    # return jsonify({
    #     "pic":syr,
    #     "uid":uis
    # })
