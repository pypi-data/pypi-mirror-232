import datetime


def serializer_dict(d):
    data = {}
    for k in d.keys():
        if isinstance(d[k], datetime.datetime):
            data[k] = d[k].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(d[k], datetime.date):
            data[k] = d[k].strftime('%Y-%m-%d')
        else:
            data[k] = d[k]
    return data


def row_to_dict(cursor, row):
    """将返回结果转换为dict"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
        if isinstance(row[idx], datetime.datetime):
            d[col[0]] = row[idx].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(row[idx], datetime.date):
            d[col[0]] = row[idx].strftime('%Y-%m-%d')
        else:
            d[col[0]] = row[idx]
    return d
