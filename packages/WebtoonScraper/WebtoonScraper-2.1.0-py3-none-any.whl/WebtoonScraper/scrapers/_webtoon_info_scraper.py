from requests_utils import requests
import itertools
import json

# 진행 중인 웹툰

url = 'https://comic.naver.com/api/webtoon/titlelist/weekday?order=user'

res = requests.get(url)

webtoons = list(itertools.chain(*res.json()['titleListMap'].values()))

# 완결 웹툰

total_pages = requests.get(
    'https://comic.naver.com/api/webtoon/titlelist/finished?page=1&order=UPDATE').json()['pageInfo']['totalPages']

webtoon_infomations: list[dict] = []
for page_no in range(1, total_pages + 1):
    print(page_no, end=' ')
    url = f'https://comic.naver.com/api/webtoon/titlelist/finished?page={page_no}&order=UPDATE'
    webtoon_infomations += requests.get(url).json()['titleList']

total_webtoon_list = webtoons + webtoon_infomations
total_webtoon_list.sort(key=lambda x: x['titleId'])

webtoon_id_and_title = {webtoon['titleId']: webtoon['titleName']
                        for webtoon in total_webtoon_list}

webtoon_id_and_title = {webtoon['titleId']: webtoon['titleName']
                        for webtoon in total_webtoon_list}

with open('webtoon_infomations.json', 'w', encoding='utf-8') as f:
    json.dump(total_webtoon_list, f, indent=4, ensure_ascii=False)

with open('webtoons_list.json', 'w', encoding='utf-8') as f:
    json.dump(webtoon_id_and_title, f, indent=4, ensure_ascii=False)
