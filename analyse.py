import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

class Analyze:
    def __init__(self, processed_df):
        self.df = processed_df
        # 筛选仅刷卡类型等于0的记录
        self.df = self.df[self.df["刷卡类型"] == 0].reset_index(drop=True)
        # 将hour列转为numpy数组
        self.hour_np = np.array(self.df["hour"])
        # 全天总有效刷卡次数
        self.total_all = len(self.hour_np)

#---任务2------------------------------------------------------------------------------
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
        plt.figure(figsize=(10,8))
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
        plt.tight_layout()
        plt.savefig("hour_distribution.png", dpi=150)
        plt.close()
        print("[任务2(b)] 已保存图像：hour_distribution.png\n")

    def task2_run(self):
        # 执行整个任务2的流程
        self.calculate_early_late_volume()
        self.draw_hour_distribution()

#---任务3--------------------------------------------------------------------------------------------------
    @staticmethod
    def analyze_route_stops( df, route_col='线路号', stops_col='ride_stops'):
        """
               计算各线路乘客的平均搭乘站点数及其标准差。
               Parameters
               ----------
               df : pd.DataFrame
                   预处理后的数据集
               route_col : str
                   线路号列名
               stops_col : str
                   搭乘站点数列名
               Returns
               -------
               pd.DataFrame
                   包含列：线路号、mean_stops、std_stops，按 mean_stops 降序排列
        """
        # 分组聚合：均值、标准差
        route_group = df.groupby(route_col)[stops_col].agg(
            mean_stops="mean",
            std_stops="std"
        ).reset_index()
        # 按均值降序排序
        route_result = route_group.sort_values(by="mean_stops", ascending=False).reset_index(drop=True)
        return route_result

    def top15_route_stops(self):
        # 调用函数并打印前10行
        route_df = self.analyze_route_stops(self.df)
        print("[任务3] 每条线路的平均搭乘站点数及标准差（前10行）：")
        print(route_df.head(10).to_string())
        print("\n")

        # 取均值最高前15条线路
        top15_df = route_df.head(15)
        # 设置画布
        plt.figure(figsize=(10, 8))

        # seaborn水平条形图
        sns.barplot(
            data=top15_df,
            x="mean_stops",
            y="线路号",
            hue="线路号",
            palette=sns.color_palette("Blues_d", len(top15_df)),
            orient="h",
            legend=False
        )
        # 添加误差棒
        y_pos = np.arange(len(top15_df))
        plt.errorbar(
            x=top15_df["mean_stops"],
            y=y_pos,
            xerr=top15_df["std_stops"],
            fmt="none",
            c="black",
            capsize=3
        )

        # 设置柱状图图主标题和轴标题
        plt.title("Top 15 Routes: Mean Ride Stops (with Std Dev)", fontsize=14)
        plt.xlabel("Mean Ride Stops", fontsize=12)
        plt.ylabel("Route ID", fontsize=12)
        # X轴从0开始
        plt.xlim(left=0)
        # 紧凑布局保存图片
        plt.tight_layout()
        plt.savefig("route_stops.png", dpi=150)
        plt.close()
        print("[任务3] 已保存图像：route_stops.png\n")

    def task3_run(self):
        self.top15_route_stops()

#---任务4--------------------------------------------------------------------------------------------------
    def peak_hour_phf(self):
        # 统计全天每小时刷卡总量，找出高峰小时
        hour_count_arr = np.zeros(24, dtype=int)
        for h in range(24):
            hour_count_arr[h] = np.sum(self.hour_np == h)
        peak_hour = np.argmax(hour_count_arr)  # 刷卡量最大的小时数值
        peak_total = hour_count_arr[peak_hour]  # 高峰小时总刷卡量

        # 筛选出高峰小时内的完整原始数据
        peak_df = self.df[self.df["hour"] == peak_hour].copy()

        # 5分钟粒度统计
        # 以5分钟为时间窗口进行聚合
        peak_df["time_5min"] = peak_df["交易时间"].dt.floor("5min")
        group_5min = peak_df.groupby("time_5min").size().reset_index(name="count_5")
        max_5_row = group_5min.loc[group_5min["count_5"].idxmax()]
        max_5_num = max_5_row["count_5"]
        max_5_start = max_5_row["time_5min"]
        max_5_end = max_5_start + pd.Timedelta(minutes=5)
        # 计算PHF5
        phf5 = peak_total / (12 * max_5_num)

        # 15分钟粒度统计
        # 以5分钟为时间窗口进行聚合
        peak_df["time_15min"] = peak_df["交易时间"].dt.floor("15min")
        group_15min = peak_df.groupby("time_15min").size().reset_index(name="count_15")
        max_15_row = group_15min.loc[group_15min["count_15"].idxmax()]
        max_15_num = max_15_row["count_15"]
        max_15_start = max_15_row["time_15min"]
        max_15_end = max_15_start + pd.Timedelta(minutes=15)
        # 计算PHF15
        phf15 = peak_total / (4 * max_15_num)

        # 4. 按题目固定格式打印输出
        print("[任务4] 高峰小时系数PHF计算结果：")
        print(f"高峰小时：{int(peak_hour):02d}:00 ~ {int(peak_hour + 1):02d}:00，刷卡量：{peak_total} 次")
        print(
            f"最大5分钟刷卡量（{max_5_start.strftime('%H:%M')}~{max_5_end.strftime('%H:%M')}）：{max_5_num} 次 PHF5 = {peak_total} / (12 × {max_5_num}) = {phf5:.4f}")
        print(
            f"最大15分钟刷卡量（{max_15_start.strftime('%H:%M')}~{max_15_end.strftime('%H:%M')}）：{max_15_num} 次 PHF15 = {peak_total} / (4 × {max_15_num}) = {phf15:.4f}")
        print()

    def task4_run(self):
        self.peak_hour_phf()


#---任务5----------------------------------------------------------------------------------------------------------------------------
    def export_route_driver_info(self):

        # 筛选线路号1101 ~ 1120的数据
        route_arr = np.array(self.df["线路号"])
        mask_route = (route_arr >= 1101) & (route_arr <= 1120)
        filter_df = self.df[mask_route].copy()

        # 定义文件夹名称，不存在则新建
        folder_name = "线路驾驶员信息"
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        # 存放所有生成文件路径，最后统一打印
        file_path_list = []

        # 遍历1101到1120全部20条线路
        for route_id in range(1101, 1121):
            # 单独取出当前线路的数据
            single_route_df = filter_df[filter_df["线路号"] == route_id]
            # 去重
            unique_mapping = single_route_df[["车辆编号", "驾驶员编号"]].drop_duplicates()

            # 拼接txt文件完整路径
            file_name = f"{route_id}.txt"
            full_file_path = os.path.join(folder_name, file_name)
            file_path_list.append(full_file_path)

            # 打开文件写入内容
            with open(full_file_path, "w", encoding="utf-8") as f:
                # 写入
                f.write(f"线路号: {route_id}\n")
                for _, row in unique_mapping.iterrows():
                    car_id = row["车辆编号"]
                    driver_id = row["驾驶员编号"]
                    f.write(f"{int(car_id)}\t{int(driver_id)}\n")

        # 按要求打印全部生成的文件路径
        print("[任务5] 已生成20个文件，路径如下：")
        for path in file_path_list:
            print(path)
        print("\n")

    def task5_run(self):
        self.export_route_driver_info()

#---任务6-----------------------------------------------------------------------------------------------------------
    def analyze_service_performance(self):
        # 1. 统计各维度服务人次
        # Top 10 司机
        top10_driver = (self.df.groupby("驾驶员编号").size()
                        .sort_values(ascending=False).head(10))
        # Top 10 线路
        top10_route = (self.df.groupby("线路号").size()
                       .sort_values(ascending=False).head(10))
        # Top 10 上车站点
        top10_station = (self.df.groupby("上车站点").size()
                         .sort_values(ascending=False).head(10))
        # Top 10 车辆
        top10_vehicle = (self.df.groupby("车辆编号").size()
                         .sort_values(ascending=False).head(10))

        # 打印各排名
        print("[任务6] 排名统计：")
        # Top 10 司机
        print("\n===Drivers Top 10===")
        for rank, (driver_id, count) in enumerate(top10_driver.items(), 1):
            print(f"  Top{rank}:  {driver_id}   count={count}")
        # Top 10 线路
        print("\n===Routes Top 10===")
        for rank, (route_id, count) in enumerate(top10_route.items(), 1):
            print(f"  Top{rank}:  {route_id}   count={count}")
        # Top 10 上车站点
        print("\n===Boarding Stations Top 10===")
        for rank, (station_id, count) in enumerate(top10_station.items(), 1):
            print(f"  Top{rank}:  {station_id}   count={count}")
        # Top 10 车辆
        print("\n===Vehicles Top 10===")
        for rank, (vehicle_id, count) in enumerate(top10_vehicle.items(), 1):
            print(f"  Top{rank}:  {vehicle_id}   count={count}")
        print()

        # 2. 构造 4×10 热力图数据
        # 列标签 Top1~Top10
        top_labels = [f"Top{i}" for i in range(1, 11)]
        # 行标签
        row_labels = ["Driver", "Route", "Boarding Station", "Vehicle"]
        # 构造DataFrame，每行一个维度
        heatmap_data = pd.DataFrame(
            [top10_driver.values, top10_route.values,
             top10_station.values, top10_vehicle.values],
            index=row_labels,
            columns=top_labels
        )

        # 3. 绘制热力图
        plt.figure(figsize=(14, 7))
        sns.heatmap(
            heatmap_data,
            annot=True,  # 格内标注数值
            fmt="d",  # 整数格式
            cmap="YlOrRd",  # 色图
            linewidths=0.5  # 格线宽度
        )
        # 标题
        plt.suptitle("Service Performance Ranking Heatmap",
                     fontsize=16, fontweight="bold")
        plt.title("counts of valid boarding records(card type = 0)",
                  fontsize=12, pad=20)


        plt.xlabel("")  # x轴无标签
        plt.xticks(rotation=0)  # x轴标签不旋转
        plt.tight_layout()
        plt.savefig("performance_heatmap.png", dpi=150, bbox_inches="tight")
        plt.close()
        print("[任务6] 已保存图像：performance_heatmap.png\n")

        # 4. 结论说明
        print("[任务6] 结论说明：")
        print(f"从热力图可观察到以下服务绩效规律：")
        print(f"  1. Top1司机服务人次为{top10_driver.iloc[0]}次，"
              f"是Top10司机均值{top10_driver.mean():.0f}次的"
              f"{top10_driver.iloc[0] / top10_driver.mean():.1f}倍，"
              f"说明头部司机工作量显著高于同行。")
        print(f"  2. Top1线路（线路{top10_route.index[0]}）客流达"
              f"{top10_route.iloc[0]}次，远超其他线路，"
              f"表明该线路为城市主干线路或途经核心商圈。")
        print(f"  3. Top1上车站点客流为{top10_station.iloc[0]}次，"
              f"站点间差异明显，反映乘客出行具有显著的集聚效应。")
        print(f"  4. 车辆维度与司机维度高度相关，热门线路的车辆服务人次普遍较高。")

    def task6_run(self):
        self.analyze_service_performance()