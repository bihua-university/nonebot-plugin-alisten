<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://nonebot.dev/"><img src="https://nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# NoneBot Plugin Alisten

_✨ NoneBot 听歌房插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/bihua-university/nonebot-plugin-alisten/main/LICENSE">
    <img src="https://img.shields.io/github/license/bihua-university/nonebot-plugin-alisten.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-alisten">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-alisten.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="python">
</p>

## 安装

使用 `nb-cli` 安装：

```bash
nb plugin install nonebot-plugin-alisten
```

使用 `pip` 安装：

```bash
pip install nonebot-plugin-alisten
```

使用 `uv` 安装：

```bash
uv add nonebot-plugin-alisten
```

## 功能特性

- 🎵 支持多音乐平台：网易云音乐、QQ音乐、Bilibili
- 🎯 支持多种搜索方式：歌曲名、BV号、特定平台歌曲名
- 🏠 支持多房间配置，每个群组独立管理
- 🔒 支持房间密码保护
- 👥 用户友好的点歌体验

## 命令

待插件启动完成后，发送 `/music` 或 `/点歌` 可开始点歌。

### 点歌命令

| 功能         | 命令                       | 权限   | 说明                               |
| ------------ | -------------------------- | ------ | ---------------------------------- |
| 普通点歌     | `/music <歌曲名>`          | 所有人 | 使用歌曲名搜索并点歌（默认网易云） |
| 中文点歌     | `/点歌 <歌曲名>`           | 所有人 | 中文别名，功能同上                 |
| 指定平台点歌 | `/music <平台>:<歌曲信息>` | 所有人 | 指定音乐平台进行点歌               |
| B站视频点歌  | `/music <BV号>`            | 所有人 | 使用Bilibili BV号点歌              |

**支持的音乐平台：**

- `wy`: 网易云音乐
- `qq`: QQ音乐
- `db`: Bilibili

**使用示例：**

```text
/music Sagitta luminis          # 搜索歌曲名
/点歌 青花瓷                     # 使用中文别名
/music BV1Xx411c7md            # 使用B站BV号
/music qq:青花瓷                # 指定QQ音乐搜索
/music wy:青花瓷                # 指定网易云搜索
```

### 配置命令

| 功能     | 命令                                                   | 权限     | 说明                   |
| -------- | ------------------------------------------------------ | -------- | ---------------------- |
| 设置配置 | `/alisten config set <服务器地址> <房间ID> [房间密码]` | 超级用户 | 配置alisten服务器信息  |
| 查看配置 | `/alisten config show`                                 | 超级用户 | 查看当前群组的配置信息 |
| 删除配置 | `/alisten config delete`                               | 超级用户 | 删除当前群组的配置     |

**配置示例：**

```text
/alisten config set http://localhost:8080 room123          # 无密码房间
/alisten config set http://localhost:8080 room123 password # 有密码房间
/alisten config show                                       # 查看配置
/alisten config delete                                     # 删除配置
```

## 使用前准备

1. **部署 alisten 服务**

   需要先部署 alisten 服务端，具体部署方法请参考 [alisten 官方文档](https://github.com/bihua-university/alisten)。

2. **配置 alisten 服务**

   在使用前，需要使用超级用户权限为每个群组配置 alisten 服务信息：

   ```text
   /alisten config set <alisten服务器地址> <房间ID> [房间密码]
   ```

3. **开始点歌**

   配置完成后，群成员即可使用点歌命令享受音乐。

## 依赖说明

本插件依赖以下组件：

- [nonebot2](https://github.com/nonebot/nonebot2) >= 2.4.3
- [nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna) >= 0.59.4
- [nonebot-plugin-orm](https://github.com/nonebot/plugin-orm) >= 0.8.2
- [nonebot-plugin-user](https://github.com/he0119/nonebot-plugin-user) >= 0.5.1

## 开发

### 环境要求

- Python 3.12+
- NoneBot 2.4.3+

### 本地开发

1. 克隆仓库

   ```bash
   git clone https://github.com/bihua-university/nonebot-plugin-alisten.git
   cd nonebot-plugin-alisten
   ```

2. 安装依赖

   ```bash
   uv sync
   ```

3. 运行测试

   ```bash
   uv run poe test
   ```

## 许可证

本项目使用 [MIT](LICENSE) 许可证开源。

## 鸣谢

- [Alisten](https://github.com/bihua-university/alisten) - 提供音乐服务支持
- [NoneBot2](https://github.com/nonebot/nonebot2) - 优秀的 Python 异步聊天机器人框架

感谢以下开发者作出的贡献：

[![contributors](https://contrib.rocks/image?repo=bihua-university/nonebot-plugin-alisten)](https://github.com/bihua-university/nonebot-plugin-alisten/graphs/contributors)
