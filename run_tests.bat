@echo off
chcp 65001 >nul
title 运行测试

echo ═══════════════════════════════════════════════════════════
echo           AI智能评分系统 - 测试运行器
echo ═══════════════════════════════════════════════════════════
echo.

:menu
echo 请选择测试类型:
echo.
echo   1. 运行所有测试
echo   2. 只运行单元测试
echo   3. 只运行集成测试
echo   4. 运行并生成覆盖率报告
echo   5. 运行特定测试文件
echo   6. 退出
echo.
set /p choice="请输入选项 (1-6): "

if "%choice%"=="1" goto all_tests
if "%choice%"=="2" goto unit_tests
if "%choice%"=="3" goto integration_tests
if "%choice%"=="4" goto coverage
if "%choice%"=="5" goto specific_test
if "%choice%"=="6" goto end
goto menu

:all_tests
echo.
echo 运行所有测试...
echo.
uv run pytest tests/ -v
goto test_done

:unit_tests
echo.
echo 运行单元测试...
echo.
uv run pytest tests/unit/ -v
goto test_done

:integration_tests
echo.
echo 运行集成测试...
echo.
echo ⚠️  注意: 集成测试需要 API 服务运行
echo    请确保已运行: python run_api.py
echo.
pause
uv run pytest tests/integration/ -v
goto test_done

:coverage
echo.
echo 运行测试并生成覆盖率报告...
echo.
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term
echo.
echo ✅ 覆盖率报告已生成: htmlcov/index.html
start htmlcov\index.html
goto test_done

:specific_test
echo.
echo 可用的测试文件:
echo.
echo 单元测试:
echo   - tests/unit/test_models.py
echo   - tests/unit/test_file_count.py
echo   - tests/unit/test_extract_zip.py
echo   - tests/unit/test_navigation.py
echo   - tests/unit/test_task_name_format.py
echo.
echo 集成测试:
echo   - tests/integration/test_config_api.py
echo   - tests/integration/test_ui_config.py
echo.
set /p testfile="请输入测试文件路径: "
echo.
uv run pytest %testfile% -v
goto test_done

:test_done
echo.
echo ═══════════════════════════════════════════════════════════
echo 测试完成
echo ═══════════════════════════════════════════════════════════
echo.
echo 按任意键继续...
pause >nul
goto menu

:end
echo.
echo 再见！
exit /b 0
