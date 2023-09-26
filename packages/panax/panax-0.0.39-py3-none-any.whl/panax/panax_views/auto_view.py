import json, time, datetime, sys, os
# from panax.database import engine, conn, session
# from sqlalchemy import text

from panax.database import db

sys.path.append(os.getcwd())
from config.sql_template import SQL_TEMPLATE
from models import MODEL_MAPPING


def generate_where_and_params(dict_where):
    #     """
    #     __exact 精确等于 like ‘aaa’
    #     __contains 包含 like ‘%aaa%’
    #     __gt 大于
    #     __gte 大于等于
    #     __lt 小于
    #     __lte 小于等于
    #     __in 存在于一个list范围内 (1, 2)
    #     __isnull 为null 不是'' ， 值：true， false
    #     """
    #
    #     """
    #     __year 时间或日期字段的年份
    #     __month 时间或日期字段的月份
    #     __day 时间或日期字段的日
    #     __date 时间或日期字段的日期部分
    #     __startswith 以…开头
    #     __endswith 以…结尾
    #     """

    arr_where = []
    param_where = dict()
    for key in dict_where.keys():
        if dict_where[key] != '':
            arr_k = key.split("__")
            if len(arr_k) == 1:
                arr_where.append(key + " = {" + key + "}")
                param_where[arr_k[0]] = dict_where[key]
            if len(arr_k) == 2:
                field = arr_k[0]
                operation = str(arr_k[1]).lower()
                if operation == "exact":
                    arr_where.append(field + " = {" + field + "}")
                    param_where[arr_k[0]] = dict_where[key]
                if operation == "contains":
                    arr_where.append(field + " like {" + field + "}")
                    param_where[arr_k[0]] = "%" + dict_where[key] + "%"
                if operation == "gt":
                    arr_where.append(field + " > {" + field + "}")
                    param_where[arr_k[0]] = dict_where[key]
                if operation == "gte":
                    arr_where.append(field + " >= {" + field + "}")
                    param_where[arr_k[0]] = dict_where[key]
                if operation == "lt":
                    arr_where.append(field + " < {" + field + "}")
                    param_where[arr_k[0]] = dict_where[key]
                if operation == "lte":
                    arr_where.append(field + " <= {" + field + "}")
                    param_where[arr_k[0]] = dict_where[key]
                if operation == "in" and len(dict_where[key]) > 0:
                    arr_where.append(field + " in (" + ",".join(['\'' + item + '\'' if isinstance(item, str) else str(item) for item in dict_where[key]]) + ") ")
                    # param_where[arr_k[0]] = dict_where[key]
                if operation == "isnull" and dict_where[key] == True:
                    arr_where.append("ISNULL(" + field + ")")
                    # param_where[arr_k[0]] = dict_where[key]
                if operation == "isnull" and dict_where[key] == False:
                    arr_where.append("NOT ISNULL(" + field + ")")
                    # param_where[arr_k[0]] = dict_where[key]

    return arr_where, param_where


def model_to_dict(model):
    data = {}
    for k in model.__dict__['__data__'].keys():
        if isinstance(model.__dict__['__data__'][k], datetime.datetime):
            data[k] = model.__dict__['__data__'][k].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(model.__dict__['__data__'][k], datetime.date):
            data[k] = model.__dict__['__data__'][k].strftime('%Y-%m-%d')
        else:
            data[k] = model.__dict__['__data__'][k]
    return data


def progress_dict(d):
    data = {}
    for k in d.keys():
        if isinstance(d[k], datetime.datetime):
            data[k] = d[k].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(d[k], datetime.date):
            data[k] = d[k].strftime('%Y-%m-%d')
        else:
            data[k] = d[k]
    return data


def dict_factory(cursor, row):
    """将返回结果转换为dict"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def auto_list(request, table_name):
    select = request.POST.get('select', '*')
    where = request.POST.get('where', '{}')
    order_by = request.POST.get('order_by', '')

    page = int(request.POST.get('page', '1'))
    size = int(request.POST.get('size', '10000'))

    str_sql = "select " + select + " from " + table_name

    if table_name in SQL_TEMPLATE:
        str_sql = "select " + select + " from (" + SQL_TEMPLATE[table_name] + ") t_template "

    dict_temp = json.loads(where)
    dict_template = dict()
    dict_where = dict()

    for key in dict_temp:
        if '__template' in key:
            dict_template[str(key).replace('__template', '')] = dict_temp[key]
        else:
            dict_where[key] = dict_temp[key]

    if dict_template:
        str_sql = str_sql.format(**dict_template)

    arr_where, param_where = generate_where_and_params(dict_where)

    if len(arr_where) > 0:
        str_sql += " where " + " and ".join(arr_where)

    if order_by:
        str_sql += " order by " + order_by

    print(str_sql)

    data_sql = "select * from (" + str_sql + ") t limit " + str((page - 1) * size) + "," + str(size)
    data_cursor = db.execute_sql(data_sql.format(**param_where))
    data = data_cursor.fetchall()


    count_sql = "select count(*) from (" + str_sql + ") t "
    count_cursor = db.execute_sql(count_sql.format(**param_where))
    count = count_cursor.fetchall()

    return {
        "code": 200,
        "data": [progress_dict(dict_factory(data_cursor, row)) for row in data],
        "total": count[0][0],
        "msg": "Success"
    }


def auto_get(request, table_name, pk):
    select = request.POST.get('select', '*')
    str_sql = "select " + select + " from " + table_name + " where id = '{id}' "
    print(str_sql)

    cursor = db.execute_sql(str_sql.format(**{"id": pk}))
    # cursor.row_factory = dict_factory
    row = cursor.fetchone()
    data = dict_factory(cursor, row)

    if not data:
        return {
            "code": 404,
            "msg": "Not Found"
        }

    return {
        "code": 200,
        "data": progress_dict(data),
        "msg": "Success"
    }


def auto_post(request, table_name):
    Model = MODEL_MAPPING[table_name]
    #
    # for r in request.POST.keys():
    #     model.__setattr__(r, request.POST[r])
    #
    # session.add(model)
    # session.commit()
    model = Model(**request.POST)
    result = model.save()

    print(result)

    return {
        "code": 200,
        "msg": "Success",
        "data": model.to_dict()
    }


def auto_put(request, table_name, pk):

    Model = MODEL_MAPPING[table_name]
    model = Model.get(Model.id == pk)

    if not model:
        return {"code": 400, "msg": "参数错误！"}

    for r in request.POST.keys():
        model.__setattr__(r, request.POST[r])

    model.save()

    return {
        "code": 200,
        "msg": "Success",
        "data": model.to_dict()
    }


def auto_delete(request, table_name, pk):
    Model = MODEL_MAPPING[table_name]
    model = Model.get(Model.id == pk)

    if not model:
        return {"code": 400, "msg": "参数错误！"}

    model.is_del = 1
    model.save()

    return {
        "code": 200,
        "msg": "Success"
    }


def auto_drop(request, table_name, pk):
    Model = MODEL_MAPPING[table_name]
    model = Model.get(Model.id == pk)

    if not model:
        return {"code": 400, "msg": "参数错误！"}

    model.delete_instance()

    return {
        "code": 200,
        "msg": "Success"
    }


auto_config = {
    "list": auto_list,
    "get": auto_get,
    "post": auto_post,
    "put": auto_put,
    "delete": auto_delete,
    "drop": auto_drop
}
