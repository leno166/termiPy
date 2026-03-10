"""
@文件: SqliteEditor.py
@作者: 雷小鸥
@日期: 2025/10/17 10:48
@许可: MIT License
@描述: 初始化 SQLite 数据库，包含主机信息、密码登录、密钥登录三张表
@版本: Version 1.0
"""
import sqlite3
from pathlib import Path
import paramiko
import io
from .core import logger, APP_DIR


def detect_key_type(key_str: str) -> str:
    """从密钥字符串中检测类型 (RSA/ECDSA/ED25519)"""
    try:
        paramiko.RSAKey.from_private_key(io.StringIO(key_str))
        return 'RSA'
    except paramiko.ssh_exception.SSHException:
        pass

    try:
        paramiko.ECDSAKey.from_private_key(io.StringIO(key_str))
        return 'ECDSA'
    except paramiko.ssh_exception.SSHException:
        pass

    try:
        paramiko.Ed25519Key.from_private_key(io.StringIO(key_str))
        return 'ED25519'
    except paramiko.ssh_exception.SSHException:
        pass

    raise ValueError("无法识别的密钥类型")


def init_database(db_path: Path, config_module):
    # print(db_path)

    # connect
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ==========================================================================================
    # 创建一个表, 主机信息:
    # 连接方式, IP, 端口
    cursor.execute("DROP TABLE IF EXISTS host_info")
    cursor.execute(f"""
                   CREATE TABLE IF NOT EXISTS host_info
                   (
                       id     INTEGER PRIMARY KEY AUTOINCREMENT,
                       name   TEXT    NOT NULL,
                       ip     TEXT    NOT NULL,
                       port   INTEGER NOT NULL,
                       remark TEXT
                   )
                   """)
    cursor.executemany(
        "INSERT INTO host_info (name, ip, port, remark) VALUES (?, ?, ?, ?)",
        [
            row for row in config_module.HOST_INFO
            if row[1] not in ['主机地址', '...']
        ]
    )

    # ==========================================================================================
    # 创建一个表, 密码登录
    # 用户名, 密码
    cursor.execute("DROP TABLE IF EXISTS password_login")
    cursor.execute("""
                   CREATE TABLE password_login
                   (
                       id       INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       password TEXT NOT NULL,
                       remark   TEXT
                   )
                   """)

    cursor.executemany(
        "INSERT INTO password_login (username, password, remark) VALUES (?, ?, ?)",
        [(u, p, r) for u, p, r in config_module.PASSWORD_INFO]
    )

    # ==========================================================================================
    # 密钥登录 准备密钥
    key_data = []
    for username, key_v_path, passphrase, remark in config_module.KEY_INFO:
        if key_v_path in ['密钥路径', './...']:
            continue
        # 直接使用 config_module.USER_PATH 解析路径
        if isinstance(key_v_path, Path):
            key_path = key_v_path
        else:
            key_path = Path(key_v_path)

        if not key_path.is_absolute():
            key_path = config_module.USER_PATH / key_path

        key_str = key_path.read_text(encoding='utf-8')
        key_type = detect_key_type(key_str)
        key_data.append((username, key_str, passphrase, key_type, remark))

    # ==========================================================================================
    # 创建一个表: 密钥登录
    # 时间, 密钥, 密钥密码, 密钥类型
    cursor.execute("DROP TABLE IF EXISTS key_login")
    cursor.execute("""
                   CREATE TABLE key_login
                   (
                       id          INTEGER PRIMARY KEY AUTOINCREMENT,
                       username    TEXT NOT NULL,
                       private_key TEXT NOT NULL,
                       passphrase  TEXT,
                       key_type    TEXT NOT NULL,
                       remark      TEXT
                   )
                   """)

    cursor.executemany(
        "INSERT INTO key_login (username, private_key, passphrase, key_type, remark) VALUES (?, ?, ?, ?, ?)",
        key_data
    )

    conn.commit()
    conn.close()

    logger.info('✅ 数据库初始化完成: %s', db_path)
