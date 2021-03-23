# -*- encoding=utf8 -*-


from airtest.core.api import *
from airtest.cli.parser import cli_setup

# connect device

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///",
    ])
# 若要修改即将生成的报告的名字在此处修改
report_name("新脚本")
# script 

