# さんすうクエスト - セットアップ手順

## ファイル構成

```
sansu-quest/
├── index.html    ← ログイン・ランキング画面
├── game.html     ← ゲーム画面
├── firebase.js   ← ★ここだけ編集する★
└── README.md
```

---

## STEP 1: 子供の名前を変更する

`firebase.js` を開いて以下を編集：

```js
const USERS = [
  { name: "たろう", avatar: "🧒" },
  { name: "はなこ", avatar: "👧" },
];
```

---

## STEP 2: Firebase プロジェクトを作る（無料）

1. https://console.firebase.google.com にアクセス
2. 「プロジェクトを作成」→ 名前を入力（例：sansu-quest）
3. Google アナリティクスは「無効」でOK → 作成

---

## STEP 3: Firestore データベースを作る

1. 左メニュー「Firestore Database」→「データベースの作成」
2. 「本番環境モード」を選択 → ロケーション「asia-northeast1」→ 有効にする
3. 「ルール」タブを開いて以下に書き換えて「公開」：

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if true;
    }
  }
}
```

---

## STEP 4: Firebase の設定値を取得して貼る

1. 左上の歯車マーク →「プロジェクトの設定」
2. 「マイアプリ」→「</>（ウェブ）」ボタンをクリック
3. アプリ名を入力（例：sansu-web）→「アプリを登録」
4. 表示された `firebaseConfig` の値を `firebase.js` にコピー：

```js
const FIREBASE_CONFIG = {
  apiKey:            "AIzaSy...",       // ← コピーした値
  authDomain:        "sansu-quest.firebaseapp.com",
  projectId:         "sansu-quest",
  storageBucket:     "sansu-quest.appspot.com",
  messagingSenderId: "123456789",
  appId:             "1:123456789:web:abc..."
};
```

---

## STEP 5: GitHub Pages にデプロイ

1. GitHubで新規リポジトリを作成（例：sansu-quest）
2. このフォルダの3ファイルをプッシュ：

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/あなたのID/sansu-quest.git
git push -u origin main
```

3. GitHubリポジトリの「Settings」→「Pages」
4. Source: 「Deploy from a branch」→ branch: `main` / folder: `/ (root)`
5. 「Save」→ 数分後にURLが発行される！

---

## アクセスURL

```
https://あなたのID.github.io/sansu-quest/
```

---

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| 画面が真っ白 | firebase.jsの設定値が間違い | コンソール(F12)でエラー確認 |
| データが保存されない | Firestoreルールが未設定 | STEP 3のルール設定を確認 |
| ランキングが出ない | まだ誰もプレイしていない | 一度ゲームをプレイすると表示される |
