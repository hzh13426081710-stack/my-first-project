"""学生成绩录入与等级统计程序。"""

from __future__ import annotations

from dataclasses import dataclass


MIN_SCORE = 0.0
MAX_SCORE = 100.0
SUBJECTS = ("语文", "数学", "英语")


@dataclass
class Student:
    """保存单个学生的成绩信息。"""

    name: str
    chinese_score: float
    math_score: float
    english_score: float

    @property
    def total_score(self) -> float:
        return self.chinese_score + self.math_score + self.english_score

    @property
    def average_score(self) -> float:
        return self.total_score / len(SUBJECTS)

    @property
    def grade(self) -> str:
        return calculate_grade(self.total_score)


def read_positive_int(prompt: str) -> int:
    """读取正整数，直到输入合法为止。"""
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
        except ValueError:
            print("输入无效，请输入一个正整数。")
            continue

        if number <= 0:
            print("人数必须大于 0，请重新输入。")
            continue

        return number


def read_non_empty_text(prompt: str) -> str:
    """读取非空字符串。"""
    while True:
        value = input(prompt).strip()
        if value:
            return value

        print("姓名不能为空，请重新输入。")


def read_score(subject: str) -> float:
    """读取 0 到 100 之间的成绩，直到输入合法为止。"""
    while True:
        value = input(f"请输入{subject}分数：").strip()
        try:
            score = float(value)
        except ValueError:
            print("输入无效，请输入数字。")
            continue

        if MIN_SCORE <= score <= MAX_SCORE:
            return score

        print("分数必须在 0 到 100 之间，请重新输入。")


def calculate_grade(total_score: float) -> str:
    """根据三科总分计算等级。"""
    if total_score >= 270:
        return "A"
    if total_score >= 240:
        return "B"
    if total_score >= 210:
        return "C"
    return "D"


def read_student(index: int) -> Student:
    """读取单个学生的信息。"""
    print(f"\n第 {index} 位学生")
    name = read_non_empty_text("请输入姓名：")
    chinese_score = read_score("语文")
    math_score = read_score("数学")
    english_score = read_score("英语")
    return Student(name, chinese_score, math_score, english_score)


def print_student_result(student: Student) -> None:
    """打印单个学生的成绩结果。"""
    print(
        f"{student.name} "
        f"总分：{student.total_score:.2f} "
        f"平均分：{student.average_score:.2f} "
        f"等级：{student.grade}"
    )


def print_summary(total_count: int, grade_counts: dict[str, int]) -> None:
    """打印班级等级统计。"""
    print("\n班级统计结果")
    print(f"班级总人数：{total_count}")
    for grade in ("A", "B", "C", "D"):
        print(f"{grade} 级人数：{grade_counts[grade]}")


def main() -> None:
    total_count = read_positive_int("请输入班级人数：")
    grade_counts = dict.fromkeys(("A", "B", "C", "D"), 0)

    for index in range(1, total_count + 1):
        student = read_student(index)
        grade_counts[student.grade] += 1
        print_student_result(student)

    print_summary(total_count, grade_counts)


if __name__ == "__main__":
    main()
