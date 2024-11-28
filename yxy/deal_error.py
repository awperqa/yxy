class CustomError(Exception):
    def __init__(self, message):
        # 调用父类的构造方法，将消息传递给父类
        super().__init__(message)
        self.message = message  # 保证 message 属性被正确赋值