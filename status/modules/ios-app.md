# iOS App

## 模块定位

移动端用户入口，未来默认走统一后端接口，飞书直连仅保留为测试模式。

## 当前状态

暂缓

## 已完成

- 现有项目已具备登录、提交、历史、详情、个人页基础界面
- 已具备飞书直连 Repository 和旧 APIService 双轨雏形

## 未完成

- 切换到后端主链路
- 清理硬编码飞书配置
- 统一正式模式和测试模式配置入口

## 验证证据

- `ios_app/iOS_Video_Intelligence/Services/FeishuAPIClient.swift`
- `ios_app/iOS_Video_Intelligence/Services/APIService.swift`

## 当前难点

- 当前优先级已切到前后端，iOS 需要等待后端接口先稳定

## 下一步任务

- 后端完成后再切换默认数据源

## 最后更新

2026-03-20
