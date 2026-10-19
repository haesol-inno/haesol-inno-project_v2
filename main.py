"""나만의 프롬프트 관리 프로그램 (콘솔)"""

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


# 메뉴 번호 → (이름, 처리 함수). 처리 함수는 데이터를 바꿨으면 True를 반환한다.
MENU_ITEMS = [
    ("1", "프롬프트 추가", add_prompt),
    ("2", "프롬프트 목록", show_list),
    ("3", "카테고리별 조회", show_by_category),
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


def main():
    prompts = create_default_prompts()

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
        handler(prompts)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 종료합니다.")
