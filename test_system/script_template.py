# -*- encoding=utf8 -*-


from airtest.core.api import *
from airtest.cli.parser import cli_setup

# connect device

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=[
            "Windows:///",
    ])

report_name("请输入即将生成的报告的名字")
# script 

