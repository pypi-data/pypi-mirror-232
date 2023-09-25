# @Time : 2023-09-25 11:24
# @Author  : inflowers@126.com
# @Desc : ==============================================
# Life is Short I Use Python!!!                      ===
# ======================================================
# @Project : JsonPlus
# @FileName: JsonPlus
# @Software: PyCharm
import simplejson


class JsonSimple(object):

    def __init__(self, _data, index_char='_', field_number='__', separate_char='.'):
        if isinstance(_data, dict):
            self.source_data = _data
        elif isinstance(_data, list):
            self.source_data = _data
        elif isinstance(_data, str):
            self.source_data = self.__load_data(_data)
        elif isinstance(_data, bytes):
            self.source_data = self.__load_data(_data)
        else:
            raise ValueError()
        self.index_char = index_char
        self.field_number = field_number
        self.separate_char = separate_char

    @staticmethod
    def __load_data(_data):
        return simplejson.loads(_data)

    @staticmethod
    def loads(_data):
        return JsonSimple(JsonSimple.__load_data(_data))

    def dumps(self, ensure_ascii=True):
        return simplejson.dumps(self.source_data, ensure_ascii=ensure_ascii)

    def __get_recursion(self, _data, paths):
        key = paths[0]
        if isinstance(_data, list):
            key = int(key)
        if len(paths) == 1:
            return _data[key]
        else:
            return self.__get_recursion(_data[key], paths[1:])

    def get_value(self, path):
        paths = path.split(self.separate_char)
        return self.__get_recursion(self.source_data, paths)

    def __set_recursion(self, _data, paths, value):
        key = paths[0]
        if isinstance(_data, list):
            key = int(key)
        if len(paths) == 1:
            if isinstance(key, int):
                if len(_data) > key:
                    _data.pop(key)
                    _data.insert(key, value)
                else:
                    _data.append(value)
            else:
                _data[key] = value
        else:
            if isinstance(_data, dict) and _data.__contains__(key):
                self.__set_recursion(_data[key], paths[1:], value)
            else:
                if isinstance(key, int):
                    if len(_data) > key:
                        _sub_data = _data[key]
                        self.__set_recursion(_sub_data, paths[1:], value)
                    else:
                        raise Exception(f'error index {key}')
                else:
                    _sub_data = {}
                    _data[key] = _sub_data
                    self.__set_recursion(_sub_data, paths[1:], value)

    def set_value(self, path, value):
        paths = path.split(self.separate_char)
        self.__set_recursion(self.source_data, paths, value)

    def __getattr__(self, item):
        if item.startswith(self.field_number):
            index = item.replace(self.field_number, '')
            value = self.source_data[index]
        elif item.startswith(self.index_char):
            index = item.replace(self.index_char, '')
            value = self.source_data[int(index)]
        else:
            value = self.source_data[item]
        if isinstance(value, (list, dict)):
            return JsonSimple(value, self.index_char)
        else:
            return value

    def __str__(self):
        return simplejson.dumps(self.source_data)



