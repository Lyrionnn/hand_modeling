# 打印 result 的整体形状
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
