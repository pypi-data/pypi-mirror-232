import platform
import datetime
import socket
import uuid
import os


def get_mac_address() -> str:
    """
    获取mac地址
    """
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)])


def platform_info() -> dict:
    """
    获取当前环境的信息
    """
    platform_processor = platform.processor()
    platform_architecture = platform.architecture()

    hostname = socket.gethostname()

    res = dict()

    res["node"] = platform.node()  # 计算机的网络名称/主机名

    res["local_datetime"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    res["platform"] = platform.platform()  # 操作系统名称及版本号
    res["system"] = platform.system()  # 操作系统名称
    res["version"] = platform.version()  # 操作系统详细版本
    res["release"] = platform.release()  # 操作系统大版本

    res["platform_machine"] = platform.machine()  # 计算机类型/平台架构
    res["platform_processor"] = platform_processor  # 计算机处理器信息/处理器名称
    res["platform_architecture"] = platform_architecture  # 操作系统的位数

    res["hostname"] = hostname
    res["mac"] = get_mac_address()

    res["cpu_count"] = os.cpu_count()

    import locale
    res["encoding"] = locale.getpreferredencoding()  # 获取系统编码类型

    return res
