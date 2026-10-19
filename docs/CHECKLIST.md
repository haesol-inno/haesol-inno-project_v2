# 평가 항목별 확인 위치

## 항목 1. 기능 동작 검증

| # | 항목 | 확인 위치 |
|---|---|---|
| 1 | Python 3.10 이상 | [logs/01_env.txt](logs/01_env.txt), README "실행 방법" |
| 2 | Git 버전, user.name / user.email | [logs/01_env.txt](logs/01_env.txt), 커밋 작성자 [logs/05_git_log.txt](logs/05_git_log.txt) |
| 3 | GitHub 저장소 URL, 코드 업로드 | https://github.com/haesol-inno/haesol-inno-project_v2 (`main.py`) |
| 4 | 샘플 저장소 clone 기록 | [logs/02_clone.txt](logs/02_clone.txt) (`octocat/Spoon-Knife`) |
| 5 | 메뉴 출력, 번호 선택 | [logs/03_run_all_features.txt](logs/03_run_all_features.txt) 첫 부분 (잘못된 입력 `99`, `abc` 처리 포함) |
| 6 | 프롬프트 추가 → 목록 반영 | 같은 로그의 "프롬프트 추가" → "프롬프트 목록" 7번 |
| 7 | 카테고리별 조회 | 같은 로그의 "[학습/요약] 카테고리 프롬프트" (1, 5번만 출력) |
| 8 | 제목 또는 내용 키워드 검색 | 같은 로그의 `이메일`(제목), `PANDAS`(내용, 대소문자 무시), `없는검색어` |
| 9 | 즐겨찾기 추가/해제 | 같은 로그의 7번 추가, 1번 해제 → 즐겨찾기 목록 |
| 10 | 브랜치 생성 및 병합 | [logs/05_git_log.txt](logs/05_git_log.txt) — `feature/*` 5개 병합 |
| 11 | README 설명·실행 방법 | [../README.md](../README.md) |

스크린샷: [screenshots/](screenshots/) (01~12, 위 항목 순서대로)

자동 테스트: `python3 -m unittest discover -s tests -v` (24개)

## 항목 2~4. 설계 설명

[DESIGN.md](DESIGN.md)

| 항목 | 위치 |
|---|---|
| 2-1 함수 분리 기준 | DESIGN 1-1 |
| 2-2 데이터 구조 | DESIGN 1-2 |
| 2-3 입력 검증 | DESIGN 1-3 |
| 2-4 커밋 기준 | DESIGN 1-4 |
| 3-1 리스트/딕셔너리 | DESIGN 2-1 |
| 3-2 while과 종료 조건 | DESIGN 2-2 |
| 3-3 검색 구현 | DESIGN 2-3 |
| 3-4 브랜치 전략 | DESIGN 2-4 |
| 4-1 데이터 유지 | DESIGN 3-1 (구현됨) |
| 4-2 같은 제목 처리 | DESIGN 3-2 (구현됨) |
| 4-3 병합 충돌 해결 순서 | DESIGN 3-3 |
| 4-4 카테고리 변경 | DESIGN 3-4 |

## 항목 5. 보너스

| 보너스 | 기능 | 메뉴 | 코드 | 확인 |
|---|---|---|---|---|
| 1 | JSON 저장/불러오기 | 자동 (변경 시 저장, 시작 시 불러오기) | `load_prompts`, `save_prompts` | [logs/04_run_after_restart.txt](logs/04_run_after_restart.txt), [logs/prompts_sample.json](logs/prompts_sample.json) |
| 1 | 카테고리별 Markdown 내보내기 | 8 | `export_markdown_files` | [logs/export_sample/](logs/export_sample/) |
| 2 | 수정 / 삭제 | 9 / 10 | `edit_prompt`, `delete_prompt` | 03 로그 "프롬프트 수정", "프롬프트 삭제" |
| 2 | 상세 보기 조회수 기록 | 5 | `show_detail` | 03 로그 "조회수: 1회" → "조회수: 2회" |
| 2 | 조회수 기준 Top 목록 | 11 | `get_top_prompts`, `show_top` | 03·04 로그 "많이 본 프롬프트 Top 5" |
