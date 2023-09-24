'''Download Webtoons from Naver Game.'''

from __future__ import annotations
import contextlib
from itertools import count
import json

from typing_extensions import override

if __name__ in ("__main__", "I_naver_game"):
    from A_scraper import Scraper
else:
    from .A_scraper import Scraper


class NaverGameScraper(Scraper[int]):
    '''Scrape webtoons from Naver Game.'''
    TEST_WEBTOON_ID = 5  # 모배툰
    BASE_URL = 'https://game.naver.com/original_series'
    IS_CONNECTION_STABLE = True

    @override
    def fetch_webtoon_information(self) -> None:
        url = f'https://apis.naver.com/nng_main/nng_main/original/series/{self.webtoon_id}'
        webtoon_data = self.requests.get(url).json()['content']
        title = webtoon_data['seriesName']
        thumbnail = webtoon_data['seriesImage']['verticalLogoImageUrl']

        self.title = title
        self.webtoon_thumbnail = thumbnail

    @override
    def fetch_episode_informations(self, episode_max_limit=500):
        # 여러 시즌을 하나로 통합
        content_raw_data = []
        for season in count(1):
            url = (f'https://apis.naver.com/nng_main/nng_main/original/series/{self.webtoon_id}/seasons/{season}/contents'
                   f'?direction=NEXT&pagingType=CURSOR&sort=FIRST&limit={episode_max_limit}')
            res = self.requests.get(url)
            res = res.json()
            if not res['content']:
                break
            content_raw_data += res['content']['data']

        # 부제목, 이미지 데이터 불러옴
        subtitles = []
        episode_image_urls = []
        episode_ids = []
        for i, episode in enumerate(content_raw_data, 1):
            subtitle = episode['feed']['title']
            content_json_data = json.loads(episode['feed']['contents'])
            image_urls = []
            for image_url in content_json_data['document']['components']:
                with contextlib.suppress(KeyError):
                    image_urls.append(image_url['src'])

            episode_ids.append(i)
            subtitles.append(subtitle)
            episode_image_urls.append(image_urls)

        self.episode_titles = subtitles
        self.episode_image_urls = episode_image_urls
        self.episode_ids = episode_ids

    @override
    def get_episode_image_urls(self, episode_no):
        return self.episode_image_urls[episode_no]
