from preprocess import Preprocessor

if __name__ == "__main__":#创建实例
    processor = Preprocessor("ICData.csv")
    result_df = processor.run()  # 启动预处理工作流