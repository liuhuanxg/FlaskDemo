import os
import time
from datetime import datetime
from threading import Thread
from flask import Flask
from flask import request
from flask import make_response  # 封装response
from flask import redirect  # 用于重定向
from flask import abort  # 响应错误
from flask import url_for  # 路由分发
from flask import session  # 引入session
from flask import flash  # Flash消息
from flask import render_template  # 返回模板
from flask_script import Manager  # 使用flask扩展
from flask_bootstrap import Bootstrap  # bootstrap集成Twitter Bootstrap
from flask_moment import Moment  # 本地化日期和时间
from flask_wtf import Form  # 引入表单
from wtforms import StringField, SubmitField  # 引入表单字段类型
from wtforms.validators import Required  # 引入数据校验的必填属性
from flask_sqlalchemy import SQLAlchemy  # 引入sqlalchemy
from flask_script import Shell  # 引入Shell添加上下文
from flask_migrate import Migrate, MigrateCommand  # 引入数据库迁移管理
from flask_mail import Mail     # 引入邮件发送
from flask_mail import Message  # 引入邮件信息

app = Flask(__name__)

app.config["SECRET_KEY"] = "A SECRET STRING"

# 配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# 配置用户邮箱
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "18737307883@163.com"
app.config['MAIL_PASSWORD'] ="lh111111"
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = '18737307883@163.com'
app.config['FLASKY_ADMIN'] = '1985054961@qq.com'


db = SQLAlchemy(app)

manager = Manager(app=app)
bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)

# 绑定迁移
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)


# 用户角色类
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __repr__(self):
        return "<Role %r>" % self.name


# 用户表
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def __repr__(self):
        return "<User %r>" % self.username


USERS = {1: {"name": "youzi"}, 2: {"name": "xiaxia"}}


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))


# 异步发送邮件
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# 发送邮件
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    t = Thread(target=send_async_email, args=[app, msg])
    t.start()
    return t

# 查询用户
def load_user(id):
    user = USERS.get(id, None)
    return user


@app.route('/')
def hello_world():
    print(request.url)
    print()
    time.sleep(3)
    # if request.remote_addr == "127.0.0.1":
    #     abort(404)

    return 'Hello World!'


@app.route("/index")
def index():
    """主路由"""
    return render_template('index.html', current_time=datetime.utcnow())


@app.route("/set_cookie")
def set_cookie():
    """设置cookie"""
    response = make_response("<h1>This document caries as cookie!</h1>")
    response.set_cookie("answer", "42")
    return response


@app.route("/redirect_demo")
def redirect_demo():
    """重定向"""
    print("111111")
    return redirect("/set_cookie")


@app.route("/get_user/<int:id>")
def get_user(id):
    user = load_user(id)
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
    mydict = {"key": "柚子"}
    mylist = ["霞"]
    mytuple = (1, "")
    myint = 1
    u = Utils()
    """测试模板过滤器"""
    h1 = "<h1>safe的h1标签</h1>"
    words = "   hELLO world"
    age = 24
    fruit = ["西瓜", "橘子", "苹果", "哈密瓜"]
    return render_template("user.html", **locals())


@app.route("/bootstrap_user")
def bootstrap_user():
    name = "霞霞"
    return render_template("bootstrap_user.html", name=name)


@app.errorhandler(404)
def page_not_found(e):
    """数据找不到页面"""
    return render_template("404.html"), 404


@app.errorhandler(500)
def inter_server_error(e):
    """服务器端错误"""
    return render_template("500.html"), 500


@app.route("/get_time")
def get_time():
    """配置时间"""
    return render_template("time.html", current_time=datetime.utcnow())


# 定义表单类
class NameForm(Form):
    name = StringField("姓名：", validators=[Required()])
    submit = SubmitField("提交")


# 指定方法为GET和POST
@app.route("/form", methods=["GET", "POST"])
def form():
    Form = NameForm()
    name = None
    if Form.validate_on_submit():
        username = Form.name.data
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
            session["known"] = False
            if app.config.get("FLASKY_ADMIN"):
                result = send_email(app.config["FLASKY_ADMIN"], "New User", "mail/user", user=user)
                print("result", result)
        else:
            session["known"] = True
        session["name"] = name
        Form.name.data = ""
        # 使用重定向可以再刷新页面时不提示是否提交表单数据
        return redirect(url_for("form"))
    return render_template("form.html", form=Form, name=session.get("name"), known=session.get("known"))


if __name__ == '__main__':
    manager.run()
