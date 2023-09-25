# coding:utf-8
# -*- coding:utf-8 -*-
# @time: 2023/9/21 13:21
# @Author: erazhan
# @File: math_utils.py

# ----------------------------------------------------------------------------------------------------------------------
import math

def radian2angle(theta_radian):
    return theta_radian * 180/math.pi

def angle2radian(theta_angle):
    return theta_angle * math.pi/180

if __name__ == "__main__":

    raw_radian = math.pi
    print(raw_radian)

    angle = radian2angle(raw_radian)
    print(angle)

    radian = angle2radian(angle)
    print(radian)
    pass
