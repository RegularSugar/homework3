import pandas as pd

# 定义数据预处理类，封装IC卡数据预处理功能
class Preprocessor:
    # 初始化构造函数，接收csv文件路径
    def __init__(self, csv_path):
        self.csv_path = csv_path  # 赋值保存传入的csv文件路径
        self.df = None  # 初始化空变量，后续存储读取的数据集DataFrame

    # 第一步：读取数据
    def load_data(self):
        print("数据集前5行：")
        self.df = pd.read_csv(self.csv_path)  # 读取指定路径的csv文件到DataFrame
        print(self.df.head())  # 打印数据集前5条样本

        print("基本信息：")
        print(f"行数={self.df.shape[0]}, 列数={self.df.shape[1]}")  # shape[0]行数 shape[1]列数
        print(self.df.dtypes)  # 打印每一列对应的数据类型
        print()

    # 第二步：时间解析
    def parse_transaction_time(self):
        # 将字符串格式的交易时间转为datetime时间类型
        self.df["交易时间"] = pd.to_datetime(self.df["交易时间"])
        # 从datetime时间中提取小时整数，新建hour列存入数据
        self.df["hour"] = self.df["交易时间"].dt.hour

    # 构造衍生字段
    def build_ride_stops(self):
        # 上下车站点数值做差取绝对值，得到搭乘站点数量，新建ride_stops列
        self.df["ride_stops"] = abs(self.df["下车站点"] - self.df["上车站点"])
        # 统计ride_stops等于0的异常记录总条数
        drop_cnt = len(self.df[self.df["ride_stops"] == 0])
        # 保留不为0的数据，同时重置行索引
        self.df = self.df[self.df["ride_stops"] != 0].reset_index(drop=True)
        # 打印被删除的异常行数
        print(f"构造 ride_stops 后删除异常记录（ride_stops==0/无法计算）行数：{drop_cnt}\n")

    # 缺失值检查
    def check_missing(self):
        # 统计每一列各自的缺失值数量
        miss_series = self.df.isnull().sum()
        # 筛选出缺失数量大于0的列
        miss_exist = miss_series[miss_series > 0]

        print("各列缺失值数量：")
        # 判断是否存在有缺失数据的列
        if len(miss_exist) > 0:
            print(miss_exist)  # 打印存在缺失的列和对应缺失条数
            self.df = self.df.dropna().reset_index(drop=True)  # 删除所有含缺失值的行并重置索引
        else:
            print("无缺失值\n")  # 全部列无缺失

    # 执行整套预处理工作流
    def run(self):
        self.load_data()  # 1.读取数据打印基础信息
        self.parse_transaction_time()  # 2.时间转换提取小时
        self.build_ride_stops()  # 3.计算站点数+剔除异常
        self.check_missing()  # 4.缺失值检测清洗
        return self.df  # 返回处理完成后的干净数据集


# 程序入口，脚本直接运行时执行下面代码
if __name__ == "__main__":
    processor = Preprocessor("ICData.csv")  # 实例化预处理对象，传入数据文件名
    result_df = processor.run()  # 启动流水线，获取清洗完毕的数据