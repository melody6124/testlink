import codecs
import json
import os
import tarfile

import yaml


def untar_file(tar_file, des_folder):
    tar = tarfile.open(tar_file)
    names = tar.getnames()
    for name in names:
        tar.extract(name, des_folder)
    tar.close()


def json_serialization_to_file(data, file):
    file_suffix = os.path.splitext(file)[-1]
    with codecs.open(file, "w", "utf-8") as fp:
        if file_suffix in ['.yaml', '.yml', '.json']:
            fp.write(json.dumps(data, indent=4, ensure_ascii=False))
        else:
            fp.write(json.dumps(data))
    # fp.close()


def json_deserialization_from_file(file):
    file_suffix = os.path.splitext(file)[-1]
    with codecs.open(file, "r", "utf-8") as fp:
        if file_suffix == '.yaml' or file_suffix == '.yml':
            content = yaml.safe_load(fp.read())
        elif file_suffix == '.json':
            content = json.loads(fp.read())
        else:
            content = fp.read()
    # with可以保证程序执行完或者抛异常都能正常关闭文件
    # fp.close()
    return content


if __name__ == '__main__':
    content = json_deserialization_from_file('./restart.json')
    print(content)
    json_serialization_to_file(content, 'restart.bak.json')
