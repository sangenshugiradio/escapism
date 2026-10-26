# ESCAPISM 現現現

今の気持ちと、目の前の景色の写真から、その瞬間だけのアンビエントを生むWebサービスです。
音はすべてブラウザの中でリアルタイムに合成します。ログインは要りません。

**サイト:** https://melodichxckk-svg.github.io/escapism/

## 使い方

1. 上の枠に、目の前の景色の写真を入れる
2. 今の気持ち、頭から離れないことを書く
3. 「手放す」を押す — 淡い光が広がってから、曲が流れはじめます

- AMBIENT / BEAT でビートの有無を選べます（再生中に切り替えると、いまの曲がそのまま変わります）
- 空いているところをタップすると音が鳴り、ダブルタップでグリッチ、長押しで音が引き、写真をなぞるとフィルターとエコー、上下にはじくと転調します
- 「動画で保存」で、いまの曲と画面を15秒の横長動画にできます（iPhoneでは共有シートから「ビデオを保存」）

## 構成

| パス | 内容 |
|---|---|
| `src/page.html` | ページ本体（音のエンジン、デザイン、端末内の解析） |
| `docs/index.html` | GitHub Pages で配信するファイル。`python3 tools/build.py` で `src/page.html` から生成 |
| `worker/` | Claude を誰でも使えるようにする中継API（Cloudflare Workers、任意） |

## 解析のしくみ

- **標準（ログイン不要・サーバー不要）**: 写真の色・明るさと、書いた言葉のキーワードから、端末の中でジャンル・編成・調・環境音・曲名・流れる文章を組み立てます。
- **Claude を使う（任意）**: `worker/` をデプロイすると、写真と言葉を Claude が読み取って選曲と文章を作ります。APIキーはサーバー側にだけ置かれ、利用者はログインなしで使えます。費用はAPIキーの持ち主にかかります。

### Claude を有効にする手順

```sh
cd worker
npm install
npx wrangler login                          # Cloudflare アカウントでログイン
npx wrangler secret put ANTHROPIC_API_KEY   # Anthropic の APIキーを貼り付け
# wrangler.toml の ALLOWED_ORIGINS がサイトのアドレスになっているか確認
npx wrangler deploy                         # 表示された https://escapism-api.<you>.workers.dev を控える
cd ..
echo "https://escapism-api.<you>.workers.dev" > tools/api_url.txt
python3 tools/build.py                      # docs/index.html にAPIのアドレスが入る
git commit -am "Enable Claude API" && git push
```

- モデルは `claude-opus-5-5`（`wrangler.toml` の `MODEL` で変更可）。応答を速くするため effort は `low`。
- 1つのIPあたり10分に30回までの簡易制限があります。公開規模に応じて Cloudflare の Rate Limiting ルールや、Anthropic Console の利用上限も設定してください。

## 注意

ESCAPISM は医療や治療ではありません。つらさが続くときは、身近な人や専門の窓口（よりそいホットライン 0120-279-338 など）に相談してください。
