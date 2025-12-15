import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd  # 新增：用于Excel导出


class TransactionType:
    """交易类型枚举"""
    INCOME = "收入"
    EXPENSE = "支出"


class Transaction:
    """交易类"""
    
    def __init__(self, transaction_id: str, amount: float, 
                 transaction_type: str, category: str, 
                 date: str, note: str = ""):
        self.transaction_id = transaction_id
        self.amount = amount
        self.type = transaction_type
        self.category = category
        self.date = date
        self.note = note
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'transaction_id': self.transaction_id,
            'amount': self.amount,
            'type': self.type,
            'category': self.category,
            'date': self.date,
            'note': self.note
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        """从字典创建交易对象"""
        return cls(
            transaction_id=data['transaction_id'],
            amount=data['amount'],
            transaction_type=data['type'],
            category=data['category'],
            date=data['date'],
            note=data.get('note', '')
        )


class Budget:
    """预算类"""
    
    def __init__(self, budget_id: str, category: str, amount: float, 
                 month: str, note: str = ""):
        self.budget_id = budget_id
        self.category = category
        self.amount = amount
        self.month = month  # 格式：YYYY-MM
        self.note = note
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'budget_id': self.budget_id,
            'category': self.category,
            'amount': self.amount,
            'month': self.month,
            'note': self.note
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Budget':
        """从字典创建预算对象"""
        return cls(
            budget_id=data['budget_id'],
            category=data['category'],
            amount=data['amount'],
            month=data['month'],
            note=data.get('note', '')
        )


class CategoryService:
    """分类服务类"""
    
    def __init__(self):
        self.default_categories = {
            TransactionType.INCOME: ["工资", "奖金", "投资", "其他收入"],
            TransactionType.EXPENSE: ["餐饮", "交通", "购物", "娱乐", "住房", "医疗", "教育", "其他支出"]
        }
        self.user_categories = {
            TransactionType.INCOME: [],
            TransactionType.EXPENSE: []
        }
        self.load_categories()
    
    def get_categories_by_type(self, transaction_type: str) -> List[str]:
        """根据交易类型获取分类列表"""
        default = self.default_categories.get(transaction_type, [])
        user = self.user_categories.get(transaction_type, [])
        return default + user
    
    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        income_categories = self.get_categories_by_type(TransactionType.INCOME)
        expense_categories = self.get_categories_by_type(TransactionType.EXPENSE)
        return list(set(income_categories + expense_categories))
    
    def add_user_category(self, transaction_type: str, category: str) -> bool:
        """添加用户自定义分类"""
        if category and category not in self.user_categories[transaction_type]:
            self.user_categories[transaction_type].append(category)
            self.save_categories()
            return True
        return False
    
    def save_categories(self, filename: str = "categories.json"):
        """保存分类配置"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.user_categories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存分类配置失败: {e}")
    
    def load_categories(self, filename: str = "categories.json"):
        """加载分类配置"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_categories = json.load(f)
                    # 确保两个类型都有列表
                    self.user_categories = {
                        TransactionType.INCOME: loaded_categories.get(TransactionType.INCOME, []),
                        TransactionType.EXPENSE: loaded_categories.get(TransactionType.EXPENSE, [])
                    }
        except Exception as e:
            print(f"加载分类配置失败: {e}")


class BudgetService:
    """预算服务类"""
    
    def __init__(self, data_file: str = "budgets.json"):
        self.data_file = data_file
        self.budgets: List[Budget] = []
        self.load_budgets()
    
    def create_budget(self, category: str, amount: float, 
                     month: str, note: str = "") -> bool:
        """创建预算"""
        # 验证金额必须为正数
        if amount <= 0:
            print(f"错误：预算金额必须大于0，当前金额：{amount}")
            return False
        try:
            # 检查是否已存在该类别该月的预算
            for budget in self.budgets:
                if budget.category == category and budget.month == month:
                    return False  # 已存在
            
            budget_id = f"B{len(self.budgets) + 1:06d}"
            budget = Budget(
                budget_id=budget_id,
                category=category,
                amount=amount,
                month=month,
                note=note
            )
            self.budgets.append(budget)
            self.save_budgets()
            return True
        except Exception as e:
            print(f"创建预算失败: {e}")
            return False
    
    def update_budget(self, budget_id: str, amount: float, 
                     month: str, note: str = "") -> bool:
        """更新预算"""
        try:
            for budget in self.budgets:
                if budget.budget_id == budget_id:
                    budget.amount = amount
                    budget.month = month
                    budget.note = note
                    self.save_budgets()
                    return True
            return False
        except Exception as e:
            print(f"更新预算失败: {e}")
            return False
    
    def delete_budget(self, budget_id: str) -> bool:
        """删除预算"""
        try:
            for i, budget in enumerate(self.budgets):
                if budget.budget_id == budget_id:
                    #bug2
                    budget_to_delete = self.budgets[i]
                    del self.budgets[i]
                    del budget_to_delete
                    self.save_budgets()
                    return True
            return False
        except Exception as e:
            print(f"删除预算失败: {e}")
            return False
    
    def get_budget_by_id(self, budget_id: str) -> Budget:
        """根据ID获取预算"""
        for budget in self.budgets:
            if budget.budget_id == budget_id:
                return budget
        return None
    
    def get_budgets_by_month(self, month: str) -> List[Budget]:
        """根据月份获取预算"""
        return [budget for budget in self.budgets if budget.month == month]
    
    def get_budget_by_category_month(self, category: str, month: str) -> Budget:
        """根据类别和月份获取预算"""
        for budget in self.budgets:
            if budget.category == category and budget.month == month:
                return budget
        return None
    
    def get_all_budgets(self) -> List[Budget]:
        """获取所有预算"""
        return self.budgets
    
    def save_budgets(self):
        """保存预算数据"""
        try:
            data = [b.to_dict() for b in self.budgets]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存预算数据失败: {e}")
    
    def load_budgets(self):
        """加载预算数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.budgets = [Budget.from_dict(item) for item in data]
        except Exception as e:
            print(f"加载预算数据失败: {e}")


class TransactionService:
    """交易服务类"""
    
    def __init__(self, data_file: str = "transactions.json"):
        self.data_file = data_file
        self.transactions: List[Transaction] = []
        self.load_transactions()
    
    # def create_transaction(self, amount: float, transaction_type: str, 
    #                       category: str, date: str, note: str = "") -> bool:
    #     """创建交易"""
    #     try:
    #         transaction_id = f"T{len(self.transactions) + 1:06d}"
    #         transaction = Transaction(
    #             transaction_id=transaction_id,
    #             amount=amount,
    #             transaction_type=transaction_type,
    #             category=category,
    #             date=date,
    #             note=note
    #         )
    #         self.transactions.append(transaction)
    #         self.save_transactions()
    #         return True
    #     except Exception as e:
    #         print(f"创建交易失败: {e}")
    #         return False
    def create_transaction(self, amount: float, transaction_type: str, 
                      category: str, date: str, note: str = "") -> bool:
        """创建交易"""
        try:
            # 添加金额验证
            if amount <= 0:
                return False
                
            # 验证日期格式
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return False
                
            transaction_id = f"T{len(self.transactions) + 1:06d}"
            transaction = Transaction(
                transaction_id=transaction_id,
                amount=amount,
                transaction_type=transaction_type,
                category=category,
                date=date,
                note=note
            )
            self.transactions.append(transaction)
            self.save_transactions()
            return True
        except Exception as e:
            print(f"创建交易失败: {e}")
            return False
    
    # def update_transaction(self, transaction_id: str, amount: float, 
    #                       transaction_type: str, category: str, 
    #                       date: str, note: str = "") -> bool:
    #     """更新交易记录"""
    #     try:
    #         for transaction in self.transactions:
    #             if transaction.transaction_id == transaction_id:
    #                 transaction.amount = amount
    #                 transaction.type = transaction_type
    #                 transaction.category = category
    #                 transaction.date = date
    #                 transaction.note = note
    #                 self.save_transactions()
    #                 return True
    #         return False
    #     except Exception as e:
    #         print(f"更新交易失败: {e}")
    #         return False
    def update_transaction(self, transaction_id: str, amount: float, 
                      transaction_type: str, category: str, 
                      date: str, note: str = "") -> bool:
        """更新交易记录"""
        try:
            # 添加金额验证
            if amount <= 0:
                return False
                
            # 验证日期格式
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return False
                
            for transaction in self.transactions:
                if transaction.transaction_id == transaction_id:
                    transaction.amount = amount
                    transaction.type = transaction_type
                    transaction.category = category
                    transaction.date = date
                    transaction.note = note
                    self.save_transactions()
                    return True
            return False
        except Exception as e:
            print(f"更新交易失败: {e}")
            return False
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """删除交易记录"""
        try:
            for i, transaction in enumerate(self.transactions):
                if transaction.transaction_id == transaction_id:
                    del self.transactions[i]
                    self.save_transactions()
                    return True
            return False
        except Exception as e:
            print(f"删除交易失败: {e}")
            return False
    
    def get_transaction_by_id(self, transaction_id: str) -> Transaction:
        """根据ID获取交易记录"""
        for transaction in self.transactions:
            if transaction.transaction_id == transaction_id:
                return transaction
        return None
    
    def get_all_transactions(self) -> List[Transaction]:
        """获取所有交易"""
        return self.transactions
    
    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> List[Transaction]:
        """根据日期范围获取交易"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            filtered_transactions = []
            for transaction in self.transactions:
                trans_date = datetime.strptime(transaction.date, "%Y-%m-%d")
                if start <= trans_date <= end:
                    filtered_transactions.append(transaction)
            
            return filtered_transactions
        except ValueError as e:
            print(f"日期格式错误: {e}")
            return []
    
    def get_transactions_by_month(self, month: str) -> List[Transaction]:
        """根据月份获取交易（格式：YYYY-MM）"""
        try:
            year, month_num = map(int, month.split('-'))
            start_date = datetime(year, month_num, 1)
            if month_num == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
            
            return self.get_transactions_by_date_range(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
        except ValueError as e:
            print(f"月份格式错误: {e}")
            return []
    
    def search_transactions(self, keyword: str = "", 
                           transaction_type: str = "", 
                           category: str = "",
                           start_date: str = "", 
                           end_date: str = "",
                           min_amount: float = None,
                           max_amount: float = None) -> List[Transaction]:
        """搜索交易"""
        results = self.transactions
        #bug1
        large_buffer = [0] * 1000
        
        # 关键词搜索
        if keyword:
            results = [t for t in results if 
                      keyword.lower() in t.note.lower() or 
                      keyword.lower() in t.category.lower() or
                      keyword in str(t.amount)]
        
        # 交易类型筛选
        if transaction_type:
            results = [t for t in results if t.type == transaction_type]
        
        # 分类筛选
        if category:
            results = [t for t in results if t.category == category]
        
        # 日期范围筛选
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                results = [t for t in results if 
                          start <= datetime.strptime(t.date, "%Y-%m-%d") <= end]
            except ValueError:
                pass
        
        # 金额范围筛选
        if min_amount is not None:
            results = [t for t in results if t.amount >= min_amount]
        
        if max_amount is not None:
            results = [t for t in results if t.amount <= max_amount]
        
        return results
    
    def export_to_csv(self, filename: str, transactions: List[Transaction] = None) -> bool:
        """导出交易数据到CSV"""
        try:
            if transactions is None:
                transactions = self.transactions
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(['交易ID', '日期', '类型', '分类', '金额', '备注'])
                
                # 写入数据
                for transaction in transactions:
                    writer.writerow([
                        transaction.transaction_id,
                        transaction.date,
                        transaction.type,
                        transaction.category,
                        transaction.amount,
                        transaction.note
                    ])
            return True
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
    
    def export_to_excel(self, filename: str, transactions: List[Transaction] = None) -> bool:
        """导出交易数据到Excel"""
        try:
            if transactions is None:
                transactions = self.transactions
            
            # 准备数据
            data = []
            for transaction in transactions:
                data.append({
                    '交易ID': transaction.transaction_id,
                    '日期': transaction.date,
                    '类型': transaction.type,
                    '分类': transaction.category,
                    '金额': transaction.amount,
                    '备注': transaction.note
                })
            
            # 创建DataFrame并导出
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"导出Excel失败: {e}")
            return False
    
    def save_transactions(self):
        """保存交易数据"""
        try:
            data = [t.to_dict() for t in self.transactions]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存交易数据失败: {e}")
    
    def load_transactions(self):
        """加载交易数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.transactions = [Transaction.from_dict(item) for item in data]
        except Exception as e:
            print(f"加载交易数据失败: {e}")


class StatisticsService:
    """统计服务类"""
    
    def __init__(self, transaction_service: TransactionService, budget_service: BudgetService = None):
        self.transaction_service = transaction_service
        self.budget_service = budget_service
    
    def calculate_total_income(self, start_date: str, end_date: str) -> float:
        """计算总收入"""
        transactions = self.transaction_service.get_transactions_by_date_range(start_date, end_date)
        income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        return income
    
    def calculate_total_expense(self, start_date: str, end_date: str) -> float:
        """计算总支出"""
        transactions = self.transaction_service.get_transactions_by_date_range(start_date, end_date)
        expense = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        return expense
    
    def calculate_net_balance(self, start_date: str, end_date: str) -> float:
        """计算净结余"""
        income = self.calculate_total_income(start_date, end_date)
        expense = self.calculate_total_expense(start_date, end_date)
        return income - expense
    
    def get_income_category_stats(self, start_date: str, end_date: str) -> Dict[str, float]:
        """获取收入分类统计"""
        transactions = self.transaction_service.get_transactions_by_date_range(start_date, end_date)
        income_transactions = [t for t in transactions if t.type == TransactionType.INCOME]
        
        category_stats = {}
        for transaction in income_transactions:
            category = transaction.category
            if category in category_stats:
                category_stats[category] += transaction.amount
            else:
                category_stats[category] = transaction.amount
        
        return category_stats
    
    def get_expense_category_stats(self, start_date: str, end_date: str) -> Dict[str, float]:
        """获取支出分类统计"""
        transactions = self.transaction_service.get_transactions_by_date_range(start_date, end_date)
        expense_transactions = [t for t in transactions if t.type == TransactionType.EXPENSE]
        
        category_stats = {}
        for transaction in expense_transactions:
            category = transaction.category
            if category in category_stats:
                category_stats[category] += transaction.amount
            else:
                category_stats[category] = transaction.amount
        
        return category_stats
    
    def get_transaction_count_by_type(self, start_date: str, end_date: str) -> Dict[str, int]:
        """获取交易数量统计"""
        transactions = self.transaction_service.get_transactions_by_date_range(start_date, end_date)
        income_count = len([t for t in transactions if t.type == TransactionType.INCOME])
        expense_count = len([t for t in transactions if t.type == TransactionType.EXPENSE])
        
        return {
            TransactionType.INCOME: income_count,
            TransactionType.EXPENSE: expense_count,
            "总计": len(transactions)
        }
    
    def get_budget_analysis(self, month: str) -> Dict[str, Dict]:
        """获取预算分析"""
        if not self.budget_service:
            return {}
        
        budgets = self.budget_service.get_budgets_by_month(month)
        transactions = self.transaction_service.get_transactions_by_month(month)
        
        analysis = {}
        for budget in budgets:
            # 计算该类别的实际支出
            actual_expense = sum(
                t.amount for t in transactions 
                if t.type == TransactionType.EXPENSE and t.category == budget.category
            )
            
            # 计算预算使用率
            usage_rate = (actual_expense / budget.amount * 100) if budget.amount > 0 else 0
            is_over_budget = actual_expense > budget.amount
            
            analysis[budget.category] = {
                'budget_amount': budget.amount,
                'actual_expense': actual_expense,
                'remaining': budget.amount - actual_expense,
                'usage_rate': usage_rate,
                'is_over_budget': is_over_budget
            }
        
        return analysis


class DataExportService:
    """数据导出服务类"""
    
    def __init__(self, transaction_service: TransactionService, statistics_service: StatisticsService):
        self.transaction_service = transaction_service
        self.statistics_service = statistics_service
    
    def export_comprehensive_report(self, filename: str, start_date: str, end_date: str) -> bool:
        """导出综合报告（包含交易数据和统计）"""
        try:
            # 获取交易数据
            transactions = self.transaction_service.get_transactions_by_date_range(start_date, end_date)
            
            # 获取统计信息
            total_income = self.statistics_service.calculate_total_income(start_date, end_date)
            total_expense = self.statistics_service.calculate_total_expense(start_date, end_date)
            net_balance = total_income - total_expense
            income_stats = self.statistics_service.get_income_category_stats(start_date, end_date)
            expense_stats = self.statistics_service.get_expense_category_stats(start_date, end_date)
            
            # 创建Excel文件
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 导出交易明细
                transaction_data = []
                for t in transactions:
                    transaction_data.append({
                        '日期': t.date,
                        '类型': t.type,
                        '分类': t.category,
                        '金额': t.amount,
                        '备注': t.note
                    })
                
                if transaction_data:
                    df_transactions = pd.DataFrame(transaction_data)
                    df_transactions.to_excel(writer, sheet_name='交易明细', index=False)
                
                # 导出统计摘要
                summary_data = {
                    '项目': ['总收入', '总支出', '净结余'],
                    '金额': [total_income, total_expense, net_balance]
                }
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='统计摘要', index=False)
                
                # 导出收入分类统计
                if income_stats:
                    income_data = [{'分类': k, '金额': v} for k, v in income_stats.items()]
                    df_income = pd.DataFrame(income_data)
                    df_income.to_excel(writer, sheet_name='收入分类统计', index=False)
                
                # 导出支出分类统计
                if expense_stats:
                    expense_data = [{'分类': k, '金额': v} for k, v in expense_stats.items()]
                    df_expense = pd.DataFrame(expense_data)
                    df_expense.to_excel(writer, sheet_name='支出分类统计', index=False)
            
            return True
        except Exception as e:
            print(f"导出综合报告失败: {e}")
            return False


class BaseScreen(tk.Frame):
    """基础界面类"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.parent = parent


class MainScreen(BaseScreen):
    """主界面"""
    
    def __init__(self, parent, app, transaction_service: TransactionService, 
                 category_service: CategoryService, statistics_service: StatisticsService):
        super().__init__(parent, app)
        self.transaction_service = transaction_service
        self.category_service = category_service
        self.statistics_service = statistics_service
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """设置UI界面"""
        # 标题和日期框架
        title_frame = tk.Frame(self)
        title_frame.pack(fill="x", padx=10, pady=10)
        
        # 标题
        title_label = tk.Label(title_frame, text="个人记账本", font=("Arial", 16, "bold"))
        title_label.pack(side="left")
        
        # 当日日期显示（右上角）
        current_date = datetime.now().strftime("%Y年%m月%d日 %A")
        self.date_var = tk.StringVar(value=current_date)
        date_label = tk.Label(title_frame, textvariable=self.date_var, font=("Arial", 12), fg="gray")
        date_label.pack(side="right")
        
        # 本月摘要框架
        summary_frame = tk.LabelFrame(self, text="本月财务摘要", font=("Arial", 12, "bold"))
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        # 收入、支出、结余显示
        self.income_var = tk.StringVar(value="收入: 0.00")
        self.expense_var = tk.StringVar(value="支出: 0.00")
        self.balance_var = tk.StringVar(value="结余: 0.00")
        
        income_label = tk.Label(summary_frame, textvariable=self.income_var, 
                               font=("Arial", 12), fg="green")
        income_label.pack(anchor="w", padx=5, pady=2)
        
        expense_label = tk.Label(summary_frame, textvariable=self.expense_var, 
                                font=("Arial", 12), fg="red")
        expense_label.pack(anchor="w", padx=5, pady=2)
        
        balance_label = tk.Label(summary_frame, textvariable=self.balance_var, 
                                font=("Arial", 12, "bold"))
        balance_label.pack(anchor="w", padx=5, pady=2)
        
        # 最近交易框架
        recent_frame = tk.LabelFrame(self, text="最近交易记录", font=("Arial", 12, "bold"))
        recent_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 交易列表
        columns = ("ID", "日期", "类型", "分类", "金额", "备注")
        self.tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=10)
        
        # 设置列宽
        self.tree.column("ID", width=0, stretch=False)  # 隐藏ID列
        self.tree.column("日期", width=100)
        self.tree.column("类型", width=80)
        self.tree.column("分类", width=100)
        self.tree.column("金额", width=100)
        self.tree.column("备注", width=200)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        # 隐藏ID列
        self.tree["displaycolumns"] = ("日期", "类型", "分类", "金额", "备注")
        
        # 滚动条
        scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 操作按钮框架
        operation_frame = tk.Frame(recent_frame)
        operation_frame.pack(side="bottom", fill="x", pady=5)
        
        edit_btn = tk.Button(operation_frame, text="修改选中记录", 
                           command=self.edit_selected_transaction,
                           bg="#2196F3", fg="white", font=("Arial", 10))
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = tk.Button(operation_frame, text="删除选中记录", 
                             command=self.delete_selected_transaction,
                             bg="#F44336", fg="white", font=("Arial", 10))
        delete_btn.pack(side="left", padx=5)
        
        # 按钮框架
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # 功能按钮
        add_btn = tk.Button(button_frame, text="记 账", command=self.navigate_to_add_transaction,
                           bg="#4CAF50", fg="white", font=("Arial", 12), width=10)
        add_btn.pack(side="left", padx=5)
        
        stats_btn = tk.Button(button_frame, text="统 计", command=self.navigate_to_statistics,
                             bg="#2196F3", fg="white", font=("Arial", 12), width=10)
        stats_btn.pack(side="left", padx=5)
        
        search_btn = tk.Button(button_frame, text="查 询", command=self.navigate_to_search,
                              bg="#FF9800", fg="white", font=("Arial", 12), width=10)
        search_btn.pack(side="left", padx=5)
        
        budget_btn = tk.Button(button_frame, text="预 算", command=self.navigate_to_budget,
                              bg="#9C27B0", fg="white", font=("Arial", 12), width=10)
        budget_btn.pack(side="left", padx=5)
        
        export_btn = tk.Button(button_frame, text="导 出", command=self.navigate_to_export,
                              bg="#607D8B", fg="white", font=("Arial", 12), width=10)
        export_btn.pack(side="left", padx=5)
    
    def refresh_data(self):
        """刷新数据"""
        # 更新日期显示
        current_date = datetime.now().strftime("%Y年%m月%d日 %A")
        self.date_var.set(current_date)
        
        # 获取当前月份（用于摘要统计）
        now = datetime.now()
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        
        # 计算统计数据（仍然使用当前月份）
        income = self.statistics_service.calculate_total_income(start_date, end_date)
        expense = self.statistics_service.calculate_total_expense(start_date, end_date)
        balance = income - expense
        
        # 更新显示
        self.income_var.set(f"收入: {income:.2f}")
        self.expense_var.set(f"支出: {expense:.2f}")
        self.balance_var.set(f"结余: {balance:.2f}")
        
        # 更新交易列表 - 改为显示所有交易记录，按日期倒序
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取所有交易记录
        all_transactions = self.transaction_service.get_all_transactions()
        
        # 按日期倒序排列，显示最近交易
        all_transactions.sort(key=lambda x: x.date, reverse=True)
        
        for transaction in all_transactions[:15]:  # 显示最近15条记录
            amount_text = f"{transaction.amount:.2f}"
            self.tree.insert("", "end", values=(
                transaction.transaction_id,  # 存储ID但不显示
                transaction.date,
                transaction.type,
                transaction.category,
                amount_text,
                transaction.note
            ))
    
    def get_selected_transaction_id(self):
        """获取选中记录的ID"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            return values[0]  # 第一个值是ID
        return None
    
    def edit_selected_transaction(self):
        """编辑选中记录"""
        transaction_id = self.get_selected_transaction_id()
        if transaction_id:
            self.app.show_edit_transaction_screen(transaction_id)
        else:
            messagebox.showwarning("警告", "请先选择要修改的记录")
    
    def delete_selected_transaction(self):
        """删除选中记录"""
        transaction_id = self.get_selected_transaction_id()
        if transaction_id:
            if messagebox.askyesno("确认删除", "确定要删除这条记录吗？此操作不可撤销！"):
                if self.transaction_service.delete_transaction(transaction_id):
                    messagebox.showinfo("成功", "记录已删除")
                    self.refresh_data()
                else:
                    messagebox.showerror("错误", "删除记录失败")
        else:
            messagebox.showwarning("警告", "请先选择要删除的记录")
    
    def navigate_to_add_transaction(self):
        """跳转到记账界面"""
        self.app.show_add_transaction_screen()
    
    def navigate_to_statistics(self):
        """跳转到统计界面"""
        self.app.show_statistics_screen()
    
    def navigate_to_search(self):
        """跳转到查询界面"""
        self.app.show_search_screen()
    
    def navigate_to_budget(self):
        """跳转到预算界面"""
        self.app.show_budget_screen()
    
    def navigate_to_export(self):
        """跳转到导出界面"""
        self.app.show_export_screen()


class AddTransactionScreen(BaseScreen):
    """记账界面"""
    
    def __init__(self, parent, app, transaction_service: TransactionService, 
                 category_service: CategoryService):
        super().__init__(parent, app)
        self.transaction_service = transaction_service
        self.category_service = category_service
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        # 标题
        title_label = tk.Label(self, text="记录交易", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 表单框架
        form_frame = tk.Frame(self)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # 交易类型
        tk.Label(form_frame, text="交易类型:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value=TransactionType.EXPENSE)
        type_frame = tk.Frame(form_frame)
        type_frame.grid(row=0, column=1, sticky="w", pady=5)
        
        expense_radio = tk.Radiobutton(type_frame, text="支出", variable=self.type_var,
                                      value=TransactionType.EXPENSE, command=self.on_type_change)
        expense_radio.pack(side="left")
        
        income_radio = tk.Radiobutton(type_frame, text="收入", variable=self.type_var,
                                     value=TransactionType.INCOME, command=self.on_type_change)
        income_radio.pack(side="left")
        
        # 分类
        tk.Label(form_frame, text="分类:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, state="readonly", width=20)
        self.category_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # 自定义分类
        self.custom_category_var = tk.StringVar()
        custom_frame = tk.Frame(form_frame)
        custom_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        tk.Label(custom_frame, text="自定义分类:", font=("Arial", 10)).pack(side="left")
        custom_entry = tk.Entry(custom_frame, textvariable=self.custom_category_var, width=15)
        custom_entry.pack(side="left", padx=5)
        add_custom_btn = tk.Button(custom_frame, text="添加", command=self.add_custom_category)
        add_custom_btn.pack(side="left")
        
        # 金额
        tk.Label(form_frame, text="金额:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
        self.amount_var = tk.StringVar()
        amount_entry = tk.Entry(form_frame, textvariable=self.amount_var, font=("Arial", 12), width=20)
        amount_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # 日期
        tk.Label(form_frame, text="日期:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(form_frame, textvariable=self.date_var, font=("Arial", 12), width=20)
        date_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # 备注
        tk.Label(form_frame, text="备注:", font=("Arial", 12)).grid(row=5, column=0, sticky="nw", pady=5)
        self.note_text = tk.Text(form_frame, width=30, height=4)
        self.note_text.grid(row=5, column=1, sticky="w", pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="保存", command=self.save_transaction,
                           bg="#4CAF50", fg="white", font=("Arial", 12), width=10)
        save_btn.pack(side="left", padx=10)
        
        reset_btn = tk.Button(button_frame, text="重置", command=self.reset_form,
                             bg="#9E9E9E", fg="white", font=("Arial", 12), width=10)
        reset_btn.pack(side="left", padx=10)
        
        back_btn = tk.Button(button_frame, text="返回", command=self.go_back,
                            bg="#607D8B", fg="white", font=("Arial", 12), width=10)
        back_btn.pack(side="left", padx=10)
        
        # 初始化分类列表
        self.on_type_change()
    
    def on_type_change(self):
        """交易类型改变时的回调"""
        transaction_type = self.type_var.get()
        categories = self.category_service.get_categories_by_type(transaction_type)
        self.category_combo['values'] = categories
        if categories:
            self.category_combo.set(categories[0])
    
    def add_custom_category(self):
        """添加自定义分类"""
        custom_category = self.custom_category_var.get().strip()
        if not custom_category:
            messagebox.showwarning("警告", "请输入分类名称")
            return
        
        transaction_type = self.type_var.get()
        if self.category_service.add_user_category(transaction_type, custom_category):
            self.on_type_change()  # 刷新分类列表
            self.category_combo.set(custom_category)
            self.custom_category_var.set("")
            messagebox.showinfo("成功", f"已添加分类: {custom_category}")
        else:
            messagebox.showwarning("警告", "分类已存在或添加失败")
    
    def validate_input(self) -> bool:
        """验证输入数据"""
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showwarning("警告", "金额必须大于0")
                return False
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的金额")
            return False
        
        if not self.category_var.get():
            messagebox.showwarning("警告", "请选择分类")
            return False
        
        try:
            datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的日期 (YYYY-MM-DD)")
            return False
        
        return True
    
    def save_transaction(self):
        """保存交易"""
        if not self.validate_input():
            return
        
        amount = float(self.amount_var.get())
        transaction_type = self.type_var.get()
        category = self.category_var.get()
        date = self.date_var.get()
        note = self.note_text.get("1.0", "end-1c").strip()
        
        if self.transaction_service.create_transaction(amount, transaction_type, category, date, note):
            messagebox.showinfo("成功", "交易记录已保存")
            self.reset_form()
            self.app.show_main_screen()
        else:
            messagebox.showerror("错误", "保存交易失败")
    
    def reset_form(self):
        """重置表单"""
        self.amount_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.note_text.delete("1.0", "end")
        self.on_type_change()
    
    def go_back(self):
        """返回主界面"""
        self.app.show_main_screen()


class EditTransactionScreen(BaseScreen):
    """编辑交易界面"""
    
    def __init__(self, parent, app, transaction_service: TransactionService, 
                 category_service: CategoryService, transaction_id: str):
        super().__init__(parent, app)
        self.transaction_service = transaction_service
        self.category_service = category_service
        self.transaction_id = transaction_id
        self.transaction = self.transaction_service.get_transaction_by_id(transaction_id)
        
        if not self.transaction:
            messagebox.showerror("错误", "未找到该交易记录")
            self.app.show_main_screen()
            return
        
        self.setup_ui()
        self.load_transaction_data()
    
    def setup_ui(self):
        """设置UI界面"""
        # 标题
        title_label = tk.Label(self, text="编辑交易记录", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 交易ID显示（不可编辑）
        id_frame = tk.Frame(self)
        id_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(id_frame, text=f"交易ID: {self.transaction_id}", 
                font=("Arial", 10), fg="gray").pack(anchor="w")
        
        # 表单框架
        form_frame = tk.Frame(self)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # 交易类型
        tk.Label(form_frame, text="交易类型:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar()
        type_frame = tk.Frame(form_frame)
        type_frame.grid(row=0, column=1, sticky="w", pady=5)
        
        expense_radio = tk.Radiobutton(type_frame, text="支出", variable=self.type_var,
                                      value=TransactionType.EXPENSE, command=self.on_type_change)
        expense_radio.pack(side="left")
        
        income_radio = tk.Radiobutton(type_frame, text="收入", variable=self.type_var,
                                     value=TransactionType.INCOME, command=self.on_type_change)
        income_radio.pack(side="left")
        
        # 分类
        tk.Label(form_frame, text="分类:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, state="readonly", width=20)
        self.category_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # 自定义分类
        self.custom_category_var = tk.StringVar()
        custom_frame = tk.Frame(form_frame)
        custom_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        tk.Label(custom_frame, text="自定义分类:", font=("Arial", 10)).pack(side="left")
        custom_entry = tk.Entry(custom_frame, textvariable=self.custom_category_var, width=15)
        custom_entry.pack(side="left", padx=5)
        add_custom_btn = tk.Button(custom_frame, text="添加", command=self.add_custom_category)
        add_custom_btn.pack(side="left")
        
        # 金额
        tk.Label(form_frame, text="金额:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
        self.amount_var = tk.StringVar()
        amount_entry = tk.Entry(form_frame, textvariable=self.amount_var, font=("Arial", 12), width=20)
        amount_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # 日期
        tk.Label(form_frame, text="日期:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=5)
        self.date_var = tk.StringVar()
        date_entry = tk.Entry(form_frame, textvariable=self.date_var, font=("Arial", 12), width=20)
        date_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # 备注
        tk.Label(form_frame, text="备注:", font=("Arial", 12)).grid(row=5, column=0, sticky="nw", pady=5)
        self.note_text = tk.Text(form_frame, width=30, height=4)
        self.note_text.grid(row=5, column=1, sticky="w", pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="保存修改", command=self.update_transaction,
                           bg="#4CAF50", fg="white", font=("Arial", 12), width=10)
        save_btn.pack(side="left", padx=10)
        
        delete_btn = tk.Button(button_frame, text="删除记录", command=self.delete_transaction,
                             bg="#F44336", fg="white", font=("Arial", 12), width=10)
        delete_btn.pack(side="left", padx=10)
        
        back_btn = tk.Button(button_frame, text="返回", command=self.go_back,
                            bg="#607D8B", fg="white", font=("Arial", 12), width=10)
        back_btn.pack(side="left", padx=10)
    
    def load_transaction_data(self):
        """加载交易数据到表单"""
        self.type_var.set(self.transaction.type)
        self.amount_var.set(str(self.transaction.amount))
        self.date_var.set(self.transaction.date)
        self.note_text.delete("1.0", "end")
        self.note_text.insert("1.0", self.transaction.note)
        
        # 初始化分类列表并设置当前分类
        self.on_type_change()
        self.category_var.set(self.transaction.category)
    
    def on_type_change(self):
        """交易类型改变时的回调"""
        transaction_type = self.type_var.get()
        categories = self.category_service.get_categories_by_type(transaction_type)
        self.category_combo['values'] = categories
        if categories and not self.category_var.get():
            self.category_combo.set(categories[0])
    
    def add_custom_category(self):
        """添加自定义分类"""
        custom_category = self.custom_category_var.get().strip()
        if not custom_category:
            messagebox.showwarning("警告", "请输入分类名称")
            return
        
        transaction_type = self.type_var.get()
        if self.category_service.add_user_category(transaction_type, custom_category):
            self.on_type_change()  # 刷新分类列表
            self.category_combo.set(custom_category)
            self.custom_category_var.set("")
            messagebox.showinfo("成功", f"已添加分类: {custom_category}")
        else:
            messagebox.showwarning("警告", "分类已存在或添加失败")
    
    def validate_input(self) -> bool:
        """验证输入数据"""
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showwarning("警告", "金额必须大于0")
                return False
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的金额")
            return False
        
        if not self.category_var.get():
            messagebox.showwarning("警告", "请选择分类")
            return False
        
        try:
            datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的日期 (YYYY-MM-DD)")
            return False
        
        return True
    
    def update_transaction(self):
        """更新交易"""
        if not self.validate_input():
            return
        
        amount = float(self.amount_var.get())
        transaction_type = self.type_var.get()
        category = self.category_var.get()
        date = self.date_var.get()
        note = self.note_text.get("1.0", "end-1c").strip()
        
        if self.transaction_service.update_transaction(
            self.transaction_id, amount, transaction_type, category, date, note
        ):
            messagebox.showinfo("成功", "交易记录已更新")
            self.app.show_main_screen()
        else:
            messagebox.showerror("错误", "更新交易失败")
    
    def delete_transaction(self):
        """删除交易"""
        if messagebox.askyesno("确认删除", "确定要删除这条记录吗？此操作不可撤销！"):
            if self.transaction_service.delete_transaction(self.transaction_id):
                messagebox.showinfo("成功", "记录已删除")
                self.app.show_main_screen()
            else:
                messagebox.showerror("错误", "删除记录失败")
    
    def go_back(self):
        """返回主界面"""
        self.app.show_main_screen()


class StatisticsScreen(BaseScreen):
    """统计界面（完整版，包含收入支出分类统计）"""
    
    def __init__(self, parent, app, transaction_service: TransactionService, 
                 statistics_service: StatisticsService):
        super().__init__(parent, app)
        self.transaction_service = transaction_service
        self.statistics_service = statistics_service
        
        self.setup_ui()
        self.refresh_statistics()
    
    def setup_ui(self):
        """设置UI界面"""
        # 标题
        title_label = tk.Label(self, text="财务统计", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 时间范围选择框架
        time_frame = tk.LabelFrame(self, text="统计时间范围", font=("Arial", 12, "bold"))
        time_frame.pack(fill="x", padx=10, pady=5)
        
        # 时间范围选择
        self.time_range_var = tk.StringVar(value="本月")
        time_options = ["本月", "上月", "今年", "去年", "自定义"]
        
        for option in time_options:
            radio = tk.Radiobutton(time_frame, text=option, variable=self.time_range_var,
                                  value=option, command=self.on_time_range_change)
            radio.pack(side="left", padx=10)
        
        # 自定义日期框架
        custom_frame = tk.Frame(time_frame)
        custom_frame.pack(fill="x", pady=5)
        
        tk.Label(custom_frame, text="开始日期:").pack(side="left")
        self.start_date_var = tk.StringVar(value=datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        start_date_entry = tk.Entry(custom_frame, textvariable=self.start_date_var, width=12)
        start_date_entry.pack(side="left", padx=5)
        
        tk.Label(custom_frame, text="结束日期:").pack(side="left")
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        end_date_entry = tk.Entry(custom_frame, textvariable=self.end_date_var, width=12)
        end_date_entry.pack(side="left", padx=5)
        
        # 统计摘要框架
        summary_frame = tk.LabelFrame(self, text="财务摘要", font=("Arial", 12, "bold"))
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        # 使用网格布局来整齐排列
        self.income_label = tk.Label(summary_frame, text="总收入: 0.00", font=("Arial", 12), fg="green")
        self.income_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.expense_label = tk.Label(summary_frame, text="总支出: 0.00", font=("Arial", 12), fg="red")
        self.expense_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        self.balance_label = tk.Label(summary_frame, text="净结余: 0.00", font=("Arial", 12, "bold"))
        self.balance_label.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        # 交易数量统计
        self.income_count_label = tk.Label(summary_frame, text="收入笔数: 0", font=("Arial", 10))
        self.income_count_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.expense_count_label = tk.Label(summary_frame, text="支出笔数: 0", font=("Arial", 10))
        self.expense_count_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        self.total_count_label = tk.Label(summary_frame, text="总交易数: 0", font=("Arial", 10))
        self.total_count_label.grid(row=1, column=2, sticky="w", padx=5, pady=2)
        
        # 创建左右分栏的框架
        stats_container = tk.Frame(self)
        stats_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 左侧：收入分类统计
        income_frame = tk.LabelFrame(stats_container, text="收入分类统计", font=("Arial", 12, "bold"))
        income_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # 收入分类统计列表
        income_columns = ("分类", "金额", "占比")
        self.income_tree = ttk.Treeview(income_frame, columns=income_columns, show="headings", height=12)
        
        # 设置列宽
        self.income_tree.column("分类", width=120)
        self.income_tree.column("金额", width=100)
        self.income_tree.column("占比", width=80)
        
        for col in income_columns:
            self.income_tree.heading(col, text=col)
        
        # 收入滚动条
        income_scrollbar = ttk.Scrollbar(income_frame, orient="vertical", command=self.income_tree.yview)
        self.income_tree.configure(yscrollcommand=income_scrollbar.set)
        
        self.income_tree.pack(side="left", fill="both", expand=True)
        income_scrollbar.pack(side="right", fill="y")
        
        # 右侧：支出分类统计
        expense_frame = tk.LabelFrame(stats_container, text="支出分类统计", font=("Arial", 12, "bold"))
        expense_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # 支出分类统计列表
        expense_columns = ("分类", "金额", "占比")
        self.expense_tree = ttk.Treeview(expense_frame, columns=expense_columns, show="headings", height=12)
        
        # 设置列宽
        self.expense_tree.column("分类", width=120)
        self.expense_tree.column("金额", width=100)
        self.expense_tree.column("占比", width=80)
        
        for col in expense_columns:
            self.expense_tree.heading(col, text=col)
        
        # 支出滚动条
        expense_scrollbar = ttk.Scrollbar(expense_frame, orient="vertical", command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=expense_scrollbar.set)
        
        self.expense_tree.pack(side="left", fill="both", expand=True)
        expense_scrollbar.pack(side="right", fill="y")
        
        # 按钮框架
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        refresh_btn = tk.Button(button_frame, text="刷新", command=self.refresh_statistics,
                              bg="#2196F3", fg="white", font=("Arial", 12), width=10)
        refresh_btn.pack(side="left", padx=10)
        
        back_btn = tk.Button(button_frame, text="返回", command=self.go_back,
                            bg="#607D8B", fg="white", font=("Arial", 12), width=10)
        back_btn.pack(side="left", padx=10)
    
    def on_time_range_change(self):
        """时间范围改变时的回调"""
        time_range = self.time_range_var.get()
        now = datetime.now()
        
        if time_range == "本月":
            start_date = now.replace(day=1)
            end_date = now
        elif time_range == "上月":
            start_date = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = now.replace(day=1) - timedelta(days=1)
        elif time_range == "今年":
            start_date = now.replace(month=1, day=1)
            end_date = now
        elif time_range == "去年":
            start_date = now.replace(year=now.year-1, month=1, day=1)
            end_date = now.replace(year=now.year-1, month=12, day=31)
        else:  # 自定义
            return  # 使用用户输入的日期
        
        self.start_date_var.set(start_date.strftime("%Y-%m-%d"))
        self.end_date_var.set(end_date.strftime("%Y-%m-%d"))
        self.refresh_statistics()
    
    def refresh_statistics(self):
        """刷新统计数据"""
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        try:
            # 计算统计数据
            income = self.statistics_service.calculate_total_income(start_date, end_date)
            expense = self.statistics_service.calculate_total_expense(start_date, end_date)
            balance = income - expense
            
            # 获取交易数量统计
            count_stats = self.statistics_service.get_transaction_count_by_type(start_date, end_date)
            
            # 更新摘要显示
            self.income_label.config(text=f"总收入: {income:.2f}")
            self.expense_label.config(text=f"总支出: {expense:.2f}")
            self.balance_label.config(text=f"净结余: {balance:.2f}")
            
            # 更新交易数量显示
            self.income_count_label.config(text=f"收入笔数: {count_stats[TransactionType.INCOME]}")
            self.expense_count_label.config(text=f"支出笔数: {count_stats[TransactionType.EXPENSE]}")
            self.total_count_label.config(text=f"总交易数: {count_stats['总计']}")
            
            # 更新分类统计
            self.update_category_stats(start_date, end_date, income, expense)
            
        except Exception as e:
            messagebox.showerror("错误", f"统计计算失败: {e}")
    
    def update_category_stats(self, start_date: str, end_date: str, total_income: float, total_expense: float):
        """更新分类统计"""
        # 清空分类统计列表
        for item in self.income_tree.get_children():
            self.income_tree.delete(item)
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # 获取收入分类统计
        income_stats = self.statistics_service.get_income_category_stats(start_date, end_date)
        if not income_stats:
            self.income_tree.insert("", "end", values=("暂无收入数据", "", ""))
        else:
            # 按金额排序
            sorted_income = sorted(income_stats.items(), key=lambda x: x[1], reverse=True)
            for category, amount in sorted_income:
                if total_income > 0:
                    percentage = (amount / total_income) * 100
                    percentage_text = f"{percentage:.1f}%"
                else:
                    percentage_text = "0.0%"
                
                self.income_tree.insert("", "end", values=(
                    category,
                    f"{amount:.2f}",
                    percentage_text
                ))
        
        # 获取支出分类统计
        expense_stats = self.statistics_service.get_expense_category_stats(start_date, end_date)
        if not expense_stats:
            self.expense_tree.insert("", "end", values=("暂无支出数据", "", ""))
        else:
            # 按金额排序
            sorted_expense = sorted(expense_stats.items(), key=lambda x: x[1], reverse=True)
            for category, amount in sorted_expense:
                if total_expense > 0:
                    percentage = (amount / total_expense) * 100
                    percentage_text = f"{percentage:.1f}%"
                else:
                    percentage_text = "0.0%"
                
                self.expense_tree.insert("", "end", values=(
                    category,
                    f"{amount:.2f}",
                    percentage_text
                ))
    
    def go_back(self):
        """返回主界面"""
        self.app.show_main_screen()


class SearchScreen(BaseScreen):
    """查询界面"""
    
    def __init__(self, parent, app, transaction_service: TransactionService, 
                 category_service: CategoryService):
        super().__init__(parent, app)
        self.transaction_service = transaction_service
        self.category_service = category_service
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        # 标题
        title_label = tk.Label(self, text="交易查询", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 查询条件框架
        condition_frame = tk.LabelFrame(self, text="查询条件", font=("Arial", 12, "bold"))
        condition_frame.pack(fill="x", padx=10, pady=5)
        
        # 关键词搜索
        tk.Label(condition_frame, text="关键词:").grid(row=0, column=0, sticky="w", pady=5)
        self.keyword_var = tk.StringVar()
        keyword_entry = tk.Entry(condition_frame, textvariable=self.keyword_var, width=20)
        keyword_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # 交易类型
        tk.Label(condition_frame, text="交易类型:").grid(row=1, column=0, sticky="w", pady=5)
        self.search_type_var = tk.StringVar(value="")
        type_combo = ttk.Combobox(condition_frame, textvariable=self.search_type_var, 
                                 values=["", TransactionType.INCOME, TransactionType.EXPENSE],
                                 state="readonly", width=15)
        type_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # 分类
        tk.Label(condition_frame, text="分类:").grid(row=2, column=0, sticky="w", pady=5)
        self.search_category_var = tk.StringVar()
        self.search_category_combo = ttk.Combobox(condition_frame, textvariable=self.search_category_var,
                                                 state="readonly", width=15)
        self.search_category_combo.grid(row=2, column=1, sticky="w", pady=5)
        
        # 日期范围
        tk.Label(condition_frame, text="开始日期:").grid(row=3, column=0, sticky="w", pady=5)
        self.search_start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(condition_frame, textvariable=self.search_start_date_var, width=12)
        start_date_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        tk.Label(condition_frame, text="结束日期:").grid(row=4, column=0, sticky="w", pady=5)
        self.search_end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(condition_frame, textvariable=self.search_end_date_var, width=12)
        end_date_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # 金额范围
        tk.Label(condition_frame, text="金额范围:").grid(row=5, column=0, sticky="w", pady=5)
        amount_frame = tk.Frame(condition_frame)
        amount_frame.grid(row=5, column=1, sticky="w", pady=5)
        
        tk.Label(amount_frame, text="从").pack(side="left")
        self.min_amount_var = tk.StringVar()
        min_amount_entry = tk.Entry(amount_frame, textvariable=self.min_amount_var, width=8)
        min_amount_entry.pack(side="left", padx=2)
        
        tk.Label(amount_frame, text="到").pack(side="left")
        self.max_amount_var = tk.StringVar()
        max_amount_entry = tk.Entry(amount_frame, textvariable=self.max_amount_var, width=8)
        max_amount_entry.pack(side="left", padx=2)
        
        # 按钮框架
        button_frame = tk.Frame(condition_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        search_btn = tk.Button(button_frame, text="搜索", command=self.search_transactions,
                              bg="#FF9800", fg="white", font=("Arial", 12), width=10)
        search_btn.pack(side="left", padx=5)
        
        clear_btn = tk.Button(button_frame, text="清空条件", command=self.clear_filters,
                             bg="#9E9E9E", fg="white", font=("Arial", 12), width=10)
        clear_btn.pack(side="left", padx=5)
        
        # 结果框架
        result_frame = tk.LabelFrame(self, text="查询结果", font=("Arial", 12, "bold"))
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 结果列表
        columns = ("日期", "类型", "分类", "金额", "备注")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        
        # 设置列宽
        self.result_tree.column("日期", width=100)
        self.result_tree.column("类型", width=80)
        self.result_tree.column("分类", width=100)
        self.result_tree.column("金额", width=100)
        self.result_tree.column("备注", width=200)
        
        for col in columns:
            self.result_tree.heading(col, text=col)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 返回按钮
        back_btn = tk.Button(self, text="返回", command=self.go_back,
                            bg="#607D8B", fg="white", font=("Arial", 12), width=10)
        back_btn.pack(pady=10)
        
        # 初始化分类列表
        self.update_category_combo()
    
    def update_category_combo(self):
        """更新分类组合框"""
        all_categories = (self.category_service.get_categories_by_type(TransactionType.INCOME) + 
                         self.category_service.get_categories_by_type(TransactionType.EXPENSE))
        self.search_category_combo['values'] = [""] + all_categories
        self.search_category_combo.set("")
    
    def search_transactions(self):
        """搜索交易"""
        keyword = self.keyword_var.get().strip()
        transaction_type = self.search_type_var.get()
        category = self.search_category_var.get()
        start_date = self.search_start_date_var.get().strip()
        end_date = self.search_end_date_var.get().strip()
        min_amount_str = self.min_amount_var.get().strip()
        max_amount_str = self.max_amount_var.get().strip()
        
        # 解析金额范围
        min_amount = None
        max_amount = None
        
        try:
            if min_amount_str:
                min_amount = float(min_amount_str)
            if max_amount_str:
                max_amount = float(max_amount_str)
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的金额")
            return
        
        # 验证金额范围
        if min_amount is not None and min_amount < 0:
            messagebox.showwarning("警告", "金额不能为负数")
            return
        
        if max_amount is not None and max_amount < 0:
            messagebox.showwarning("警告", "金额不能为负数")
            return
        
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            messagebox.showwarning("警告", "最小金额不能大于最大金额")
            return
        
        # 如果选择了类型但未选择分类，更新分类列表
        if transaction_type and not category:
            categories = self.category_service.get_categories_by_type(transaction_type)
            self.search_category_combo['values'] = [""] + categories
        
        results = self.transaction_service.search_transactions(
            keyword=keyword if keyword else "",
            transaction_type=transaction_type if transaction_type else "",
            category=category if category else "",
            start_date=start_date if start_date else "",
            end_date=end_date if end_date else "",
            min_amount=min_amount,
            max_amount=max_amount
        )
        
        # 清空结果列表
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 显示结果
        for transaction in results:
            amount_text = f"{transaction.amount:.2f}"
            self.result_tree.insert("", "end", values=(
                transaction.date,
                transaction.type,
                transaction.category,
                amount_text,
                transaction.note
            ))
    
    def clear_filters(self):
        """清空筛选条件"""
        self.keyword_var.set("")
        self.search_type_var.set("")
        self.search_category_var.set("")
        self.search_start_date_var.set("")
        self.search_end_date_var.set("")
        self.min_amount_var.set("")
        self.max_amount_var.set("")
        self.update_category_combo()
        
        # 清空结果列表
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
    
    def go_back(self):
        """返回主界面"""
        self.app.show_main_screen()


class BudgetScreen(BaseScreen):
    """预算管理界面"""
    
    def __init__(self, parent, app, budget_service: BudgetService, 
                 category_service: CategoryService, statistics_service: StatisticsService):
        super().__init__(parent, app)
        self.budget_service = budget_service
        self.category_service = category_service
        self.statistics_service = statistics_service
        
        self.setup_ui()
        self.refresh_budgets()
    
    def setup_ui(self):
        """设置UI界面"""
        # 标题
        title_label = tk.Label(self, text="预算管理", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 预算设置框架
        budget_setting_frame = tk.LabelFrame(self, text="设置预算", font=("Arial", 12, "bold"))
        budget_setting_frame.pack(fill="x", padx=10, pady=5)
        
        # 月份选择
        tk.Label(budget_setting_frame, text="月份:").grid(row=0, column=0, sticky="w", pady=5)
        self.budget_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        month_entry = tk.Entry(budget_setting_frame, textvariable=self.budget_month_var, width=12)
        month_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # 分类选择
        tk.Label(budget_setting_frame, text="分类:").grid(row=1, column=0, sticky="w", pady=5)
        self.budget_category_var = tk.StringVar()
        self.budget_category_combo = ttk.Combobox(budget_setting_frame, textvariable=self.budget_category_var,
                                                 state="readonly", width=15)
        self.budget_category_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # 预算金额
        tk.Label(budget_setting_frame, text="预算金额:").grid(row=2, column=0, sticky="w", pady=5)
        self.budget_amount_var = tk.StringVar()
        amount_entry = tk.Entry(budget_setting_frame, textvariable=self.budget_amount_var, width=15)
        amount_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # 备注
        tk.Label(budget_setting_frame, text="备注:").grid(row=3, column=0, sticky="w", pady=5)
        self.budget_note_var = tk.StringVar()
        note_entry = tk.Entry(budget_setting_frame, textvariable=self.budget_note_var, width=20)
        note_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(budget_setting_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        add_budget_btn = tk.Button(button_frame, text="添加预算", command=self.add_budget,
                                  bg="#4CAF50", fg="white", font=("Arial", 10))
        add_budget_btn.pack(side="left", padx=5)
        
        update_budget_btn = tk.Button(button_frame, text="更新预算", command=self.update_budget,
                                    bg="#2196F3", fg="white", font=("Arial", 10))
        update_budget_btn.pack(side="left", padx=5)
        
        delete_budget_btn = tk.Button(button_frame, text="删除预算", command=self.delete_budget,
                                    bg="#F44336", fg="white", font=("Arial", 10))
        delete_budget_btn.pack(side="left", padx=5)
        
        # 预算列表框架
        budget_list_frame = tk.LabelFrame(self, text="预算列表", font=("Arial", 12, "bold"))
        budget_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 预算列表
        columns = ("ID", "月份", "分类", "预算金额", "实际支出", "剩余", "使用率", "备注")
        self.budget_tree = ttk.Treeview(budget_list_frame, columns=columns, show="headings", height=12)
        
        # 设置列宽
        self.budget_tree.column("ID", width=0, stretch=False)  # 隐藏ID列
        self.budget_tree.column("月份", width=80)
        self.budget_tree.column("分类", width=100)
        self.budget_tree.column("预算金额", width=90)
        self.budget_tree.column("实际支出", width=90)
        self.budget_tree.column("剩余", width=90)
        self.budget_tree.column("使用率", width=80)
        self.budget_tree.column("备注", width=150)
        
        for col in columns:
            self.budget_tree.heading(col, text=col)
        
        # 隐藏ID列
        self.budget_tree["displaycolumns"] = ("月份", "分类", "预算金额", "实际支出", "剩余", "使用率", "备注")
        
        # 滚动条
        scrollbar = ttk.Scrollbar(budget_list_frame, orient="vertical", command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=scrollbar.set)
        
        self.budget_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 预算分析框架
        analysis_frame = tk.LabelFrame(self, text="预算分析", font=("Arial", 12, "bold"))
        analysis_frame.pack(fill="x", padx=10, pady=5)
        
        self.analysis_text = tk.Text(analysis_frame, height=4, width=80)
        self.analysis_text.pack(fill="x", padx=5, pady=5)
        
        # 底部按钮框架
        bottom_button_frame = tk.Frame(self)
        bottom_button_frame.pack(pady=10)
        
        refresh_btn = tk.Button(bottom_button_frame, text="刷新", command=self.refresh_budgets,
                              bg="#2196F3", fg="white", font=("Arial", 12), width=10)
        refresh_btn.pack(side="left", padx=10)
        
        back_btn = tk.Button(bottom_button_frame, text="返回", command=self.go_back,
                            bg="#607D8B", fg="white", font=("Arial", 12), width=10)
        back_btn.pack(side="left", padx=10)
        
        # 初始化分类列表
        self.update_budget_category_combo()
    
    def update_budget_category_combo(self):
        """更新预算分类组合框"""
        expense_categories = self.category_service.get_categories_by_type(TransactionType.EXPENSE)
        self.budget_category_combo['values'] = expense_categories
        if expense_categories:
            self.budget_category_combo.set(expense_categories[0])
    
    def get_selected_budget_id(self):
        """获取选中预算的ID"""
        selection = self.budget_tree.selection()
        if selection:
            item = selection[0]
            values = self.budget_tree.item(item, 'values')
            return values[0]  # 第一个值是ID
        return None
    
    def add_budget(self):
        """添加预算"""
        try:
            category = self.budget_category_var.get()
            amount = float(self.budget_amount_var.get())
            month = self.budget_month_var.get()
            note = self.budget_note_var.get()
            
            if amount <= 0:
                messagebox.showwarning("警告", "预算金额必须大于0")
                return
            
            if self.budget_service.create_budget(category, amount, month, note):
                messagebox.showinfo("成功", "预算已添加")
                self.refresh_budgets()
                self.clear_budget_form()
            else:
                messagebox.showwarning("警告", "该类别在该月份已存在预算")
                
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的金额")
    
    def update_budget(self):
        """更新预算"""
        budget_id = self.get_selected_budget_id()
        if not budget_id:
            messagebox.showwarning("警告", "请先选择要更新的预算")
            return
        
        try:
            amount = float(self.budget_amount_var.get())
            month = self.budget_month_var.get()
            note = self.budget_note_var.get()
            
            if amount <= 0:
                messagebox.showwarning("警告", "预算金额必须大于0")
                return
            
            if self.budget_service.update_budget(budget_id, amount, month, note):
                messagebox.showinfo("成功", "预算已更新")
                self.refresh_budgets()
            else:
                messagebox.showerror("错误", "更新预算失败")
                
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的金额")
    
    def delete_budget(self):
        """删除预算"""
        budget_id = self.get_selected_budget_id()
        if budget_id:
            if messagebox.askyesno("确认删除", "确定要删除这个预算吗？"):
                if self.budget_service.delete_budget(budget_id):
                    messagebox.showinfo("成功", "预算已删除")
                    self.refresh_budgets()
                else:
                    messagebox.showerror("错误", "删除预算失败")
        else:
            messagebox.showwarning("警告", "请先选择要删除的预算")
    
    def refresh_budgets(self):
        """刷新预算列表"""
        # 清空预算列表
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        # 获取所有预算
        all_budgets = self.budget_service.get_all_budgets()
        
        # 按月份倒序排列
        all_budgets.sort(key=lambda x: x.month, reverse=True)
        
        # 更新预算列表
        for budget in all_budgets:
            # 获取实际支出和预算分析
            budget_analysis = self.statistics_service.get_budget_analysis(budget.month)
            analysis_data = budget_analysis.get(budget.category, {})
            
            actual_expense = analysis_data.get('actual_expense', 0)
            remaining = analysis_data.get('remaining', budget.amount)
            usage_rate = analysis_data.get('usage_rate', 0)
            
            # 设置使用率颜色
            usage_text = f"{usage_rate:.1f}%"
            if usage_rate > 100:
                usage_text = f"{usage_rate:.1f}% ⚠️"
            elif usage_rate > 80:
                usage_text = f"{usage_rate:.1f}% ⚠️"
            
            self.budget_tree.insert("", "end", values=(
                budget.budget_id,
                budget.month,
                budget.category,
                f"{budget.amount:.2f}",
                f"{actual_expense:.2f}",
                f"{remaining:.2f}",
                usage_text,
                budget.note
            ))
        
        # 更新预算分析文本
        self.update_budget_analysis()
    
    def update_budget_analysis(self):
        """更新预算分析"""
        current_month = datetime.now().strftime("%Y-%m")
        budget_analysis = self.statistics_service.get_budget_analysis(current_month)
        
        self.analysis_text.delete("1.0", "end")
        
        if not budget_analysis:
            self.analysis_text.insert("1.0", f"{current_month} 月份暂无预算数据")
            return
        
        total_budget = sum(data['budget_amount'] for data in budget_analysis.values())
        total_expense = sum(data['actual_expense'] for data in budget_analysis.values())
        overall_usage_rate = (total_expense / total_budget * 100) if total_budget > 0 else 0
        
        analysis_text = f"{current_month} 月份预算分析:\n\n"
        analysis_text += f"总预算: {total_budget:.2f}\n"
        analysis_text += f"总支出: {total_expense:.2f}\n"
        analysis_text += f"总体使用率: {overall_usage_rate:.1f}%\n\n"
        
        # 找出超预算的类别
        over_budget_categories = [
            category for category, data in budget_analysis.items() 
            if data['is_over_budget']
        ]
        
        if over_budget_categories:
            analysis_text += "⚠️ 超预算类别:\n"
            for category in over_budget_categories:
                analysis_text += f"  • {category}\n"
        
        self.analysis_text.insert("1.0", analysis_text)
    
    def clear_budget_form(self):
        """清空预算表单"""
        self.budget_amount_var.set("")
        self.budget_note_var.set("")
    
    def go_back(self):
        """返回主界面"""
        self.app.show_main_screen()


class ExportScreen(BaseScreen):
    """数据导出界面"""
    
    def __init__(self, parent, app, transaction_service: TransactionService,
                 export_service: DataExportService):
        super().__init__(parent, app)
        self.transaction_service = transaction_service
        self.export_service = export_service
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        # 标题
        title_label = tk.Label(self, text="数据导出", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 导出选项框架
        option_frame = tk.LabelFrame(self, text="导出选项", font=("Arial", 12, "bold"))
        option_frame.pack(fill="x", padx=10, pady=5)
        
        # 导出格式选择
        tk.Label(option_frame, text="导出格式:").grid(row=0, column=0, sticky="w", pady=5)
        self.export_format_var = tk.StringVar(value="CSV")
        format_frame = tk.Frame(option_frame)
        format_frame.grid(row=0, column=1, sticky="w", pady=5)
        
        csv_radio = tk.Radiobutton(format_frame, text="CSV", variable=self.export_format_var, value="CSV")
        csv_radio.pack(side="left")
        
        # excel_radio = tk.Radiobutton(format_frame, text="Excel", variable=self.export_format_var, value="Excel")
        # excel_radio.pack(side="left")
        
        # report_radio = tk.Radiobutton(format_frame, text="综合报告", variable=self.export_format_var, value="Report")
        # report_radio.pack(side="left")
        
        # 时间范围选择
        tk.Label(option_frame, text="时间范围:").grid(row=1, column=0, sticky="w", pady=5)
        self.export_time_range_var = tk.StringVar(value="全部数据")
        time_combo = ttk.Combobox(option_frame, textvariable=self.export_time_range_var,
                                 values=["全部数据", "本月", "上月", "今年", "去年", "自定义"],
                                 state="readonly", width=15)
        time_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # 自定义日期框架
        custom_date_frame = tk.Frame(option_frame)
        custom_date_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        tk.Label(custom_date_frame, text="开始日期:").pack(side="left")
        self.export_start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(custom_date_frame, textvariable=self.export_start_date_var, width=12)
        start_date_entry.pack(side="left", padx=5)
        
        tk.Label(custom_date_frame, text="结束日期:").pack(side="left")
        self.export_end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(custom_date_frame, textvariable=self.export_end_date_var, width=12)
        end_date_entry.pack(side="left", padx=5)
        
        # 文件路径选择
        tk.Label(option_frame, text="保存路径:").grid(row=3, column=0, sticky="w", pady=5)
        path_frame = tk.Frame(option_frame)
        path_frame.grid(row=3, column=1, sticky="w", pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(path_frame, textvariable=self.file_path_var, width=30)
        file_entry.pack(side="left")
        
        browse_btn = tk.Button(path_frame, text="浏览", command=self.browse_file)
        browse_btn.pack(side="left", padx=5)
        
        # 导出按钮框架
        button_frame = tk.Frame(option_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        export_btn = tk.Button(button_frame, text="开始导出", command=self.export_data,
                              bg="#4CAF50", fg="white", font=("Arial", 12), width=15)
        export_btn.pack(side="left", padx=10)
        
        # 统计信息框架
        stats_frame = tk.LabelFrame(self, text="导出统计", font=("Arial", 12, "bold"))
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=6, width=80)
        self.stats_text.pack(fill="x", padx=5, pady=5)
        
        # 底部按钮框架
        bottom_button_frame = tk.Frame(self)
        bottom_button_frame.pack(pady=10)
        
        refresh_btn = tk.Button(bottom_button_frame, text="刷新统计", command=self.update_stats,
                              bg="#2196F3", fg="white", font=("Arial", 12), width=10)
        refresh_btn.pack(side="left", padx=10)
        
        back_btn = tk.Button(bottom_button_frame, text="返回", command=self.go_back,
                            bg="#607D8B", fg="white", font=("Arial", 12), width=10)
        back_btn.pack(side="left", padx=10)
        
        # 初始化统计信息
        self.update_stats()
    
    def browse_file(self):
        """浏览文件保存路径"""
        file_format = self.export_format_var.get()
        
        if file_format == "CSV":
            file_types = [("CSV文件", "*.csv")]
            default_extension = ".csv"
        # elif file_format == "Excel":
        #     file_types = [("Excel文件", "*.xlsx")]
        #     default_extension = ".xlsx"
        # else:  # Report
        #     file_types = [("Excel报告", "*.xlsx")]
        #     default_extension = ".xlsx"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            filetypes=file_types,
            title="选择保存位置"
        )
        
        if filename:
            self.file_path_var.set(filename)
    
    def get_export_data(self):
        """获取要导出的数据"""
        time_range = self.export_time_range_var.get()
        now = datetime.now()
        
        if time_range == "全部数据":
            return self.transaction_service.get_all_transactions()
        elif time_range == "本月":
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
        elif time_range == "上月":
            start_date = (now.replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
            end_date = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
        elif time_range == "今年":
            start_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
        elif time_range == "去年":
            start_date = now.replace(year=now.year-1, month=1, day=1).strftime("%Y-%m-%d")
            end_date = now.replace(year=now.year-1, month=12, day=31).strftime("%Y-%m-%d")
        else:  # 自定义
            start_date = self.export_start_date_var.get()
            end_date = self.export_end_date_var.get()
            if not start_date or not end_date:
                messagebox.showwarning("警告", "请输入自定义日期范围")
                return []
        
        return self.transaction_service.get_transactions_by_date_range(start_date, end_date)
    
    def export_data(self):
        """导出数据"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请选择保存路径")
            return
        
        transactions = self.get_export_data()
        if not transactions:
            messagebox.showwarning("警告", "没有数据可导出")
            return
        
        export_format = self.export_format_var.get()
        success = False
        
        try:
            if export_format == "CSV":
                success = self.transaction_service.export_to_csv(file_path, transactions)
            elif export_format == "Excel":
                success = self.transaction_service.export_to_excel(file_path, transactions)
            else:  # Report
                # 获取日期范围用于报告
                if transactions:
                    dates = [t.date for t in transactions]
                    start_date = min(dates)
                    end_date = max(dates)
                    success = self.export_service.export_comprehensive_report(file_path, start_date, end_date)
                else:
                    success = False
            
            if success:
                messagebox.showinfo("成功", f"数据已导出到: {file_path}")
                self.update_stats()
            else:
                messagebox.showerror("错误", "导出失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出过程中发生错误: {str(e)}")
    
    def update_stats(self):
        """更新统计信息"""
        transactions = self.transaction_service.get_all_transactions()
        total_count = len(transactions)
        
        # 按类型统计
        income_count = len([t for t in transactions if t.type == TransactionType.INCOME])
        expense_count = len([t for t in transactions if t.type == TransactionType.EXPENSE])
        
        # 计算总金额
        total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        total_expense = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        
        stats_text = f"数据统计概览:\n\n"
        stats_text += f"总交易记录数: {total_count}\n"
        stats_text += f"收入记录数: {income_count}\n"
        stats_text += f"支出记录数: {expense_count}\n"
        stats_text += f"总收入: {total_income:.2f}\n"
        stats_text += f"总支出: {total_expense:.2f}\n"
        stats_text += f"净结余: {total_income - total_expense:.2f}\n"
        stats_text += f"\n数据时间范围: {transactions[0].date if transactions else '无'} 至 {transactions[-1].date if transactions else '无'}"
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats_text)
    
    def go_back(self):
        """返回主界面"""
        self.app.show_main_screen()


class PersonalFinanceApp:
    """个人记账本应用主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("个人记账本 - 完整版")
        self.root.geometry("900x700")
        
        # 初始化服务
        self.category_service = CategoryService()
        self.transaction_service = TransactionService()
        self.budget_service = BudgetService()
        self.statistics_service = StatisticsService(self.transaction_service, self.budget_service)
        self.export_service = DataExportService(self.transaction_service, self.statistics_service)
        
        # 创建主容器
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        # 初始化界面
        self.current_screen = None
        self.show_main_screen()
    
    def show_main_screen(self):
        """显示主界面"""
        self.switch_screen(MainScreen, self.transaction_service, 
                          self.category_service, self.statistics_service)
    
    def show_add_transaction_screen(self):
        """显示记账界面"""
        self.switch_screen(AddTransactionScreen, self.transaction_service, 
                          self.category_service)
    
    def show_edit_transaction_screen(self, transaction_id: str):
        """显示编辑交易界面"""
        self.switch_screen(EditTransactionScreen, self.transaction_service, 
                          self.category_service, transaction_id)
    
    def show_statistics_screen(self):
        """显示统计界面"""
        self.switch_screen(StatisticsScreen, self.transaction_service, 
                          self.statistics_service)
    
    def show_search_screen(self):
        """显示查询界面"""
        self.switch_screen(SearchScreen, self.transaction_service, 
                          self.category_service)
    
    def show_budget_screen(self):
        """显示预算管理界面"""
        self.switch_screen(BudgetScreen, self.budget_service,
                          self.category_service, self.statistics_service)
    
    def show_export_screen(self):
        """显示数据导出界面"""
        self.switch_screen(ExportScreen, self.transaction_service,
                          self.export_service)
    
    def switch_screen(self, screen_class, *args):
        """切换界面"""
        if self.current_screen:
            self.current_screen.destroy()
        
        self.current_screen = screen_class(self.container, self, *args)
        self.current_screen.pack(fill="both", expand=True)

