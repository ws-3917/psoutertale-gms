# 字图配置生成主程序 - 0616重置版
import csv, json, os
from PIL import Image, ImageFont, ImageDraw
from termcolor import colored
def bashcmd(cmd):
    os.system(f"bash -c \"{cmd}\"")
# 字图类，每个字体独立
class FontGlyph:
    # 所属项目（用来查询路径），语言列表，字图宽度
    def __init__(self, project : str, langlist : list, totalwidth:int = 4096):
        self.project = project
        self.langlist = langlist
        self.totalwidth = totalwidth
        self.rest_y = 3   # 松弛间隔，防止行之间重叠
        self.rest_x = 3   # 横向间隔
        # 根据project读取对应路径下的base,获取字体列表和基本信息
        with open(f"info/{self.project}/base.json", encoding="utf-8") as file:
            self.baseinfo = dict(json.loads(file.read()))
        self.fontlist = tuple(self.baseinfo.keys())

        # 预加载所有配置信息到内存
        self.fontinfo = dict()
        self.charset = dict()
        for lang in self.langlist:
            with open(f"info/{self.project}/{lang}.json", encoding="utf-8") as file:
                self.fontinfo[lang] = dict(json.loads(file.read()))
            with open(f"charset/{lang}.txt", encoding="utf-8") as file:
                self.charset[lang] = file.read()
        
        # 0714 - special特殊字符列表（手动绘制字形）
        specialChar = os.listdir(f'special/{self.fontlist[0]}')
        self.special_char_list = [os.path.splitext(file)[0]
                                    for file in specialChar if file.lower().endswith('.png')]
    
    # 获取字体大小
    def loadsize(self, font) -> None:
        self.fontsize = dict()
        testfont = ["A", "g", "赢"]     # 用来确定字体实际大小的测试用汉字
        for lang in self.langlist:
            fontobj = ImageFont.truetype(
                f"fonts/" + self.fontinfo[lang][font]["fontfile"], 
                self.fontinfo[lang][font]["size"]
            )
            self.fontsize[lang] = (
                max([fontobj.getbbox(ch)[2] for ch in testfont]),
                max([fontobj.getbbox(ch)[3] for ch in testfont]),
            )
    
    # 自动计算图片高度
    def totalheight(self, font) -> int:
        height = 0
        for lang in self.langlist:
            charcount = len(self.charset[lang]) # 字符数
            char_perline = self.totalwidth // (
                self.fontinfo[lang][font].get("extra_x", 0) + self.fontsize[lang][0] + self.rest_x
            )
            height += (self.fontsize[lang][1] + self.rest_y + self.fontinfo[lang][font].get("extra_y", 0)) * (charcount // char_perline + 1)
        return height

    def check(self, ch) -> str:
        # 特殊字符直接放行或跳过
        ch_code = hex(ord(ch))
        if ch in [' ', '　'] or ch_code in self.special_char_list:
            return 'yep'
        if ch == '\n':
            return 'nope'
        testglyph = Image.new("1", (self.width, self.height), 0)
        ImageDraw.Draw(testglyph).text((0, 0), ch, 
                                       fill=1, font=self.font)  
        # 检查字图
        if testglyph != self.fail:
            return 'yep'
        # 尝试使用fallback
        else:
            ImageDraw.Draw(testglyph).text((0, 0), ch, fill=1, font=self.fallbackfont)
            if testglyph != self.fallbackfail:
                return 'fallback'
            else:
                return 'nope'
    
    def addfont(self, ch, fontname, fallback=False) -> None:
        # 先获取基本信息
        if fallback:
            # cfg = self.fallbackcfg
            font = self.fallbackfont
        else:
            font = self.font
        
        cfg = self.cfg
        start_x = cfg.get("start_x", 0)
        start_y = cfg.get("start_y", 0)
        if fallback:
            start_x = self.fallbackcfg.get("start_x", start_x)
            start_y = self.fallbackcfg.get("start_y", start_y)
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
        # 0714 - 特殊字形手动添加
        ch_code = hex(ord(ch))
        if ch_code in self.special_char_list:
            symbol = Image.open(f"special/{fontname}/{ch_code}.png")
            resize_factor = int(self.cfg.get("special_factor", max(round(self.cfg["size"] / 16.0), 1)))
            special_y = int(self.cfg.get("special_y", 0))
            symbol = symbol.resize((resize_factor * symbol.size[0], resize_factor * symbol.size[1]), Image.Resampling.NEAREST)
            self.glyph.paste(symbol, (self.x + start_x, self.y + start_y + special_y))
        else:
            self.drawtool.text((self.x + start_x, self.y + start_y),
                                ch, fill=(255, 255), font=font)
        # test
        # testglyph = Image.new("LA", (width, height), 0)
        # ImageDraw.Draw(testglyph).text((start_x, start_y), ch, fill=(0, 255), font=font)
        # pixel = testglyph.load()
        # threshold = max(cfg.get("threshold", 0), 0)
        # for x in range(width):
        #     for y in range(height):
        #         pixel[x, y] = (pixel[x, y][0], 255 * int(pixel[x, y][1] > threshold))
        # testglyph = testglyph.convert("RGBA")
        # bashcmd(f"mkdir -p test/{fontname}/")
        # testglyph.save(f"test/{fontname}/uni{format(ord(ch), '04x')}.png")
        ###

        # 添加csv数据
        if self.project == 'psot':
            self.csv.append((ord(ch), self.x, self.y, width, height,
                            0, 0, width, height))
        elif self.project == 'tsus':
            self.csv.append((ord(ch), self.x, self.y, width, height,
                            width, 0))

        # 移动画笔，准备下一次绘制
        self.x += width + self.rest_x
   
    # 主任务：生成字图
    def task(self) -> None:
        # 对于每个字体
        for fontname in self.fontlist:
            # 创建新字图
            print(colored(f"--> {fontname}", "blue"))
            self.loadsize(fontname)
            self.glyph = Image.new('LA', (self.totalwidth, self.totalheight(fontname)), (0, 0))
            self.drawtool = ImageDraw.Draw(self.glyph)
            self.x = 0
            self.prev_y = self.y = 0
            self.csv = [tuple(self.baseinfo[fontname].values())]
            # 针对每种语言
            for lang in self.langlist:
                # 加载配置文件和字符集
                print(colored(f" -> {lang}", "yellow"))
                self.cfg = self.fontinfo[lang][fontname]
                (self.width, self.height) = self.fontsize[lang]
                self.width += self.cfg.get("extra_x", 0)
                self.height += self.cfg.get("extra_y", 0)
                self.font = ImageFont.truetype(f"fonts/" + self.cfg["fontfile"], self.cfg["size"])
                if lang == "en_US":
                    self.encfg = self.cfg
                    self.enfont = self.font
                self.fallbackcfg = self.cfg.get("fallback", self.cfg)
                if self.fallbackcfg:
                    self.fallbackfont = ImageFont.truetype(f"fonts/" + self.fallbackcfg["fontfile"], self.fallbackcfg["size"])
                    self.fallbackfail = Image.new("1", (self.width, self.height), 0)
                    ImageDraw.Draw(self.fallbackfail).text((0, 0), "𪾰", fill=1, font=self.fallbackfont)
                
                # 生成绘制失败字符图
                self.fail = Image.new("1", (self.width, self.height), 0)
                ImageDraw.Draw(self.fail).text((0, 0), "𪾰", fill=1, font=self.font)
                # 开始逐一绘制字符
                self.errorcount = 0
                for ch in self.charset[lang]:
                    # 检查字符是否可用
                    status = self.check(ch) # 返回值有 yep, nope, fallback
                    if status == 'yep':
                        self.addfont(ch, fontname)    # addfont有csv的添加
                    elif status == 'fallback':
                        # print(colored(f"{ch}", "magenta"), end='')
                        # self.errorcount += 1
                        # if self.errorcount % 50 == 0:
                        #     print()
                        self.addfont(ch, fontname, fallback=True)
                    elif status == 'nope':
                        if ch != '\n':
                            self.errorcount += 1
                            print(colored(f"{ch}", "red"), end='')
                            if self.errorcount % 50 == 0:
                                print()
                        continue
                    
                if self.errorcount > 0:
                    self.errorcount = 0
                    print()
                # 完毕后调整坐标位
                self.x = 0
                self.y += self.height + self.rest_y   # 此处和之前算height的+rest都是为了避免重叠打的补丁
                # 处理透明度
                pixel = self.glyph.load()
                threshold = max(self.cfg.get("threshold", 0), 0)
                for x in range(self.totalwidth):
                    for y in range(self.prev_y, self.y):
                        pixel[x, y] = (pixel[x, y][0], 255 * int(pixel[x, y][1] > threshold))
            # 全部结束后，保存图片和csv到文件
            ind = -len(self.langlist) if len(self.langlist) <= 1 else -2
                
            bashcmd(f"mkdir -p dist/{self.project}/{self.langlist[ind]}")
            self.glyph.save(f"dist/{self.project}/{self.langlist[ind]}/{fontname}.png")
            if self.project == 'psot':
                output_csv = f"dist/{self.project}/{self.langlist[ind]}/{fontname}.csv"
            elif self.project == 'tsus':
                output_csv = f"dist/{self.project}/{self.langlist[ind]}/glyphs_{fontname}.csv"
            with open(output_csv, "w", encoding="utf-8", newline='') as file:
                self.writer = csv.writer(file, delimiter=';')
                self.writer.writerows(self.csv)