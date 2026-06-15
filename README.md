# 王弘森-25361149-第三次人工智能编程作业
仓库链接: https://github.com/RegularSugar/homework3.git
## 1. 任务拆解与 AI 协作策略
&emsp;&emsp;本次作业包含6项公交刷卡数据分析任务，在与AI协作的过程中，我按照如下步骤进行操作：<br>
### 1）基础模块架构
&emsp;&emsp;首先自主将项目分为主程序，预处理和数据分析三个模块，询问AI合理性；得到肯定回答后，要求AI创建Analyze类、完成__init__初始化逻辑。<br>
### 2）单任务串行开发
&emsp;&emsp;首先给出指令让AI完成预处理模块内容，要求过滤刷卡类型=0的有效客流数据、预生成 hour 数值数组。<br>
&emsp;&emsp;随后按照任务顺逐个开发功能。一轮对话只下发一个任务的完整需求，一次只生成一个任务对应的方法函数。单个任务内细分：先数值统计逻辑、再绘图代码、最后打印输出格式约束。<br>
### 3）debug
&emsp;&emsp;开发过程中，出现错误，先自己解决；若不能一下子解决，把警告报错、运行绘图异常截图并描述，让AI针对性修改出错片段。<br>
&emsp;&emsp;所有功能代码全部完成后，将完整代码一次性发给AI，进行检查和优化。

## 2. 核心 Prompt 迭代记录
### 初代 Prompt:
&emsp;&emsp;帮我写任务6的热力图功能代码，把司机、线路、站点、车辆Top10客流使用Seaborn做成热力图。
### 存在的问题
1.色板选择随意， 低客流深色、高客流浅色，不符合逻辑；<br>
2.没有关闭多余图例；<br>
3.热力图数值标注字体排版不好；<br>
4.没有适配作业要求的主次标题分层排版。<br>
### 优化后的Prompt
&emsp;&emsp;重写任务6热力图绘制代码，严格遵守以下调色与绘图规范：<br>
&emsp;&emsp;1.调色板使用黄橙红递进渐变YlOrRd，数值越小颜色越浅、客流数值越大颜色越深；
2.热力图格子之间增加细分割线 linewidths=0.5，格子内数字格式设置为整数"；
3.分层标题：大总标题用 suptitle 加粗字号 16，下方小字副标题说明数据筛选条件；
4.去掉多余 X 轴大标签；
5.保存图片时dpi设为150；
6.不要额外生成颜色图例条以外多余组件，保持图表简洁；
### 迭代效果：
&emsp;&emsp;生成了合格的图片
## 3. Debug 与异常处理记录
### 报错现象
&emsp;&emsp;PyCharm 静态类型检查在三处绘图代码行持续抛出相同警告：
`应为类型 'float'，但实际为 'tuple[Literal[10], Literal[8]]'`<br>
&emsp;&emsp;报错位置为所有`plt.figure(figsize=(10,8))`、`plt.figure(figsize=(14,7))`画布创建语句。<br>
&emsp;&emsp;程序运行完全正常，图片可以正常导出保存，但PyCharm仍然警告。
### 排查与解决过程
#### 1. 问题根源判断
&emsp;&emsp;根据报错提示，应该改成一个float数而不是元组，但这样不符合原来的要求<br>
#### 2. 尝试修改
&emsp;&emsp;根据AI建议，将尺寸改为浮点字面量`(10.0, 8.0)`，代码依然会被识别为`tuple[float, float]`；matplotlib官方参数签名对元组传入的类型标注兼容性不足，因此持续触发类型不匹配警告。<br>
#### 3. 最终解决
&emsp;&emsp;把又一次报错结果发给AI，AI又建议彻底放弃使用figsize传递元组的写法，先初始化空白画布对象，再调用对象方法分别设置宽度、高度浮点数值，规避 tuple 类型：
```python
# 替换原代码 plt.figure(figsize=(10,8))
fig = plt.figure()
fig.set_figwidth(10.0)
fig.set_figheight(8.0)
```

## 4. 人工代码审查 (Code Review)
```python
def peak_hour_phf(self):
    # 创建长为24（24小时）的整型numpy零数组，用来存储0-23每个小时的刷卡总数量
    hour_count_arr = np.zeros(24, dtype=int)
    # 遍历24个小时，逐一统计客流量
    for h in range(24):
        # 求和得到该小时全部刷卡记录数，其中通过self.hour_np == h筛选
        hour_count_arr[h] = np.sum(self.hour_np == h)
        
    #-----------------------------高峰小时识别-------------------------------------------------
    # 获取高峰小时的索引
    peak_hour = np.argmax(hour_count_arr)
    # 取出高峰小时全天总刷卡量
    peak_total = hour_count_arr[peak_hour]

    # 筛选高峰小时内的原始数据，copy副本以防止修改原始数据集
    peak_df = self.df[self.df["hour"] == peak_hour_int].copy()

    # -------------------------5分钟粒度统计---------------------------------------------
    # 将时间向下对齐到5分钟刻度，生成分组标签
    peak_df["time_5min"] = peak_df["交易时间"].dt.floor("5min")
    # 按5分钟时间分组，统计每组刷卡数量，同时重命名计数字段
    group_5min = peak_df.groupby("time_5min").size().reset_index(name="count_5")
    # 找到客流量最高的5分钟那一行数据
    max_5_row = group_5min.loc[group_5min["count_5"].idxmax()]
    # 提取峰值5分钟的刷卡次数
    max_5_num = max_5_row["count_5"]
    # 峰值窗口起始时间
    max_5_start = max_5_row["time_5min"]
    # 起始时间+5分钟=结束时间
    max_5_end = max_5_start + pd.Timedelta(minutes=5)
    # 套用PHF5公式
    phf5 = peak_total / (12 * max_5_num)

    # --------------------------15分钟粒度统计------------------------------------------
    # 将时间向下对齐到15分钟刻度，生成分组标签
    peak_df["time_15min"] = peak_df["交易时间"].dt.floor("15min")
    # 按15分钟时间分组，统计每组刷卡数量，同时重命名计数字段
    group_15min = peak_df.groupby("time_15min").size().reset_index(name="count_15")
    # 找到客流量最高的15分钟那一行数据
    max_15_row = group_15min.loc[group_15min["count_15"].idxmax()]
    # 提取峰值15分钟的刷卡次数
    max_15_num = max_15_row["count_15"]
    # 峰值窗口起始时间
    max_15_start = max_15_row["time_15min"]
    # 起始时间+5分钟=结束时间
    max_15_end = max_15_start + pd.Timedelta(minutes=15)
    # 套用PHF15公式
    phf15 = peak_total / (4 * max_15_num)

    # 按格式要求打印结果
    print("[任务4] 高峰小时系数PHF计算结果：")
    # 使用int()强制转换格式，避免报错，:02d用0填补个位数空缺
    print(f"高峰小时：{int(peak_hour):02d}:00 ~ {int(peak_hour + 1):02d}:00，刷卡量：{peak_total} 次")
    # 打印5分钟粒度统计结果
    print(f"最大5分钟刷卡量（{max_5_start.strftime('%H:%M')}~{max_5_end.strftime('%H:%M')}）：{max_5_num} 次 PHF5 = {peak_total} / (12 × {max_5_num}) = {phf5:.4f}")
    # 打印15分钟粒度统计结果
    print(f"最大15分钟刷卡量（{max_15_start.strftime('%H:%M')}~{max_15_end.strftime('%H:%M')}）：{max_15_num} 次 PHF15 = {peak_total} / (4 × {max_15_num}) = {phf15:.4f}")
    print()
    
# 方便在主程序清晰调用任务4
def task4_run(self):
    self.peak_hour_phf()