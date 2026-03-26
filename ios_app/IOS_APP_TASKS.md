# iOS App Tasks

## 目标与非目标

### 目标
- [x] 默认链路切换到统一后端 `http://192.168.0.32:8002`
  验收：App 默认不再依赖 Mock 登录和飞书直连即可完成登录、提交、列表、详情、概览通信。
- [x] 在不改页面结构的前提下完成局域网联调
  验收：`Login / Submit / History / Detail / Profile` 保持现有布局和信息层级。
- [x] 保留旧链路作为兜底代码
  验收：`LocalMockAuthService` 和 `FeishuVideoRepository` 仍可编译，但不再作为默认入口。

### 非目标
- [ ] CoreData、本地缓存、离线浏览
  验收：本轮不新增本地持久化模型或缓存同步逻辑。
- [ ] 搜索增强、分享扩展、实时进度、UI 重构
  验收：不新增页面，不重做交互，不扩功能范围。

## 环境常量
- [x] 后端基址：`http://192.168.0.32:8002`
  验收：服务层统一从 `AppConfig.Server.baseURL` 读取。
- [x] 认证接口：`POST /auth/login`
  验收：请求体为 JSON `{ "username": "...", "password": "..." }`。
- [x] 视频接口：`POST /videos/submit`、`GET /videos`、`GET /videos/{id}`、`GET /videos/stats`、`GET /videos/overview`
  验收：不再残留默认 `/api/...` 旧路径。

## 里程碑清单

### 配置接线
- [x] 更新 `AppConfig` 默认模式为后端模式
  验收：`AppServices.authService` 绑定 `BackendAuthService`，`AppServices.videoRepository` 绑定 `BackendVideoRepository`。
- [x] 统一 `APIService` 基址和请求封装
  验收：所有服务请求都从 `AppConfig.Server.baseURL` 生成 URL，并支持 Bearer Token。

### 认证
- [x] 登录切换到 `/auth/login`
  验收：后端返回 `token + user` 后，`AuthManager` 能持久化并恢复登录态。
- [x] 错误映射对齐后端
  验收：401 登录失败显示“用户名或密码错误”，其他 FastAPI `detail` 文本可直接透传。

### 提交
- [x] 提交页接入 `/videos/submit`
  验收：提交成功后保留现有成功弹窗，失败时显示后端错误信息。
- [x] 视频类型统计接入 `/videos/stats`
  验收：提交页统计卡片由真实后端数据驱动，空数据时页面不崩溃。

### 历史/详情
- [x] 历史页接入 `/videos`
  验收：保持现有分页汇总 + 前端搜索/分类/排序体验。
- [x] 详情页进入后刷新 `/videos/{id}`
  验收：列表传入的初始内容可先展示，接口返回后覆盖为最新详情。

### 个人页
- [x] 个人页统计接入 `/videos/overview`
  验收：累计、今日、待处理不再硬编码，空数据和失败场景可稳定展示。

### 测试验证
- [x] 补充服务层解码与错误映射测试
  验收：覆盖登录成功、401、FastAPI `detail`、snake_case DTO 解码。
- [ ] 手动局域网联调
  验收：真机或模拟器完成登录、提交、列表、详情、个人页检查并记录结果。
- [ ] 真机验证局域网可达
  验收：确认 iOS 设备访问的是 `192.168.0.32:8002`，不再出现 `127.0.0.1`。

### 遗留问题
- [ ] `/auth/me` 会话校验
  验收：后续如需自动校验 token 有效性，再单独补启动鉴权流程。
- [ ] Feishu 兜底模式解耦
  验收：如后续仍保留飞书模式，可再把对 `AuthManager.shared` 的依赖替换为更干净的注入。

## 验收标准
- [ ] App 能启动且不因局域网配置崩溃
  验收：`xcodebuild` 构建通过，启动流程进入登录页或主 Tab。
- [ ] 登录、提交、历史、详情、个人页全部走统一后端
  验收：抓包或日志可确认请求路径为 `/auth/...` 和 `/videos/...`。
- [ ] 默认入口不再依赖飞书直连和本地 Mock 登录
  验收：不开启 `useFeishuDirect` 也能完成核心联调。

## 阻塞项
- [ ] Windows 后端需持续监听 `0.0.0.0:8002`
  说明：若后端未启动或局域网 IP 变化，iOS 联调会直接失败。
- [ ] 真机/模拟器需要与 Windows 后端处于同一局域网
  说明：跨网段或公司网络隔离会导致联调结果失真。

## 变更记录
- 2026-03-26：默认服务切换到局域网 FastAPI 后端；补齐登录、提交、列表、详情、统计、概览链路；新增维护型任务看板。
