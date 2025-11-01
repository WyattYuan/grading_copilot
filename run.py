"""
一键启动前后端服务
同时启动 FastAPI 后端和 Streamlit 前端
"""

import sys
import subprocess
import time
from pathlib import Path
import signal
import platform

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import config


def start_api_server():
    """启动 API 服务器"""
    print("🚀 启动 FastAPI 后端服务...")
    print(f"📍 API地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"📖 API文档: http://{config.API_HOST}:{config.API_PORT}/docs")

    # 使用 subprocess.Popen 启动独立进程
    if platform.system() == "Windows":
        api_process = subprocess.Popen(
            [sys.executable, str(project_root / "run_api.py")],
            cwd=str(project_root),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        api_process = subprocess.Popen(
            [sys.executable, str(project_root / "run_api.py")],
            cwd=str(project_root),
            preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
        )
    return api_process


def start_ui_server():
    """启动 Streamlit 前端服务"""
    print("\n🎨 启动 Streamlit 前端界面...")
    print(f"📍 UI地址: http://localhost:{config.STREAMLIT_PORT}")

    # 使用 subprocess.Popen 启动独立进程
    if platform.system() == "Windows":
        ui_process = subprocess.Popen(
            [sys.executable, str(project_root / "run_ui.py")],
            cwd=str(project_root),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        ui_process = subprocess.Popen(
            [sys.executable, str(project_root / "run_ui.py")],
            cwd=str(project_root),
            preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
        )
    return ui_process


def main():
    """主函数"""
    print("=" * 60)
    print("🎓 AI智能评分系统 - 一键启动")
    print("=" * 60)

    api_process = None
    ui_process = None

    try:
        # 启动后端
        api_process = start_api_server()

        print("\n⏳ 等待后端服务启动...")
        time.sleep(3)

        # 启动前端
        ui_process = start_ui_server()

        print("\n" + "=" * 60)
        print("✅ 服务启动成功!")
        print("=" * 60)
        print(f"📍 后端API: http://{config.API_HOST}:{config.API_PORT}")
        print(f"📍 前端界面: http://localhost:{config.STREAMLIT_PORT}")
        print(f"📖 API文档: http://{config.API_HOST}:{config.API_PORT}/docs")
        print("=" * 60)
        print("\n💡 按 Ctrl+C 停止所有服务\n")

        # 等待子进程
        while True:
            # 检查进程是否还在运行
            api_poll = api_process.poll()
            ui_poll = ui_process.poll()

            if api_poll is not None:
                print(f"\n⚠️  后端服务已退出 (退出码: {api_poll})")
                break

            if ui_poll is not None:
                print(f"\n⚠️  前端服务已退出 (退出码: {ui_poll})")
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
    finally:
        # 清理进程
        if api_process and api_process.poll() is None:
            print("  ⏹️  停止后端服务...")
            if platform.system() == "Windows":
                api_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                api_process.terminate()
            try:
                api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_process.kill()

        if ui_process and ui_process.poll() is None:
            print("  ⏹️  停止前端服务...")
            if platform.system() == "Windows":
                ui_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                ui_process.terminate()
            try:
                ui_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                ui_process.kill()

        print("✅ 所有服务已停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
