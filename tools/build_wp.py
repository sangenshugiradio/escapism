"""Builds wordpress/escapism-wordpress.html from src/page.html.

The result is meant for a WordPress "Custom HTML" block. Compared with the page itself:
- every CSS rule is scoped under #escapism, so the theme and the page do not restyle each other
- every element id gets an "esc-" prefix, so it cannot collide with ids the theme uses
- the script runs inside a function, so none of its names leak into the WordPress page
- the page lives in a box of its own height instead of taking over <html> and <body>
"""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
page = (root / "src/page.html").read_text()
ROOT = "#escapism"

# ---- split the fragment into its parts ----
style = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
script = re.search(r"<script>(.*?)</script>", page, re.S).group(1)
fonts = re.search(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>', page).group(0)
body = page[page.index("</style>") + len("</style>"):page.index("<script>")]

# ---- the podcast artwork is served next to the GitHub Pages build ----
SITE = "https://sangenshugiradio.github.io/escapism/"
body = body.replace('src="sangenshugi-radio.jpg"', f'src="{SITE}sangenshugi-radio.jpg"')

# ---- ids get a prefix everywhere they are referenced ----
ids = sorted(set(re.findall(r'\bid="([^"]+)"', body)), key=len, reverse=True)
for i in ids:
    body = body.replace(f'id="{i}"', f'id="esc-{i}"').replace(f'for="{i}"', f'for="esc-{i}"')
    script = script.replace(f'$("{i}")', f'$("esc-{i}")').replace(f'.id === "{i}"', f'.id === "esc-{i}"')
    style = re.sub(rf"#{re.escape(i)}(?![\w-])", f"#esc-{i}", style)
style = style.replace("url(#waver)", "url(#esc-waver)")
leftover = [i for i in ids if re.search(rf'\$\("{re.escape(i)}"\)', script)]
assert not leftover, leftover


# ---- scope every selector under #escapism ----
def scope_selector(sel):
    sel = sel.strip()
    if sel in (":root", "body", "html"):
        return ROOT
    if sel.startswith(':root:not([data-theme="light"])'):
        return ROOT
    if sel.startswith(":root"):
        return None                      # the viewer's explicit theme toggle does not exist on WordPress
    return f"{ROOT} {sel}"


def block_end(css, i):
    """index just past the brace that closes the block opening at css[i] == '{'"""
    depth = 0
    for j in range(i, len(css)):
        if css[j] == "{":
            depth += 1
        elif css[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
    raise ValueError("unbalanced css")


def scope(css):
    out, i = [], 0
    while i < len(css):
        if css[i].isspace():
            i += 1
            continue
        if css.startswith("/*", i):
            j = css.index("*/", i) + 2
            out.append(css[i:j])
            i = j
            continue
        brace = css.index("{", i)
        head = css[i:brace].strip()
        end = block_end(css, brace)
        inner = css[brace + 1:end - 1]
        if head.startswith("@keyframes"):
            out.append(css[i:end])
        elif head.startswith("@"):
            out.append(f"{head} {{\n{scope(inner)}\n}}")
        else:
            if head == "html, body":
                i = end
                continue
            sels = [s for s in (scope_selector(p) for p in head.split(",")) if s]
            if sels:
                out.append(f"{', '.join(dict.fromkeys(sels))} {{{inner}}}")
        i = end
    return "\n".join(out)


scoped = scope(style)

# the page used to fill the window; on WordPress it is a box in the flow of the post
embed_css = f"""
{ROOT} {{ position: relative; isolation: isolate; padding: 0; overflow: hidden; text-align: left; }}
{ROOT} *, {ROOT} *::before, {ROOT} *::after {{ box-sizing: border-box; }}
{ROOT} :where(h1, h2, h3, p, ul, ol, li, figure, form) {{ margin: 0; padding: 0; border: 0; background: none; color: inherit; font-size: inherit; line-height: inherit; text-transform: none; }}
{ROOT} :where(button, textarea, select, input, label) {{ padding: 0; border: 0; background: none; font: inherit; color: inherit; letter-spacing: inherit; text-transform: none; text-shadow: none; box-shadow: none; border-radius: 0; margin: 0; min-height: 0; min-width: 0; width: auto; max-width: none; }}
{ROOT} .poster {{ height: min(100svh, 900px); min-height: 680px; }}
@media (min-width: 700px) {{ {ROOT} .poster {{ height: min(calc(100svh - 48px), 900px); margin: 24px auto; }} }}
{ROOT} .sheet {{ z-index: 100000; }}
{ROOT} .composeRow textarea {{ width: auto; }}
{ROOT} .sheet ul {{ padding-left: 1.1em; }}
{ROOT} .crisis ul {{ padding-left: 1.1em; }}
"""

# the script keeps every name to itself
script = "(() => {\n" + script.strip() + "\n})();"

html = f"""<!-- ESCAPISM 現現現 — paste into a WordPress "Custom HTML" block -->
{fonts}
<style>
{scoped}
{embed_css}
</style>
<div id="escapism" lang="ja">
{body.strip()}
</div>
<script>
{script}
</script>
"""
out = root / "wordpress/escapism-wordpress.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print("built", out, len(html), "chars,", len(ids), "ids prefixed")
