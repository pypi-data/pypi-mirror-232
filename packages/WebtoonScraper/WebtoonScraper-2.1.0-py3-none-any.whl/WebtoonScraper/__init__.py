"""
░██╗░░░░░░░██╗███████╗██████╗░████████╗░█████╗░░█████╗░███╗░░██╗░██████╗░█████╗░██████╗░░█████╗░██████╗░███████╗██████╗░
░██║░░██╗░░██║██╔════╝██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗████╗░██║██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
░╚██╗████╗██╔╝█████╗░░██████╦╝░░░██║░░░██║░░██║██║░░██║██╔██╗██║╚█████╗░██║░░╚═╝██████╔╝███████║██████╔╝█████╗░░██████╔╝
░░████╔═████║░██╔══╝░░██╔══██╗░░░██║░░░██║░░██║██║░░██║██║╚████║░╚═══██╗██║░░██╗██╔══██╗██╔══██║██╔═══╝░██╔══╝░░██╔══██╗
░░╚██╔╝░╚██╔╝░███████╗██████╦╝░░░██║░░░╚█████╔╝╚█████╔╝██║░╚███║██████╔╝╚█████╔╝██║░░██║██║░░██║██║░░░░░███████╗██║░░██║
░░░╚═╝░░░╚═╝░░╚══════╝╚═════╝░░░░╚═╝░░░░╚════╝░░╚════╝░╚═╝░░╚══╝╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝

Scrape webtoons with ease.
"""  # noqa

if __name__ in {"__main__", "__init__"}:
    from directory_merger import DirectoryMerger
else:
    from .directory_merger import DirectoryMerger

__title__ = "WebtoonScraper"
__description__ = "Scraping webtoons with ease."
__url__ = "https://github.com/ilotoki0804/WebtoonScraper"
__raw_source_url__ = "https://raw.githubusercontent.com/ilotoki0804/WebtoonScraper/master"
__version_info__ = (2, 1, 0)
__version__ = str.join('.', map(str, __version_info__))
__author__ = "ilotoki0804"
__author_email__ = "ilotoki0804@gmail.com"
__license__ = "MIT License"
