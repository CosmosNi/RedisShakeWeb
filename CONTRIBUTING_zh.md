# 为 Redis-Shake 管理平台贡献

[English](CONTRIBUTING.md) | [中文](CONTRIBUTING_zh.md)

我们欢迎您的贡献！我们希望让为这个项目做贡献变得尽可能简单和透明，无论是：

- 报告错误
- 讨论代码的当前状态
- 提交修复
- 提出新功能
- 成为维护者

## 我们使用 Github Flow 开发

Pull requests 是向我们的代码库提出更改的最佳方式。我们积极欢迎您的 pull requests：

1. Fork 仓库并从 `main` 创建您的分支。
2. 如果您添加了应该测试的代码，请添加测试。
3. 如果您更改了 API，请更新文档。
4. 确保测试套件通过。
5. 确保您的代码符合代码规范。
6. 发出 pull request！

## 开发环境设置

### 前置要求

- **Node.js** 16+ 和 npm
- **Python** 3.8+
- **Git**
- **Redis** 服务器（用于测试）

### 设置步骤

1. **Fork 并克隆仓库**
   ```bash
   git clone https://github.com/your-username/redis-shake-management.git
   cd redis-shake-management
   ```

2. **后端设置**
   ```bash
   cd backend
   
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 启动开发服务器
   python -m app.main
   ```

3. **前端设置**
   ```bash
   cd frontend
   
   # 安装依赖
   npm install
   
   # 启动开发服务器
   npm start
   ```

4. **Redis-Shake 二进制文件**
   - 从 [Redis-Shake releases](https://github.com/tair-opensource/RedisShake/releases) 下载
   - 将二进制文件放置在 `bin/redis-shake`

## 代码规范

### Python (后端)

- 遵循 **PEP 8** 代码风格
- 使用 **类型提示** 进行所有函数参数和返回值
- 编写 **文档字符串** 用于所有公共函数和类
- 使用 **async/await** 进行异步操作
- 保持函数简洁（通常少于 50 行）

示例：
```python
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """获取任务的实时状态。
    
    Args:
        task_id: 任务的唯一标识符
        
    Returns:
        包含任务状态信息的字典
        
    Raises:
        TaskNotFoundError: 当任务不存在时
    """
    # 实现代码...
```

### JavaScript/React (前端)

- 使用 **ESLint** 进行代码检查
- 遵循 **React Hooks** 最佳实践
- 使用 **函数式组件** 而不是类组件
- 使用 **TypeScript** 风格的 JSDoc 注释
- 保持组件简洁和可重用

示例：
```javascript
/**
 * 任务状态组件
 * @param {Object} props - 组件属性
 * @param {string} props.taskId - 任务ID
 * @param {Function} props.onStatusChange - 状态变化回调
 */
const TaskStatus = ({ taskId, onStatusChange }) => {
  // 组件实现...
};
```

## 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_task_service.py

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 前端测试

```bash
cd frontend

# 运行所有测试
npm test

# 运行测试并生成覆盖率报告
npm test -- --coverage
```

## 提交信息规范

我们使用 [Conventional Commits](https://conventionalcommits.org/) 规范：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

### 类型

- **feat**: 新功能
- **fix**: 错误修复
- **docs**: 文档更改
- **style**: 代码格式更改（不影响代码含义）
- **refactor**: 代码重构
- **test**: 添加或修改测试
- **chore**: 构建过程或辅助工具的变动

### 示例

```
feat(frontend): 添加实时任务监控图表

- 集成 ECharts 用于数据可视化
- 添加实时数据更新功能
- 支持多种图表类型

Closes #123
```

## 报告错误

我们使用 GitHub issues 来跟踪公共错误。通过 [开启新 issue](https://github.com/your-username/redis-shake-management/issues/new) 报告错误；这很简单！

**优秀的错误报告** 通常包含：

- 问题的简要摘要和/或背景
- 重现步骤
  - 要具体！
  - 如果可能，提供示例代码
- 您期望发生什么
- 实际发生了什么
- 注释（可能包括您认为可能导致问题的原因，或您尝试过但没有效果的方法）

## 功能请求

我们欢迎功能请求！但请花一点时间了解您的想法是否符合项目的范围和目标。请提供尽可能多的细节和上下文。

## 许可证

通过贡献，您同意您的贡献将在与项目相同的 MIT 许可证下获得许可。

## 行为准则

### 我们的承诺

为了营造一个开放和欢迎的环境，我们作为贡献者和维护者承诺，无论年龄、体型、残疾、种族、性别认同和表达、经验水平、国籍、个人外貌、种族、宗教或性认同和取向如何，参与我们的项目和社区对每个人来说都是无骚扰的体验。

### 我们的标准

有助于创造积极环境的行为示例包括：

- 使用欢迎和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 专注于对社区最有利的事情
- 对其他社区成员表现出同理心

## 获得帮助

如果您需要帮助或有疑问：

- 查看 [文档](docs/)
- 搜索现有的 [issues](https://github.com/your-username/redis-shake-management/issues)
- 创建新的 [issue](https://github.com/your-username/redis-shake-management/issues/new)
- 参与 [讨论](https://github.com/your-username/redis-shake-management/discussions)

感谢您的贡献！🎉
