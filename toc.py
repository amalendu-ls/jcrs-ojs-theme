"""Issue table of contents markup (used by build.py for the Home and Current Issue pages)."""

ICON = {
    "author": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm0 1.5c-2.7 0-5.5 1.3-5.5 3.3V14h11v-1.2c0-2-2.8-3.3-5.5-3.3Z"/></svg>',
    "pages": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 1h5.5L13 4.5V15H4V1Zm5 1.2V5h2.8L9 2.2ZM6 8h5v1H6V8Zm0 2.5h5v1H6v-1Z"/></svg>',
    "views": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 14V9h2.5v5H2Zm4.75 0V5h2.5v9h-2.5ZM11.5 14V2H14v12h-2.5Z"/></svg>',
    "download": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M7.25 1.5h1.5v7.1l2.3-2.3 1.06 1.06L8 11.47 3.89 7.36 4.95 6.3l2.3 2.3V1.5ZM2.5 12.5h11V14h-11v-1.5Z"/></svg>',
}


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def article_item(a):
    lang = ' lang="bn"' if a["lang"] == "bn" else ""
    keywords = ""
    if a.get("keywords"):
        keywords = f'<p class="jcrs-kw"><b>Keywords:</b> {esc(", ".join(a["keywords"]))}</p>'
    article = "{{article:%s}}" % a["id"]
    galley = "{{galley:%s:%s}}" % (a["id"], a["galley"])
    return f"""          <li><div class="obj_article_summary">
            <h3 class="title"><a href="{article}"{lang}>{esc(a['title'])}</a></h3>
            <div class="meta"><div class="authors">{ICON['author']}{esc(a['authors'])}</div><div class="pages">{ICON['pages']}{esc(a['pages'])}</div></div>
            <div class="jcrs-art-actions">
              <ul class="galleys_links"><li><a class="obj_galley_link pdf" href="{galley}">PDF</a></li></ul>
              <span class="jcrs-art-stats">{ICON['views']}Abstract views: {a['abstractViews']}<span class="sep" aria-hidden="true">|</span>{ICON['download']}Downloads: {a['downloads']}</span>
            </div>
            <details class="jcrs-abstract"><summary>Abstract</summary><div{lang}><p>{esc(a['abstract'])}</p>{keywords}</div></details>
          </div></li>"""


def toc_sections(data):
    """Section labels, authors, pages, abstract toggle, PDF link and view/download counts."""
    out, section = [], None
    for a in data["articles"]:
        if a["section"] != section:
            if section is not None:
                out.append("        </ul>\n      </div>")
            section = a["section"]
            out.append(f'      <div class="section">\n        <h2>{esc(section)}</h2>\n'
                       '        <ul class="cmp_article_list articles">')
        out.append(article_item(a))
    out.append("        </ul>\n      </div>")
    return '    <div class="sections">\n' + "\n".join(out) + "\n    </div>"


def home_toc(data):
    return ('<section class="jcrs-current page_issue">\n'
            '    <div class="jcrs-current-head"><h2>Current Issue</h2><a href="{{archive}}">View all issues →</a></div>\n'
            f'    <p class="jcrs-current-meta"><strong>{esc(data["issue"])}</strong> · Published: {esc(data["published"])}</p>\n'
            f'    <div class="obj_issue_toc">\n{toc_sections(data)}\n    </div>\n  </section>')


ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"}


def _cover(i, cls):
    label = f"Vol. {i['vol']} No. {i['num']} ({i['year']})"
    if i["cover"]:
        return f'<a class="cover {cls}" href="{{{{issue:{i["id"]}}}}}"><img src="{i["cover"]}" alt="Cover of {label}" loading="lazy"></a>'
    return (f'<a class="cover {cls}" href="{{{{issue:{i["id"]}}}}}" aria-label="{label}">'
            f'<span class="jcrs-cover-ph">JCRS<small>{i["year"]}</small></span></a>')


def archive_summary(data):
    issues = data["issues"]
    return (f'{len(issues)} issues · {sum(i["items"] for i in issues)} articles and editorials · '
            f'Volume I ({issues[-1]["year"]}) to Volume {ROMAN[issues[0]["vol"]]} ({issues[0]["year"]}) · free to read and download')


def archive_html(data):
    issues = data["issues"]
    latest, rest = issues[0], issues[1:]
    out = [f"""  <div class="jcrs-latest obj_issue_summary">
    {_cover(latest, '')}
    <div class="jcrs-latest-body">
      <span class="jcrs-badge-new">Latest Issue</span>
      <h2><a class="title" href="{{{{issue:{latest['id']}}}}}">Vol. {latest['vol']} No. {latest['num']} ({latest['year']})</a></h2>
      <p class="jcrs-latest-meta">Volume {ROMAN[latest['vol']]}, Issue {latest['num']} · {latest['month']} · {latest['items']} items</p>
      <a class="jcrs-btn jcrs-btn-solid" href="{{{{issue:{latest['id']}}}}}">View issue</a>
    </div>
  </div>"""]
    vol = None
    for i in rest:
        if i["vol"] != vol:
            if vol is not None:
                out.append("  </ul>")
            vol = i["vol"]
            out.append(f'  <h2 class="jcrs-vol"><span>Volume {ROMAN[vol]}</span> {i["year"]}</h2>\n  <ul class="issues_archive">')
        out.append(f"""    <li><div class="obj_issue_summary">
      {_cover(i, '')}
      <div class="jcrs-issue-body">
        <h2><a class="title" href="{{{{issue:{i['id']}}}}}">Vol. {i['vol']} No. {i['num']} ({i['year']})</a></h2>
        <div class="description"><p>{i['month']} · {i['items']} items</p></div>
      </div>
      <a class="jcrs-issue-go" href="{{{{issue:{i['id']}}}}}" aria-label="Open Vol. {i['vol']} No. {i['num']}">→</a>
    </div></li>""")
    out.append("  </ul>")
    return "\n".join(out)
