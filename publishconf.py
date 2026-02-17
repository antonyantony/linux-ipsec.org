# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)

from pelicanconf import *  # noqa: F403


# If your site is available via HTTPS, make sure SITEURL begins with https://
# When GITHUB_PAGES is set (e.g. "antonyantony/linux-ipsec.org"), use GitHub Pages URL
GITHUB_PAGES = os.environ.get("GITHUB_PAGES", "")
if GITHUB_PAGES:
    owner, repo = GITHUB_PAGES.split("/", 1)
    SITEURL = f"https://{owner}.github.io/{repo}"
    RELATIVE_URLS = True
else:
    SITEURL = "https://linux-ipsec.org"
    RELATIVE_URLS = False

FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

# DISQUS_SITENAME = ""
# GOOGLE_ANALYTICS = ""
