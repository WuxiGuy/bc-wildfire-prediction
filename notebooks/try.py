import pandas as pd

# 创建一个示例DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': ['a', 'b', 'c']
})

# 创建一个新行的数据
new_row = {'A': 4, 'B': 'd'}

# 使用append()函数增加新行
# 注意：append()函数返回一个新的DataFrame对象，不会修改原始DataFrame，除非你重新赋值
df = df._append(new_row, ignore_index=True)

print(df)
