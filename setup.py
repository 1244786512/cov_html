# -*- coding: utf-8 -*-
import subprocess

# author = wxf

if __name__ == "__main__":
    # 执行 shell 命令
    command = 'pyinstaller --add-data "static:static" --add-data "templates:templates" --add-data "version:."  --onefile main.py -n cov-html'
    subprocess.run(command, shell=True, check=True)
