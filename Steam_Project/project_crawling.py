import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://store.steampowered.com/charts/topselling/KR'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(url, headers=headers)
html = response.text
soup = BeautifulSoup(html, 'lxml')

# 게임 하나하나의 정보를 담고 있는 '큰 덩어리'들을 모두 찾는다.
game_rows = soup.select('tr._2-RN6nWOY56sNmcDHu069P')

game_data = []
# 각 덩어리(row)를 순서대로 하나씩 처리한다.
for row in game_rows:
    # 이 덩어리 '안에서만' 순위를 찾는다.
    rank = row.select_one('td._34h48M_x9S-9Q2FFPX_CcU').text.strip()
    
    # 이 덩어리 '안에서만' 제목을 찾는다.
    title = row.select_one('div._1n_4-zvf0n4aqGEksbgW9N').text.strip()
    
    # 이 덩어리 '안에서만' 가격을 찾는다.
    price_element = row.select_one('td._3IyfUchPbsYMEaGjJU3GOP ._3j4dI1yA7cRfCvK8h406OB')
    price = price_element.text.strip() if price_element else "가격 정보 없음"

    # ✨ [추가] 이 덩어리 '안에서만' 순위 변동을 찾는다.
    change_element = row.select_one('td._1ZdIh_OWh9DUr5O4OCypQn')
    change = change_element.text.strip() if change_element else 'N/A'

    # ✨ [추가] 이 덩어리 '안에서만' 주간 순위를 찾는다.
    weeks_element = row.select_one('td.xm7JpnZElM9XGF4ruu0Z-')
    weeks = weeks_element.text.strip() if weeks_element else 'N/A'
    
    # 추출한 모든 정보를 딕셔너리로 저장
    game_data.append({
        '순위': rank,
        '제목': title,
        '순위 변동': change,
        '차트 진입 주': weeks,
        '가격': price
    })

# pandas DataFrame으로 변환하여 출력
df = pd.DataFrame(game_data)
print(df)