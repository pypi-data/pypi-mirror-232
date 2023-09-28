#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""生成带 Logo 的二维码
    python3 create_qrcode.py -h
"""
import os
import argparse
import base64
from io import BytesIO
import qrcode
from PIL import Image, ImageDraw


class QRMaker:
    """二维码生成器"""

    def __init__(self, data: str, qr_size: int, is_log: bool = False):
        self._data = data
        self._qr_size = qr_size
        self._qr_image = None
        self._is_log = is_log == True
        # 生成二维码
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        self._qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGBA").resize((qr_size, qr_size))

    def add_logo(self, logo_path: str) -> "QRMaker":
        """添加 Logo 图片
        Args:
            logo_path (str): Logo 图片路径
        Returns:
            QRMaker: _description_
        """
        if isinstance(logo_path, str) and logo_path.endswith(".png") and os.path.exists(logo_path):
            logo_image = create_logo_image(logo_path, int(self._qr_size * 0.2))
            paste_image_center(self._qr_image, logo_image)
        return self

    def save_image(self, save_path: str):
        """保存二维码
        Args:
            save_path (str): 保存二维码图片路径
        """
        self._qr_image.save(save_path)

    def to_base64(self) -> str:
        """将图片转换为 Base64 字符串
        Returns:
            str: 图片 Base64 字符串
        """
        # 将图片保存到内存中
        buffer = BytesIO()
        self._qr_image.save(buffer, format="PNG")
        # 将图片转换为 Base64 字符串
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return "data:image/png;base64," + base64_image

    def show_image(self):
        """显示二维码图片"""
        self._qr_image.show()


def set_image_radius(image: Image, radius_width: int):
    """设置图片圆角
    Args:
        image (PIL.Image): 目标图片
        radius_width (int): 圆角尺寸
    """
    radius_width = int(min(image.size[0] * 0.5, image.size[1] * 0.5, radius_width))
    border_mask = Image.new("L", image.size, 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius_width, fill=255)
    image.putalpha(border_mask)


def paste_image_center(image1: Image, image2: Image):
    """将 image2 粘贴到 image1 的中心

    Args:
        image1 (PIL.Image): 目标图片
        image2 (PIL.Image): 粘贴的图片
    """
    border_mask = Image.new("L", image2.size, 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.rounded_rectangle((0, 0, image2.size[0], image2.size[0]), int(image2.size[0] * 0.2), fill=255)

    offset_size = int((image1.size[0] - image2.size[0]) * 0.5)
    image1.paste(image2, (offset_size, offset_size), mask=border_mask)


def create_logo_image(logo_path: str, logo_size: int) -> Image:
    """处理 logo 图片

    Args:
        logo_path (str): logo 图片路径
        logo_size (int): logo 目标尺寸

    Returns:
        _type_: _description_
    """
    # 打开 logo 图像
    logo_image = Image.open(logo_path)
    logo_image = logo_image.convert("RGBA").resize((logo_size, logo_size))
    # 设置 logo 圆角
    set_image_radius(logo_image, int(logo_size * 0.2))
    # 白边
    border_size = logo_image.size[0] + 8
    border_color = (255, 255, 255, 255)
    border_image = Image.new("RGBA", (border_size, border_size), border_color)
    set_image_radius(border_image, int(border_size * 0.2))
    paste_image_center(border_image, logo_image)
    # logo
    logo_image = border_image
    # 灰边
    border_size = logo_image.size[0] + 2
    border_color = (220, 220, 220, 255)
    border_image = Image.new("RGBA", (border_size, border_size), border_color)
    set_image_radius(border_image, int(border_size * 0.2))
    paste_image_center(border_image, logo_image)
    # logo
    logo_image = border_image
    return logo_image


def main():
    """main"""
    parser = argparse.ArgumentParser(description="生成带 Logo 的二维码")
    parser.add_argument("-V", "--version", action="version", version="0.0.4", help="Display version")
    parser.add_argument("-data", "--data", dest="data", required=True, help="二维码信息, 例: http://www.xxx.com")
    parser.add_argument("-save", "--save", dest="save", help="保存二维码路径, 默认: qr_code.png")
    parser.add_argument("-logo", "--logo", dest="logo", help="要添加的 logo 图片地址")
    parser.add_argument("-size", "--size", dest="size", type=int, default=512, help="二维码尺寸, 默认 512px")
    parser.add_argument("--base64", action="store_true", help="打印 base64")
    parser.add_argument("--log", action="store_true", help="打印 log")
    parser.add_argument("--show", action="store_true", help="直接显示二维码图片")
    # 解析参数
    args = parser.parse_args()
    # 生成二维码
    qr_maker = QRMaker(args.data, args.size, args.log)

    if args.logo and str(args.logo).endswith(".png"):
        qr_maker.add_logo(args.logo)

    if args.save and str(args.save).endswith(".png"):
        qr_maker.save_image(args.save)

    if args.base64:
        print(qr_maker.to_base64())

    if args.show:
        qr_maker.show_image()


if __name__ == "__main__":
    main()
