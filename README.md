# UNSW-ES Bulldogs website

The club's public website. Everything lives in this one GitHub organisation (`easternsuburbsbulldogs`):
the files, the hosting (GitHub Pages) and the hourly news update (GitHub Actions). There is no other
account, server or database to look after.

- **Live preview:** https://easternsuburbsbulldogs.github.io
- **Publishing:** any change saved to the `main` branch goes live in about a minute.
- **Cost:** free.

---

## Handing the site to a new president

1. The new president creates a free GitHub account (github.com/signup).
2. An existing owner opens **github.com/orgs/easternsuburbsbulldogs → People → Invite member**, enters
   the new president's username or email, picks **Owner** and sends it. The invite lasts 7 days; resend it
   from **People → Invitations** if it runs out.
3. Once they have accepted, the outgoing president can be removed from **People**. Keep at least two
   owners at all times so the club can never be locked out.
4. In **Settings → Billing and plans** (billing email) and **Settings → Profile** (public email), use
   president@unswesbulldogs.com.au so notices follow the role, not the person.

---

## Common jobs

Small text changes can be made right on github.com: open the file, click the pencil, edit, then
**Commit changes**. Bigger changes are easier on a computer with the repo downloaded and Python installed.

| Job | Where |
|---|---|
| Change wording on a page | The page's file in `public/` (for example `public/about/rules.html`) |
| Add a news post | Copy `public/news/_template.html`, follow the notes at its top, then run `python tools/news_index.py public` |
| Change a coach, assistant or team detail | `tools/teams_section.py` (lists at the top), then run `python tools/teams_section.py public` |
| Add a coach photo | Put a square photo in `public/coaches/` and point to it in `tools/teams_section.py` |
| Change training times or grounds | `tools/train_section.py`, then run `python tools/train_section.py public` |
| Re-order AFL / AFLW players | `tools/players_rows.py` (`ORDER` list), then run `python tools/players_rows.py public` |
| Colour palette | `public/site.js`, top: `ROTATE` (a different palette each day), `DEFAULT_THEME` (used when `ROTATE` is false), `SHOW_SWITCHER` (the picker in the menu) |
| Tune how Play AFL news mixes with ours | `public/site.js`: the `NEWS` settings |

After running any of the `tools/` scripts, commit the changed files in `public/` and the site updates.

## Play AFL news

Every hour GitHub Actions runs `tools/fetch-playafl-news.mjs`, which reads the AFL Sydney / SFL news feed,
keeps stories that mention the club, and publishes them as `news.json`. The home page and the News page
blend these in with the club's own articles. Club articles always take priority, and a Play AFL story that
we have written up ourselves never shows twice. If Play AFL is down, the site simply shows the club's own
articles. You can see each run under the **Actions** tab, and start one by hand with **Run workflow**.

## Going live on unswesbulldogs.com.au

1. Wherever the club's domain is managed, add the DNS records GitHub asks for in
   **Settings → Pages → Custom domain** (enter `www.unswesbulldogs.com.au`). Tick **Enforce HTTPS** once it
   is offered.
2. Point the search tags at the real address and switch off preview mode:
   `python tools/seo.py public https://www.unswesbulldogs.com.au` (without the word `preview`), then commit.
3. Before cancelling Wix, list the old Wix page addresses and add a small forwarding page for each, so
   their Google ranking carries over to the new pages.

## What's where

```
public/          the website itself (HTML, site.css, site.js, images, fonts)
tools/           small scripts that rebuild parts of the pages from simple lists
.github/         the publish-and-news workflow
```
