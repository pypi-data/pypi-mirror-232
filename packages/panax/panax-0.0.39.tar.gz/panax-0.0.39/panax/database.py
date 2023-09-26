import datetime, uuid
import peewee as pw


db = pw.MySQLDatabase(
    host='121.42.197.244',
    user='root',
    passwd='BpPass123!@#',
    database='delongtest2',
    charset='utf8'
)


def gen_id():
    return uuid.uuid4().hex


class BaseModel(pw.Model):
    id = pw.CharField(unique=True, default=gen_id(), verbose_name="主键ID")
    created = pw.DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    is_del = pw.IntegerField(default=0)

    class Meta:
        database = db

    def to_dict(self):
        data = {}
        for k in self.__dict__['__data__'].keys():
            if isinstance(self.__dict__['__data__'][k], datetime.datetime):
                data[k] = self.__dict__['__data__'][k].strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(self.__dict__['__data__'][k], datetime.date):
                data[k] = self.__dict__['__data__'][k].strftime('%Y-%m-%d')
            else:
                data[k] = self.__dict__['__data__'][k]
        return data
