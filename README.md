# SSH Playbook 自动化执行器

一个专为**测试人员**设计的 SSH 自动化工具，旨在以**极低的认知负担**快速执行临时任务。  
无论你是需要重复运行一组 Shell 命令，还是希望用 Python 编写复杂的自动化逻辑，本项目都能让你在**一分钟内**上手并投入工作。

---

## ✨ 核心优势

- **超快部署**：下载即用，无需安装 Python 或依赖库。
- **两种模式，自由选择**：
  - **Easy 模式**：直接写 Shell 脚本，支持 `#upload` / `#download` 指令，零学习成本。
  - **普通模式**：在 VSCode 中打开项目文件夹，利用 `interface.py` 提供的智能提示，像写普通 Python 一样编写剧本，按 `Ctrl+Shift+B` 一键执行。
- **针对测试场景优化**：临时性、低复用性、快速验证——不引入复杂的幂等性或状态管理，只做你最需要的“机械任务”自动化。
- **文件传输内置**：在脚本中随时上传/下载文件，无需切换工具。

---

## 🚀 快速开始（1 分钟上手）

### 1. 下载可执行文件
从 [Releases](https://github.com/your-repo/releases) 页面下载对应系统的压缩包，解压后得到：
- `ssh_playbook`（Linux/macOS）或 `ssh_playbook.exe`（Windows）
- `config.py`（配置文件模板）
- `interface.py`（用于普通模式的类型提示）

将可执行文件所在的目录添加到系统 `PATH` 中，或直接在目录中打开终端。

### 2. 配置主机信息
编辑 `config.py`，填入你的 SSH 服务器信息：
```python
# 主机列表：名称，IP，端口，备注
HOST_INFO = [
    ('测试服务器1', '192.168.1.10', 22, ''),
    ('测试服务器2', '192.168.1.11', 22, ''),
]

# 密码登录：用户名，密码，备注
PASSWORD_INFO = [
    ('root', 'your_password', ''),
]

# 密钥登录：用户名，密钥路径（相对于 USER_PATH 或绝对路径），密码短语，备注
KEY_INFO = [
    ('root', 'id_rsa', None, ''),
]
```

**注意**：`USER_PATH` 默认指向 `可执行文件所在目录/.ssh`，可将密钥文件放在该目录下。

### 3. 运行你的第一个任务

#### 🟢 Easy 模式：直接写 Shell 脚本
创建一个 Shell 脚本 `my_task.sh`：
```bash
#!/bin/bash
# 查看系统信息
uname -a

# 上传本地文件到远程
#upload ./local.txt /tmp/remote.txt

# 执行远程命令
df -h

# 下载远程文件到本地
#download /var/log/syslog ./syslog.log
```

然后执行：
```bash
ssh_playbook --easy my_task.sh
```

#### 🔵 普通模式：用 VSCode 写 Python 剧本
1. 用 VSCode 打开项目文件夹（包含 `config.py`、`interface.py`）。
2. 新建一个 Python 文件 `test.py`，内容如下：
   ```python
   from interface import SshSession, app

   # 自动连接主机（支持按名称/IP筛选）
   with app.auto_connect_from_db(name='测试服务器1') as session:
       # 执行命令
       result = session.cmd('ls -l /tmp')
       for line in result:
           print(line)

       # 上传文件
       session.upload(Path('./local.txt'), '/tmp/remote.txt')

       # 下载文件
       session.download(Path('./syslog.log'), '/var/log/syslog')

       # 使用 easy_cmd 直接运行多行命令
       session.easy_cmd('''
           echo "Hello"
           pwd
       ''')
   ```
3. 按 `Ctrl+Shift+B`（或运行 Tasks: Run Build Task）即可执行。  
   （项目已预置 `.vscode/tasks.json`，无需额外配置）

---

## 📖 详细使用指南

### Easy 模式详解

#### 基本语法
- 脚本就是普通的 Shell 脚本，每一行命令会被依次执行。
- 支持 `#` 开头的特殊指令：
  - `#upload <本地路径> <远程路径>`：将本地文件上传到远程主机。
  - `#download <远程路径> <本地路径>`：将远程文件下载到本地。
- 其他以 `#` 开头的行视为注释，不会执行。

#### 示例
```bash
#!/bin/bash
# 更新软件包
apt update
apt upgrade -y

# 上传新的配置文件
#upload ./nginx.conf /etc/nginx/nginx.conf

# 重启服务
systemctl restart nginx

# 下载日志
#download /var/log/nginx/access.log ./access.log
```

#### 指定主机
默认会尝试连接数据库中的所有主机，直到成功。  
你也可以用 `--host` 指定主机名称或 IP（部分匹配）：
```bash
ssh_playbook --easy my_task.sh --host 192.168.1.10
```

---

### 普通模式详解

#### 项目结构
```
your-project/
├── config.py          # SSH 连接配置
├── interface.py       # 类型提示文件（VSCode 自动补全）
├── .vscode/
│   └── tasks.json     # 一键运行配置
└── your_scripts/      # （可选）存放你的 Python 剧本
```

#### 编写 Python 剧本
在项目根目录下创建任意 `.py` 文件，从 `interface` 导入所需对象：
```python
from pathlib import Path
from interface import SshSession, app

def main():
    # 连接主机（支持 name/ip/port 筛选）
    session, executor, auth_info = app.auto_connect_from_db(ip='192.168.1.10')
    with session:
        # 执行命令并获取输出（生成器）
        for line in session.cmd('tail -f /var/log/app.log', timeout=10):
            if 'ERROR' in line:
                print(f'发现错误: {line}')
                break

        # 上传文件
        session.upload(Path('./data.txt'), '/tmp/data.txt')

        # 使用 easy_cmd 直接打印输出
        session.easy_cmd('df -h')

if __name__ == '__main__':
    main()
```

#### 一键运行
- 在 VSCode 中打开你的剧本文件，按 `Ctrl+Shift+B` 即可运行。
- 或者打开命令面板（`Ctrl+Shift+P`），输入 `Run Build Task`。

#### 高级用法
- 利用 Python 的完整生态：你可以引入 `requests`、`pandas` 等库，与测试数据交互。
- 多主机并行：使用 `threading` 或 `concurrent.futures` 同时对多台主机执行任务。
- 记录结果到数据库：项目内置 SQLite，你可以直接读写自己的数据表。

---

## ⚙️ 配置文件说明

`config.py` 控制 SSH 连接信息，格式如下：

```python
# 主机信息（必填）
HOST_INFO = [
    ('别名', 'IP地址', 端口, '备注'),
    ('server1', '192.168.1.10', 22, '测试机1'),
]

# 密码登录信息（可选）
PASSWORD_INFO = [
    ('用户名', '密码', '备注'),
    ('root', '123456', ''),
]

# 密钥登录信息（可选）
KEY_INFO = [
    ('用户名', '密钥路径', '密码短语', '备注'),
    ('root', 'id_rsa', None, ''),
]
```

**说明**：
- 密钥路径可以是绝对路径，也可以是相对于 `USER_PATH`（即可执行文件所在目录下的 `.ssh` 文件夹）的相对路径。
- 程序启动时会自动创建数据库 `release/ssh.db`，并导入上述信息。
- 如果同时配置了密码和密钥，程序会先尝试密钥，再尝试密码，直到成功连接。

---

## 🆚 为什么比 MobaXterm 录制更适合测试人员？

| 需求               | MobaXterm 录制 Shell          | 本工具（Easy 模式）                     |
|--------------------|-------------------------------|------------------------------------------|
| **临时性任务**      | 录制简单，但修改麻烦           | 直接修改 Shell 脚本，瞬间完成             |
| **低复用性**        | 宏文件难以复用                 | 脚本可复制、版本控制、稍改即用             |
| **快速验证**        | 需打开 GUI、加载会话、点击录制  | 一条命令 + 脚本，秒级执行                   |
| **认知负担**        | 录制直观，但修改困难增加思考   | 就是 Shell 脚本，零学习成本                |
| **文件传输集成**    | 需额外用 SFTP 标签，无法自动化 | 脚本内直接 #upload/#download，全自动化      |
| **跨平台**          | 仅 Windows                    | Windows/Linux/macOS 全支持                  |

---

## ❓ 常见问题

### Q1：需要安装 Python 吗？
不需要！可执行文件已打包所有依赖，下载即可运行。

### Q2：如何查看执行日志？
日志默认保存在 `可执行文件目录/logs/app YYYY年MM月DD日 HH时MM分SS秒.log`，记录了所有连接和命令执行信息。

### Q3：Easy 模式下如何实现循环或条件判断？
Easy 模式仅支持纯粹的 Shell 脚本，因此可以使用 Shell 本身的循环和条件语句。例如：
```bash
for i in {1..5}; do
    echo "count $i"
done
```

如果逻辑过于复杂，建议使用普通模式（Python 剧本）。

### Q4：普通模式下如何调试？
你可以在剧本中加入 `print()` 输出，或在 VSCode 中配置 Python 调试器（需安装 Python 扩展）。项目根目录的 `.vscode/launch.json` 已预置调试配置。

### Q5：支持密钥密码短语吗？
支持。在 `KEY_INFO` 中填写密码短语即可（`None` 表示无密码）。

### Q6：如何处理连接失败？
程序会依次尝试所有主机和认证方式，直到成功。如果全部失败，将抛出异常并终止。你可以在普通模式中用 `try...except` 捕获异常，自定义处理。

---

## 📦 构建自己的版本

如果你想修改或扩展功能，可以从源码构建：

```bash
git clone https://github.com/your-repo/ssh-playbook.git
cd ssh-playbook
pip install -r requirements.txt
python build.py    # 生成可执行文件（使用 PyInstaller）
```

构建后的可执行文件位于 `dist/` 目录下。

---

## 📄 许可证

MIT License © 2026 雷小鸥

---

**现在，去让那些重复的机械命令见鬼吧！** 🚀