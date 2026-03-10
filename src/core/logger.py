"""
@文件: logger.py
@作者: 雷小鸥
@日期: 2025/12/9 11:09
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import logging
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

from .helper import ROOT, APP_DIR

LOG_DIR_PATH = APP_DIR / 'logs'
LOG_DIR_PATH.mkdir(exist_ok=True)

LOG_NAME = 'app'

# 定义时间格式字符串
LOG_TIMESTAMP_FORMAT = '%Y年%m月%d日 %H时%M分%S秒'
# 生成当前时间戳字符串
LOG_TIMESTAMP_STR = datetime.now().strftime(LOG_TIMESTAMP_FORMAT)

# 注意：这里先只定义路径，不要急着创建 FileHandler，等 cleanup 之后再创建更安全
LOG_FILE_PATH = LOG_DIR_PATH / f'{LOG_NAME} {LOG_TIMESTAMP_STR}.log'

logger = logging.getLogger(LOG_NAME)

# ================= 配置区域 =================
# ⚠️ 截止日期设置：2026年11月11日
# 格式：YYYY-MM-DD
EXPIRATION_DATE_STR = "2026-06-15"
EXPIRATION_DATE = datetime.strptime(EXPIRATION_DATE_STR, "%Y-%m-%d").date()


# ===========================================

def check_expiration():
    """
    检查当前日期是否超过授权截止日期。
    如果过期，打印错误信息并终止程序。
    """
    today = datetime.now().date()

    if today > EXPIRATION_DATE:
        error_msg = f"""
╔══════════════════════════════════════════════════════════╗
║  ⛔ 系统已停止服务 (System Expired)                       ║
╠══════════════════════════════════════════════════════════╣
║  当前日期：{today}                                        ║
║  截止日期：{EXPIRATION_DATE}                              ║
║                                                          ║
║  您的授权/试用期已于 {EXPIRATION_DATE_STR} 结束。           ║
║  请联系管理员更新版本或获取新的授权码。                     ║
╚══════════════════════════════════════════════════════════╝
        """
        # 尝试记录到标准输出（因为 logger 可能还没完全初始化）
        print(error_msg)

        # 如果 logger 已经部分可用，也可以尝试记录一条 critical 日志
        if logger.handlers:
            logger.critical("System expired. Terminating.")

        # 强制退出程序，返回码 1 表示异常退出
        sys.exit(1)

    # 可选：在到期前 N 天发出警告 (例如提前 7 天)
    warning_threshold = EXPIRATION_DATE - timedelta(days=7)
    if today >= warning_threshold and today <= EXPIRATION_DATE:
        days_left = (EXPIRATION_DATE - today).days
        warning_msg = f"⚠️  警告：系统将在 {days_left} 天后过期 ({EXPIRATION_DATE})，请尽快联系管理员！"
        print(warning_msg)
        # 注意：此时 logger 可能还没 addHandler，所以先 print，等 setup_logger 完成后会自动记录


def is_old(path: Path, days=30) -> bool:
    """
    判断日志文件是否过期
    """
    # 构造正则表达式匹配文件名中的日期部分
    # 假设文件名格式固定为: "app 2023年01月01日 ..."
    pattern = rf'^{re.escape(LOG_NAME)}\s+(\d{{4}}年\d{{2}}月\d{{2}}日)'
    match = re.search(pattern, path.name)

    if not match:
        return False

    file_date_str = match.group(1)

    try:
        # 【核心修复】使用 strptime 将字符串解析为 datetime 对象
        # 原代码错误地使用了 strftime
        parsed_dt = datetime.strptime(file_date_str, "%Y年%m月%d日")
        file_date = parsed_dt.date()

        cutoff_date = datetime.now().date() - timedelta(days=days)
        return file_date < cutoff_date
    except ValueError:
        # 如果日期格式不合法（例如 2023年13月01日），视为不过期或不处理
        return False


def cleanup_old_logs(days=30):
    """
    清理旧日志文件
    """
    # 匹配格式：app *.log
    # 注意：glob 模式不需要正则，直接用通配符
    for log_file in LOG_DIR_PATH.glob(f'{LOG_NAME} *.log'):
        # 避免删除当前正在写入的文件（虽然时间上通常不会命中，但加个保护更稳妥）
        if log_file == LOG_FILE_PATH:
            continue

        if is_old(log_file, days=days):
            try:
                log_file.unlink()
                # 注意：此时 logger 可能还没完全配置好 handler，
                # 如果 setup_logger 还没运行完，这里打印可能会丢失或报错。
                # 最安全的做法是在 setup_logger 配置完 handler 后再调用 cleanup，
                # 或者这里只用 print。
                print(f'Deleted old log file: {log_file}')
            except Exception as e:
                print(f"Failed to delete {log_file}: {e}")


def setup_logger():
    check_expiration()

    # 如果已经配置过 handler，直接返回
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 【优化顺序】先清理旧日志，再创建新的文件句柄
    # 这样避免清理逻辑影响到刚刚初始化的变量，也避免在 handler 未就绪时记录日志
    cleanup_old_logs(days=30)

    # 定义格式化器
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-1s | %(filename)s:%(lineno)4d - %(funcName)s() ->| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建文件句柄 (此时 LOG_FILE_PATH 已确定且未被删除)
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 创建控制台句柄
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)  # 建议控制台也加上格式，否则很难看

    # 添加句柄
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 记录初始化信息
    logger.info(f"Logger initialized. Writing to: {LOG_FILE_PATH}")

    return logger


# 模块加载时自动初始化
setup_logger()
