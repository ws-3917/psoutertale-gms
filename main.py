import os, sys
from tools import *
def main():
    project = 'psot-low'    # 项目名，如果命名为psot则生成outertale特定格式，否则为gms通用格式
    sys.path.append(os.getcwd())
    bashcmd(f"mkdir -p dist/{project}")
    FontGlyph(project, ['en_US', 'symbols1']).task()
    FontGlyph(project, ['ru_RU', 'symbols1']).task()
    FontGlyph(project, ['tr_TR', 'symbols1']).task()
    FontGlyph(project, ['en_US', 'symbols1', "ja_JP", 'symbols2']).task()
    FontGlyph(project, ['en_US', 'symbols1', "zh_CN", 'symbols2']).task()
    FontGlyph(project, ['en_US', 'symbols1', "zh_TW", 'symbols2']).task()
    print("--- 成功生成所有字图！")

if __name__ == '__main__':
    main()