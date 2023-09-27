import json


def import_data_from_file(collection, filename):
    with open(filename, 'r') as file:
        data = json.load(file)  # 解析JSON字符串为Python字典
        if isinstance(data, list):
            for document in data:
                collection.insert_one(document)
        else:
            collection.insert_one(data)
