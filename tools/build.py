"""Builds docs/index.html (served by GitHub Pages) from src/page.html."""
import pathlib
root = pathlib.Path(__file__).resolve().parent.parent
page = (root / "src/page.html").read_text()
head = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="今の気持ちと目の前の景色から、その瞬間だけのアンビエントを生む。ログイン不要。">
<meta property="og:title" content="ESCAPISM 現現現">
<meta property="og:description" content="今の気持ちと目の前の景色から、その瞬間だけのアンビエントを生む。">
<meta name="theme-color" content="#ecebe6">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.5 system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""
(root / "docs/index.html").write_text(head + page + "\n</body>\n</html>\n")
print("built docs/index.html")
