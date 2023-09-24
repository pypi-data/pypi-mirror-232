if __name__ in {"__main__", "__init__"}:
    from A_scraper import Scraper
    from B_naver_webtoon import NaverWebtoonScraper
    from C_best_challenge import BestChallengeScraper
    from D_webtoon_originals import WebtoonOriginalsScraper
    from E_webtoon_canvas import WebtoonCanvasScraper
    from G_bufftoon import BufftoonScraper
    from H_naver_post import NaverPostScraper, NaverPostWebtoonId
    from I_naver_game import NaverGameScraper
    from J_lezhin_comics import LezhinComicsScraper
    from K_kakaopage import KakaopageScraper
else:
    from .A_scraper import Scraper
    from .B_naver_webtoon import NaverWebtoonScraper
    from .C_best_challenge import BestChallengeScraper
    from .D_webtoon_originals import WebtoonOriginalsScraper
    from .E_webtoon_canvas import WebtoonCanvasScraper
    from .G_bufftoon import BufftoonScraper
    from .H_naver_post import NaverPostScraper, NaverPostWebtoonId
    from .I_naver_game import NaverGameScraper
    from .J_lezhin_comics import LezhinComicsScraper
    from .K_kakaopage import KakaopageScraper
