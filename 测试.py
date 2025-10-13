relatedIds = '112,113'
# relatedIds = 112,113 # 类型是元组
print(type(relatedIds))
if isinstance(relatedIds, tuple):
    print("类型是元组")
elif isinstance(relatedIds, str):
    print("类型是字符串")
else:
    print(f"类型是其他: {type(relatedIds)}")
relatedIds_list = []
for x in relatedIds.split(','):
    relatedIds_list.append(x)
# relatedIds_list = [str(x) for x in relatedIds]
print(relatedIds_list)
if '112' in relatedIds_list:
    print("在列表中")
for i in relatedIds_list:
    print(i)