"""main.py 기능 테스트 (표준 라이브러리 unittest만 사용)

실행: python3 -m unittest discover -s tests -v
"""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main  # noqa: E402


def run_with_inputs(func, inputs, *args):
    """inputs를 차례로 입력한 것처럼 func를 실행하고 (반환값, 출력 문자열)을 돌려준다."""
    output = io.StringIO()
    with patch("builtins.input", side_effect=list(inputs)), redirect_stdout(output):
        result = func(*args)
    return result, output.getvalue()


class PromptTestCase(unittest.TestCase):
    def setUp(self):
        self.prompts = main.create_default_prompts()


class AddPromptTest(PromptTestCase):
    def test_add_prompt_is_listed(self):
        changed, _ = run_with_inputs(main.add_prompt, ["새 프롬프트", "내용", "1"], self.prompts)
        self.assertTrue(changed)
        self.assertEqual(self.prompts[-1]["title"], "새 프롬프트")
        self.assertEqual(self.prompts[-1]["category"], "텍스트 생성")
        self.assertFalse(self.prompts[-1]["favorite"])
        self.assertEqual(self.prompts[-1]["views"], 0)

        _, output = run_with_inputs(main.show_list, [], self.prompts)
        self.assertIn("7. [텍스트 생성] 새 프롬프트", output)

    def test_empty_and_out_of_range_inputs_are_asked_again(self):
        inputs = ["", "   ", "제목", "내용", "99", "abc", "7", "", "직접 카테고리"]
        _, output = run_with_inputs(main.add_prompt, inputs, self.prompts)
        self.assertIn("입력값이 비어 있습니다", output)
        self.assertIn("1~7 사이의 번호", output)
        self.assertIn("숫자를 입력해주세요", output)
        self.assertEqual(self.prompts[-1]["category"], "직접 카테고리")

    def test_duplicate_title_can_be_cancelled(self):
        count = len(self.prompts)
        changed, output = run_with_inputs(main.add_prompt, ["  회의록   3줄 요약 ", "n"], self.prompts)
        self.assertFalse(changed)
        self.assertIn("같은 제목", output)
        self.assertEqual(len(self.prompts), count)

    def test_ids_stay_unique_after_delete(self):
        self.prompts.pop()  # 마지막(id 6) 삭제
        self.prompts.pop(0)  # 첫 번째(id 1) 삭제
        run_with_inputs(main.add_prompt, ["새 제목", "내용", "1"], self.prompts)
        ids = [prompt["id"] for prompt in self.prompts]
        self.assertEqual(len(ids), len(set(ids)))


class QueryTest(PromptTestCase):
    def test_category_shows_only_that_category(self):
        _, output = run_with_inputs(main.show_by_category, ["4"], self.prompts)  # 학습/요약
        lines = [line for line in output.splitlines() if line[:1].isdigit() and ". [" in line]
        self.assertEqual(len(lines), 2)
        self.assertTrue(all("[학습/요약]" in line for line in lines))

    def test_custom_category_appears_in_category_list(self):
        self.prompts.append(main.make_prompt(self.prompts, "t", "c", "나만의 분류"))
        self.assertIn("나만의 분류", main.get_all_categories(self.prompts))

    def test_search_matches_title_or_content_ignoring_case(self):
        title_hit = main.find_prompts(self.prompts, lambda p: main.matches_keyword(p, "이메일"))
        content_hit = main.find_prompts(self.prompts, lambda p: main.matches_keyword(p, "PANDAS"))
        no_hit = main.find_prompts(self.prompts, lambda p: main.matches_keyword(p, "없는검색어"))
        self.assertEqual([number for number, _ in title_hit], [2])
        self.assertEqual([number for number, _ in content_hit], [6])
        self.assertEqual(no_hit, [])

    def test_search_result_keeps_full_list_numbers(self):
        _, output = run_with_inputs(main.search_prompt, ["엑셀"], self.prompts)
        self.assertIn("6. [업무 자동화] 엑셀 데이터 정리 자동화", output)


class FavoriteTest(PromptTestCase):
    def test_toggle_on_and_off(self):
        run_with_inputs(main.toggle_favorite, ["2"], self.prompts)
        self.assertTrue(self.prompts[1]["favorite"])
        _, output = run_with_inputs(main.show_favorites, [], self.prompts)
        self.assertIn("정중한 업무 이메일 작성 ⭐", output)

        run_with_inputs(main.toggle_favorite, ["2"], self.prompts)
        self.assertFalse(self.prompts[1]["favorite"])

    def test_invalid_number_changes_nothing(self):
        before = [prompt["favorite"] for prompt in self.prompts]
        changed, _ = run_with_inputs(main.toggle_favorite, ["0"], self.prompts)
        self.assertFalse(changed)
        self.assertEqual(before, [prompt["favorite"] for prompt in self.prompts])


class EditDeleteTest(PromptTestCase):
    def test_edit_keeps_value_on_enter(self):
        changed, _ = run_with_inputs(main.edit_prompt, ["2", "", "새 내용", "n"], self.prompts)
        self.assertTrue(changed)
        self.assertEqual(self.prompts[1]["title"], "정중한 업무 이메일 작성")
        self.assertEqual(self.prompts[1]["content"], "새 내용")

    def test_edit_category(self):
        run_with_inputs(main.edit_prompt, ["2", "", "", "y", "3"], self.prompts)
        self.assertEqual(self.prompts[1]["category"], "코드 작성")

    def test_delete_requires_confirmation(self):
        count = len(self.prompts)
        run_with_inputs(main.delete_prompt, ["1", "n"], self.prompts)
        self.assertEqual(len(self.prompts), count)
        run_with_inputs(main.delete_prompt, ["1", "y"], self.prompts)
        self.assertEqual(len(self.prompts), count - 1)
        self.assertNotEqual(self.prompts[0]["title"], "회의록 3줄 요약")


class ViewsTest(PromptTestCase):
    def test_detail_increments_views(self):
        run_with_inputs(main.show_detail, ["3"], self.prompts)
        _, output = run_with_inputs(main.show_detail, ["3"], self.prompts)
        self.assertEqual(self.prompts[2]["views"], 2)
        self.assertIn("조회수: 2회", output)

    def test_top_sorted_by_views_then_list_order(self):
        for number, views in [(1, 1), (3, 5), (4, 2), (6, 2)]:
            self.prompts[number - 1]["views"] = views
        top = main.get_top_prompts(self.prompts, limit=3)
        self.assertEqual([number for number, _ in top], [3, 4, 6])

    def test_top_excludes_unviewed(self):
        self.assertEqual(main.get_top_prompts(self.prompts), [])


class PersistenceTest(PromptTestCase):
    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "prompts.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def load(self):
        with redirect_stdout(io.StringIO()):
            return main.load_prompts(self.path)

    def test_save_and_load_round_trip(self):
        self.prompts[0]["views"] = 3
        self.prompts[1]["favorite"] = True
        main.save_prompts(self.prompts, self.path)
        self.assertEqual(self.load(), self.prompts)
        with open(self.path, encoding="utf-8") as file:
            self.assertIn("회의록 3줄 요약", file.read())  # 한글이 그대로 저장됨

    def test_missing_file_starts_with_defaults(self):
        self.assertEqual(len(self.load()), len(main.DEFAULT_PROMPTS))

    def test_broken_file_is_backed_up(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("{깨진 json")
        prompts = self.load()
        self.assertEqual(len(prompts), len(main.DEFAULT_PROMPTS))
        self.assertTrue(os.path.exists(self.path + ".broken"))

    def test_missing_optional_fields_are_filled(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump([{"title": "a", "content": "b", "category": "기타"}], file)
        prompt = self.load()[0]
        self.assertEqual((prompt["id"], prompt["favorite"], prompt["views"]), (1, False, 0))

    def test_main_saves_changes_and_keeps_them_after_restart(self):
        inputs = ["6", "2", "0"]  # 2번 즐겨찾기 추가 후 종료
        run_with_inputs(main.main, inputs, self.path)
        self.assertTrue(self.load()[1]["favorite"])


class ExportTest(PromptTestCase):
    def test_export_one_file_per_category(self):
        with tempfile.TemporaryDirectory() as export_dir:
            with open(os.path.join(export_dir, "지난번.md"), "w", encoding="utf-8") as file:
                file.write("old")
            paths = main.export_markdown_files(self.prompts, export_dir)
            names = sorted(os.path.basename(path) for path in paths)
            self.assertEqual(names, sorted(os.listdir(export_dir)))
            self.assertIn("학습_요약.md", names)
            self.assertNotIn("기타.md", names)  # 프롬프트가 없는 카테고리는 만들지 않음

            with open(os.path.join(export_dir, "학습_요약.md"), encoding="utf-8") as file:
                text = file.read()
            self.assertTrue(text.startswith("# 학습/요약"))
            self.assertIn("## 1. 회의록 3줄 요약 ⭐", text)
            self.assertIn("## 5. 개념 설명 (초등학생 눈높이)", text)

    def test_code_fence_is_longer_than_backticks_in_content(self):
        self.assertEqual(main.code_fence("plain"), "```")
        self.assertEqual(main.code_fence("```python\nx\n```"), "````")


class MenuTest(unittest.TestCase):
    def test_invalid_menu_then_exit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "prompts.json")
            _, output = run_with_inputs(main.main, ["99", "abc", "0"], path)
        self.assertEqual(output.count("잘못된 입력입니다"), 2)
        self.assertIn("프로그램을 종료합니다.", output)
        self.assertFalse(os.path.exists(path))  # 아무것도 바꾸지 않으면 저장하지 않음


if __name__ == "__main__":
    unittest.main()
