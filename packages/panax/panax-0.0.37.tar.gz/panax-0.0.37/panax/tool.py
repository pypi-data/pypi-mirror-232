import argparse

import sys
import os
sys.path.append(os.getcwd())

from panax import db, BaseModel
from config import APP_SETTING
from peewee_migrate import Router
import models


def init():
    print("==init==")
    print("==finished==")


def migrate():
    print("==migrateing==")

    db.connect()

    router = Router(db)
    router.create(auto=models)
    router.run()

    db.close()

    print("==migrate finished==")


# def upgrade():
#     print("==upgrade==")
#     repo = os.path.join(os.getcwd(), 'db_migrate')
#     if not os.path.exists(repo):
#         print("Repo Not Found!")
#
#     api.upgrade(APP_SETTING["connection"], repo)


def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-f", help="")
    parser.add_argument("exec", help="参数: [init, migrate, upgrade]")

    # 解析
    args = parser.parse_args()
    exec = args.exec
    # f = args.f

    if exec == "init":
        init()
    elif exec == "migrate":
        migrate()
    # elif exec == "upgrade":
    #     upgrade()
    else:
        print("参数错误")


if __name__ == '__main__':
    main()
