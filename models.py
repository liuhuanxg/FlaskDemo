# -*- coding: utf-8 -*-
"""
@Time       :2020/7/20 18:16
@Author     :liuhuan
@verssion   :v1.0
@effect     :models
"""
from app import db


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


# 1、创建数据表
# db.create_all()

# 2、删除数据表
# db.drop_all()

# 3、插入数据行

admin_role = Role(name='Admin')
mod_role = Role(name='Moderator')
user_role = Role(name='User')
user_john = User(username='john', role=admin_role)
user_susan = User(username='susan', role=user_role)
user_david = User(username='david', role=user_role)
print(user_david.id)
# ①、插入单条数据
# db.session.add(admin_role)

# ②、插入多条数据
# db.session.add_all([admin_role, mod_role, user_role, user_david, user_susan, user_john])

# ③、db.session.rollback()数据库事务回滚

# 4、修改行
# admin_role.name = "Administrator"
# db.session.add(admin_role)

# 5、删除行
# db.session.delete(mod_role)

# 6、查询行

db.session.commit()