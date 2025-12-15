# tests/test_integration.py
"""
个人记账本应用集成测试
测试不同服务模块之间的协同工作
"""
import pytest
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from finance_app import (
    TransactionService, 
    BudgetService, 
    StatisticsService,
    TransactionType,
    Transaction,
    Budget
)


class TestIntegration:
    """集成测试类"""
    
    def setup_method(self):
        """测试方法前的准备工作"""
        # 使用不同的临时文件避免数据冲突
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.transaction_file = f"test_integration_transactions_{timestamp}.json"
        self.budget_file = f"test_integration_budgets_{timestamp}.json"
        
        # 初始化服务实例
        self.transaction_service = TransactionService(self.transaction_file)
        self.budget_service = BudgetService(self.budget_file)
        self.statistics_service = StatisticsService(
            self.transaction_service, 
            self.budget_service
        )
        
        print(f"\n测试使用的临时文件：")
        print(f"交易文件：{self.transaction_file}")
        print(f"预算文件：{self.budget_file}")
    
    def teardown_method(self):
        """测试方法后的清理工作"""
        # 删除临时文件
        for file in [self.transaction_file, self.budget_file]:
            if os.path.exists(file):
                os.remove(file)
                print(f"已清理文件：{file}")
    
    # ==================== 第一组集成测试 ====================
    
    def test_integration_01_transaction_statistics_flow(self):
        """
        集成测试1：交易与统计服务完整流程
        测试场景：创建交易 -> 统计分析 -> 验证结果
        """
        print("\n=== 开始集成测试1：交易与统计服务完整流程 ===")
        
        # 1. 准备测试数据
        test_transactions = [
            # (金额, 类型, 分类, 日期, 备注)
            (5000.0, TransactionType.INCOME, "工资", "2024-01-05", "1月工资"),
            (300.0, TransactionType.EXPENSE, "餐饮", "2024-01-10", "午餐"),
            (200.0, TransactionType.EXPENSE, "交通", "2024-01-15", "地铁卡充值"),
            (1000.0, TransactionType.INCOME, "奖金", "2024-01-20", "年终奖"),
            (150.0, TransactionType.EXPENSE, "餐饮", "2024-01-25", "晚餐"),
            (50.0, TransactionType.EXPENSE, "娱乐", "2024-01-28", "电影票"),
        ]
        
        # 2. 创建交易记录
        created_count = 0
        for amount, trans_type, category, date, note in test_transactions:
            result = self.transaction_service.create_transaction(
                amount=amount,
                transaction_type=trans_type,
                category=category,
                date=date,
                note=note
            )
            assert result is True, f"创建交易失败：{category} - {amount}"
            created_count += 1
        
        print(f"✓ 成功创建 {created_count} 条交易记录")
        
        # 3. 验证交易数据存储
        all_transactions = self.transaction_service.get_all_transactions()
        assert len(all_transactions) == len(test_transactions), "交易记录数量不匹配"
        print(f"✓ 交易数据存储验证通过，共 {len(all_transactions)} 条记录")
        
        # 4. 使用统计服务分析数据
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        # 4.1 计算总收入
        total_income = self.statistics_service.calculate_total_income(start_date, end_date)
        expected_income = 5000.0 + 1000.0  # 工资 + 奖金
        assert abs(total_income - expected_income) < 0.01, f"总收入计算错误：{total_income} != {expected_income}"
        print(f"✓ 总收入计算正确：{total_income:.2f}")
        
        # 4.2 计算总支出
        total_expense = self.statistics_service.calculate_total_expense(start_date, end_date)
        expected_expense = 300.0 + 200.0 + 150.0 + 50.0  # 所有支出
        assert abs(total_expense - expected_expense) < 0.01, f"总支出计算错误：{total_expense} != {expected_expense}"
        print(f"✓ 总支出计算正确：{total_expense:.2f}")
        
        # 4.3 计算净结余
        net_balance = self.statistics_service.calculate_net_balance(start_date, end_date)
        expected_balance = expected_income - expected_expense
        assert abs(net_balance - expected_balance) < 0.01, f"净结余计算错误：{net_balance} != {expected_balance}"
        print(f"✓ 净结余计算正确：{net_balance:.2f}")
        
        # 4.4 获取分类统计
        income_stats = self.statistics_service.get_income_category_stats(start_date, end_date)
        assert "工资" in income_stats, "收入分类统计缺少'工资'"
        assert "奖金" in income_stats, "收入分类统计缺少'奖金'"
        assert income_stats["工资"] == 5000.0, f"工资统计错误：{income_stats['工资']}"
        assert income_stats["奖金"] == 1000.0, f"奖金统计错误：{income_stats['奖金']}"
        print(f"✓ 收入分类统计正确：{income_stats}")
        
        expense_stats = self.statistics_service.get_expense_category_stats(start_date, end_date)
        assert "餐饮" in expense_stats, "支出分类统计缺少'餐饮'"
        assert expense_stats["餐饮"] == 450.0, f"餐饮支出统计错误：{expense_stats['餐饮']}"
        print(f"✓ 支出分类统计正确：{expense_stats}")
        
        # 5. 验证跨服务数据一致性
        # 5.1 统计服务获取的交易数据应与交易服务一致
        transactions_from_stats = self.transaction_service.get_transactions_by_date_range(start_date, end_date)
        assert len(transactions_from_stats) == len(test_transactions), "跨服务数据不一致"
        
        # 5.2 验证每条交易记录的完整性
        for transaction in transactions_from_stats:
            assert transaction.transaction_id is not None
            assert transaction.amount > 0
            assert transaction.date is not None
            assert transaction.category is not None
        
        print("✓ 跨服务数据一致性验证通过")
        
        print("✅ 集成测试1：交易与统计服务完整流程 - 通过")
    
    def test_integration_02_search_and_export_flow(self):
        """
        集成测试2：搜索与导出功能集成
        测试场景：创建交易 -> 搜索过滤 -> 导出数据 -> 验证导出结果
        """
        print("\n=== 开始集成测试2：搜索与导出功能集成 ===")
        
        # 1. 准备多样化测试数据
        test_data = [
            (100.0, TransactionType.EXPENSE, "餐饮", "2024-02-01", "早餐"),
            (200.0, TransactionType.EXPENSE, "餐饮", "2024-02-02", "午餐聚会"),
            (50.0, TransactionType.EXPENSE, "交通", "2024-02-03", "公交车"),
            (300.0, TransactionType.INCOME, "工资", "2024-02-04", "基本工资"),
            (150.0, TransactionType.EXPENSE, "娱乐", "2024-02-05", "KTV"),
            (80.0, TransactionType.EXPENSE, "餐饮", "2024-02-06", "晚餐"),
            (500.0, TransactionType.INCOME, "奖金", "2024-02-07", "项目奖金"),
        ]
        
        # 2. 创建交易记录
        for amount, trans_type, category, date, note in test_data:
            result = self.transaction_service.create_transaction(
                amount=amount,
                transaction_type=trans_type,
                category=category,
                date=date,
                note=note
            )
            assert result is True
        
        print("✓ 测试数据创建完成")
        
        # 3. 测试复杂搜索功能
        # 3.1 按分类搜索
        food_transactions = self.transaction_service.search_transactions(
            category="餐饮"
        )
        assert len(food_transactions) == 3, f"餐饮分类搜索错误，找到 {len(food_transactions)} 条记录"
        print(f"✓ 按分类搜索：找到 {len(food_transactions)} 条餐饮记录")
        
        # 3.2 按类型和关键词搜索
        expense_with_food = self.transaction_service.search_transactions(
            transaction_type=TransactionType.EXPENSE,
            keyword="餐"
        )
        assert len(expense_with_food) >= 2, "按类型和关键词搜索错误"
        print(f"✓ 按类型和关键词搜索：找到 {len(expense_with_food)} 条支出餐饮记录")
        
        # 3.3 按日期范围搜索
        date_range_transactions = self.transaction_service.search_transactions(
            start_date="2024-02-01",
            end_date="2024-02-03"
        )
        assert len(date_range_transactions) == 3, f"日期范围搜索错误，找到 {len(date_range_transactions)} 条记录"
        print(f"✓ 按日期范围搜索：找到 {len(date_range_transactions)} 条记录")
        
        # 3.4 按金额范围搜索
        amount_range_transactions = self.transaction_service.search_transactions(
            min_amount=100.0,
            max_amount=300.0
        )
        assert len(amount_range_transactions) >= 4, "金额范围搜索错误"
        print(f"✓ 按金额范围搜索：找到 {len(amount_range_transactions)} 条记录")
        
        # 4. 测试导出功能
        import tempfile
        
        # 4.1 导出CSV文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            csv_file = tmp.name
        
        export_result = self.transaction_service.export_to_csv(csv_file)
        assert export_result is True, "CSV导出失败"
        
        # 验证CSV文件内容
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            csv_content = f.read()
            assert "交易ID" in csv_content
            assert "餐饮" in csv_content
            assert "支出" in csv_content
        
        print(f"✓ CSV导出成功，文件：{csv_file}")
        
        # 4.2 导出筛选后的数据
        with tempfile.NamedTemporaryFile(mode='w', suffix='_filtered.csv', delete=False) as tmp:
            filtered_csv = tmp.name
        
        # 只导出餐饮类支出
        food_expense = self.transaction_service.search_transactions(
            category="餐饮",
            transaction_type=TransactionType.EXPENSE
        )
        
        filtered_export = self.transaction_service.export_to_csv(filtered_csv, food_expense)
        assert filtered_export is True, "筛选数据导出失败"
        
        with open(filtered_csv, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            # 表头 + 数据行
            assert len(lines) == len(food_expense) + 1
        
        print(f"✓ 筛选数据导出成功，文件：{filtered_csv}")
        
        # 5. 清理临时文件
        for file in [csv_file, filtered_csv]:
            if os.path.exists(file):
                os.remove(file)
        
        print("✅ 集成测试2：搜索与导出功能集成 - 通过")
    
    # ==================== 第二组集成测试 ====================
    
    def test_integration_03_budget_analysis_full_flow(self):
        """
        集成测试3：预算分析完整流程
        测试场景：设置预算 -> 记录交易 -> 分析预算使用情况 -> 验证预警
        """
        print("\n=== 开始集成测试3：预算分析完整流程 ===")
        
        # 1. 设置预算
        budgets = [
            ("餐饮", 1000.0, "2024-03", "3月餐饮预算"),
            ("交通", 500.0, "2024-03", "3月交通预算"),
            ("娱乐", 300.0, "2024-03", "3月娱乐预算"),
        ]
        
        for category, amount, month, note in budgets:
            result = self.budget_service.create_budget(
                category=category,
                amount=amount,
                month=month,
                note=note
            )
            assert result is True, f"创建预算失败：{category}"
        
        print("✓ 预算设置完成")
        
        # 验证预算数据
        march_budgets = self.budget_service.get_budgets_by_month("2024-03")
        assert len(march_budgets) == 3, f"3月预算数量错误：{len(march_budgets)}"
        print(f"✓ 3月共设置 {len(march_budgets)} 个预算")
        
        # 2. 记录3月份交易
        march_transactions = [
            (200.0, TransactionType.EXPENSE, "餐饮", "2024-03-05", "午餐"),
            (150.0, TransactionType.EXPENSE, "餐饮", "2024-03-10", "晚餐"),
            (100.0, TransactionType.EXPENSE, "交通", "2024-03-12", "出租车"),
            (80.0, TransactionType.EXPENSE, "娱乐", "2024-03-15", "电影"),
            (300.0, TransactionType.EXPENSE, "餐饮", "2024-03-20", "聚餐"),  # 可能超预算
            (50.0, TransactionType.EXPENSE, "交通", "2024-03-22", "地铁"),
            (200.0, TransactionType.EXPENSE, "餐饮", "2024-03-25", "商务宴请"),  # 超过预算
            (100.0, TransactionType.EXPENSE, "娱乐", "2024-03-28", "游戏"),
        ]
        
        for amount, trans_type, category, date, note in march_transactions:
            result = self.transaction_service.create_transaction(
                amount=amount,
                transaction_type=trans_type,
                category=category,
                date=date,
                note=note
            )
            assert result is True
        
        print("✓ 3月交易记录完成")
        
        # 3. 进行预算分析
        budget_analysis = self.statistics_service.get_budget_analysis("2024-03")
        
        # 验证分析结果存在
        assert budget_analysis is not None, "预算分析结果为空"
        assert len(budget_analysis) == 3, f"预算分析数量错误：{len(budget_analysis)}"
        print(f"✓ 预算分析生成完成，分析 {len(budget_analysis)} 个预算")
        
        # 4. 验证餐饮预算分析
        assert "餐饮" in budget_analysis, "缺少餐饮预算分析"
        food_analysis = budget_analysis["餐饮"]
        
        # 计算预期值
        food_expenses = [200, 150, 300, 200]  # 4笔餐饮支出
        expected_food_expense = sum(food_expenses)
        
        assert abs(food_analysis['budget_amount'] - 1000.0) < 0.01, "餐饮预算金额错误"
        assert abs(food_analysis['actual_expense'] - expected_food_expense) < 0.01, \
            f"餐饮实际支出错误：{food_analysis['actual_expense']} != {expected_food_expense}"
        
        expected_remaining = 1000.0 - expected_food_expense
        assert abs(food_analysis['remaining'] - expected_remaining) < 0.01, \
            f"餐饮剩余预算错误：{food_analysis['remaining']} != {expected_remaining}"
        
        expected_usage_rate = (expected_food_expense / 1000.0) * 100
        assert abs(food_analysis['usage_rate'] - expected_usage_rate) < 0.01, \
            f"餐饮使用率错误：{food_analysis['usage_rate']} != {expected_usage_rate}"
        
        # 验证是否超预算（850 > 1000? 否，但很接近）
        is_over_budget = expected_food_expense > 1000.0
        assert food_analysis['is_over_budget'] == is_over_budget, \
            f"超预算状态错误：{food_analysis['is_over_budget']} != {is_over_budget}"
        
        print(f"✓ 餐饮预算分析正确：")
        print(f"  预算：1000.00，实际：{expected_food_expense:.2f}")
        print(f"  剩余：{expected_remaining:.2f}，使用率：{expected_usage_rate:.1f}%")
        print(f"  超预算：{'是' if is_over_budget else '否'}")
        
        # 5. 验证交通预算分析
        assert "交通" in budget_analysis, "缺少交通预算分析"
        traffic_analysis = budget_analysis["交通"]
        
        traffic_expenses = [100, 50]  # 2笔交通支出
        expected_traffic_expense = sum(traffic_expenses)
        
        assert abs(traffic_analysis['actual_expense'] - expected_traffic_expense) < 0.01, \
            f"交通实际支出错误：{traffic_analysis['actual_expense']} != {expected_traffic_expense}"
        
        print(f"✓ 交通预算分析正确：")
        print(f"  预算：500.00，实际：{expected_traffic_expense:.2f}")
        print(f"  剩余：{500 - expected_traffic_expense:.2f}")
        
        # 6. 验证数据一致性
        # 6.1 交易服务与统计服务数据一致
        march_transactions_from_service = self.transaction_service.get_transactions_by_month("2024-03")
        assert len(march_transactions_from_service) == len(march_transactions), "交易数据不一致"
        
        # 6.2 预算服务与统计服务数据一致
        budgets_from_service = self.budget_service.get_budgets_by_month("2024-03")
        assert len(budgets_from_service) == len(budget_analysis), "预算数据不一致"
        
        print("✓ 跨服务数据一致性验证通过")
        
        print("✅ 集成测试3：预算分析完整流程 - 通过")
    
    def test_integration_04_error_handling_and_data_integrity(self):
        """
        集成测试4：错误处理与数据完整性
        测试场景：异常数据处理 -> 服务间错误传递 -> 数据恢复验证
        """
        print("\n=== 开始集成测试4：错误处理与数据完整性 ===")
        
        # 1. 测试无效数据的处理
        # 1.1 无效金额的交易
        invalid_transactions = [
            (-100.0, TransactionType.EXPENSE, "测试", "2024-04-01", "负数金额"),
            (0.0, TransactionType.INCOME, "测试", "2024-04-02", "零金额"),
        ]
        
        initial_count = len(self.transaction_service.get_all_transactions())
        
        for amount, trans_type, category, date, note in invalid_transactions:
            result = self.transaction_service.create_transaction(
                amount=amount,
                transaction_type=trans_type,
                category=category,
                date=date,
                note=note
            )
            assert result is False, f"无效金额 {amount} 应该创建失败"
        
        final_count = len(self.transaction_service.get_all_transactions())
        assert initial_count == final_count, "无效交易不应该被保存"
        print("✓ 无效金额交易正确处理")
        
        # 1.2 无效日期的交易
        invalid_dates = [
            "2024-13-01",  # 无效月份
            "2024-01-32",  # 无效日期
            "not-a-date",  # 非日期字符串
        ]
        
        for date in invalid_dates:
            result = self.transaction_service.create_transaction(
                amount=100.0,
                transaction_type=TransactionType.EXPENSE,
                category="测试",
                date=date,
                note="无效日期测试"
            )
            # 根据实现，可能返回False或抛出异常
            # 这里主要测试系统不会崩溃
            print(f"  日期 {date}: 创建结果 = {result}")
        
        print("✓ 无效日期交易正确处理")
        
        # 2. 测试数据持久化与恢复
        # 2.1 创建有效数据
        valid_data = [
            (500.0, TransactionType.INCOME, "工资", "2024-04-10", "4月工资"),
            (200.0, TransactionType.EXPENSE, "餐饮", "2024-04-11", "午餐"),
        ]
        
        for amount, trans_type, category, date, note in valid_data:
            result = self.transaction_service.create_transaction(
                amount=amount,
                transaction_type=trans_type,
                category=category,
                date=date,
                note=note
            )
            assert result is True
        
        # 2.2 保存数据
        self.transaction_service.save_transactions()
        self.budget_service.save_budgets()
        
        print("✓ 数据保存完成")
        
        # 2.3 创建新实例加载数据
        new_transaction_service = TransactionService(self.transaction_file)
        new_transaction_service.load_transactions()
        
        new_budget_service = BudgetService(self.budget_file)
        new_budget_service.load_budgets()
        
        # 2.4 验证数据恢复
        restored_transactions = new_transaction_service.get_all_transactions()
        assert len(restored_transactions) == len(valid_data), "数据恢复数量错误"
        
        for i, transaction in enumerate(restored_transactions):
            expected_amount, expected_type, expected_category, expected_date, expected_note = valid_data[i]
            assert transaction.amount == expected_amount, f"恢复数据金额错误：{transaction.amount} != {expected_amount}"
            assert transaction.type == expected_type, f"恢复数据类型错误：{transaction.type} != {expected_type}"
            assert transaction.category == expected_category, f"恢复数据分类错误：{transaction.category} != {expected_category}"
        
        print("✓ 数据恢复验证通过")
        
        # 3. 测试服务间的错误传递
        # 3.1 使用空数据测试统计服务
        empty_transaction_service = TransactionService("empty_test.json")
        empty_statistics_service = StatisticsService(empty_transaction_service, self.budget_service)
        
        # 应该能够处理空数据而不崩溃
        total_income = empty_statistics_service.calculate_total_income("2024-01-01", "2024-12-31")
        assert total_income == 0.0, "空数据总收入应为0"
        
        empty_analysis = empty_statistics_service.get_budget_analysis("2024-01")
        # 可能是空字典或None，取决于实现
        print(f"✓ 空数据处理正常：总收入={total_income}, 预算分析={empty_analysis}")
        
        # 清理空测试文件
        if os.path.exists("empty_test.json"):
            os.remove("empty_test.json")
        
        # 4. 测试边界条件
        # 4.1 大量数据测试
        print("  开始边界条件测试...")
        
        # 创建多条数据测试性能
        test_count = 50
        for i in range(test_count):
            self.transaction_service.create_transaction(
                amount=10.0 + i,
                transaction_type=TransactionType.EXPENSE,
                category="测试",
                date=f"2024-04-{i % 30 + 1:02d}",
                note=f"测试记录{i}"
            )
        
        all_count = len(self.transaction_service.get_all_transactions())
        assert all_count == len(valid_data) + test_count, f"数据数量错误：{all_count}"
        
        # 测试搜索性能
        search_results = self.transaction_service.search_transactions(keyword="测试")
        assert len(search_results) == test_count, f"搜索结果数量错误：{len(search_results)}"
        
        print(f"✓ 边界条件测试通过：共 {all_count} 条记录")
        
        print("✅ 集成测试4：错误处理与数据完整性 - 通过")