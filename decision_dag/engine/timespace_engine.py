from math import *


def space_angle(latA, lonA, latB, lonB):
    """
    Args:
        point p1(latA, lonA)
        point p2(latB, lonB)
    Returns:
        bearing between the two GPS points,
        default: the basis of heading direction is north
    """
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = (brng + 360) % 360
    return brng


def space_distance(lat1, lon1, lat2, lon2):  # 纬度1，经度1，纬度2，经度2（十进制度数）
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000


directions = [
    {"dir": "北", "angles": [0]},
    {"dir": "北偏东", "angles": [0, 45]},
    {"dir": "东北", "angles": [45]},
    {"dir": "东偏北", "angles": [45, 90]},
    {"dir": "东", "angles": [90]},
    {"dir": "东偏南", "angles": [90, 135]},
    {"dir": "东南", "angles": [135]},
    {"dir": "南偏东", "angles": [135, 180]},
    {"dir": "南", "angles": [180]},
    {"dir": "南偏西", "angles": [180, 225]},
    {"dir": "西南", "angles": [225]},
    {"dir": "西偏南", "angles": [225, 270]},
    {"dir": "西", "angles": [270]},
    {"dir": "西偏北", "angles": [270, 315]},
    {"dir": "西北", "angles": [315]},
    {"dir": "北偏西", "angles": [315, 360]},
]


def angle_desc(angle):
    for dir in directions:
        angles = dir['angles']
        if len(angles) == 1 and abs(angle - angles[0]) < 2 or (len(angles) > 1 and angles[0] < angle < angles[1]):
            if len(angles) == 1:
                return dir["dir"], f'正{dir["dir"]}'
            diff = angle - angles[0]
            if angles[1] % 90 == 0:
                diff = angles[1] - angle
            return dir["dir"], f'{dir["dir"]}{diff:0.2f}度'


def space_relation(p1, p2):
    """
    计算空间关系
    :param p1: （lat, lon)
    :param p2:  (lat, lon)
    :return: p1相对于p2的空间关系
    """
    latlon = [p2[0], p2[1], p1[0], p1[1]]
    angle = space_angle(*latlon)
    dist = space_distance(*latlon)
    if dist < 1000:
        dist_spec = f'{int(dist)}米'
    elif dist > 100000:
        dist_spec = f'{dist/1000:0.1f}千米'
    else:
        dist_spec = f'{dist:0.1f}千米'
    _dir, _spec = angle_desc(angle)
    return {
        "direction": _dir,
        "angle": angle,
        "angle_text": _spec,
        "distance": dist,
        "distance_text": dist_spec
    }


def time_relation(x, y):
    """
    计算时间关系
    :param x: 时间点或时间段元组
    :param y: 时间点或时间段元组
    :return: x相当于y的时间关系
    """
    if not isinstance(x, list) and not isinstance(x, tuple):
        x = [x, x]
    if not isinstance(y, list) and not isinstance(y, tuple):
        y = [y, y]

    if x[0] == y[0] and x[1] == y[1]:
        return "Equal"

    if x[1] < y[0]:
        return "Before", y[0]-x[1]
    if y[1] < x[0]:
        return "After", x[0]-y[1]
    if x[1] == y[0]:
        return "MeetBy"
    if y[1] == x[0]:
        return "Meet"
    if x[0] < y[0] < x[1] < y[1]:
        return "OverlapBy"
    if y[0] < x[0] < y[1] < x[1]:
        return "OverlapWith"
    if x[0] == y[0]:
        return "StartBy" if x[1] < y[1] else "Start"
    if x[1] == y[1]:
        return "End" if x[0] > y[0] else "EndBy"

    return "Include" if x[0] < y[0] else "During"


if __name__ == "__main__":
    print(time_relation(1, 1))
    print(time_relation(1, 2))
    print(time_relation(2, 1))

    print(time_relation([1, 4], [1, 4]))

    print(time_relation([1, 2], [3, 4]))
    print(time_relation([3, 4], [1, 2]))
    print(time_relation([1, 2], [2, 3]))
    print(time_relation([3, 4], [2, 3]))
    print(time_relation([1, 3], [2, 4]))
    print(time_relation([2, 4], [1, 3]))
    print(time_relation([1, 2], [1, 3]))
    print(time_relation([1, 3], [1, 2]))
    print(time_relation([1, 4], [2, 4]))
    print(time_relation([2, 4], [1, 4]))
    print(time_relation([1, 4], [2, 3]))
    print(time_relation([2, 3], [1, 5]))


    #  北京-上海
    # print(space_angle(40, 116, 31, 121))
    # print(space_distance(40, 116, 31, 121))
    #  北京-上海
    print(space_relation([40, 116], [31, 121]))
    #  上海-北京
    print(space_relation([31, 121], [40, 116]))

    # 南京-上海
    print(space_relation([32, 119], [31, 121]))
