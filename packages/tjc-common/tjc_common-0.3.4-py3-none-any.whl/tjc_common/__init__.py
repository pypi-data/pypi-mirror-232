import os
from os.path import expanduser
import platform
import time
from configparser import ConfigParser


def get_timespan(_t0):
    t1 = time.time()
    span = t1 - _t0
    return span


_t0 = time.time()

from tyjuliasetup import use_sysimage, use_backend  # NOQA: E402


def read_config():
    sysimage_path = ''
    need_use_sysimage = False
    need_print_time = True
    tjc_backend = ''  # 如'jnumpy'

    conn = ConfigParser()

    # Online
    ty_path = os.getenv("TONGYUAN_PATH")
    file_path = ty_path + "/syslab-python/tjc_common.ini"
    
    # 桌面版，该段代码确保桌面版直接启动julia能正常使用python调julia功能
    # if platform.system().lower() == 'windows':
    #     file_path = "C:/Users/Public/TongYuan/syslab-python/tjc_common.ini"
    # else:
    #     file_path = expanduser("~/TongYuan/syslab-python/tjc_common.ini")

    if os.path.exists(file_path):
        conn.read(file_path, encoding='utf-8')
        if conn.has_option('Config', 'sysimage_path'):
            sysimage_path = conn.get('Config', 'sysimage_path')

        if conn.has_option('Config', 'need_use_sysimage'):
            need_use_sysimage = conn.get(
                'Config', 'need_use_sysimage') == 'True'

        if conn.has_option('Config', 'need_print_time'):
            need_print_time = conn.get('Config', 'need_print_time') == 'True'

        if conn.has_option('Config', 'tjc_backend'):
            tjc_backend = conn.get('Config', 'tjc_backend')

    return sysimage_path, need_use_sysimage, need_print_time, tjc_backend

# 使用映像初始化


def init_with_sysimage():
    # 读配置文件
    sysimage_path, need_use_sysimage, need_print_time, tjc_backend = read_config()

    if tjc_backend != '':
        use_backend(tjc_backend)

    # Online
    # if sysimage_path == '':
    #     ty_path = os.getenv("TONGYUAN_PATH")
    #     if platform.system().lower() == 'windows':
    #         sysimage_path = ty_path + "/.julia/environments/v1.7/JuliaSysimage.dll"
    #     elif platform.system().lower() == 'linux':
    #         sysimage_path = ty_path + "/.julia/environments/v1.7/JuliaSysimage.so"

    # 桌面版，julia1.7升级julia1.9，julia1.9不存在镜像，故该段代码注释
    # if sysimage_path == '':
    #     if platform.system().lower() == 'windows':
    #         sysimage_path = "C:/Users/Public/TongYuan/.julia/environments/v1.7/JuliaSysimage.dll"
    #     else:
    #         sysimage_path = expanduser("~/TongYuan/.julia/environments/v1.7/JuliaSysimage.so")

    # if need_use_sysimage:
    #     if os.path.exists(sysimage_path):
    #         use_sysimage(sysimage_path)
    #     else:
    #         print("%s 文件不存在！" % sysimage_path)

    import tyjuliacall  # NOQA: E402
    if need_print_time:
        print(f"导入tyjuliacall: {get_timespan(_t0):.2f} s")


# 初始化
init_with_sysimage()
