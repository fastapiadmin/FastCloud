import base64
import random
import string
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from app.config.setting import settings


class CaptchaUtil:
    """
    验证码工具类
    """

    @classmethod
    def generate_captcha(cls) -> tuple[str, str]:
        """
        生成带有噪声和干扰的验证码图片（4位随机字符）。

        返回:
        - tuple[str, str]: Base64 PNG 字符串与验证码明文。
        """
        # 生成4位随机验证码
        chars = string.digits + string.ascii_letters
        captcha_value = "".join(random.sample(chars, 4))

        # 创建一张随机颜色背景的图片
        width, height = 160, 60
        background_color = tuple(random.randint(230, 255) for _ in range(3))
        image = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(image)

        # 使用指定字体
        font = ImageFont.truetype(font=settings.CAPTCHA_FONT_PATH, size=settings.CAPTCHA_FONT_SIZE)

        # 计算文本总宽度和高度
        total_width = sum(draw.textbbox((0, 0), char, font=font)[2] for char in captcha_value)
        text_height = draw.textbbox((0, 0), captcha_value[0], font=font)[3]

        # 计算起始位置,使文字居中
        x_start = (width - total_width) / 2
        y_start = (height - text_height) / 2 - draw.textbbox((0, 0), captcha_value[0], font=font)[1]

        # 绘制字符
        x = x_start
        for char in captcha_value:
            # 使用深色文字,增加对比度
            text_color = tuple(random.randint(0, 80) for _ in range(3))

            # 随机偏移,增加干扰
            x_offset = x + random.uniform(-2, 2)
            y_offset = y_start + random.uniform(-2, 2)

            # 绘制字符
            draw.text((x_offset, y_offset), char, font=font, fill=text_color)

            # 更新x坐标,增加字符间距的随机性
            x += draw.textbbox((0, 0), char, font=font)[2] + random.uniform(1, 5)

        # 添加干扰线
        for _ in range(4):
            line_color = tuple(random.randint(150, 200) for _ in range(3))
            points = [(i, int(random.uniform(0, height))) for i in range(0, width, 20)]
            draw.line(points, fill=line_color, width=1)

        # 添加随机噪点
        for _ in range(width * height // 60):
            point_color = tuple(random.randint(0, 255) for _ in range(3))
            draw.point(
                (random.randint(0, width), random.randint(0, height)),
                fill=point_color,
            )

        # 将图像数据保存到内存中并转换为base64
        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        base64_string = base64.b64encode(buffer.getvalue()).decode()

        return base64_string, captcha_value

    @classmethod
    def captcha_arithmetic(cls, difficulty: str = "medium") -> tuple[str, int]:
        """
        创建算术验证码图片（加减乘运算）；浅色底、居中算式，无旋转与干扰线/噪点。

        参数:
        - difficulty (str): 难度级别（easy / medium / hard），控制数字范围与可用运算符。

        返回:
        - tuple[str, int]: base64 编码的 PNG 图片字符串与正确答案（整数）。
        """
        difficulty_config = {
            "easy": {"num_range": (1, 9), "operators": ["+", "-"]},
            "medium": {"num_range": (1, 15), "operators": ["+", "-", "*"]},
            "hard": {"num_range": (1, 20), "operators": ["+", "-", "*"]},
        }
        config = difficulty_config.get(difficulty, difficulty_config["medium"])

        operators = config["operators"]
        operator = random.choice(operators)
        num_range = config["num_range"]

        if operator == "-":
            num1 = random.randint(num_range[0] + 5, num_range[1])
            num2 = random.randint(num_range[0], num1 - 1)
        elif operator == "*":
            num1 = random.randint(num_range[0], min(10, num_range[1]))
            num2 = random.randint(num_range[0], min(10, num_range[1]))
        else:
            num1 = random.randint(num_range[0], num_range[1])
            num2 = random.randint(num_range[0], num_range[1])

        result_map = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
        }
        captcha_value = result_map[operator](num1, num2)

        width, height = 160, 60
        image = Image.new("RGB", (width, height), color=(248, 249, 250))
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(font=settings.CAPTCHA_FONT_PATH, size=settings.CAPTCHA_FONT_SIZE)

        text = f"{num1} {operator} {num2} = ?"
        tb = draw.textbbox((0, 0), text, font=font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        x = (width - tw) // 2
        y = (height - th) // 2 - tb[1]
        draw.text((x, y), text, fill=(55, 65, 81), font=font)

        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        base64_string = base64.b64encode(buffer.getvalue()).decode()

        return base64_string, captcha_value
