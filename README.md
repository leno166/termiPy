# SSH Playbook

**SSH Playbook** is a lightweight SSH automation tool written in Python. It allows you to execute commands, transfer files, and handle interactive sessions across multiple servers using simple Python scripts – no YAML or DSL required. Think of it as a Pythonic alternative to Ansible for scenarios that need fine-grained control over interactive commands.

## ✨ Features

- 🐍 **Python-based** – Write your automation logic in pure Python, leveraging the full power of the language.
- 🔐 **Multiple authentication methods** – Support for password, private key (RSA/ECDSA/ED25519), and passphrase-protected keys.
- 🗄️ **Database-driven** – Store host and credential information in a SQLite database; easy to manage and query.
- 🤖 **Auto-connect** – Automatically tries all available credentials (keys and passwords) to connect to a host.
- 💬 **Interactive command handling** – Built‑in IPC mechanism to handle commands that require interaction (e.g., `sudo`, `passwd`, `ftp`).
- 📁 **File transfer** – Upload and download files with progress bars (via SFTP).
- 📦 **Single executable** – Can be packaged with PyInstaller into a standalone binary for easy distribution.
- 📝 **Logging** – Automatic log rotation, cleanup, and optional expiration control (useful for trial versions).
- 🌐 **Cross-platform** – Works on Windows and Linux (macOS should work as well).

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure hosts and credentials
Create a `config.py` inside the `tmp/` directory (or adjust `APP_DIR` in `src/core/helper.py`). Example:

```python
# tmp/config.py
HOST_INFO = [
    ('web-server', '192.168.1.10', 22, 'Production web server'),
    ('db-server',  '192.168.1.20', 22, 'MySQL server'),
]

PASSWORD_INFO = [
    ('root', 'mysecretpassword', 'root password'),
]

KEY_INFO = [
    ('deploy', '~/.ssh/id_rsa', None, 'deployment key'),
]
```

### 3. Write a playbook script
Create a Python script in the same directory (e.g., `deploy.py`). The system will execute all `.py` files except `config.py` and `interface.py`.

```python
# tmp/deploy.py
from src.sShell import SshSession

# app is automatically injected by the framework
session, executor, auth = app.auto_connect_from_db(name='web-server')

with session:
    # Run a simple command
    result = session.cmd('uname -a')
    for line in result:
        print(line)

    # Upload a file
    session.upload(Path('/local/path/file.txt'), '/remote/path/file.txt')

    # Download a file
    session.download(Path('/local/download'), '/remote/file.log')
```

### 4. Run the playbook
```bash
python main.py
```

## 📖 Detailed Usage

### Database auto-connection
```python
# Connect using filters (name, ip, port, remark)
session, executor, auth = app.auto_connect_from_db(name='web-server')
```

### Manual connection
```python
from src.sShell import AutoConnect, SshConnect, SshExecutor, SshSession

# Manual password login
ssh = SshConnect('192.168.1.10', 22, 'root')
ssh.password_connect('password')
executor = SshExecutor(ssh.ssh_client)
session = SshSession(executor)

with session:
    session.easy_cmd('ls -la')
```

### Interactive commands
The `SshSession` provides a context manager that handles the IPC pipe. Use `session.cmd()` to get an iterator over lines:

```python
with session:
    with session.cmd('sudo systemctl restart nginx', timeout=30) as output:
        for line in output:
            if 'password' in line:
                # Send password when prompted
                session.terminal_in.input = 'mypassword\n'
            print(line)
```

### File transfer with progress
```python
with session:
    session.upload(Path('large.zip'), '/tmp/large.zip')   # shows progress bar
    session.download(Path('backup.log'), '/var/log/app.log')
```

## 🛠 Building a Standalone Executable

Run the provided `build.py` script:

```bash
python build.py
```

This will:
1. Package the application using PyInstaller with the `main.spec` configuration.
2. Move the resulting executable (`ssh_playbook.exe` on Windows, `ssh_playbook` on Linux) into the `tmp/` directory (defined as `APP_DIR`).

After building, you can distribute the single executable along with your playbook scripts and `config.py`.

## 📁 Project Structure

```
.
├── main.py               # Entry point
├── build.py              # Packaging script
├── main.spec             # PyInstaller spec
├── src/                  # Core modules
│   ├── core/             # IPC, terminal management, logging, helpers
│   └── sShell/           # SSH connection, session, auto-connect logic
└── tmp/                  # User workspace (config.py, playbooks, logs)
    ├── config.py
    ├── deploy.py
    └── logs/             # Rotated log files
```

## 🔧 Configuration Details

- `APP_DIR` – Directory where user scripts and config reside. Default: `tmp/` in development, same directory as executable when frozen.
- `ROOT` – Project root (used for locating modules).
- Database: SQLite file `release/ssh.db` is automatically created and initialized from `config.py` on first run.

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

**Note**: Some parts of the code contain Chinese comments and logs for internal use; the core functionality is fully usable in English environments.