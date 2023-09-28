
## Get eval() method Jsonpath by json value

Search for the (string, int, float, bool) value in a json object, and
return the jsonpath in a string formatted to use in eval() method.

__For example__:
    import json
    from eval_jsonpath_elam.evalpath import get_jsonpath_by_key

    json_data = { 
        "objectKeyNameList": [ 
            {"someBoolKey": False },
            {"someFloatKey": 123456.34 },
            {"someIntKey": 7890 },
            {"someStrKey": "my_search_string" }
        ]
    }

    json_object = json.loads( json.dumps( json_data ) )
    eval_string = get_jsonpath_by_key(json_object, "my_search_string") 
    print( eval_string ) # "['objectKeyNameList'][3]['someStrKey']"
    print( eval( "json_object" + eval_string ) ) # "my_search_string"

## Optional parameters

| Property Name | Values | Doc |
| ------ | ------ | ------ |
| `dot_notation` | `false` or `true` | default to __False__; this allows to be compatible to Python (ie: "['someObj']['Array'][3]['obj1']['key'][2]['prop']"). When set to __True__; allows string to be returned to be compatible to Java/Javascript (ie: "someObj.Array[3].obj1.key[2].prop")|
| `contains_string` | `false` or `true` | default to __True__; this searches for all occurances of the search string. When set to __False__; will only find the first occurance of the search string, int, float, or bool |

**Note**: bool, int, float, complex data types will be automatically converted to strings during search.
      returned_json_path_string will return a string of the json path if found, otherwise the `None` object will be returned.
      Search string is case sensitive.

## License

[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html#license-text)


## Authors

- [Eric Lam](https://www.github.com/genericgenie)


#### The following is example code tested in Windows 11 with Python 3.11.4:
```python
import json

# either import this:
from eval_jsonpath_elam import evalpath
# or import this:
from eval_jsonpath_elam.evalpath import get_jsonpath_by_key

json_data = {
    "alpha": ["aaa", "bbb", "ccc"],
    "dimensions": {"length": "112", "width": "103", "height": "42", "once": "thing1"},
    "meta_data": [
        {
            "id": 11089769,
            "key1": "imported_gallery_files",
            "value": [
                "https://abc.com/unnamed-3.jpg",
                "https://abc.com/unnamed-2.jpg",
                "https://abc.com/unnamed-4.jpg",
            ],
        },
        {
            "id": 11089779,
            "key2": "imported_gallery_files2",
            "value": [
                "https://abc.com/unnamed-5.jpg",
                "https://abc.com/unnamed-6.jpg",
                "https://abc.com/unnamed-7.jpg",
            ],
            "value2": {
                "branch1": ["thing0"],
                "branch2": [
                    {"branch2_0": "thing1"},
                    {"branch2_1": "thing2"},
                    {"branch2_2": "thing3"},
                ],
            },
        },
    ],
}


# used to just print the list of strings using eval(json_path_string)
def print_python_json(x):
    for v in x:
        print(f'data{v} = {eval("data" + v)}')
    print()

# load json into object
data = json.loads(json.dumps(json_data))

# find the key "thing" in json, and return the json path in eval string format
path_str = get_jsonpath_by_key(data, "thing")
print_python_json(path_str)
path_str = evalpath.get_jsonpath_by_key(data, 42)
print_python_json(path_str1)

path_str = get_jsonpath_by_key(data, 42, dot_notation=True)
print(path_str[0])
path_str = get_jsonpath_by_key(data, 11089769)
print_python_json(path_str)

path_str = get_jsonpath_by_key(data, "thing1", contains_string=False)
print_python_json(path_str)
path_str = get_jsonpath_by_key(data, "imported_gallery_files", contains_string=False)
print_python_json(path_str)
path_str = get_jsonpath_by_key(data, "imported_gallery_files", contains_string=True)
print_python_json(path_str)
```