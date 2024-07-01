import os, tools, sys
def main():
    project = 'psot'    # psot 或 tsus
    sys.path.append(os.getcwd())
    tools.bashcmd(f"mkdir -p dist/{project}")
    tools.FontGlyph(project, ['en_US', 'symbols']).task()
    tools.FontGlyph(project, ['en_US', 'symbols', "zh_CN"]).task()
    tools.FontGlyph(project, ['en_US', 'symbols', "zh_TW"]).task()
    tools.FontGlyph(project, ['en_US', 'symbols', "ja_JP"]).task()
    print("--- 成功生成所有字图！")

if __name__ == '__main__':
    main()