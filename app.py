from datetime import datetime
from flask import Flask
from flask import make_response     # 封装response
from flask import redirect          # 用于重定向
from flask import abort             # 响应错误
from flask import url_for           # 路由分发
from flask import session           # 引入session
from flask import flash             # Flash消息
from flask import render_template   # 返回模板
from flask_script import Manager    # 使用flask扩展
from flask_bootstrap import Bootstrap   # bootstrap集成Twitter Bootstrap
from flask_moment import Moment     # 本地化日期和时间
from flask_wtf import Form          # 引入表单
from wtforms import StringField,SubmitField  # 引入表单字段类型
from wtforms.validators import Required      # 引入数据校验的必填属性

app = Flask(__name__)
manager = Manager(app=app)
bootstrap = Bootstrap(app) 
moment =  Moment(app)
app.config["SECRET_KEY"] = "A SECRET STRING"


USERS={1:{"name":"youzi"},2:{"name":"xiaxia"}}
# 查询用户
def load_user(id):
    user = USERS.get(id,None)
    return user

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route("/index")
def index():
    """主路由"""
    return render_template('index.html',current_time=datetime.utcnow())

@app.route("/set_cookie")
def set_cookie():
    """设置cookie"""
    response =  make_response("<h1>This document caries as cookie!</h1>")
    response.set_cookie("answer","42")
    return response

@app.route("/redirect_demo")
def redirect_demo():
    """重定向"""
    print("111111")
    return redirect("/set_cookie")

@app.route("/get_user/<int:id>")
def get_user(id):
    user =  load_user(id)
    if not user:
        abort(404)
    return "hello,{}".format(user)

class Utils:
    def my_method(self):
        return "hello"

@app.route("/show_user/<int:id>")
def show_user(id):
    user = load_user(id)
    print(type(id))
    if not user:
        abort(404)
    """返回的数据"""
    name = user.get("name")
    mydict = {"key":"柚子"}
    mylist = ["霞"]
    mytuple = (1,"")
    myint = 1
    u = Utils()
    """测试模板过滤器"""
    h1 = "<h1>safe的h1标签</h1>"
    words = "   hELLO world"
    age = 24
    fruit = ["西瓜", "橘子", "苹果", "哈密瓜"]
    return render_template("user.html",**locals())

@app.route("/bootstrap_user")
def bootstrap_user():
    name = "霞霞"
    return render_template("bootstrap_user.html",name=name)

@app.errorhandler(404)
def page_not_found(e):
    """数据找不到页面"""
    return render_template("404.html"),404

@app.errorhandler(500)
def inter_server_error(e):
    """服务器端错误"""
    return render_template("500.html"),500

@app.route("/get_time")
def get_time():
    """配置时间"""
    return render_template("time.html",current_time=datetime.utcnow())


# 定义表单类
class NameForm(Form):
    name = StringField("姓名：",validators=[Required()])
    submit = SubmitField("提交")

# 指定方法为GET和POST
@app.route("/form", methods=["GET", "POST"])
def form():
    Form = NameForm()
    name = None
    if Form.validate_on_submit():
        old_name = session.get("name")
        print(old_name)
        if old_name is not None and old_name != Form.name.data:
            flash("你已经修改了名字")
        name = Form.name.data
        session["name"] = name
        Form.name.data = ""
        # 使用重定向可以再刷新页面时不提示是否提交表单数据
        return redirect(url_for("form"))
    return render_template("form.html",form=Form, name=session.get("name"))

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
