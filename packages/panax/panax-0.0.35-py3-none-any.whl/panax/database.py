import sys
import os
import uuid
import datetime
import peewee as pw

sys.path.append(os.getcwd())
from config import APP_SETTING


# engine = create_engine(APP_SETTING["connection"])
# conn = engine.connect()
# session = Session(engine)
#
# Base = declarative_base(engine)


db = pw.MySQLDatabase(
    host='121.42.197.244',
    user='root',
    passwd='',
    database='delongtest2',
    charset='utf8'
)


def gen_id():
    return uuid.uuid4().hex


def dt_format(v):
    if isinstance(v, datetime.datetime):
        return v.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(v, datetime.date):
        return v.strftime('%Y-%m-%d')
    else:
        return v


# class BaseModel(Base):
#     """基类模型"""
#     __abstract__ = True
#
#     id = Column(String(32), default=gen_id, primary_key=True, comment="主键ID")
#     created = Column(DateTime, nullable=True, default=datetime.datetime.now, comment="创建时间")
#     is_del = Column(Integer, comment="是否删除", default=0)
#
#     def to_dict(self):
#         return {c.name: dt_format(getattr(self, c.name)) for c in self.__table__.columns}


class BaseModel(pw.Model):
    __abstract__ = True

    id = pw.CharField(unique=True, default=gen_id, primary_key=True, verbose_name="主键ID")
    created = pw.DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    is_del = pw.IntegerField(default=0)

    class Meta:
        database = db

