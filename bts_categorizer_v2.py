import asyncio
from playwright.async_api import async_playwright
import time
import constant_template

async def get_label_from_issue(page, url, number):
    try:
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_selector(".labels", state="visible", timeout=10000)    
        
        # '큰틀' skip
        issue_type = await page.locator("#type-val").inner_text()
        if issue_type == ' 큰틀' :
            return
        # BTS issue 레이블 스크래핑
        issue_label = await page.locator(".labels").inner_text()
        issue_labels = issue_label.split()


        issue_robot = []

        # 로봇
        robots=list(set(issue_labels).intersection(constant_template.ROBOT_LABEL))

        for robot in robots:
            for old, new in constant_template.ROBOT_MAPPING.items():
                if(robot.startswith(old)):
                    robot_number = robot[len(old):]
                    if robot.endswith('tation'):
                        robot_number = '-1, ' + new + '-2'
                    else:
                        if robot_number == '':
                            robot_number = '-R1, ' + new + '-R2'
                        if not robot_number.startswith('-'):
                            robot_number = '-C' + robot_number
                    issue_robot.append(new + robot_number)


        # 위치, 스텝, 원인
        issue_location=''
        issue_step=''
        issue_cause='robot'
        for issue_label in issue_labels:
            location = constant_template.LOCATION_LABEL.get(issue_label) # 동일한 값 없으면 'None' 리턴
            if location:
                issue_location = location
            step = constant_template.STEP_LABEL.get(issue_label)
            if step:
                issue_step = step
            cause = constant_template.CAUSE_LABEL.get(issue_label)
            if cause:
                issue_cause = cause

        # 기타 주요 이슈
        etc = list(set(issue_labels).intersection(constant_template.ETC_LABEL))

        # 이슈번호, 로봇, 위치, 스텝, 원인, 기타 주요 이슈
        result = [str(number), ', '.join(issue_robot), issue_location, issue_step, issue_cause, ', '.join(etc) ]
        
    except Exception as e:
        print(f"An error occurred at {url}: {e}")
        return None

    return result


async def fetch_all_texts(start_num, end_num, is_headless=True, max_concurrent=12):
    async with async_playwright() as p:
        # 브라우저와 컨텍스트 생성 (세션 유지)
        browser = await p.chromium.launch(headless=is_headless)
        context = await browser.new_context()  # 단일 컨텍스트 사용

        # 로그인
        login_page = await context.new_page()
        BTS_URL = constant_template.BTS_URL
        await login_page.goto(BTS_URL + str(start_num), wait_until="domcontentloaded")
        await asyncio.gather(
            login_page.get_by_placeholder("사번/Employee Number").fill(id_bts),
            login_page.get_by_label("패스워드").fill(pw_bts)
        )
        await login_page.keyboard.press('Enter')
        
        # 로그인 완료 대기 (필요시 대기 시간 설정)
        await login_page.wait_for_load_state("networkidle")

        # URL 리스트 & 이슈 번호 리스트 동적 생성
        urls = [f"{BTS_URL}{i}" for i in range(start_num, end_num + 1)]
        numbers = list(range(start_num, end_num + 1)) 
        
        semaphore = asyncio.Semaphore(max_concurrent)  # 동시 작업 수 제한        
        iter = start_num-1

        async def sem_task(url, number):
            nonlocal iter
            async with semaphore:  # 작업 수 제한 적용
                page = await context.new_page()  # 동일 컨텍스트에서 새 페이지 생성 (세션 유지)
                result = await get_label_from_issue(page, url, number)
                await page.close()
                iter += 1
                # 진행률 출력
                print(f'Progress: {iter}/{end_num}', end='\r')
                return result

        # 모든 URL에 대해 병렬 작업 생성
        tasks = [sem_task(url, number) for url, number in zip(urls, numbers)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # `return_exceptions=True` : 개별 URL에서 발생한 오류가 전체 작업을 중단시키지 않음
        
        await context.close()
        await browser.close()  

        return results


# 결과를 텍스트 파일로 저장하는 함수
def save_results_to_file(results, filename="output.txt"):
    with open(filename, 'w', encoding='utf-8') as f:
        for result in results:
            if result is not None:  # None이 아닌 경우만 저장
                f.write("\t".join(result) + "\n")  # 탭으로 구분하고 줄바꿈 추가


# Initiate
if __name__ == "__main__":
    id_bts = constant_template.ID 
    pw_bts = constant_template.PASSwORD 

    # ✏️기본 설정
    start_num = constant_template.START_NUMBER
    end_num = constant_template.END_NUMBER
    is_headless = True    

    # 실행 및 결과 처리
    start = time.time()
    results = asyncio.run(fetch_all_texts(start_num, end_num, True))

    # 결과를 파일로 저장
    path = f"C:/Users/USER/Desktop/{time.strftime("%Y%m%d")}_{start_num+~+end_num}.txt"
    save_results_to_file(results, path)
    print(f"\nResults saved to {path}")
    print(f"Time taken: {(time.time() - start):.3f} s")