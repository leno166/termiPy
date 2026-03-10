"""
@文件: config.py
@作者: 雷小鸥
@日期: 2026/3/10 12:53
@许可: MIT License
@描述: 
@版本: Version 1.0
"""

# 主机信息： (name, ip, port, remark)
HOST_INFO = [
    ('主机名称', '主机地址', '端口', '备注',),
    ('...', '...', '...', '...',),
]

# 密码登录信息： (username, password, remark)
PASSWORD_INFO = [
    ('用户名', '密码', '备注',),
    ('...', '...', '...'),
]

# 密钥登录信息： (username, key_path, passphrase, remark)
# key_path = USER_PATH / ...
KEY_INFO = [
    ('用户名', '密钥路径', '密钥口令', '备注',),
    ('...', './...', '...', '...',),
]
