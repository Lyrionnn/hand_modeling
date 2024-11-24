import os
import json
import math
import numpy as np
# 以下的数字代表是这个点的x坐标序号，+1 为y坐标序号 
# 0-21   index = 2 * num + 1
WRIST = 1 # 腕部关键点  
THUMB_TIP = 9 #大拇指顶点
INDEX_FINGER_TIP = 17 #食指顶点
MIDDLE_FINGER_TIP = 25 #中指顶点
RING_FINGER_TIP = 33 #无名指顶点
PINKY_TIP = 41 #小指顶点

'''
WT  大拇指 ——> 腕部
WI  食指
WM  中指
WR  无名指
WP  小指
'''

# 计算最大值和最小值
def find_local_extremes(numbers):
    if len(numbers) < 3:
        return "输入的数字串过短，无法找到局部最大值和最小值", []

    extremes = []
    transitions = []  # 记录时间变化点

    for i in range(1, len(numbers) - 1):
        if numbers[i] >= numbers[i - 1] and numbers[i] >= numbers[i + 1] and numbers[i - 1] != numbers[i + 1]:
            extremes.append((i, numbers[i], "最高点"))
        elif numbers[i] <= numbers[i - 1] and numbers[i] <= numbers[i + 1] and numbers[i - 1] != numbers[i + 1]:
            extremes.append((i, numbers[i], "最低点"))
        # elif numbers[i - 1] == numbers[i + 1]:
        #     print("重复")
    
    if len(extremes) == 0:
        return "没有找到局部最大值和最小值", []

    # 记录时间变化点
    for i in range(1, len(extremes)):
        if extremes[i][2] == "最高点" and extremes[i-1][2] == "最低点":
            transitions.append((extremes[i-1][0], extremes[i][0], "升为最高点"))
        elif extremes[i][2] == "最低点" and extremes[i-1][2] == "最高点":
            transitions.append((extremes[i-1][0], extremes[i][0], "降为最低点"))

    return extremes, transitions

# 计算抓伸周期
def calculate_transition_times(transitions):
    high_to_low_times = []
    low_to_high_times = []

    for i in range(1, len(transitions)):
        if transitions[i][2] == "降为最低点":
            high_to_low_time = transitions[i][1] - transitions[i][0]
            high_to_low_times.append(high_to_low_time)
        elif transitions[i][2] == "升为最高点":
            low_to_high_time = transitions[i][1] - transitions[i][0]
            low_to_high_times.append(low_to_high_time)

    return high_to_low_times, low_to_high_times

# 计算2、3、4、5指相对于腕部关键点的距离
def get_distance(label):
    WT = []
    WI = []
    WM = []
    WR = []
    WP = []
    for line in label:
        x1, y1 = line[1], line[2]
        coordinates = [(line[i], line[i + 1]) for i in range(9, 42, 8)]

        distances = [math.sqrt((x - x1) ** 2 + (y - y1) ** 2) for x, y in coordinates]

        wt_distance, wi_distance, wm_distance, wr_distance, wp_distance = distances

        WT.append(wt_distance)
        WI.append(wi_distance)
        WM.append(wm_distance)
        WR.append(wr_distance)
        WP.append(wp_distance)

    return WT, WI, WM, WR, WP

def get_info(dist):
    extremes, transitions = find_local_extremes(dist)
    high_to_low_times, low_to_high_times = calculate_transition_times(transitions)
    return extremes, transitions, high_to_low_times, low_to_high_times

def process(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
        label = data["label"]
        
    WT, WI, WM, WR, WP = get_distance(label)
    
    wt_extremes, wt_transitions, wt_high_to_low_times, wt_low_to_high_times = get_info(WT)
    wi_extremes, wi_transitions, wi_high_to_low_times, wi_low_to_high_times = get_info(WI)
    wm_extremes, wm_transitions, wm_high_to_low_times, wm_low_to_high_times = get_info(WM)
    wr_extremes, wr_transitions, wr_high_to_low_times, wr_low_to_high_times = get_info(WR)
    wp_extremes, wp_transitions, wp_high_to_low_times, wp_low_to_high_times = get_info(WP)
    
    # single = [[wt_extremes, wt_transitions, wt_high_to_low_times, wt_low_to_high_times],
    #           [wi_extremes, wi_transitions, wi_high_to_low_times, wi_low_to_high_times],
    #           [wm_extremes, wm_transitions, wm_high_to_low_times, wm_low_to_high_times],
    #           [wr_extremes, wr_transitions, wr_high_to_low_times, wr_low_to_high_times],
    #           [wp_extremes, wp_transitions, wp_high_to_low_times, wp_low_to_high_times]]
    
    # wt_info = ['WT', max(wt_high_to_low_times), min(wt_high_to_low_times), sum(wt_high_to_low_times) / len(wt_high_to_low_times), max(wt_low_to_high_times), min(wt_low_to_high_times),sum(wt_low_to_high_times) / len(wt_low_to_high_times)]
    # wi_info = ['WI', max(wi_high_to_low_times), min(wi_high_to_low_times), sum(wi_high_to_low_times) / len(wi_high_to_low_times), max(wi_low_to_high_times), min(wi_low_to_high_times),sum(wi_low_to_high_times) / len(wi_low_to_high_times)]
    # wm_info = ['WM', max(wm_high_to_low_times), min(wm_high_to_low_times), sum(wm_high_to_low_times) / len(wm_high_to_low_times), max(wm_low_to_high_times), min(wm_low_to_high_times),sum(wm_low_to_high_times) / len(wm_low_to_high_times)]
    # wr_info = ['WR', max(wr_high_to_low_times), min(wr_high_to_low_times), sum(wr_high_to_low_times) / len(wr_high_to_low_times), max(wr_low_to_high_times), min(wr_low_to_high_times),sum(wr_low_to_high_times) / len(wr_low_to_high_times)]
    # wp_info = ['WP', max(wp_high_to_low_times), min(wp_high_to_low_times), sum(wp_high_to_low_times) / len(wp_high_to_low_times), max(wp_low_to_high_times), min(wp_low_to_high_times),sum(wp_low_to_high_times) / len(wp_low_to_high_times)]

    
    wt_info = [max(wt_high_to_low_times), min(wt_high_to_low_times), sum(wt_high_to_low_times) / len(wt_high_to_low_times), max(wt_low_to_high_times), min(wt_low_to_high_times),sum(wt_low_to_high_times) / len(wt_low_to_high_times)]
    wi_info = [max(wi_high_to_low_times), min(wi_high_to_low_times), sum(wi_high_to_low_times) / len(wi_high_to_low_times), max(wi_low_to_high_times), min(wi_low_to_high_times),sum(wi_low_to_high_times) / len(wi_low_to_high_times)]
    wm_info = [max(wm_high_to_low_times), min(wm_high_to_low_times), sum(wm_high_to_low_times) / len(wm_high_to_low_times), max(wm_low_to_high_times), min(wm_low_to_high_times),sum(wm_low_to_high_times) / len(wm_low_to_high_times)]
    wr_info = [max(wr_high_to_low_times), min(wr_high_to_low_times), sum(wr_high_to_low_times) / len(wr_high_to_low_times), max(wr_low_to_high_times), min(wr_low_to_high_times),sum(wr_low_to_high_times) / len(wr_low_to_high_times)]
    wp_info = [max(wp_high_to_low_times), min(wp_high_to_low_times), sum(wp_high_to_low_times) / len(wp_high_to_low_times), max(wp_low_to_high_times), min(wp_low_to_high_times),sum(wp_low_to_high_times) / len(wp_low_to_high_times)]

    
    return [wt_info, wi_info, wm_info, wr_info, wp_info]

# 定义文件路径
label_folder = 'mask_output/all'  # label文件夹路径
txt_file = 'mask_output/yaozhui.txt'  # jinzhuibing.txt文件路径

# 读取txt文件中的序号名
with open(txt_file, 'r') as file:
    sequence_numbers = file.read().splitlines()

result = []

# 遍历label文件夹中的文件
for seq_num in sequence_numbers:
    json_file = f'p{seq_num}L.json'
    json_path = os.path.join(label_folder, json_file)
    
    # 检查文件是否存在
    if os.path.exists(json_path):
        print(json_path)
        single = process(json_path)
        #print(single)
        result.append(single)
    # else:
    #     print(f'File {json_file} does not exist in the label folder.')

# print(result)

# # 打印 result 的整体形状
# print(f"Result has {len(result)} elements.")

# # 遍历 result 打印每个单独元素的形状
# for i, single in enumerate(result):
#     print(f"\nElement {i} has {len(single)} sub-elements:")
#     for j, sub_list in enumerate(single):
#         print(f"  Sub-element {j} has {len(sub_list)} items:")
#         if isinstance(sub_list, list):
#             for k, sub_sub_list in enumerate(sub_list):
#                 if isinstance(sub_sub_list, list):
#                     print(f"    Sub-sub-element {k} has {len(sub_sub_list)} items.")

# # 将 result 中的所有 single 列表转换为 numpy 数组
# result_array = np.array(result)

# # 计算 result 中所有 single 列表的平均值
# average_single = np.mean(result_array, axis=0)

# #打印结果
# print("Average values in the same shape as 'single':")
# print(average_single)

# # 以相同的形状存储结果
# average_single_list = average_single.tolist()

# # 打印结果
# print("Average values stored in the same shape as 'single':")
# print(average_single_list)

