import logging
from functools import reduce
from itertools import groupby
from typing import List, Dict, Union


def list_dict_group(data: List[Dict], key):
    new_data = {"list_data": list(), "dict_data": dict()}
    data.sort(key=lambda x: x.get(key, ""))
    group_data = groupby(data, key=lambda x: x.get(key, ""))
    for data_key, values in group_data:
        _values = list(values)
        new_data["list_data"].append({"key": data_key, "values": _values})
        new_data["dict_data"].update({data_key: _values})

    return new_data


def remove_list_dict_duplicate(list_dict_data):
    """
    去除列表字典里的重复数据
    :param list_dict_data: 列表字典
    :return:
    """
    return reduce(lambda x, y: x if y in x else x + [y], [[], ] + list_dict_data)


def retry(func, params: Union[dict, list, tuple], check_func, num=1):
    """
    执行失败重试
    :param func: 要执行的函数
    :param params: 要执行的函数的参数值
    :param check_func: 校验函数
    :param num: 重试次数
    :return:
    """
    result = None
    for i in range(num):
        try:
            if params:
                if isinstance(params, dict):
                    result = func(**params)
                elif isinstance(params, list) or isinstance(params, tuple):
                    result = func(*params)
                else:
                    break
            else:
                result = func()
            flag = check_func(result)
            if flag:
                break
        except Exception as e:
            logging.error(f"error={e}")
    return result


def check_value(value, default):
    if not value:
        value = default
    return value


def check_or_add_growth_rate(data: List[dict], value_key: str, growth_rate_key: str = "growth_rate",
                             start_growth_rate: float = None, flag: bool = True, digits: int = None):
    for i, _ in enumerate(data):
        if _.get(growth_rate_key) and value_key in _:
            if i == 0:
                if start_growth_rate:
                    data[i][growth_rate_key] = start_growth_rate
                else:
                    data[i][growth_rate_key] = 0
            else:
                pre = check_value(data[i - 1].get(value_key, 0), 0) if data[i - 1].get(value_key, 0) else 0
                current = check_value(data[i].get(value_key, 0), 0) if data[i].get(value_key, 0) else 0
                value = float(current - pre) / pre if pre else 0
                if flag:
                    value = value * 100
                if digits:
                    value = round(value, digits)
                data[i][growth_rate_key] = value
