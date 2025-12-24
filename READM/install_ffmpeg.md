# FFmpeg 安装指南

## 方式 1：使用 Chocolatey（推荐）

以管理员身份打开 PowerShell，运行：

```powershell
choco install ffmpeg -y
```

安装完成后，重启终端验证：

```powershell
ffmpeg -version
```

## 方式 2：手动安装

1. 访问 FFmpeg 官网：https://ffmpeg.org/download.html
2. 点击 Windows 图标
3. 选择 "Windows builds from gyan.dev"
4. 下载 "ffmpeg-release-essentials.zip"
5. 解压到 `C:\ffmpeg`
6. 添加到系统环境变量：
   - 打开"系统属性" → "环境变量"
   - 在"系统变量"中找到 `Path`
   - 添加 `C:\ffmpeg\bin`
7. 重启终端验证

## 方式 3：使用 Scoop

```powershell
scoop install ffmpeg
```

## 验证安装

```powershell
ffmpeg -version
```

应该看到类似输出：
```
ffmpeg version 6.0 Copyright (c) 2000-2023 the FFmpeg developers
```
