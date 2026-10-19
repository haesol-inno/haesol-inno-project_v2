"""나만의 프롬프트 관리 프로그램 (콘솔)

프롬프트는 prompts.json 파일에 저장되므로 프로그램을 종료해도 유지된다.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "prompts.json")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# 카테고리 체계는 이 목록 한 곳에서만 관리한다.
CATEGORIES = ["텍스트 생성", "이미지 생성", "코드 작성", "학습/요약", "업무 자동화", "기타"]

DEFAULT_PROMPTS = [
    {
        "title": "회의록 3줄 요약",
        "content": (
            "아래 회의록을 읽고 결정 사항, 담당자, 마감일 중심으로 3줄로 요약해줘. "
            "각 줄은 '- '로 시작하고, 정해지지 않은 항목은 '미정'이라고 적어줘.\n\n[회의록 붙여넣기]"
        ),
        "category": "학습/요약",
        "favorite": True,
    },
    {
        "title": "정중한 업무 이메일 작성",
        "content": (
            "너는 10년 차 비즈니스 커뮤니케이션 전문가야. 아래 상황을 바탕으로 "
            "정중하지만 간결한 업무 이메일을 작성해줘. 제목, 인사, 본문, 맺음말 순서로 써줘.\n\n상황: [상황 설명]"
        ),
        "category": "텍스트 생성",
        "favorite": False,
    },
    {
        "title": "SNS 홍보 이미지",
        "content": (
            "Flat illustration of a cozy study cafe, warm morning sunlight, laptop and coffee on a wooden desk, "
            "pastel color palette, clean composition, empty space at the top for a headline, 4:5 ratio"
        ),
        "category": "이미지 생성",
        "favorite": False,
    },
    {
        "title": "파이썬 코드 리뷰어",
        "content": (
            "아래 파이썬 코드를 리뷰해줘. 버그 가능성, 읽기 어려운 부분, 더 파이썬다운 표현을 "
            "각각 번호 목록으로 알려주고, 수정한 코드도 함께 보여줘.\n\n```python\n[코드 붙여넣기]\n```"
        ),
        "category": "코드 작성",
        "favorite": True,
    },
    {
        "title": "개념 설명 (초등학생 눈높이)",
        "content": (
            "[개념]을 초등학교 5학년도 이해할 수 있게 설명해줘. "
            "일상 속 비유 1개와 간단한 예시 2개를 포함하고, 마지막에 한 문장으로 정리해줘."
        ),
        "category": "학습/요약",
        "favorite": False,
    },
    {
        "title": "엑셀 데이터 정리 자동화",
        "content": (
            "다음 표 데이터에서 중복 행을 제거하고, 날짜를 YYYY-MM-DD 형식으로 통일한 뒤 "
            "담당자별 건수를 집계하는 파이썬(pandas) 코드를 작성해줘. 컬럼: [컬럼 목록]"
        ),
        "category": "업무 자동화",
        "favorite": False,
    },
]


def input_non_empty(message):
    """빈 값이 아닐 때까지 반복해서 입력받는다."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("입력값이 비어 있습니다. 다시 입력해주세요.")


def input_number(message, min_value, max_value):
    """min_value~max_value 범위의 정수를 입력받는다. 잘못된 입력이면 None을 반환한다."""
    value = input(message).strip()
    try:
        number = int(value)
    except ValueError:
        print("숫자를 입력해주세요.")
        return None
    if number < min_value or number > max_value:
        print(f"{min_value}~{max_value} 사이의 번호를 입력해주세요.")
        return None
    return number


def confirm(message):
    """y/n 질문을 하고 y면 True를 반환한다."""
    while True:
        answer = input(f"{message} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("y 또는 n을 입력해주세요.")


def choose_category():
    """기본 카테고리 중 하나를 고르거나 직접 입력받는다."""
    custom_number = len(CATEGORIES) + 1
    while True:
        print("카테고리 선택:")
        for number, category in enumerate(CATEGORIES, start=1):
            print(f"{number}) {category}")
        print(f"{custom_number}) 직접 입력")

        number = input_number("선택: ", 1, custom_number)
        if number is None:
            continue
        if number == custom_number:
            return input_non_empty("카테고리 이름: ")
        return CATEGORIES[number - 1]


def next_id(prompts):
    """지금까지 쓰인 가장 큰 id보다 1 큰 값을 반환한다 (삭제 후에도 id가 겹치지 않게)."""
    return max((prompt["id"] for prompt in prompts), default=0) + 1


def make_prompt(prompts, title, content, category, favorite=False):
    """필드를 모두 갖춘 프롬프트 딕셔너리를 만든다."""
    return {
        "id": next_id(prompts),
        "title": title,
        "content": content,
        "category": category,
        "favorite": favorite,
        "views": 0,
    }


def create_default_prompts():
    """기본 데이터를 복사해 id와 조회수 필드를 붙인 새 목록을 만든다."""
    prompts = []
    for prompt in DEFAULT_PROMPTS:
        prompts.append(make_prompt(
            prompts, prompt["title"], prompt["content"], prompt["category"], prompt["favorite"]
        ))
    return prompts


def normalize_title(title):
    """제목 비교용: 앞뒤 공백 제거, 연속 공백 하나로, 영문 소문자로."""
    return " ".join(title.split()).lower()


def find_same_title(prompts, title, exclude=None):
    """같은 제목(정규화 기준)의 프롬프트를 찾는다. exclude는 비교에서 뺄 프롬프트."""
    for prompt in prompts:
        if prompt is not exclude and normalize_title(prompt["title"]) == normalize_title(title):
            return prompt
    return None


def check_duplicate_title(prompts, title, exclude=None):
    """같은 제목이 있으면 경고하고 계속 진행할지 묻는다. 진행해도 되면 True."""
    if find_same_title(prompts, title, exclude) is None:
        return True
    print(f"'{title}'와(과) 같은 제목의 프롬프트가 이미 있습니다.")
    return confirm("그래도 저장할까요? (구분은 번호로 합니다)")


def add_prompt(prompts):
    """새 프롬프트를 입력받아 목록에 추가한다."""
    print("\n=== 프롬프트 추가 ===")
    title = input_non_empty("제목: ")
    if not check_duplicate_title(prompts, title):
        print("추가를 취소했습니다.")
        return False
    content = input_non_empty("내용: ")
    print()
    category = choose_category()

    prompts.append(make_prompt(prompts, title, content, category))
    print("\n프롬프트가 추가되었습니다!")
    return True


def print_prompt_line(number, prompt):
    """'번호. [카테고리] 제목 ⭐' 형식으로 한 줄 출력한다."""
    star = " ⭐" if prompt["favorite"] else ""
    print(f"{number}. [{prompt['category']}] {prompt['title']}{star}")


def show_list(prompts):
    """저장된 모든 프롬프트를 번호와 함께 출력한다."""
    print("\n=== 프롬프트 목록 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다. 먼저 프롬프트를 추가해주세요.")
        return False

    for number, prompt in enumerate(prompts, start=1):
        print_prompt_line(number, prompt)
    print(f"\n총 {len(prompts)}개의 프롬프트")
    return False


def find_prompts(prompts, condition):
    """condition(prompt)가 참인 프롬프트를 (전체 목록 기준 번호, 프롬프트) 목록으로 반환한다.

    전체 목록 기준 번호를 유지해서, 결과에 보이는 번호를
    상세 보기/즐겨찾기/수정/삭제에 그대로 입력할 수 있게 한다.
    """
    return [
        (number, prompt)
        for number, prompt in enumerate(prompts, start=1)
        if condition(prompt)
    ]


def print_matches(matches):
    """find_prompts()의 결과를 출력한다."""
    for number, prompt in matches:
        print_prompt_line(number, prompt)


def get_all_categories(prompts):
    """기본 카테고리에 사용자가 직접 입력한 카테고리를 더한 목록을 반환한다."""
    categories = list(CATEGORIES)
    for prompt in prompts:
        if prompt["category"] not in categories:
            categories.append(prompt["category"])
    return categories


def show_by_category(prompts):
    """선택한 카테고리의 프롬프트만 출력한다."""
    print("\n=== 카테고리별 조회 ===")
    categories = get_all_categories(prompts)
    for number, category in enumerate(categories, start=1):
        print(f"{number}) {category}")

    number = input_number("선택: ", 1, len(categories))
    if number is None:
        return False
    category = categories[number - 1]

    matches = find_prompts(prompts, lambda prompt: prompt["category"] == category)
    print(f"\n[{category}] 카테고리 프롬프트:")
    if not matches:
        print("이 카테고리에 등록된 프롬프트가 없습니다.")
        return False
    print_matches(matches)
    print(f"\n총 {len(matches)}개의 프롬프트")
    return False


def matches_keyword(prompt, keyword):
    """키워드가 제목 또는 내용에 포함되면 True (영문 대소문자 무시)."""
    keyword = keyword.lower()
    return keyword in prompt["title"].lower() or keyword in prompt["content"].lower()


def search_prompt(prompts):
    """키워드가 제목 또는 내용에 포함된 프롬프트를 찾는다."""
    print("\n=== 프롬프트 검색 ===")
    keyword = input_non_empty("검색어: ")

    matches = find_prompts(prompts, lambda prompt: matches_keyword(prompt, keyword))
    print("\n검색 결과:")
    if not matches:
        print("검색 결과가 없습니다.")
        return False
    print_matches(matches)
    print(f"\n{len(matches)}개의 프롬프트를 찾았습니다.")
    return False


def select_prompt(prompts):
    """번호를 입력받아 해당 프롬프트를 반환한다. 잘못된 번호면 None."""
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return None
    number = input_number(f"번호 입력 (1~{len(prompts)}): ", 1, len(prompts))
    if number is None:
        return None
    return prompts[number - 1]


def print_detail(prompt):
    """프롬프트 한 개의 전체 정보를 출력한다."""
    line = "─" * 40
    print()
    print(line)
    print(f"제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    print(f"즐겨찾기: {'⭐' if prompt['favorite'] else '-'}")
    print(f"조회수: {prompt['views']}회")
    print(line)
    print("내용:")
    print(prompt["content"])
    print(line)


def show_detail(prompts):
    """선택한 프롬프트의 전체 내용을 출력하고 조회수를 1 올린다."""
    print("\n=== 프롬프트 상세 보기 ===")
    prompt = select_prompt(prompts)
    if prompt is None:
        return False
    prompt["views"] += 1
    print_detail(prompt)
    return True


def toggle_favorite(prompts):
    """선택한 프롬프트의 즐겨찾기 상태를 추가/해제한다."""
    print("\n=== 즐겨찾기 관리 ===")
    prompt = select_prompt(prompts)
    if prompt is None:
        return False

    prompt["favorite"] = not prompt["favorite"]
    if prompt["favorite"]:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에 추가했습니다! ⭐")
    else:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에서 해제했습니다.")
    return True


def show_favorites(prompts):
    """즐겨찾기된 프롬프트만 모아서 출력한다."""
    print("\n=== 즐겨찾기 목록 ===")
    matches = find_prompts(prompts, lambda prompt: prompt["favorite"])
    if not matches:
        print("즐겨찾기한 프롬프트가 없습니다. (메뉴 6번에서 추가할 수 있습니다)")
        return False
    print_matches(matches)
    print(f"\n총 {len(matches)}개의 즐겨찾기")
    return False


def normalize_prompts(data):
    """JSON에서 읽은 값을 검사해 프롬프트 목록으로 만든다. 형식이 틀리면 ValueError."""
    if not isinstance(data, list):
        raise ValueError("최상위 값이 리스트가 아닙니다.")

    prompts = []
    for item in data:
        if not isinstance(item, dict) or not all(
            isinstance(item.get(key), str) for key in ("title", "content", "category")
        ):
            raise ValueError("title, content, category가 없는 항목이 있습니다.")
        views = item.get("views", 0)
        prompts.append({
            "id": item.get("id"),
            "title": item["title"],
            "content": item["content"],
            "category": item["category"],
            "favorite": item.get("favorite") is True,
            "views": views if isinstance(views, int) and views >= 0 else 0,
        })

    # id가 없거나 겹치는 항목에는 새 id를 붙인다.
    used_ids = set()
    for prompt in prompts:
        if isinstance(prompt["id"], int) and prompt["id"] not in used_ids:
            used_ids.add(prompt["id"])
        else:
            prompt["id"] = None
    for prompt in prompts:
        if prompt["id"] is None:
            prompt["id"] = max(used_ids, default=0) + 1
            used_ids.add(prompt["id"])
    return prompts


def load_prompts(path):
    """JSON 파일에서 프롬프트를 불러온다. 파일이 없거나 손상되었으면 기본 데이터로 시작한다."""
    if not os.path.exists(path):
        print("저장된 데이터가 없어 기본 프롬프트로 시작합니다.")
        return create_default_prompts()

    try:
        with open(path, encoding="utf-8") as file:
            prompts = normalize_prompts(json.load(file))
    except (OSError, ValueError) as error:  # json.JSONDecodeError도 ValueError의 일종
        backup_path = path + ".broken"
        print(f"데이터 파일을 읽을 수 없습니다: {error}")
        try:
            os.replace(path, backup_path)
            print(f"손상된 파일은 {os.path.basename(backup_path)}로 보관하고 기본 프롬프트로 시작합니다.")
        except OSError:
            print("기본 프롬프트로 시작합니다.")
        return create_default_prompts()

    print(f"{os.path.basename(path)}에서 프롬프트 {len(prompts)}개를 불러왔습니다.")
    return prompts


def save_prompts(prompts, path):
    """프롬프트 목록을 JSON 파일로 저장한다.

    임시 파일에 먼저 쓴 뒤 바꿔치기해서, 저장 도중 문제가 생겨도 기존 파일이 깨지지 않게 한다.
    """
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(prompts, file, ensure_ascii=False, indent=2)
    os.replace(temp_path, path)


def safe_filename(name):
    """파일 이름에 쓸 수 없는 문자를 '_'로 바꾼다. (예: '학습/요약' → '학습_요약')"""
    cleaned = "".join("_" if char in '\\/:*?"<>|' else char for char in name).strip()
    return cleaned or "카테고리"


def code_fence(text):
    """내용 안의 ``` 보다 긴 백틱 울타리를 만들어 코드 블록이 중간에 끊기지 않게 한다."""
    longest = run = 0
    for char in text:
        run = run + 1 if char == "`" else 0
        longest = max(longest, run)
    return "`" * max(3, longest + 1)


def build_category_markdown(category, matches):
    """한 카테고리의 프롬프트들을 Markdown 문서 문자열로 만든다."""
    lines = [f"# {category}", "", f"총 {len(matches)}개의 프롬프트", ""]
    for number, prompt in matches:
        star = " ⭐" if prompt["favorite"] else ""
        fence = code_fence(prompt["content"])
        lines += [
            f"## {number}. {prompt['title']}{star}",
            "",
            f"- 즐겨찾기: {'예' if prompt['favorite'] else '아니오'}",
            f"- 조회수: {prompt['views']}",
            "",
            fence + "text",
            prompt["content"],
            fence,
            "",
        ]
    return "\n".join(lines)


def export_markdown_files(prompts, export_dir):
    """카테고리별 Markdown 파일을 만들고, 만든 파일 경로 목록을 반환한다.

    export_dir는 내보내기 전용 폴더라서, 지난번에 만든 .md 파일은 지우고 새로 만든다
    (삭제되거나 이름이 바뀐 카테고리 파일이 남지 않도록).
    """
    os.makedirs(export_dir, exist_ok=True)
    for name in os.listdir(export_dir):
        if name.endswith(".md"):
            os.remove(os.path.join(export_dir, name))

    paths = []
    for category in get_all_categories(prompts):
        matches = find_prompts(prompts, lambda prompt: prompt["category"] == category)
        if not matches:
            continue
        path = os.path.join(export_dir, safe_filename(category) + ".md")
        with open(path, "w", encoding="utf-8") as file:
            file.write(build_category_markdown(category, matches))
        paths.append(path)
    return paths


def export_markdown(prompts):
    """전체 프롬프트를 카테고리별 Markdown 파일로 내보낸다."""
    print("\n=== Markdown 내보내기 ===")
    if not prompts:
        print("내보낼 프롬프트가 없습니다.")
        return False
    try:
        paths = export_markdown_files(prompts, EXPORT_DIR)
    except OSError as error:
        print(f"내보내기에 실패했습니다: {error}")
        return False

    print(f"{os.path.basename(EXPORT_DIR)}/ 폴더에 {len(paths)}개 파일을 만들었습니다.")
    for path in paths:
        print(f"- {os.path.relpath(path, BASE_DIR)}")
    return False


def input_or_keep(label, current):
    """새 값을 입력받는다. 아무것도 입력하지 않으면(Enter) 현재 값을 그대로 둔다."""
    value = input(f"{label} (Enter = 그대로 유지): ").strip()
    return value if value else current


def edit_prompt(prompts):
    """선택한 프롬프트의 제목/내용/카테고리를 수정한다."""
    print("\n=== 프롬프트 수정 ===")
    prompt = select_prompt(prompts)
    if prompt is None:
        return False

    print(f"\n현재 제목: {prompt['title']}")
    title = input_or_keep("새 제목", prompt["title"])
    if not check_duplicate_title(prompts, title, exclude=prompt):
        print("수정을 취소했습니다.")
        return False

    print(f"\n현재 내용: {prompt['content']}")
    content = input_or_keep("새 내용", prompt["content"])

    print(f"\n현재 카테고리: {prompt['category']}")
    category = prompt["category"]
    if confirm("카테고리를 변경할까요?"):
        category = choose_category()

    if (title, content, category) == (prompt["title"], prompt["content"], prompt["category"]):
        print("\n변경된 내용이 없습니다.")
        return False
    prompt["title"] = title
    prompt["content"] = content
    prompt["category"] = category
    print("\n프롬프트가 수정되었습니다!")
    return True


def delete_prompt(prompts):
    """선택한 프롬프트를 확인 후 삭제한다."""
    print("\n=== 프롬프트 삭제 ===")
    prompt = select_prompt(prompts)
    if prompt is None:
        return False
    if not confirm(f"'{prompt['title']}' 프롬프트를 삭제할까요?"):
        print("삭제를 취소했습니다.")
        return False

    prompts.remove(prompt)
    print("프롬프트가 삭제되었습니다. (뒤의 프롬프트 번호가 하나씩 당겨집니다)")
    return True


TOP_LIMIT = 5


def get_top_prompts(prompts, limit=TOP_LIMIT):
    """조회수가 1 이상인 프롬프트를 조회수 높은 순으로 최대 limit개 반환한다.

    sort는 안정 정렬이라 조회수가 같으면 목록 순서(먼저 등록된 것)가 앞에 온다.
    """
    matches = find_prompts(prompts, lambda prompt: prompt["views"] > 0)
    matches.sort(key=lambda match: match[1]["views"], reverse=True)
    return matches[:limit]


def show_top(prompts):
    """조회수 기준 인기 프롬프트 Top 목록을 출력한다."""
    print(f"\n=== 많이 본 프롬프트 Top {TOP_LIMIT} ===")
    top = get_top_prompts(prompts)
    if not top:
        print("아직 조회한 프롬프트가 없습니다. (메뉴 5번 상세 보기로 조회수가 쌓입니다)")
        return False
    for rank, (number, prompt) in enumerate(top, start=1):
        star = " ⭐" if prompt["favorite"] else ""
        print(f"{rank}위. ({prompt['views']}회) {number}. [{prompt['category']}] {prompt['title']}{star}")
    return False


# 메뉴 번호 → (이름, 처리 함수). 처리 함수는 데이터를 바꿨으면 True를 반환한다.
MENU_ITEMS = [
    ("1", "프롬프트 추가", add_prompt),
    ("2", "프롬프트 목록", show_list),
    ("3", "카테고리별 조회", show_by_category),
    ("4", "프롬프트 검색", search_prompt),
    ("5", "프롬프트 상세 보기", show_detail),
    ("6", "즐겨찾기 추가/해제", toggle_favorite),
    ("7", "즐겨찾기 목록", show_favorites),
    ("8", "카테고리별 Markdown 내보내기", export_markdown),
    ("9", "프롬프트 수정", edit_prompt),
    ("10", "프롬프트 삭제", delete_prompt),
    ("11", f"많이 본 프롬프트 Top {TOP_LIMIT}", show_top),
]


def show_menu():
    """메인 메뉴를 출력한다."""
    print()
    print("=== 나만의 프롬프트 관리 ===")
    for key, label, _ in MENU_ITEMS:
        print(f"{key}. {label}")
    print("0. 종료")


def find_menu_handler(choice):
    """메뉴 번호에 해당하는 처리 함수를 찾는다. 없으면 None."""
    for key, _, handler in MENU_ITEMS:
        if key == choice:
            return handler
    return None


def main(data_file=DATA_FILE):
    prompts = load_prompts(data_file)

    while True:
        show_menu()
        choice = input("선택: ").strip()

        if choice == "0":
            print("프로그램을 종료합니다.")
            break

        handler = find_menu_handler(choice)
        if handler is None:
            print(f"잘못된 입력입니다. 메뉴 번호(0~{len(MENU_ITEMS)})를 입력해주세요.")
            continue
        if handler(prompts):
            try:
                save_prompts(prompts, data_file)
                print(f"(변경 내용을 {os.path.basename(data_file)}에 저장했습니다)")
            except OSError as error:
                print(f"저장에 실패했습니다: {error}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 종료합니다.")
