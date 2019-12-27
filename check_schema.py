# -*- coding: UTF-8 -*-

import xlrd
from test_file.mapping import create_mapping

file = 'test_file/MAX原始数据汇总20191111.xlsx'


def flatting():
    result = []

    for m in create_mapping():
        upper_case = [x.upper() for x in m["Candidate"]]
        result.extend(upper_case)

    return result


mappings = flatting()


def compare(schema_value):
    result = []

    schemas = schema_value.split(",")
    for schema_name in schemas:
        tmp_name = schema_name.strip().upper()
        if tmp_name in mappings:
            continue
        else:
            result.append(tmp_name)

    return result


if __name__ == "__main__":
    wb = xlrd.open_workbook(filename=file)  # 打开文件

    sheets = wb.sheet_names()  # 获取所有表格名字
    if len(sheets) > 1:
        print(sheets)
        raise RuntimeError("存在多张 sheet")

    sheet1 = wb.sheet_by_index(0)  # 通过索引获取表格

    result = []

    for rl in range(1, sheet1.nrows):
        schema_type = sheet1.cell_value(rowx=rl, colx=7)
        if schema_type == "原始数据":
            schema_value = sheet1.cell_value(rowx=rl, colx=5)
            result.extend(compare(schema_value))

    print(set(result))
