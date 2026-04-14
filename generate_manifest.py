"""
generate_manifest.py
chibi-parts/ フォルダをスキャンして manifest.json を生成する
GitHubにプッシュする前に1回実行してください

使い方: python generate_manifest.py

アイテムの値段を変えたいとき:
  chibi-costs.json を編集してから実行してください
  書かれていないアイテムは自動で値段が決まります（1番目=無料）
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARTS_DIR = os.path.join(BASE_DIR, 'chibi-parts')
TRANSFORMS_FILE = os.path.join(BASE_DIR, 'chibi-transforms.json')
COSTS_FILE = os.path.join(BASE_DIR, 'chibi-costs.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'manifest.json')

CATEGORY_CONFIG = {
    'eyes':        {'display_name': 'め',       'z_index': 10},
    'mouth':       {'display_name': 'くち',     'z_index': 11},
    'hair':        {'display_name': 'かみ',     'z_index': 20},
    'tops':        {'display_name': 'トップス', 'z_index': 5},
    'bottoms':     {'display_name': 'ボトムス', 'z_index': 4},
    'shoes':       {'display_name': 'くつ',     'z_index': 3},
    'accessories': {'display_name': 'アクセ',   'z_index': 25},
}

IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.webp')

def file_to_name(filename):
    return os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')

def main():
    transforms = {}
    if os.path.isfile(TRANSFORMS_FILE):
        with open(TRANSFORMS_FILE, 'r', encoding='utf-8') as f:
            transforms = json.load(f)
        print(f'transforms読み込み: {len(transforms)}件')
    else:
        print('chibi-transforms.json が見つかりません（デフォルト値を使用）')

    costs = {}
    if os.path.isfile(COSTS_FILE):
        with open(COSTS_FILE, 'r', encoding='utf-8') as f:
            costs = json.load(f)
        print(f'chibi-costs.json 読み込み: {len(costs)}件')
    else:
        print('chibi-costs.json が見つかりません（自動で値段を設定します）')

    manifest = {'categories': {}}

    if not os.path.isdir(PARTS_DIR):
        print(f'エラー: {PARTS_DIR} が見つかりません')
        print('chibi-parts/ フォルダを作って画像を入れてください')
        return

    for folder in sorted(os.listdir(PARTS_DIR)):
        full = os.path.join(PARTS_DIR, folder)
        if not os.path.isdir(full):
            continue
        config = CATEGORY_CONFIG.get(folder)
        if not config:
            print(f'スキップ（未知のフォルダ）: {folder}')
            continue

        items = []
        for i, f in enumerate(sorted(os.listdir(full))):
            if not f.lower().endswith(IMAGE_EXTS):
                continue
            item_id = folder + '_' + os.path.splitext(f)[0]

            if item_id in costs:
                cost = costs[item_id]
            else:
                cost = 0 if i == 0 else (50 + i * 30)

            item = {
                'id': item_id,
                'name': file_to_name(f),
                'file': f'chibi-parts/{folder}/{f}',
                'cost': cost,
            }
            if item_id in transforms:
                item['transform'] = transforms[item_id]
            items.append(item)

        manifest['categories'][folder] = {
            'display_name': config['display_name'],
            'z_index': config['z_index'],
            'items': items,
        }
        print(f'{folder}: {len(items)}件')

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print()
    print(f'manifest.json を生成しました: {OUTPUT_FILE}')
    print('次のファイルをGitHubにプッシュしてください:')
    print('  - manifest.json')
    print('  - chibi-costs.json')
    print('  - chibi-parts/ (フォルダごと)')
    print('  - chibi-avatar.html')
    print('  - chibi-transforms.json')

if __name__ == '__main__':
    main()
