import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def scrape_detail_page(detail_url, headers):
    details = {
        "출시일": "정보 없음",
        "개발자": "정보 없음",
        "배포자": "정보 없음",
        "최근 리뷰": "정보 없음",
        "모든 리뷰": "정보 없음",
        "게임 설명": "정보 없음",
        "지원 언어": "정보 없음",
        "필요 사양": "정보 없음",
    }

    try:
        response = requests.get(detail_url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        dev_element = soup.select_one('#developers_list a')
        if dev_element:
            details["개발자"] = dev_element.text.strip()
        
        publisher_subtitle = soup.find('div', class_='subtitle', string=re.compile(r'\s*발행자:\s*'))
        if publisher_subtitle:
            publisher_element = publisher_subtitle.find_next_sibling('div', class_='summary')
            if publisher_element:
                details["배포자"] = publisher_element.text.strip()

        release_date_element = soup.select_one('.release_date .date')
        if release_date_element:
            details["출시일"] = release_date_element.text.strip()
        
        review_rows = soup.select('.user_reviews_summary_row')
        if len(review_rows) > 0:
            recent_summary = review_rows[0].select_one('.game_review_summary').text.strip()
            recent_count_text = review_rows[0].select_one('.responsive_hidden').text.strip()
            details["최근 리뷰"] = f"{recent_summary} {recent_count_text}"

        if len(review_rows) > 1:
            all_summary = review_rows[1].select_one('.game_review_summary').text.strip()
            all_count_text = review_rows[1].select_one('.responsive_hidden').text.strip()
            details["모든 리뷰"] = f"{all_summary} {all_count_text}"

        description_element = soup.select_one('#game_area_description')
        if description_element:
            details["게임 설명"] = description_element.get_text(strip=True)[:200] + "..."

        lang_elements = soup.select('table.game_language_options tr td.ellipsis')
        languages = [lang.text.strip() for lang in lang_elements if lang.text.strip()]
        details["지원 언어"] = ", ".join(languages) if languages else "정보 없음"

        sys_req_element = soup.select_one('.sysreq_content[data-os="win"] .game_area_sys_req_full ul')
        if sys_req_element:
            details["필요 사양"] = " ".join(sys_req_element.get_text(strip=True).split())[:200] + "..."


    except Exception as e:
        print(f"  상세 페이지 처리 중 오류: {e}")
    
    return details


url = 'https://store.steampowered.com/charts/topselling/KR'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

main_response = requests.get(url, headers=headers)
main_soup = BeautifulSoup(main_response.text, 'lxml')

game_rows = main_soup.select('tr._2-RN6nWOY56sNmcDHu069P')
all_game_data = []

print("스팀 TOP 5 게임 상세 정보를 추출합니다...")
for row in game_rows[:5]:
    rank = row.select_one('td._34h48M_x9S-9Q2FFPX_CcU').text.strip()
    title = row.select_one('div._1n_4-zvf0n4aqGEksbgW9N').text.strip()
    
    list_page_data = {
        "순위": rank,
        "제목": title,
    }

    detail_link_element = row.select_one('td._18kGHKeOavDDdJVs9FVhpo a')
    if detail_link_element:
        detail_url = detail_link_element['href']
        print(f"[{rank}위: {title}] 상세 페이지 분석 중...")
        
        detail_data = scrape_detail_page(detail_url, headers)
        
        list_page_data.update(detail_data)
        
        time.sleep(1)

    all_game_data.append(list_page_data)


df = pd.DataFrame(all_game_data)

desired_order = ["순위", "제목", "개발자", "배포자", "출시일", "최근 리뷰", "모든 리뷰", "지원 언어", "게임 설명", "필요 사양"]
existing_columns = [col for col in desired_order if col in df.columns]
df = df[existing_columns]


print("\n--- ✅ 최종 크롤링 결과 ---")
print(df)

# 만약 특정 게임의 전체 설명이나 사양을 보고 싶다면 아래처럼 접근 가능
# print("\n--- 1위 게임 전체 설명 ---")
# print(df.loc[0, '게임 설명'])