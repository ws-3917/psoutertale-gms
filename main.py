import os
import sys
from concurrent.futures import ProcessPoolExecutor
from tools import FontGlyph, sort_charset  # 请确保正确导入 FontGlyph 类

def process_language_task(args):
    project, langlist = args
    font_glyph = FontGlyph(project, langlist)
    font_glyph.task()

if __name__ == '__main__':
    project = 'psot'
    sys.path.append(os.getcwd())
    os.makedirs(f"dist/{project}", exist_ok=True)
    
    language_tasks = [
        ['en_US', 'symbols1'],
        ['JPlatin', 'JPsymbols1', 'ja_JP', 'JPsymbols2'],
        ['ru_RU', 'symbols1'],
        ['en_US', 'symbols1', 'zh_CN', 'symbols2'],
        ['en_US', 'symbols1', 'zh_TW', 'symbols2']
    ]
    
    task_args = [(project, langlist) for langlist in language_tasks]
    all_languages = set(lang for langs in language_tasks for lang in langs)
    
    # 在并行处理之前预处理字符集文件
    for lang in all_languages:
        sort_charset(f"charset/{lang}.txt")
    
    with ProcessPoolExecutor() as executor:
        executor.map(process_language_task, task_args)
    
    for dirname in ['cs_CZ', 'es_ES', 'tr_TR']:
        output_dir = f"dist/{project}/{dirname}"
        if os.path.exists(output_dir):
            os.system(f"bash -c 'rm -rf {output_dir}'")
        os.makedirs(output_dir, exist_ok=True)
        os.system(f"bash -c 'cp -rf dist/{project}/en_US/* {output_dir}'")
    
    print("--- 成功生成所有字图！")