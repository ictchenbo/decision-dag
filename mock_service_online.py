from flask import Flask, request

app = Flask(__name__)
# logging.getLogger().setLevel(logging.DEBUG)


@app.route('/get_basic_info', methods=['POST'])
def get_basic_info():
    print(request.json)
    return {
        "description": "获取某地的基本战场环境信息，包括敌情态势、海底环境、岸滩环境，如果为null，则表示不存在相应的环境",
        "code": 20000,
        "msg": "OK",
        "data": {
            "name": "黄金沙滩",
            "coordinates": [],
            "be_data": {
                "敌情态势": {
                    "岸滩火炮": 5,
                    "岸滩碉堡": 1,
                    "岸滩防空炮": 0
                },
                "海底环境": {
                    "海底地形": "浅水",
                    "水下障碍": "无"
                },
                "岸滩环境": {
                    "岸滩名称": "黄金沙滩",
                    "经纬度范围": [],
                    "所属地区": "",
                    "正面宽度": 3800,
                    "纵深长度": 128,
                    "底质": "沙",
                    "坡度": 2.5,
                    "平均坡度": 1.8,
                    "可登陆规模": 15000
                }
            }
        }
    }


@app.route('/weather_forecast', methods=['POST'])
def weather_forecast():
    print(request.json)
    return {
        "description": "天气预报服务 对给定地点的给定时间进行预测",
        "code": 20000,
        "msg": "OK",
        "data": {
            "place": "黄金沙滩",
            "time": "2025-04-20",
            "result": {
                "气温": 35.2,
                "气压": 98.5,
                "风向": 10,
                "风速": 2,
                "水平能见度": 200,
                "小时降雨量": 1,
                "相对湿度": 30,
                "雷暴": None,
                "台风": None,
                "雾": None,
                "霾": None
            }
        }
    }


@app.route('/ocean_forecast', methods=['POST'])
def ocean_forecast():
    print(request.json)
    return {
        "description": "海洋环境预报服务 对给定海域地点给定时间进行预测",
        "code": 20000,
        "msg": "OK",
        "data": {
            "place": "黄金沙滩",
            "time": "2025-04-20",
            "result": {
                "海浪浪向": 5,
                "海浪有效波高": 0.3,
                "涌浪浪向": 4,
                "涌浪有效波高": 0.5,
                "海流": 0.001,
                "潮汐": 0,
                "海温": 28,
            }
        }
    }


@app.route('/generate_path', methods=['POST'])
def generate_path():
    return {
        'msg': 'generate_path result',
        'pathSchema': [
            ['地点A', '地点C', '地点B'],
            ['地点A', '地点D', '地点B'],
        ]
    }


@app.route('/get_basic_info2', methods=['POST'])
def get_basic_info2():
    return {
        'msg': 'knowledge result',
        "vehicleInfo": {
            "name": "大G",
            "length": 3,
            "width": 2.4,
            "height": 2,
            "weight": 2,
            "type": "越野汽车",
        },
        "passpointsInfo": {
            "地点A": {
                "type": "高原",
                "limitWeight": 1728,
                "limitHeight": None,
                "limitWidth": None,
                "maxGradient": 64.3,
                "maxDitchWidth": 1.2,
                "maxVerticalHeight": 1.4
            },
            "地点B": {
                "type": "平原",
                "limitWeight": 1000,
                "limitHeight": None,
                "limitWidth": None,
                "maxGradient": 34.3,
                "maxDitchWidth": 1.2,
                "maxVerticalHeight": 1.4
            },
            "地点C": {
                "type": "公路",
                "limitWeight": 1428,
                "limitHeight": 3,
                "limitWidth": None,
                "maxGradient": 42.3,
                "maxDitchWidth": 1.2,
                "maxVerticalHeight": 1.7
            },
            "地点D": {
                "type": "公路",
                "limitWeight": 1329,
                "limitHeight": 1.8,
                "limitWidth": None,
                "maxGradient": 34.3,
                "maxDitchWidth": 1.5,
                "maxVerticalHeight": 1.4
            }
        },
    }


@app.route('/sift_path', methods=['POST'])
def sift_path():
    return {
        'msg': 'sift_path result',

        'canPassRoad': [
            '地点A', '地点C', '地点B'
        ]
    }


@app.route('/evaluate_path', methods=['POST'])
def evaluate_path():
    return {
        'msg': 'evaluate_path result',
        "path": "道路A->道路C->道路B",
        "score": "7.8"

    }


@app.route('/get_results', methods=['POST'])
def get_results():
    return {
        'msg': 'get_results result',
        'res': [
            {
                "vehicle": "大G",
                "roadInfos": "道路A->道路C->道路B",
                "score": "7.8",
                "passTime": "10h"
            }
        ]
    }


@app.route('/navigate', methods=['GET', 'POST'])
def navigate():
    from mock_service import get_navigate_path

    return {
        'code': 20000,
        'msg': '获取导航路径成功',
        'data': {
            'paths': get_navigate_path('start', 'end')
        }
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8222, debug=True)
