import csv
import sys
from PIL import Image, ImageDraw, ImageFont
import re

KEY_WIDTH = 80
KEY_HEIGHT = 80
MARGIN = 20
FONT_SIZE = 24

def load_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return [row for row in reader]

def parse_shape_option(option_str):
    # 例: "5x3+5x3" → [(5,3), (5,3)]
    blocks = []
    for part in option_str.split('+'):
        m = re.match(r'(\d+)x(\d+)', part)
        if not m:
            raise ValueError(f"Invalid shape part: {part}")
        rows, cols = int(m.group(1)), int(m.group(2))
        blocks.append((rows, cols))
    return blocks

def split_layout_by_shape(layout, shape_blocks):
    # 各行ごとにshape_blocksの列数で分割し、各ブロックの行を集める
    num_blocks = len(shape_blocks)
    # 各ブロックの列数リスト
    block_cols = [cols for cols, rows in shape_blocks]
    block_rows = [rows for cols, rows in shape_blocks]
    # 各ブロックの行リストを初期化
    blocks = [[] for _ in range(num_blocks)]
    for row in layout:
        col_idx = 0
        for b, cols in enumerate(block_cols):
            part = row[col_idx:col_idx+cols]
            # 足りなければ空欄で埋める
            if len(part) < cols:
                part += [''] * (cols - len(part))
            blocks[b].append(part)
            col_idx += cols
    # 各ブロックの行数が足りなければ空行で埋める
    for b, rows in enumerate(block_rows):
        while len(blocks[b]) < rows:
            blocks[b].append([''] * block_cols[b])
        # 余分な行は切り捨て
        blocks[b] = blocks[b][:rows]
    return blocks

def render_image_with_shape(blocks, output_path):
    # 横にブロックを並べる（簡易実装）
    total_cols = sum(max(len(row) for row in block) if block else 0 for block in blocks)
    max_rows = max(len(block) for block in blocks)
    width = total_cols * KEY_WIDTH + 2 * MARGIN + (len(blocks)-1)*KEY_WIDTH//2
    height = max_rows * KEY_HEIGHT + 2 * MARGIN
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    x_offset = MARGIN
    for block in blocks:
        block_rows = len(block)
        block_cols = max(len(row) for row in block) if block else 0
        for i, row in enumerate(block):
            for j, key in enumerate(row):
                x0 = x_offset + j * KEY_WIDTH
                y0 = MARGIN + i * KEY_HEIGHT
                x1 = x0 + KEY_WIDTH
                y1 = y0 + KEY_HEIGHT
                draw.rectangle([x0, y0, x1, y1], outline='black', width=2)
                bbox = draw.textbbox((0, 0), key, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                draw.text((x0 + (KEY_WIDTH - w) / 2, y0 + (KEY_HEIGHT - h) / 2), key, fill='black', font=font)
        x_offset += block_cols * KEY_WIDTH + KEY_WIDTH//2  # ブロック間スペース
    image.save(output_path)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='キーボード配列画像生成')
    parser.add_argument('input_csv', help='入力CSVファイル')
    parser.add_argument('output_png', help='出力PNGファイル')
    parser.add_argument('--shape', help='外形指定 例: 5x3+5x3', default=None)
    args = parser.parse_args()
    layout = load_csv(args.input_csv)
    if args.shape:
        shape_blocks = parse_shape_option(args.shape)
        blocks = split_layout_by_shape(layout, shape_blocks)
        render_image_with_shape(blocks, args.output_png)
    else:
        render_image(layout, args.output_png)

def render_image(layout, output_path):
    rows = len(layout)
    cols = max(len(row) for row in layout)
    width = cols * KEY_WIDTH + 2 * MARGIN
    height = rows * KEY_HEIGHT + 2 * MARGIN
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype('arial.ttf', FONT_SIZE)
    except:
        font = ImageFont.load_default()
    for i, row in enumerate(layout):
        for j, key in enumerate(row):
            x0 = MARGIN + j * KEY_WIDTH
            y0 = MARGIN + i * KEY_HEIGHT
            x1 = x0 + KEY_WIDTH
            y1 = y0 + KEY_HEIGHT
            draw.rectangle([x0, y0, x1, y1], outline='black', width=2)
            bbox = draw.textbbox((0, 0), key, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text((x0 + (KEY_WIDTH - w) / 2, y0 + (KEY_HEIGHT - h) / 2), key, fill='black', font=font)
    image.save(output_path)

if __name__ == '__main__':
    main() 