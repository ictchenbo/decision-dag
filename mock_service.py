import requests
import time
import json

daoda_service = 'http://127.0.0.1:10201'

headers = {
    "accessToken": "1",
    "appId": "1",
    "Content-Type": "application/x-www-form-urlencoded"
}


def get_entity_detail(entity_id, service_conf=None):
    if service_conf:
        url = service_conf.get('api_address')
    else:
        url = daoda_service + "/onto-kg-gateway/daodaIndividualService/searchIndividualDetailById"
    requrl = f'{url}?individualId={entity_id}'
    # print(requrl)
    # params = {
    #     "individualId": entity_id
    # }
    # data = parse.urlencode(params, doseq=True)
    # res = requests.post(url, headers=headers, data=data)
    res = requests.post(requrl, headers=headers, timeout=5)

    if res.status_code == 200:
        print(res.text)
        rows = res.json()["data"].get("data", [])
        print(rows)
        if rows:
            return True, rows[0]
    return False, res.text


def find_property(entity, filter):
    dataProperties = entity.get("dataProperties", [])
    for item in dataProperties:
        if filter(item):
            return item["dpValue"]
    return None


def get_xy(entity: dict):
    x = find_property(entity, lambda item: item["dpId"] == "latitude" or item["dpName"] == "纬度")
    y = find_property(entity, lambda item: item["dpId"] == "longitude" or item["dpName"] == "经度")
    if x and isinstance(x, str):
        x = float(x)
    if y and isinstance(y, str):
        y = float(y)
    if x is not None and y is not None:
        return [x, y]
    return None


def get_time(entity: dict):
    time_prop = find_property(entity, lambda item: item["dpName"] == "时间")
    if time_prop:
        return int(time.mktime(time.strptime(time_prop, "%Y-%m-%dT%H:%M:%S")))
    return None


def get_decision_process(process_id, service_conf=None):
    if service_conf:
        url = service_conf.get('api_address')
    else:
        url = daoda_service + "/onto-kg-gateway/daodaIndividualService/searchIndividualDetailById"


def get_wind_speed(speed: str):
    if not speed or not speed.endswith("级"):
        return 0
    num = int(speed[-2:-1])
    return 0.1 * num ** 3


weatherData = json.load(open('mock_data/weatherData.json', encoding='utf8'))
for item in weatherData:
    item["times"] = f"{item['date'].replace('/', '-')}T{item['time']}"


def get_weather(stime: str):
    if len(weatherData) == 1 and weatherData[0]["times"] == stime:
        return weatherData[0]
    for i in range(len(weatherData) - 1):
        xi = weatherData[i]
        xj = weatherData[i+1]
        if xi["times"] <= stime < xj["times"]:
            return xi
    return None


def get_env(stime, place=None):
    info = get_weather(stime)
    if info:
        return {
            "降雨量": 10 if "xiaoyu" in info["weather"] else 20 if "dayu" in info["weather"] else 0,
            "温度": float(info["temp"][0:-1]),
            "风速": get_wind_speed(info["windSpeed"]),
            "地形": '高原'
        }
    return None


def get_navigate_path(place_start, place_end):
    path1 = [121.620681, 25.133046, 121.608747, 25.125043, 121.603885, 25.117573, 121.600791, 25.113037, 121.593424,
             25.109302, 121.592393, 25.099162, 121.58871, 25.093291, 121.585763, 25.089689, 121.588268, 25.079148,
             121.578986, 25.078614, 121.569262, 25.08235, 121.56499, 25.08235, 121.560275, 25.084618, 121.557476,
             25.084885, 121.55173, 25.085819, 121.548194, 25.081549, 121.544805, 25.07808, 121.55114, 25.069139]
    path2 = [121.620681, 25.133046, 121.608747, 25.125043, 121.61606, 25.11659, 121.624918, 25.113153, 121.631246,
             25.106564, 121.635675, 25.09711, 121.644849, 25.088515, 121.648962, 25.083644, 121.647064, 25.075335,
             121.632511, 25.06903, 121.617009, 25.066165, 121.595813, 25.064445, 121.583158, 25.067884, 121.573984,
             25.070463, 121.548991, 25.073042]

    return {
        "path1": path1,
        "path2": path2
    }
