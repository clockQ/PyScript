import json
import requests
docs_api = 'http://192.168.180.191:45560/bit-matrix-cmdb/v2/api-docs?group=CMDB%20API'

response = requests.get(docs_api, headers={}, params={})
resp_json = response.json()

definitions = resp_json['definitions']
paths = resp_json['paths']


def parse_definition(definition):
    if 'properties' not in definition.keys():
        return {}

    properties = definition['properties']

    result = {}
    for k, v in properties.items():
        if 'type' in v.keys():
            if v['type'] == 'integer':
                result[k] = 0
                continue
            elif v['type'] == 'string':
                result[k] = 'string'
                continue
            elif v['type'] == 'array':
                items = v['items']
                if '$ref' in items.keys():
                    ref = items['$ref'].split('/')[-1]
                    result[k] = [parse_definition(definitions[ref])]
                elif items['type'] == 'string':
                    result[k] = ['string']
                elif items['type'] == 'object':
                    result[k] = [{}]
                    continue
                else:
                    raise Exception('未知参数', k, v)
                continue
            elif v['type'] == 'object':
                result[k] = {}
                continue
            elif v['type'] == 'boolean':
                result[k] = True
                continue
            else:
                raise Exception('未知参数', k, v)
        elif '$ref' in v.keys():
            ref = v['$ref'].split('/')[-1]
            result[k] = parse_definition(definitions[ref])
            continue
        else:
            raise Exception('未知参数', k, v)
    return result

result = {}
for path, info in list(paths.items()):
    for method, v in info.items():
        tag = v['tags'][0]
        old_lst = result.get(tag, [])

        methods = {}
        methods['sub_title'] = v['summary']
        methods['url'] = path
        methods['method'] = method
        methods['parameters'] = [(param['name'], param['description']) for param in v.get('parameters', [])]

        ref = v['responses']['200']['schema']['$ref'].split('/')[-1]
        responses = parse_definition(definitions[ref])
        methods['responses'] = responses

        old_lst.append(methods)
        result[tag] = old_lst


def echo(f, str):
    f.write(str)
    f.write('\n')

sort_lst = [
    '数据字典接口',
    '维度数据查询接口',
    '账号的资源权限接口',
    '资源实例关系接口',
    '资源实例接口',
    '资源类型属性接口',
    '资源类型接口',
    '资源纳管接口',
    '资源账号配置',
]
with open('test.txt', 'w') as f:
    index = 0

    for title in sort_lst:
        sub_index = 0
        index += 1
        echo(f, f'{index} {title}')

        for method_info in result[title]:
            sub_index += 1
            echo(f, f"{index}.{sub_index} {method_info['sub_title']}")
            echo(f, f"\tURL： {method_info['url']}")
            echo(f, f"\t类型： {method_info['method'].upper()}")
            echo(f, f"\t入参：")
            param_index = 0
            for param in method_info['parameters']:
                param_index += 1
                echo(f, f"\t\t{param_index}. {' - '.join(param)}")

            echo(f, f"\t出参：")
            echo(f, '\t\t' + json.dumps(method_info['responses'], indent=4).replace('\n', '\r\n\t\t'))

            echo(f, '\n')
        echo(f, '')
