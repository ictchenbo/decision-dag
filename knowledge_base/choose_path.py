# External Script：路径选择服务
# 输入：path_points
# 输出：path_name
# 输出：path_detail

path_name = None
path_detail = None

maxt = 10000000000

for k, v in path_points.items():
    time = v['total_time']
    if time < maxt:
        maxt = time
        path_name = k
        path_detail = v

total_time = str(int(maxt)) + '分'
