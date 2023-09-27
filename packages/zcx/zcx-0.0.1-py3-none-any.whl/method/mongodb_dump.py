import json


def dump_data_to_file(collection, filename):
    data = list(collection.find({}))
    cleaned_data = []
    for document in data:
        cleaned_document = document.copy()
        cleaned_document['_id'] = str(document['_id'])
        cleaned_data.append(cleaned_document)

    with open(filename, 'w') as file:
        json.dump(cleaned_data, file)
