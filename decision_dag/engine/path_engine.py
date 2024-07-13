# coding=utf-8
import requests
import math
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta

from geopy import distance

from mock_service import get_weather


def CalcAzimuth(lon1, lat1, lon2, lat2):
    """
    Args:
    point p1(latA, lonA)
    point p2(latB, lonB)
    Returns:
    bearing between the two GPS points,
    default: the basis of heading direction is north
    """
    lat1_rad = lat1 * math.pi / 180
    lon1_rad = lon1 * math.pi / 180
    lat2_rad = lat2 * math.pi / 180
    lon2_rad = lon2 * math.pi / 180
    y = math.sin(lon2_rad - lon1_rad) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon2_rad - lon1_rad)
    brng = math.atan2(y, x) * 180 / math.pi
    return float((brng + 360.0) % 360.0)


def GeoDistance(lon1, lat1, lon2, lat2):
    """

    Args:
        lat1 (_type_): 
        lon1 (_type_): 
        lat2 (_type_): 
        lon2 (_type_): 

    Returns:
        distance between the two GPS points,
    """
    x = distance.geodesic((lat1, lon1),(lat2, lon2))
    return x.km

def CalcSituation(lon, lat, brng, dist):
    x = distance.geodesic(dist)
    next = x.destination((lat, lon), brng)
    return (next.longitude, next.latitude)


def TransformPath(daoda_path):
    path = []
    for point_ in zip(daoda_path[::2], daoda_path[1::2]):
        path.append(point_)
    return path
    GeoDistance

# @app.route('/GenerateSpaceShift', methods=['POST', 'GET'])
def GenerateDisAndAzimuth(path):
    """ 
    Get (GeoDistance, Azimuth) according to the path length of L+1. 
    Returns:
        _type_: dis_list and azi_list of length L
    """
    # get (Dis, Azimuth) between each point pair
    dis_list = []
    azi_list = []
    sum_dis_list = []
    prev_point_ = path[0]
    init_dis = 0
    for point_ in path[1:]:
        lon1_, lat1_ = prev_point_
        lon2_, lat2_ = point_
        init_dis = init_dis + GeoDistance(lon1_, lat1_, lon2_, lat2_)
        sum_dis_list.append(init_dis)
        dis_list.append(GeoDistance(lon1_, lat1_, lon2_, lat2_))
        azi_list.append(CalcAzimuth(lon1_, lat1_, lon2_, lat2_))
        prev_point_ = point_
    return sum_dis_list, dis_list, azi_list


def GeneratePoint(delta_t, shift_from_source, dis_list_, azi_list_, sum_dis_list_, t, path):
    """_summary_

    Args:
        shift_from_source (float): 当前物体走过的距离总和
        neighbor_point (tuple): 离当前位置最近的走过的经纬度点
        path (_type_): _description_

    Returns:
        _type_: _description_
    """

    res = requests.get(url="http://192.168.27.145:8282/inference/_execute/rules_speed?time={}".format(t))
    speed = res.json()['data']['result']
    # 速度换算
    curspeed = speed * delta_t / 60
    index = 0
    for dis_ in sum_dis_list_:
        if shift_from_source > dis_:
            index = index + 1
        else:
            break
    
    # 得到当前位置到经纬度的间隔，方向角和距离
    pre_cur_dis = shift_from_source - sum_dis_list_[index-1] if index > 0 else shift_from_source
    # 加上单位时间内走的距离
    cur_dis = pre_cur_dis + curspeed

    cur_degree = azi_list_[index]

    neighbor_point = path[index]
    # print("#Sanity Check: neighbor point {}".format(neighbor_point))
    # print(neighbor_point, cur_degree, cur_dis)
    # 这里需要将时间粒度设置的尽量小，否则会出现在转折点附近计算不准确的问题。解决方案是：如果单位时间内走过的距离，
    # 没有经过转折点，则直接就算，否则需要分段计算
    # if GeoDistance(prev_point, path[index+1]) <    
    # if GeoDistance(prev_point, path):
    existing_node = None
    if cur_dis < dis_list_[index]:
        new_point = CalcSituation(neighbor_point[0], neighbor_point[1], cur_degree, cur_dis)
        shift_from_source = shift_from_source + curspeed
    else:
        cur_dis = cur_dis - dis_list_[index]
        if index + 1 < len(azi_list_):
            new_point = CalcSituation(path[index+1][0], path[index+1][1], azi_list_[index+1], cur_dis)
            shift_from_source = shift_from_source + curspeed
            existing_node = path[index+1]
        else:
            # 到达终点，
            new_point = path[-1]
            shift_from_source = shift_from_source + (dis_list_[index] - pre_cur_dis)
    
    return existing_node, new_point, shift_from_source, speed


time_format = "%Y-%m-%dT%H:%M"


def get_path_points(path1, start_time, delta_t=10):
    """

    :param path1:  路径
    :param delta_t: 单位时间 分钟为单位
    :return:
    """

    path = TransformPath(path1)
    sum_dis_list, dis_list, azi_list, = GenerateDisAndAzimuth(path)
    t = datetime.strptime(start_time, time_format)
    shift_from_source = 0
    total_distance = sum_dis_list[-1]
    generate_points = []
    total_time = 0
    while True:
        if shift_from_source >= total_distance:
            break
        t = t + timedelta(minutes=delta_t)
        total_time += delta_t
        ts = t.strftime(time_format)
        existing_point, new_point, shift_from_source, speed = GeneratePoint(delta_t, shift_from_source, dis_list, azi_list,
                                                                     sum_dis_list, ts, path)
        weather = get_weather(ts)
        # print(new_point)
        if existing_point:
            generate_points.append({
                "long": existing_point[0],
                "lat": existing_point[1],
                "speed": speed,
                "weather": weather
            })

        generate_points.append({
            "long": new_point[0],
            "lat": new_point[1],
            "speed": speed,
            "weather": weather
        })

    return {
        "total_time": total_time,
        "process": generate_points
    }


if __name__ == '__main__':
    
    path1 = [121.620681,25.133046,121.608747,25.125043,121.603885,25.117573,121.600791,25.113037,121.593424,25.109302,121.592393,25.099162,121.58871,25.093291,121.585763,25.089689,121.588268,25.079148,121.578986,25.078614,121.569262,25.08235,121.56499,25.08235,121.560275,25.084618,121.557476,25.084885,121.55173,25.085819,121.548194,25.081549,121.544805,25.07808,121.55114,25.069139]
    path2 = [121.620681,25.133046,121.608747,25.125043,121.61606,25.11659,121.624918,25.113153,121.631246,25.106564,121.635675,25.09711,121.644849,25.088515,121.648962,25.083644,121.647064,25.075335,121.632511,25.06903,121.617009,25.066165,121.595813,25.064445,121.583158,25.067884,121.573984,25.070463,121.548991,25.073042]

    print(get_path_points(path1))
