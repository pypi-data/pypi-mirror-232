import argparse
import configparser
import json
import os

import pymongo
from happy_python import HappyLog

from method.file_create import create_config_if_not_exists
from method.mongodb_base import delete_document
from method.mongodb_base import find_document
from method.mongodb_base import insert_document
from method.mongodb_base import update_document
from method.mongodb_dump import dump_data_to_file
from method.mongodb_import import import_data_from_file

create_config_if_not_exists()

user_home = os.path.expanduser("~")

DEFAULT_CONFIG_PATH = os.path.join(user_home, ".zcx", "config.ini")
DEFAULT_LOG_CONFIG_PATH = os.path.join(user_home, ".zcx", "log.ini")


def main():
    parser = argparse.ArgumentParser(prog='mongodb_tool',
                                     description='MongoDB工具',
                                     usage='%(prog)s [-c <config_file>] [-l <log_config_file>][-i <data>] [-d <data>] [-s <data>]'
                                           ' [-u <data>] [--dump <filename>] [--import <filename>]')

    parser.add_argument('-c',
                        metavar='CONFIG_FILE',
                        help='配置文件路径，默认为 ~/.zcx/config.ini',
                        default=None)

    parser.add_argument('-l',
                        metavar='LOG_CONFIG_FILE',
                        help='日志配置文件路径，默认为 ~/.zcx/log.ini',
                        default=None)

    parser.add_argument('-i',
                        help='执行插入操作，提供数据（JSON格式）',
                        action='store',
                        dest='insert_data',
                        type=json.loads)

    parser.add_argument('-d',
                        help='执行删除操作，提供查询条件（JSON格式）',
                        action='store',
                        dest='delete_data',
                        type=json.loads)

    parser.add_argument('-s',
                        help='执行查询操作，提供查询条件（JSON格式）',
                        action='store',
                        dest='search_data',
                        type=str,
                        nargs='?',
                        const={},
                        default=None)

    parser.add_argument('-u',
                        help='执行更新操作，提供查询条件和更新数据（JSON格式）',
                        action='store',
                        dest='update_data',
                        type=json.loads)

    parser.add_argument('--dump',
                        help='导出数据到指定文件（JSON格式）',
                        action='store',
                        dest='dump_file',
                        type=str)

    parser.add_argument('--import',
                        help='从指定文件导入数据（JSON格式）',
                        action='store',
                        dest='import_file',
                        type=str)

    args = parser.parse_args()

    config_file_path = args.c or DEFAULT_CONFIG_PATH

    # config
    config = configparser.ConfigParser()
    config.read(config_file_path)

    mongodb_connection = config.get('main', 'db_url')
    db_name = config.get('main', 'db_name')
    collection_name = config.get('main', 'collection_name')

    client = pymongo.MongoClient(mongodb_connection)
    db = client[db_name]
    collection = db[collection_name]

    # log
    log_config_file_path = args.l or DEFAULT_LOG_CONFIG_PATH
    hlog = HappyLog.get_instance(log_config_file_path)

    hlog.var('args', args)

    if args.insert_data:
        inserted_id = insert_document(collection, args.insert_data)
        hlog.info(f"已插入数据，ID: {inserted_id}")
    elif args.search_data is not None:
        if args.search_data:
            try:
                search_criteria = json.loads(args.search_data)
                found_documents = find_document(collection, search_criteria)
                hlog.info("以下数据已查询：")
                for document in found_documents:
                    hlog.info(document)
            except json.JSONDecodeError:
                hlog.error("查询条件必须为JSON格式")
        else:
            found_documents = find_document(collection, {})
            hlog.info("以下数据已查询：")
            for document in found_documents:
                hlog.info(document)
    elif args.update_data:
        update_query = {"name": args.update_data["name"]}
        updated_count = update_document(collection, update_query, args.update_data)
        hlog.info(f"已更新{updated_count}条数据")
    elif args.delete_data:
        deleted_count = delete_document(collection, args.delete_data)
        hlog.info(f"已删除{deleted_count}条数据")
    elif args.dump_file:
        dump_data_to_file(collection, args.dump_file)
        hlog.info(f"数据已导出至文件：{args.dump_file}")
    elif args.import_file:
        import_data_from_file(collection, args.import_file)
        hlog.info(f"数据已从文件导入：{args.import_file}")
    else:
        hlog.error("命令行参数错误，请查看使用说明：")
        parser.print_help()


if __name__ == "__main__":
    main()
