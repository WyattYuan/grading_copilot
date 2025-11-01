"""
测试模块组织说明

tests/
├── unit/              # 单元测试（测试单个组件）
│   ├── test_models.py         # 数据模型测试
│   ├── test_file_utils.py     # 文件工具测试
│   └── test_navigation.py     # 导航逻辑测试
│
├── integration/       # 集成测试（测试多个组件协作）
│   ├── test_api_config.py     # API 配置集成测试
│   └── test_ui_workflow.py    # UI 完整工作流测试
│
├── helpers/           # 测试辅助工具
│   ├── create_test_data.py    # 创建测试数据
│   └── fixtures.py            # 测试固件
│
└── deprecated/        # 已废弃的测试（保留用于参考）
    └── ...

运行测试:
    pytest tests/unit/              # 运行单元测试
    pytest tests/integration/       # 运行集成测试
    pytest tests/                   # 运行所有测试
"""
