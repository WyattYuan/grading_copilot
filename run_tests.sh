#!/bin/bash
# 测试运行器 - Linux/Mac 版本

set -e

echo "═══════════════════════════════════════════════════════════"
echo "          AI智能评分系统 - 测试运行器"
echo "═══════════════════════════════════════════════════════════"
echo

show_menu() {
    echo "请选择测试类型:"
    echo
    echo "  1. 运行所有测试"
    echo "  2. 只运行单元测试"
    echo "  3. 只运行集成测试"
    echo "  4. 运行并生成覆盖率报告"
    echo "  5. 运行特定测试文件"
    echo "  6. 退出"
    echo
}

while true; do
    show_menu
    read -p "请输入选项 (1-6): " choice
    
    case $choice in
        1)
            echo
            echo "运行所有测试..."
            echo
            pixi run pytest tests/ -v
            ;;
        2)
            echo
            echo "运行单元测试..."
            echo
            pixi run pytest tests/unit/ -v
            ;;
        3)
            echo
            echo "运行集成测试..."
            echo
            echo "⚠️  注意: 集成测试需要 API 服务运行"
            echo "   请确保已运行: python run_api.py"
            echo
            read -p "按 Enter 继续..."
            pixi run pytest tests/integration/ -v
            ;;
        4)
            echo
            echo "运行测试并生成覆盖率报告..."
            echo
            pixi run pytest tests/ --cov=src --cov-report=html --cov-report=term
            echo
            echo "✅ 覆盖率报告已生成: htmlcov/index.html"
            if command -v xdg-open &> /dev/null; then
                xdg-open htmlcov/index.html
            elif command -v open &> /dev/null; then
                open htmlcov/index.html
            fi
            ;;
        5)
            echo
            echo "可用的测试文件:"
            echo
            echo "单元测试:"
            echo "  - tests/unit/test_models.py"
            echo "  - tests/unit/test_file_count.py"
            echo "  - tests/unit/test_extract_zip.py"
            echo "  - tests/unit/test_navigation.py"
            echo "  - tests/unit/test_task_name_format.py"
            echo
            echo "集成测试:"
            echo "  - tests/integration/test_config_api.py"
            echo "  - tests/integration/test_ui_config.py"
            echo
            read -p "请输入测试文件路径: " testfile
            echo
            pixi run pytest "$testfile" -v
            ;;
        6)
            echo
            echo "再见！"
            exit 0
            ;;
        *)
            echo "无效选项，请重试"
            ;;
    esac
    
    echo
    echo "═══════════════════════════════════════════════════════════"
    echo "测试完成"
    echo "═══════════════════════════════════════════════════════════"
    echo
    read -p "按 Enter 继续..."
done
