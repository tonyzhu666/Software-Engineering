# """
# 个人记账本应用 - 主入口文件
# """
# import tkinter as tk
# from finance_app import PersonalFinanceApp

# def main():
#     """主函数"""
#     try:
#         root = tk.Tk()
#         app = PersonalFinanceApp(root)
#         root.mainloop()
#     except Exception as e:
#         print(f"应用程序启动失败: {e}")
#         input("按回车键退出...")

# if __name__ == "__main__":
#     main()
"""
个人记账本应用 - 主入口文件
"""
import tkinter as tk
from finance_app import PersonalFinanceApp

def main():
    """主函数"""
    try:
        root = tk.Tk()
        app = PersonalFinanceApp(root)
        root.mainloop()
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()