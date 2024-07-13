# External Script：模拟地形环境行进速度计算逻辑
# 输入：subject_type
# 输入：time
# 输出：subject
# 输出：env
# 输出：speed
import re


def env_speed(subject, env: dict):
    temp_f = 0 if -10 <= env['温度'] <= 40 else 0.3
    rain_f = min(1.0, 0.1 * math.log2(env['降雨量'])) if env['降雨量'] >= 1 else 0
    wind_f = min(1.0, 0.05 * math.log2(env['风速'])) if env['风速'] >= 2 else 0
    land_f = {'平原': 0, '草原': 0.3, '丘陵': 0.4, '山地': 0.5, '沼泽': 0.7, '水体': 0.9}.get(env['地形'], 0.2)
    weather_f = min(1.0, temp_f + rain_f + wind_f)
    env_f = 0.5 * weather_f + 0.5 * land_f

    return subject['最大速度'] * (1 - env_f)


def get_subject(object_type):
    return {
        '最大速度': 10
    }


def get_env(time, place=None):
    return {
        '温度': 20,
        '降雨量': 5,
        '风速': 3,
        '地形': '丘陵'
    }


subject = get_subject(subject_type)
env = get_env(time)
speed = env_speed(subject, env)
match = bool(re.match("^abc", "abc1"))
