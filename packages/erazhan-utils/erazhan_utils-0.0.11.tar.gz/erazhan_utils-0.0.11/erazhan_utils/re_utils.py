# coding:utf-8
# -*- coding:utf-8 -*-
# @time: 2023/9/21 11:07
# @Author: erazhan
# @File: re_utils.py

# ----------------------------------------------------------------------------------------------------------------------
import re

def clean_illegal_character(text, illegal_flag = 1):
    '''清洗文本中的非法字符，都是不常见的不可显示字符，例如退格，响铃等'''
    try:
        if illegal_flag == 1:
            ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
            text = ILLEGAL_CHARACTERS_RE.sub(r'', text)
        elif illegal_flag == 2:
            text = text.encode("utf-8").decode("utf-8-sig")
        else:
            text = text
    except:
        text = text
    return text




if __name__ == "__main__":

    text = "./ic15_data/recognition_train/﻿word_1.png"
    data = {"text":text}
    print(data)
    data["new_text"] = clean_illegal_character(text)
    print(data)

    nn_text = text.encode("utf-8").decode("utf-8-sig")
    print(nn_text)
