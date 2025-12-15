# # tests/test_transaction_service.py
# import pytest
# from datetime import datetime, timedelta
# from finance_app import TransactionService, TransactionType, Transaction
# import os
# import json
import os
import sys
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from finance_app import TransactionService, TransactionType, Transaction
import json


class TestTransactionService:
    def setup_method(self):
        """每个测试方法前执行"""
        self.test_file = "test_transactions.json"
        self.service = TransactionService(self.test_file)
    
    def teardown_method(self):
        """每个测试方法后执行"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_create_transaction_success(self):
        """测试成功创建交易记录"""
        result = self.service.create_transaction(
            amount=100.0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-01",
            note="午餐"
        )
        
        assert result is True
        assert len(self.service.transactions) == 1
        transaction = self.service.transactions[0]
        assert transaction.amount == 100.0
        assert transaction.type == TransactionType.EXPENSE
        assert transaction.category == "餐饮"
        assert transaction.date == "2024-01-01"
        assert transaction.note == "午餐"
        assert transaction.transaction_id.startswith("T")
    
    def test_create_transaction_invalid_amount(self):
        """测试创建交易记录时金额无效"""
        # 测试金额为0
        result = self.service.create_transaction(
            amount=0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-01"
        )
        assert result is False
        
        # 测试金额为负数
        result = self.service.create_transaction(
            amount=-50.0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-01"
        )
        assert result is False
    
    def test_update_transaction_success(self):
        """测试成功更新交易记录"""
        # 先创建一条记录
        self.service.create_transaction(
            amount=100.0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-01",
            note="午餐"
        )
        
        transaction_id = self.service.transactions[0].transaction_id
        
        # 更新记录
        result = self.service.update_transaction(
            transaction_id=transaction_id,
            amount=150.0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-02",
            note="晚餐"
        )
        
        assert result is True
        transaction = self.service.get_transaction_by_id(transaction_id)
        assert transaction.amount == 150.0
        assert transaction.date == "2024-01-02"
        assert transaction.note == "晚餐"
    
    def test_update_transaction_not_found(self):
        """测试更新不存在的交易记录"""
        result = self.service.update_transaction(
            transaction_id="T999999",
            amount=100.0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-01"
        )
        assert result is False
    
    def test_delete_transaction_success(self):
        """测试成功删除交易记录"""
        self.service.create_transaction(
            amount=100.0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-01"
        )
        
        transaction_id = self.service.transactions[0].transaction_id
        initial_count = len(self.service.transactions)
        
        result = self.service.delete_transaction(transaction_id)
        
        assert result is True
        assert len(self.service.transactions) == initial_count - 1
        assert self.service.get_transaction_by_id(transaction_id) is None
    
    def test_get_transactions_by_date_range(self):
        """测试按日期范围获取交易记录"""
        # 创建多条测试记录
        test_data = [
            (100.0, "2024-01-01"),
            (200.0, "2024-01-15"),
            (300.0, "2024-01-31"),
            (400.0, "2024-02-01"),
        ]
        
        for amount, date in test_data:
            self.service.create_transaction(
                amount=amount,
                transaction_type=TransactionType.EXPENSE,
                category="餐饮",
                date=date
            )
        
        # 获取1月份的记录
        result = self.service.get_transactions_by_date_range(
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        assert len(result) == 3
        dates = [t.date for t in result]
        assert "2024-01-01" in dates
        assert "2024-01-15" in dates
        assert "2024-01-31" in dates
        assert "2024-02-01" not in dates
    
    def test_get_transactions_by_month(self):
        """测试按月份获取交易记录"""
        # 创建多条测试记录
        test_data = [
            (100.0, "2024-01-15"),
            (200.0, "2024-01-20"),
            (300.0, "2024-02-01"),
        ]
        
        for amount, date in test_data:
            self.service.create_transaction(
                amount=amount,
                transaction_type=TransactionType.EXPENSE,
                category="餐饮",
                date=date
            )
        
        # 获取1月份的记录
        result = self.service.get_transactions_by_month("2024-01")
        
        assert len(result) == 2
        for transaction in result:
            assert transaction.date.startswith("2024-01")
    
    def test_search_transactions_by_keyword(self):
        """测试按关键词搜索交易记录"""
        # 创建多条测试记录
        test_data = [
            (100.0, "午餐", TransactionType.EXPENSE, "餐饮"),
            (200.0, "交通费", TransactionType.EXPENSE, "交通"),
            (300.0, "晚餐", TransactionType.EXPENSE, "餐饮"),
        ]
        
        for amount, note, trans_type, category in test_data:
            self.service.create_transaction(
                amount=amount,
                transaction_type=trans_type,
                category=category,
                date="2024-01-01",
                note=note
            )
        
        # 搜索包含"餐"的记录
        result = self.service.search_transactions(keyword="餐")
        assert len(result) == 2
        
        # 搜索包含"交通"的记录
        result = self.service.search_transactions(keyword="交通")
        assert len(result) == 1
    
    def test_search_transactions_by_type(self):
        """测试按交易类型搜索"""
        # 创建收入和支出记录
        self.service.create_transaction(
            amount=100.0,
            transaction_type=TransactionType.INCOME,
            category="工资",
            date="2024-01-01",
            note="月薪"
        )
        
        self.service.create_transaction(
            amount=50.0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-01",
            note="午餐"
        )
        
        # 搜索收入记录
        result = self.service.search_transactions(
            transaction_type=TransactionType.INCOME
        )
        assert len(result) == 1
        assert result[0].type == TransactionType.INCOME
    
    def test_search_transactions_by_amount_range(self):
        """测试按金额范围搜索"""
        test_data = [50.0, 100.0, 150.0, 200.0]
        
        for amount in test_data:
            self.service.create_transaction(
                amount=amount,
                transaction_type=TransactionType.EXPENSE,
                category="餐饮",
                date="2024-01-01"
            )
        
        # 搜索金额在100-200之间的记录
        result = self.service.search_transactions(
            min_amount=100.0,
            max_amount=200.0
        )
        assert len(result) == 3
        
        # 搜索金额大于150的记录
        result = self.service.search_transactions(
            min_amount=150.0
        )
        assert len(result) == 2
    
    def test_export_to_csv_success(self):
        """测试导出CSV文件"""
        # 创建测试数据
        self.service.create_transaction(
            amount=100.0,
            transaction_type=TransactionType.EXPENSE,
            category="餐饮",
            date="2024-01-01",
            note="午餐"
        )
        
        # 导出到文件
        filename = "test_export.csv"
        result = self.service.export_to_csv(filename)
        
        assert result is True
        assert os.path.exists(filename)
        
        # 验证文件内容
        with open(filename, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            assert "交易ID" in content
            assert "2024-01-01" in content
            assert "餐饮" in content
        
        # 清理
        os.remove(filename)
    
    def test_load_and_save_transactions(self):
        """测试加载和保存交易记录"""
        # 创建测试数据
        test_data = [
            (100.0, TransactionType.EXPENSE, "餐饮", "2024-01-01", "午餐"),
            (200.0, TransactionType.INCOME, "工资", "2024-01-01", "月薪"),
        ]
        
        for amount, trans_type, category, date, note in test_data:
            self.service.create_transaction(
                amount=amount,
                transaction_type=trans_type,
                category=category,
                date=date,
                note=note
            )
        
        # 保存数据
        self.service.save_transactions()
        
        # 创建新的服务实例加载数据
        new_service = TransactionService(self.test_file)
        new_service.load_transactions()
        
        assert len(new_service.transactions) == 2
        assert new_service.transactions[0].amount == 100.0
        assert new_service.transactions[1].type == TransactionType.INCOME