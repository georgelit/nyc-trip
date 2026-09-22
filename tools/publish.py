#!/usr/bin/env python3
"""Публикация страницы поездки в Нью-Йорк на GitHub Pages с сохранением истории версий.

    ./publish.sh "что изменил"

Что происходит: подтягиваются чужие правки, номер версии увеличивается,
штамп проставляется в шапку и подвал, текущее состояние замораживается
в v/vN.html, перестраивается страница истории, всё уходит в GitHub.
"""
import io, os, re, subprocess, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "index.html")
VDIR = os.path.join(ROOT, "v")
LOG  = os.path.join(VDIR, "versions.tsv")
MONTHS = ["янв","фев","мар","апр","мая","июн","июл","авг","сен","окт","ноя","дек"]


def git(*args, check=True):
    r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit("git %s: %s" % (" ".join(args), (r.stderr or r.stdout).strip()))
    return r.stdout.strip()


def read_log():
    if not os.path.exists(LOG):
        return []
    rows = []
    for line in io.open(LOG, encoding="utf-8").read().splitlines():
        if line.strip():
            parts = line.split("\t")
            while len(parts) < 4:
                parts.append("")
            rows.append(parts[:4])          # номер, iso-время, автор, комментарий
    return rows


def history_page(rows):
    items = []
    for n, iso, author, msg in reversed(rows):
        d = datetime.datetime.fromisoformat(iso)
        when = "%d %s %d, %02d:%02d" % (d.day, MONTHS[d.month - 1], d.year, d.hour, d.minute)
        items.append(
            '    <li class="v">\n'
            '      <a class="num" href="v%s.html">v%s</a>\n'
            '      <span class="when">%s</span>\n'
            '      <span class="msg">%s</span>\n'
            '      <span class="who">%s</span>\n'
            '    </li>' % (n, n, when, msg or "без комментария", author))
    return HIST_TPL.replace("{{ITEMS}}", "\n".join(items)).replace("{{COUNT}}", str(len(rows)))


HIST_TPL = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>История версий — Нью-Йорк</title>
<meta name="theme-color" content="#f4f2ec" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#12110f" media="(prefers-color-scheme: dark)">
<style>
  :root {
    --paper:#f4f2ec; --card:#fffefb; --ink:#16150f; --ink-soft:#56534a;
    --ink-faint:#8b877c; --rule:#dcd7c9; --sat:#c2410c;
    --serif: ui-serif,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
    --sans: ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
    --mono: ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root { --paper:#12110f; --card:#1b1a17; --ink:#f0ede5; --ink-soft:#a8a397;
            --ink-faint:#726e64; --rule:#2e2c27; --sat:#fb923c; }
  }
  :root[data-theme="dark"] { --paper:#12110f; --card:#1b1a17; --ink:#f0ede5; --ink-soft:#a8a397;
            --ink-faint:#726e64; --rule:#2e2c27; --sat:#fb923c; }
  :root[data-theme="light"] { --paper:#f4f2ec; --card:#fffefb; --ink:#16150f; --ink-soft:#56534a;
            --ink-faint:#8b877c; --rule:#dcd7c9; --sat:#c2410c; }
  * { box-sizing:border-box; }
  html { -webkit-text-size-adjust:100%; }
  body { margin:0; background:var(--paper); color:var(--ink); font-family:var(--sans);
         font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased; }
  .wrap { max-width:760px; margin:0 auto;
          padding:0 max(20px,env(safe-area-inset-left)) 70px max(20px,env(safe-area-inset-right)); }
  header { padding:48px 0 22px; border-bottom:1px solid var(--rule); }
  .eyebrow { font-family:var(--mono); font-size:12px; letter-spacing:.16em; text-transform:uppercase;
             color:var(--ink-faint); margin:0 0 12px; }
  h1 { font-family:var(--serif); font-weight:600; letter-spacing:-.02em; font-size:clamp(30px,6vw,46px);
       line-height:1.05; margin:0 0 14px; }
  .lede { color:var(--ink-soft); margin:0; max-width:58ch; }
  ol { list-style:none; margin:26px 0 0; padding:0; display:flex; flex-direction:column; gap:10px; }
  .v { background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:14px 16px;
       display:grid; grid-template-columns:auto auto 1fr auto; gap:6px 14px; align-items:baseline; }
  .num { font-family:var(--mono); font-size:15px; font-weight:600; color:var(--sat);
         text-decoration:none; border-bottom:1px solid currentColor; }
  .when { font-family:var(--mono); font-size:13px; color:var(--ink-faint);
          font-variant-numeric:tabular-nums; white-space:nowrap; }
  .msg { color:var(--ink-soft); }
  .who { font-family:var(--mono); font-size:12px; color:var(--ink-faint); white-space:nowrap; }
  .v:first-child { border-color:var(--sat); }
  .v:first-child::after { content:"актуальная"; grid-column:1/-1; font-family:var(--mono); font-size:11px;
                          letter-spacing:.1em; text-transform:uppercase; color:var(--sat); }
  @media (max-width:600px) {
    .v { grid-template-columns:auto 1fr; }
    .msg { grid-column:1/-1; }
    .who { grid-column:1/-1; }
  }
  footer { margin-top:40px; padding-top:20px; border-top:1px solid var(--rule);
           font-family:var(--mono); font-size:12px; color:var(--ink-faint); }
  a { color:var(--sat); text-underline-offset:2px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="eyebrow">Нью-Йорк · 7–11 октября 2026</p>
    <h1>История версий</h1>
    <p class="lede">Каждая публикация замораживается отдельной страницей и остаётся доступной навсегда.
      Всего версий: {{COUNT}}. <a href="../">Открыть актуальную →</a></p>
  </header>
  <ol>
{{ITEMS}}
  </ol>
  <footer>Страница собирается автоматически при публикации</footer>
</div>
</body>
</html>
"""

BANNER = ('<div class="archived">'
          '<span>Архивная версия v%s от %s</span>'
          '<span><a href="../">Открыть актуальную →</a> · <a href="./">все версии</a></span>'
          '</div>')


def main():
    msg = " ".join(sys.argv[1:]).strip() or "правки"
    os.makedirs(VDIR, exist_ok=True)

    # Чужие правки подтягиваем ДО того, как что-то менять, иначе push отобьётся.
    git("pull", "--rebase", "--autostash", check=False)

    rows = read_log()
    n = int(rows[-1][0]) + 1 if rows else 1
    now = datetime.datetime.now()
    stamp = "%d.%02d %02d:%02d" % (now.day, now.month, now.hour, now.minute)
    author = git("config", "user.name", check=False) or "неизвестно"

    page = io.open(PAGE, encoding="utf-8").read()
    page, k1 = re.subn(r'<span class="ver">[^<]*</span>',
                       '<span class="ver">верс. %d · %s</span>' % (n, stamp), page)
    page, k2 = re.subn(r'(<a href="v/">)[^<]*(</a>)',
                       r'\g<1>версия %d · %s\g<2>' % (n, stamp), page)
    if not k1 or not k2:
        sys.exit("не нашёл штамп версии в index.html (шапка: %d, подвал: %d)" % (k1, k2))
    io.open(PAGE, "w", encoding="utf-8").write(page)

    # Снимок: тот же файл, но с плашкой и ссылками, поправленными на подпапку v/
    snap = page.replace('href="v/"', 'href="./"').replace("VLOG = 'v/versions.tsv'", "VLOG = './versions.tsv'")
    snap = snap.replace('<div class="wrap">', '<div class="wrap">\n  ' + BANNER % (n, stamp), 1)
    io.open(os.path.join(VDIR, "v%d.html" % n), "w", encoding="utf-8").write(snap)

    rows.append([str(n), now.isoformat(timespec="minutes"), author, msg])
    io.open(LOG, "w", encoding="utf-8").write(
        "\n".join("\t".join(r) for r in rows) + "\n")
    io.open(os.path.join(VDIR, "index.html"), "w", encoding="utf-8").write(history_page(rows))

    git("add", "-A")
    if not git("status", "--porcelain"):
        print("изменений нет, публиковать нечего")
        return
    git("commit", "-m", "v%d: %s" % (n, msg))
    git("push")
    print("✅ опубликована версия %d (%s)" % (n, stamp))
    print("   страница:  https://georgelit.github.io/nyc-trip/")
    print("   история:   https://georgelit.github.io/nyc-trip/v/")
    print("   обновится в браузере в течение примерно двух минут")


main()
