# 字图配置生成主程序 - 优化版
import csv
import json
import os
from PIL import Image, ImageFont, ImageDraw
from concurrent.futures import ProcessPoolExecutor

def sort_charset(file_path, chars_per_line=50):
    # 读取文件并处理字符
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        ch_list = [ch for ch in content if ch != '\n']
    
    # 去重并排序
    ch_list = sorted(set(ch_list))
    
    # 写入处理后的内容
    with open(file_path, "w", encoding="utf-8") as file:
        for i, ch in enumerate(ch_list):
            if i > 0 and i % chars_per_line == 0:
                file.write("\n")
            file.write(ch)

def process_language_task(args):
    project, langlist = args
    font_glyph = FontGlyph(project, langlist)
    font_glyph.task()

class FontGlyph:
    def __init__(self, project: str, langlist: list, totalwidth: int = 4096):
        self.project = project
        self.langlist = langlist
        self.totalwidth = totalwidth
        self.rest_y = 0   # 松弛间隔，防止行之间重叠
        self.rest_x = 0   # 横向间隔

        # 根据 project 读取 base.json，获取字体列表和基本信息
        with open(f"info/{self.project}/base.json", encoding="utf-8") as file:
            self.baseinfo = json.load(file)
        if 'psot' in self.project:
            if 'ru_RU' in langlist:
                for value in self.baseinfo.values():
                    value["shift_y"] -= 2
                    value["height"] = int(value["height"] * 4 / 5)
            if 'en_US' in langlist:
                for value in self.baseinfo.values():
                    value["shift_y"] -= 2

        self.fontlist = tuple(self.baseinfo.keys())

        # 预加载所有配置信息到内存
        self.fontinfo = {}
        self.charset = {}
        for lang in self.langlist:
            with open(f"info/{self.project}/{lang}.json", encoding="utf-8") as file:
                self.fontinfo[lang] = json.load(file)
            with open(f"charset/{lang}.txt", encoding="utf-8") as file:
                self.charset[lang] = file.read()
        
        # special 特殊字符列表（手动绘制字形）
        os.makedirs(f'special/{self.project}', exist_ok=True)
        open(f'special/{self.project}/special.txt', 'a').close()
        with open(f'special/{self.project}/special.txt', 'r', encoding='utf-8') as file:
            self.special_char_list = [line.strip() for line in file]
    
    def loadsize(self, font) -> None:
        self.fontsize = {}
        test_chars = ["A", "g", "赢"]     # 用来确定字体实际大小的测试字符
        for lang in self.langlist:
            cfg = self.fontinfo[lang][font]
            font_obj = ImageFont.truetype(f"fonts/{cfg['fontfile']}", cfg["size"])
            widths = [font_obj.getbbox(ch)[2] for ch in test_chars if font_obj.getbbox(ch)]
            heights = [font_obj.getbbox(ch)[3] for ch in test_chars if font_obj.getbbox(ch)]
            self.fontsize[lang] = (
                max(widths) if widths else 0,
                max(heights) if heights else 0,
            )
    def totalheight(self, font) -> tuple:
        height = 0
        totalcount = 0
        for lang in self.langlist:
            charcount = len(self.charset[lang].replace('\n', ''))  # 字符数
            totalcount += charcount
            char_width = self.fontinfo[lang][font].get("extra_x", 0) + self.fontsize[lang][0] + self.rest_x
            if char_width == 0:
                continue
            char_per_line = self.totalwidth // char_width
            line_height = self.fontsize[lang][1] + self.rest_y + self.fontinfo[lang][font].get("extra_y", 0)
            height += line_height * (charcount // char_per_line + 1)
        return (height, totalcount)

    def check(self, ch, fontname) -> str:
        # 特殊字符直接放行或跳过
        ch_code = hex(ord(ch))
        if ch in [' ', '　']:
            return 'yep'
        if ch == '\n':
            return 'nope'
        if self.font.getbbox(ch):
            return 'yep'
        # 尝试使用 special 字符
        if ch_code in self.special_char_list and os.path.exists(f"special/{self.project}/{fontname}/{ch_code}.png"):
            return 'yep'
        # 尝试使用 fallback
        if self.fallbackfont and self.fallbackfont.getbbox(ch):
            return 'fallback'
        return 'nope'

    def addfont(self, ch, fontname, fallback=False) -> None:
        # 获取基本信息
        font = self.fallbackfont if fallback else self.font
        cfg = self.fallbackcfg if fallback else self.cfg
        start_x = cfg.get("start_x", 0)
        start_y = cfg.get("start_y", 0)
        width = self.width
        height = self.height

        # 检查是否有单独的控制
        specials = cfg.get("special", {})
        if ch in specials:
            specialcfg = specials[ch]
            start_x += specialcfg.get("start_x", 0)
            start_y += specialcfg.get("start_y", 0)
            width += specialcfg.get("extra_x", 0)
            height += specialcfg.get("extra_y", 0)

        # 检查是否会换行
        if self.x + width > self.totalwidth:
            self.x = 0
            self.y += self.height + self.rest_y

        # 开始绘制
        ch_code = hex(ord(ch))
        if ch_code in self.special_char_list and os.path.exists(f"special/{self.project}/{fontname}/{ch_code}.png"):
            symbol = Image.open(f"special/{self.project}/{fontname}/{ch_code}.png")
            resize_factor = int(cfg.get("special_factor", max(round(cfg["size"] / 16.0), 1)))
            special_y = int(cfg.get("special_y", 0))
            special_x = int(cfg.get("special_x", 0))
            symbol = symbol.resize((resize_factor * symbol.size[0], resize_factor * symbol.size[1]), Image.Resampling.NEAREST)
            self.glyph.paste(symbol, (self.x + start_x + special_x, self.y + start_y + special_y))
        else:
            self.drawtool.text((self.x + start_x, self.y + start_y),
                                ch, fill=(255, 255), font=font)

        # 添加 csv 数据
        if "dttvl" in self.project:
            self.fnt.append(
                f"char id={ord(ch)} x={self.x} y={self.y} width={width} height={height} xoffset=0 yoffset=0 xadvance={self.width} page=0 chnl=15\n"
            )
        elif 'psot' in self.project:
            self.csv.append((ord(ch), self.x, self.y, width, height, 0, 0, width, height))
        else:
            bbox = font.getbbox(ch)
            advance_width = bbox[2] - bbox[0] if bbox else width
            self.csv.append((ord(ch), self.x, self.y, width, height, advance_width, 0))

        # 移动画笔，准备下一次绘制
        self.x += width + self.rest_x
    
    def process_font(self, fontname):
        # 创建新字图
        self.loadsize(fontname)
        total_height, total_count = self.totalheight(fontname)
        self.glyph = Image.new('LA', (self.totalwidth, total_height), (0, 0))
        self.drawtool = ImageDraw.Draw(self.glyph)
        self.x = 0
        self.prev_y = self.y = 0
        self.csv = [tuple(self.baseinfo[fontname].values())]
        self.fnt = []

        # 针对每种语言
        for lang in self.langlist:
            self.process_language(lang, fontname)

        # 全部结束后，保存图片和 csv 到文件
        ind = -len(self.langlist) if len(self.langlist) <= 1 else -2
        output_dir = f"dist/{self.project}/{self.langlist[ind]}"
        os.makedirs(output_dir, exist_ok=True)
        self.glyph.save(f"{output_dir}/{fontname}.png")

        if "dttvl" in self.project:
            output_fnt = f"{output_dir}/{fontname}.fnt"
            with open(output_fnt, "w", encoding="utf-8") as file:
                file.writelines(self.fnt)
        else:
            if 'psot' in self.project:
                output_csv = f"{output_dir}/{fontname}.csv"
            else:
                output_csv = f"{output_dir}/glyphs_{fontname}.csv"
            with open(output_csv, "w", encoding="utf-8", newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerows(self.csv)
    def process_language(self, lang, fontname):
        # 加载配置文件和字符集
        self.cfg = self.fontinfo[lang][fontname]
        self.width, self.height = self.fontsize[lang]
        self.width += self.cfg.get("extra_x", 0)
        self.height += self.cfg.get("extra_y", 0)
        self.font = ImageFont.truetype(f"fonts/{self.cfg['fontfile']}", self.cfg["size"])
        if lang == "en_US":
            self.encfg = self.cfg
            self.enfont = self.font
        self.fallbackcfg = self.cfg.get("fallback")
        if self.fallbackcfg:
            self.fallbackfont = ImageFont.truetype(f"fonts/{self.fallbackcfg['fontfile']}", self.fallbackcfg["size"])
        else:
            self.fallbackfont = None

        if not self.fnt:
            total_height, total_count = self.totalheight(fontname)
            self.fnt.extend([
                f'info face="{fontname}" size={self.cfg["size"]} bold=0 italic=0 charset="" unicode=1 stretch=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0 outline=0\n',
                f'common lineHeight={self.height} base=10 scaleW={self.totalwidth} scaleH={total_height} pages=1 packed=0 alphaChnl=0 redChnl=4 greenChnl=4 blueChnl=4\n',
                f'page id=0 file="{fontname}.png"\n',
                f'chars count={total_count}\n'
            ])

        # 开始逐一绘制字符
        self.errorcount = 0
        for ch in self.charset[lang]:
            # 检查字符是否可用
            status = self.check(ch, fontname)  # 返回值有 yep, nope, fallback
            if status == 'yep':
                self.addfont(ch, fontname)
            elif status == 'fallback':
                self.addfont(ch, fontname, fallback=True)
            elif status == 'nope':
                continue
        # 完毕后调整坐标位
        self.x = 0
        self.y += self.height + self.rest_y
        # 处理透明度
        pixel = self.glyph.load()
        threshold = max(self.cfg.get("threshold", 0), 0)
        for x in range(self.totalwidth):
            for y in range(self.prev_y, self.y):
                alpha = 255 if pixel[x, y][1] > threshold else 0
                pixel[x, y] = (pixel[x, y][0], alpha)

    def task(self) -> None:
        args_list = [(self.project, self.langlist, self.totalwidth, fontname) for fontname in self.fontlist]
        with ProcessPoolExecutor() as executor:
            executor.map(process_font_wrapper, args_list)

def process_font_wrapper(args):
    project, langlist, totalwidth, fontname = args
    font_glyph = FontGlyph(project, langlist, totalwidth)
    font_glyph.process_font(fontname)