"""
outfit画像のチェック柄背景を透過に変換するスクリプト
チェック柄（灰色＋白の市松模様）を検出して透明にします

使い方:
  python fix_transparency.py

※ partsフォルダと同じ場所に置いて実行してください
※ 元画像は parts_backup/ にバックアップされます
"""

from PIL import Image
import os
import shutil
import numpy as np

# 設定
PARTS_DIR = "./parts"
BACKUP_DIR = "./parts_backup"

def is_checker_pixel(img_array, x, y):
    """チェック柄のピクセルかどうか判定"""
    r, g, b = img_array[y, x, 0], img_array[y, x, 1], img_array[y, x, 2]

    # 典型的なチェック柄の色（Photopea / 画像編集ソフトの透過表示）
    # 白: (255, 255, 255) または近い色
    # 灰: (204, 204, 204) または (192, 192, 192) または近い色
    is_white = (r > 248 and g > 248 and b > 248)
    is_gray = (180 < r < 215) and (180 < g < 215) and (180 < b < 215) and abs(int(r) - int(g)) < 5 and abs(int(g) - int(b)) < 5

    return is_white or is_gray


def detect_checker_size(img_array):
    """チェック柄の1マスのサイズを自動検出（8px or 16px が一般的）"""
    # 左上の角からチェック柄のパターンを探す
    for size in [8, 16, 10, 12, 4, 6]:
        # 最初の数マスがチェック柄パターンかチェック
        match_count = 0
        total_check = 0
        for by in range(0, min(size * 4, img_array.shape[0]), size):
            for bx in range(0, min(size * 4, img_array.shape[1]), size):
                total_check += 1
                # ブロック内の代表ピクセル
                px = min(bx + size // 2, img_array.shape[1] - 1)
                py = min(by + size // 2, img_array.shape[0] - 1)
                if is_checker_pixel(img_array, px, py):
                    match_count += 1
        if total_check > 0 and match_count / total_check > 0.4:
            return size
    return 8  # デフォルト


def remove_checker_background(img_path, output_path):
    """チェック柄背景を透過に変換"""
    img = Image.open(img_path)

    # すでにRGBAで完全に透過が効いている場合はスキップ
    if img.mode == 'RGBA':
        arr = np.array(img)
        # 角のピクセルが透明ならすでに透過済み
        corners = [
            arr[0, 0, 3],
            arr[0, -1, 3],
            arr[-1, 0, 3],
            arr[-1, -1, 3],
        ]
        if all(c < 10 for c in corners):
            print(f"  → すでに透過済み、スキップ: {os.path.basename(img_path)}")
            shutil.copy2(img_path, output_path)
            return False

    # RGBに変換して処理
    img_rgb = img.convert('RGB')
    arr = np.array(img_rgb)
    h, w = arr.shape[:2]

    # RGBA画像を作成
    result = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    result_arr = np.array(result)

    # 各ピクセルを判定
    for y in range(h):
        for x in range(w):
            r, g, b = arr[y, x]

            # チェック柄の色かどうか
            is_white = (r > 248 and g > 248 and b > 248)
            is_gray = (180 < r < 215) and (180 < g < 215) and (180 < b < 215) and abs(int(r) - int(g)) < 5 and abs(int(g) - int(b)) < 5

            if is_white or is_gray:
                # 周囲のピクセルもチェック柄色かチェック（孤立した白/灰は服の可能性）
                neighbors_checker = 0
                neighbors_total = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            neighbors_total += 1
                            nr, ng, nb = arr[ny, nx]
                            n_white = (nr > 248 and ng > 248 and nb > 248)
                            n_gray = (180 < nr < 215) and (180 < ng < 215) and (180 < nb < 215) and abs(int(nr) - int(ng)) < 5 and abs(int(ng) - int(nb)) < 5
                            if n_white or n_gray:
                                neighbors_checker += 1

                # 周囲の半分以上がチェック柄色なら背景と判定
                if neighbors_total > 0 and neighbors_checker / neighbors_total >= 0.5:
                    result_arr[y, x] = [0, 0, 0, 0]  # 透明
                else:
                    result_arr[y, x] = [r, g, b, 255]  # 服の白として残す
            else:
                result_arr[y, x] = [r, g, b, 255]  # そのまま

    result = Image.fromarray(result_arr)
    result.save(output_path, 'PNG')
    return True


def main():
    if not os.path.exists(PARTS_DIR):
        print(f"エラー: {PARTS_DIR} フォルダが見つかりません")
        print("partsフォルダと同じ場所にこのスクリプトを置いて実行してください")
        return

    # バックアップ
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"バックアップフォルダ作成: {BACKUP_DIR}")

    # outfit_XX.png のみ処理
    files = sorted([f for f in os.listdir(PARTS_DIR) if f.startswith('outfit_') and f.endswith('.png')])

    if not files:
        print("outfit_XX.png ファイルが見つかりません")
        return

    print(f"処理対象: {len(files)} ファイル\n")

    fixed = 0
    skipped = 0

    for fname in files:
        src = os.path.join(PARTS_DIR, fname)
        backup = os.path.join(BACKUP_DIR, fname)

        # バックアップ
        if not os.path.exists(backup):
            shutil.copy2(src, backup)

        print(f"処理中: {fname}...", end="")
        try:
            changed = remove_checker_background(src, src)
            if changed:
                fixed += 1
                print(f"  → 透過処理完了 ✓")
            else:
                skipped += 1
        except Exception as e:
            print(f"  → エラー: {e}")
            skipped += 1

    print(f"\n完了！ 修正: {fixed}件, スキップ: {skipped}件")
    print(f"元画像のバックアップ: {BACKUP_DIR}/")


if __name__ == '__main__':
    main()
