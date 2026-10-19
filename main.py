"""나만의 프롬프트 관리 프로그램 (콘솔)"""


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


# 메뉴 번호 → (이름, 처리 함수). 처리 함수는 데이터를 바꿨으면 True를 반환한다.
MENU_ITEMS = []


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
    prompts = []

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
