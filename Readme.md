### 목적
- BTS에 이슈 로봇/위치/스텝/원인으로 구분 -> 기간 혹은 로봇 등 특정 지표에 따른 이슈 현황을 모니터링하는 데에 용이하게 함
- 레이블링을 통해 주요 이슈를 트래킹하여 어떤 요소가 전체 이슈 추이에 영향을 미치는지 확인

### 실행 방법
1. constant.py [#BTS USER] 란에 id, password 입력
2. constant.py [#BTS ISSUE NUMBER] 란에 원하는 이슈 번호 범위(start_num, end_num) 입력
3. 코드 실행 후 바탕화면에 생성된 txt 파일 내용을 복사해 전용 시트에 붙여넣기

- 추후 레이블 변경 발생 시 constant.py에 반영
