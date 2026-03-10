"""
@文件: tmp.script
@作者: 雷小鸥
@日期: 2026/3/10 09:22
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interface import app, SshSession
from pathlib import Path

session: SshSession
session, *_ = app.auto_connect_from_db()

with session:
    # session.upload(Path(r'D:\User\Documents\pyProjects\terminal\release\ssh.db'), '/opt/other/test.db')

    # print([fn for fn in dir(session) if not fn.startswith('_')])

    # ping_success = session.ping('172.31.254.38')
    # print(ping_success)

    # with session.cmd('ls -l') as out:
    #     for line in out:
    #         print(line)

    session.easy_cmd('cd /')

    session.easy_cmd('ls')

    session.easy_cmd('cd var')

    session.easy_cmd('ls')

    session.easy_cmd('cd log')

    session.easy_cmd('ls | grep sys')

    session.download(Path('./syslog'), 'syslog')

    # session.download(Path(__file__).parent / 'logs.tar.gz', '/opt/other/logs.tar.gz')

session.close()
