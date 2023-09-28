import os
import shutil
from pathlib import Path

from setuptools.command.install import install


class CustomInstallCommand(install):
    def run(self):
        # 在安装之前创建配置文件
        create_config_if_not_exists()
        super().run()


def create_config_if_not_exists():
    user_home = str(Path.home())

    user_config_dir = os.path.join(user_home, ".zcx")

    if not os.path.exists(user_config_dir):
        os.makedirs(user_config_dir)

    user_config_file = os.path.join(user_config_dir, "config.ini")
    user_log_config_file = os.path.join(user_config_dir, "log.ini")

    if not os.path.exists(user_config_file):
        default_config_file = os.path.join("conf", "config.ini.sample")
        shutil.copy(default_config_file, user_config_file)

    if not os.path.exists(user_log_config_file):
        default_log_config_file = os.path.join("conf", "log.ini.sample")
        shutil.copy(default_log_config_file, user_log_config_file)
