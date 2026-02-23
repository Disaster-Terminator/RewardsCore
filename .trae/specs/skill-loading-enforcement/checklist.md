# Checklist

## 验证项

- [x] dev-agent.md 包含物理环境前置检查（Move-Item, Remove-Item, 禁止 pip install）
- [x] dev-agent.md 包含环境异常阻断协议
- [x] dev-agent.md 执行序列明确"强制加载 SOP"步骤
- [x] test-agent.md 包含物理环境前置检查（Playwright 进程安全, 测试目录隔离）
- [x] test-agent.md 执行序列明确"强制加载 SOP"步骤
- [x] test-execution/SKILL.md 包含二维错误诊断矩阵
- [x] 二维矩阵覆盖所有场景（rscore 成功/失败 × python main.py 成功/失败）
- [x] 二维矩阵明确状态标签输出

## 预期效果

- Agent 唤醒时，物理边界约束作为常驻上下文强制生效
- Agent 无法跳过 Skill 加载步骤
- test-agent 能够精准区分环境问题 vs 业务问题 vs 配置问题
