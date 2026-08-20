#!/usr/bin/env python3
"""Validate structured course-paper grading results using only the stdlib."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


def number(value: Any, label: str, errors: list[str]) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        errors.append(f"{label}: expected a number, got {value!r}")
        return Decimal("0")


def rounded(value: Decimal, digits: int) -> Decimal:
    quantum = Decimal("1").scaleb(-digits)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def calculate_total(
    course: dict[str, Any], student: dict[str, Any], errors: list[str], label: str
) -> Decimal | None:
    mode = course.get("formula_mode")
    paper = number(student.get("paper_score"), f"{label}.paper_score", errors)
    attendance = number(
        student.get("attendance_score"), f"{label}.attendance_score", errors
    )
    presentation = number(
        student.get("presentation_score"), f"{label}.presentation_score", errors
    )

    if mode == "weighted_components":
        paper_weight = number(
            course.get("paper_weight", 0.5), "course.paper_weight", errors
        )
        return attendance + presentation + paper * paper_weight

    if mode == "weighted_average":
        weights = course.get(
            "weights", {"attendance": 0.2, "presentation": 0.3, "paper": 0.5}
        )
        if not isinstance(weights, dict):
            errors.append("course.weights: expected an object")
            return None
        attendance_weight = number(
            weights.get("attendance"), "course.weights.attendance", errors
        )
        presentation_weight = number(
            weights.get("presentation"), "course.weights.presentation", errors
        )
        paper_weight = number(weights.get("paper"), "course.weights.paper", errors)
        if attendance_weight + presentation_weight + paper_weight != Decimal("1"):
            errors.append("course.weights: weights must sum to 1")
        return (
            attendance * attendance_weight
            + presentation * presentation_weight
            + paper * paper_weight
        )

    errors.append(
        "course.formula_mode: expected 'weighted_average' or 'weighted_components'"
    )
    return None


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"input: cannot read valid UTF-8 JSON: {exc}"]

    course = data.get("course")
    students = data.get("students")
    if not isinstance(course, dict):
        return ["course: expected an object"]
    if not isinstance(students, list) or not students:
        return ["students: expected a non-empty array"]

    rubric = course.get("rubric")
    if not isinstance(rubric, dict) or not rubric:
        errors.append("course.rubric: expected a non-empty object")
        rubric = {}

    digits = int(course.get("round_digits", 1))
    min_comment = int(course.get("comment_min_chars", 0))
    min_reason = int(course.get("reason_min_chars", 0))
    ids: set[str] = set()
    totals: list[Decimal] = []

    for index, student in enumerate(students, start=1):
        if not isinstance(student, dict):
            errors.append(f"students[{index}]: expected an object")
            continue

        student_id = str(student.get("student_id", "")).strip()
        name = str(student.get("name", "")).strip()
        label = f"students[{index}]({student_id or name or 'unknown'})"
        if not student_id:
            errors.append(f"{label}.student_id: missing")
        elif student_id in ids:
            errors.append(f"{label}.student_id: duplicate {student_id!r}")
        else:
            ids.add(student_id)
        if not name:
            errors.append(f"{label}.name: missing")

        scores = student.get("scores")
        if not isinstance(scores, dict):
            errors.append(f"{label}.scores: expected an object")
            scores = {}

        score_sum = Decimal("0")
        for item, maximum_raw in rubric.items():
            maximum = number(maximum_raw, f"course.rubric.{item}", errors)
            if item not in scores:
                errors.append(f"{label}.scores.{item}: missing")
                continue
            value = number(scores[item], f"{label}.scores.{item}", errors)
            if value < 0 or value > maximum:
                errors.append(
                    f"{label}.scores.{item}: {value} outside 0..{maximum}"
                )
            score_sum += value

        extra_items = sorted(set(scores) - set(rubric))
        if extra_items:
            errors.append(f"{label}.scores: unknown item(s) {', '.join(extra_items)}")

        paper_score = number(student.get("paper_score"), f"{label}.paper_score", errors)
        if score_sum != paper_score:
            errors.append(
                f"{label}.paper_score: reported {paper_score}, item sum is {score_sum}"
            )

        expected_total = calculate_total(course, student, errors, label)
        reported_total = number(
            student.get("course_total"), f"{label}.course_total", errors
        )
        if expected_total is not None:
            expected_total = rounded(expected_total, digits)
            if reported_total != expected_total:
                errors.append(
                    f"{label}.course_total: reported {reported_total}, expected {expected_total}"
                )
        totals.append(reported_total)

        score_range = course.get("course_total_range")
        if isinstance(score_range, list) and len(score_range) == 2:
            lower = number(score_range[0], "course.course_total_range[0]", errors)
            upper = number(score_range[1], "course.course_total_range[1]", errors)
            if reported_total < lower or reported_total > upper:
                errors.append(
                    f"{label}.course_total: {reported_total} outside {lower}..{upper}"
                )

        reason = str(student.get("reason", "")).strip()
        if len(reason) < min_reason:
            errors.append(
                f"{label}.reason: {len(reason)} chars, minimum is {min_reason}"
            )
        comment = str(student.get("comment", "")).strip()
        if len(comment) < min_comment:
            errors.append(
                f"{label}.comment: {len(comment)} chars, minimum is {min_comment}"
            )
        keywords = student.get("content_keywords", [])
        if keywords and isinstance(keywords, list):
            if not any(str(keyword) in comment for keyword in keywords):
                errors.append(
                    f"{label}.comment: none of content_keywords appears in comment"
                )

    max_same = int(course.get("max_same_total", 0) or 0)
    if max_same > 0:
        for value, count in Counter(totals).items():
            if count > max_same:
                errors.append(
                    f"course_total: {value} appears {count} times; maximum is {max_same}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate paper item scores, course totals, and comment completeness."
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON grading file")
    args = parser.parse_args()
    errors = validate(args.input)
    if errors:
        print(f"FAIL: {len(errors)} issue(s) found.")
        for error in errors:
            print(f"- {error}")
        return 1
    data = json.loads(args.input.read_text(encoding="utf-8"))
    print(f"PASS: {len(data['students'])} record(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
