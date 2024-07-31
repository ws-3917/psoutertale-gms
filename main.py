import os, tools, sys
def main():
    project = 'psot'    # psot 或 tsus
    sys.path.append(os.getcwd())
    tools.bashcmd(f"mkdir -p dist/{project}")
    
    # tools.FontGlyph(project, ['en_US', 'symbols1']).task()
    # tools.FontGlyph(project, ['ru_RU', 'symbols1']).task()
    # tools.FontGlyph(project, ['tr_TR', 'symbols1']).task()
    # tools.FontGlyph(project, ['en_US', 'symbols1', "ja_JP", 'symbols2']).task()
    tools.FontGlyph(project, ['en_US', 'symbols1', "zh_CN", 'symbols2']).task()
    # tools.FontGlyph(project, ['en_US', 'symbols1', "zh_TW", 'symbols2']).task()
    print("--- 成功生成所有字图！")

if __name__ == '__main__':
    main()