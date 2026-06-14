import numpy as np
import matplotlib.pyplot as plt

class Analyze:
    def __init__(self, processed_df):
        self.df = processed_df
        # 筛选仅刷卡类型等于0的记录
        self.df = self.df[self.df["刷卡类型"] == 0].reset_index(drop=True)
        # 将hour列转为numpy数组
        self.hour_np = np.array(self.df["hour"])
        # 全天总有效刷卡次数
        self.total_all = len(self.hour_np)

    def calculate_early_late_volume(self):
        #统计早7点前、22点后刷卡量并计算占比，使用numpy布尔索引

        # 筛选早峰前：hour < 7
        mask_early = self.hour_np < 7
        count_early = np.sum(mask_early)

        # 筛选深夜时段：hour >= 22
        mask_late = self.hour_np >= 22
        count_late = np.sum(mask_late)

        # 计算占比，保留两位小数
        percent_early = round((count_early / self.total_all) * 100, 2)
        percent_late = round((count_late / self.total_all) * 100, 2)

        # 打印结果
        print("[任务2(a)] 早峰前/深夜上车刷卡量：")
        print(f"早上7点前公共交通上车刷卡量为：{count_early} 次，占全天 {percent_early}%")
        print(f"晚上10点后公共交通上车刷卡量为：{count_late} 次，占全天 {percent_late}%")
        print()
        return count_early, count_late, percent_early, percent_late

    def draw_hour_distribution(self):
        # 绘制24小时刷卡量分布柱状图，高亮早晚时段并保存图片
        # 初始化0-23小时计数数组
        hour_count_arr = np.zeros(24, dtype=int)
        # 逐小时统计刷卡数量
        for hour in range(24):
            hour_count_arr[hour] = np.sum(self.hour_np == hour)

        # 设置柱子颜色：默认蓝色，早<7、晚>=22 橙色高亮
        bar_color_list = ["#2374E1"] * 24
        for h in range(24):
            if h < 7 or h >= 22:
                bar_color_list[h] = "#ff7f24"

        # 创建画布并绘制柱状图
        plt.figure(figsize=(14,8))
        x_coords = np.arange(0, 24)
        plt.bar(x_coords, hour_count_arr,
                color=bar_color_list,
                label="Early & Late Highlight")

        # 设置图表标题、坐标轴标签
        plt.title("24-hour Boarding Counts Distribution", fontsize=14)
        plt.xlabel("Hour (0~23)", fontsize=12)
        plt.ylabel("Boarding Count", fontsize=12)
        # X轴刻度步长为2
        plt.xticks(np.arange(0, 24, 2))
        plt.grid(color="gray", alpha=0.4)
        plt.legend()
        plt.savefig("hour_distribution.png", dpi=150)
        plt.show()
        print("[任务2(b)] 已保存图像：hour_distribution.png\n")

    def task2_run(self):
        # 执行整个任务2流程
        self.calculate_early_late_volume()
        self.draw_hour_distribution()

