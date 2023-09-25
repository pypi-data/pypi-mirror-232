### JsonSimple

JsonSimple demo:

```python
from JsonSimple import JsonSimple


js = JsonSimple('{"code":0,"data":{"total":2,"list":[{"id":1,"name":"zhang_san","0":"a"},{"id":2,"name":"li"}]}}')
data = js.data.list._0.__0  # noqa
print(data)
# a
data = js.data.list._0.name  # noqa
print(data)
# zhang_san
data = js.get_value('data.list.0.0')
print(data)
# a

js.set_value('data.list.0.50', '5455555')
print(js)
# {"code": 0, "data": {"total": 2, "list": [{"id": 1, "name": "zhang_san", "0": "a", "50": "5455555"}, {"id": 2, "name": "li"}]}}
js.set_value('data.list.0.new_field.name', 'new_name')
print(js)
# {"code": 0, "data": {"total": 2, "list": [{"id": 1, "name": "zhang_san", "0": "a", "50": "5455555", "new_field": {"name": "new_name"}}, {"id": 2, "name": "li"}]}}

```
