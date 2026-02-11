#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from dataclasses import dataclass, field
from typing import TypeVar, Generic, List, Optional, Any, Iterator
from functools import total_ordering

# Определяем TypeVar с ограничением сравнения
T = TypeVar("T", bound="Comparable")


class Comparable:
    """Класс-маркер для типов, поддерживающих сравнение"""

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._compare_to(other) < 0

    def _compare_to(self, other: Any) -> int:
        """Метод, который должен быть реализован в наследниках"""
        raise NotImplementedError("Должен быть реализован в наследниках")


@dataclass(order=True, frozen=True)
class Range(Generic[T]):
    """
    Универсальный диапазон значений от start до end (не включая end)

    Атрибуты:
        start: начальное значение диапазона
        end: конечное значение диапазона
    """

    start: T
    end: T

    def __post_init__(self) -> None:
        """Проверка, что start < end"""
        if self.start >= self.end:
            raise ValueError(
                f"start ({self.start}) должен быть меньше end ({self.end})"
            )

    @property
    def length(self) -> Any:
        """Длина диапазона (разность end - start)"""
        try:
            return self.end - self.start
        except TypeError:
            # Для типов, не поддерживающих вычитание
            return None

    def contains(self, value: T) -> bool:
        """Проверяет, содержится ли значение в диапазоне [start, end)"""
        return self.start <= value < self.end

    def overlaps(self, other: "Range[T]") -> bool:
        """Проверяет, пересекается ли диапазон с другим диапазоном"""
        return not (self.end <= other.start or self.start >= other.end)

    def intersection(self, other: "Range[T]") -> Optional["Range[T]"]:
        """Возвращает пересечение двух диапазонов или None если нет пересечения"""
        if not self.overlaps(other):
            return None

        start = max(self.start, other.start)
        end = min(self.end, other.end)

        return Range(start, end)

    def union(self, other: "Range[T]") -> List["Range[T]"]:
        """Возвращает объединение двух диапазонов"""
        if not self.overlaps(other) and not self.is_adjacent_to(other):
            return [self, other]

        start = min(self.start, other.start)
        end = max(self.end, other.end)

        return [Range(start, end)]

    def is_adjacent_to(self, other: "Range[T]") -> bool:
        """Проверяет, являются ли диапазоны смежными"""
        return self.end == other.start or self.start == other.end

    def split(self, point: T) -> List["Range[T]"]:
        """Разделяет диапазон в указанной точке"""
        if not self.contains(point):
            raise ValueError(f"Точка {point} не находится в диапазоне {self}")

        return [Range(self.start, point), Range(point, self.end)]

    def __contains__(self, value: T) -> bool:
        """Поддержка оператора 'in'"""
        return self.contains(value)

    def __len__(self) -> Optional[int]:
        """Длина диапазона для целочисленных типов"""
        if isinstance(self.start, int) and isinstance(self.end, int):
            return self.end - self.start
        return None

    def __iter__(self) -> Iterator[T]:
        """Итерация по значениям диапазона (только для int)"""
        if isinstance(self.start, int) and isinstance(self.end, int):
            current = self.start
            while current < self.end:
                yield current
                current += 1
        else:
            raise TypeError(
                "Итерация поддерживается только для целочисленных диапазонов"
            )

    def __str__(self) -> str:
        """Строковое представление"""
        return f"[{self.start}, {self.end})"


# Реализация конкретных типов для демонстрации
@dataclass(order=True, frozen=True)
class ComparableInt(Comparable):
    """Целое число с поддержкой сравнения"""

    value: int

    def _compare_to(self, other: "ComparableInt") -> int:
        return self.value - other.value

    def __add__(self, other: Any) -> "ComparableInt":
        if isinstance(other, ComparableInt):
            return ComparableInt(self.value + other.value)
        elif isinstance(other, int):
            return ComparableInt(self.value + other)
        return NotImplemented

    def __sub__(self, other: Any) -> "ComparableInt":
        if isinstance(other, ComparableInt):
            return ComparableInt(self.value - other.value)
        elif isinstance(other, int):
            return ComparableInt(self.value - other)
        return NotImplemented

    def __str__(self) -> str:
        return str(self.value)


@dataclass(order=True, frozen=True)
class ComparableFloat(Comparable):
    """Вещественное число с поддержкой сравнения"""

    value: float

    def _compare_to(self, other: "ComparableFloat") -> int:
        if self.value < other.value:
            return -1
        elif self.value > other.value:
            return 1
        else:
            return 0

    def __str__(self) -> str:
        return f"{self.value:.2f}"


# Контейнер для работы с коллекцией диапазонов
@dataclass
class RangeContainer(Generic[T]):
    """Контейнер для хранения и работы с множеством диапазонов"""

    name: str
    ranges: List[Range[T]] = field(default_factory=list)

    def add_range(self, range_obj: Range[T]) -> None:
        """Добавить диапазон в контейнер"""
        self.ranges.append(range_obj)

    def add_ranges(self, *ranges: Range[T]) -> None:
        """Добавить несколько диапазонов"""
        for r in ranges:
            self.add_range(r)

    def find_containing_range(self, value: T) -> Optional[Range[T]]:
        """Найти диапазон, содержащий указанное значение"""
        for r in self.ranges:
            if value in r:
                return r
        return None

    def merge_overlapping_ranges(self) -> "RangeContainer[T]":
        """Объединить пересекающиеся диапазоны"""
        if not self.ranges:
            return RangeContainer(self.name + "_merged", [])

        # Сортируем диапазоны по start
        sorted_ranges = sorted(self.ranges, key=lambda x: x.start)
        merged = [sorted_ranges[0]]

        for current in sorted_ranges[1:]:
            last = merged[-1]

            # Если пересекаются или смежные - объединяем
            if last.overlaps(current) or last.is_adjacent_to(current):
                new_start = min(last.start, current.start)
                new_end = max(last.end, current.end)
                merged[-1] = Range(new_start, new_end)
            else:
                merged.append(current)

        return RangeContainer(self.name + "_merged", merged)

    def get_total_coverage(self) -> Optional[Range[T]]:
        """Получить общий охватывающий диапазон"""
        if not self.ranges:
            return None

        starts = [r.start for r in self.ranges]
        ends = [r.end for r in self.ranges]

        return Range(min(starts), max(ends))

    def filter_by_value(self, value: T) -> List[Range[T]]:
        """Получить все диапазоны, содержащие указанное значение"""
        return [r for r in self.ranges if value in r]

    def get_gaps(self) -> List[Range[T]]:
        """Получить все промежутки между диапазонами"""
        if len(self.ranges) < 2:
            return []

        sorted_ranges = sorted(self.ranges, key=lambda x: x.start)
        gaps = []

        for i in range(len(sorted_ranges) - 1):
            current = sorted_ranges[i]
            next_range = sorted_ranges[i + 1]

            if current.end < next_range.start:
                gaps.append(Range(current.end, next_range.start))

        return gaps

    def __len__(self) -> int:
        """Количество диапазонов в контейнере"""
        return len(self.ranges)

    def __str__(self) -> str:
        """Строковое представление"""
        ranges_str = "\n  ".join(str(r) for r in self.ranges)
        return f"RangeContainer '{self.name}' ({len(self)} диапазонов):\n  {ranges_str}"


def demonstrate_range_operations() -> None:
    """Демонстрация работы с универсальными диапазонами"""

    print("=== Демонстрация универсального класса Range ===\n")

    # 1. Работа с целыми числами
    print("1. Диапазоны целых чисел:")
    int_range1 = Range(ComparableInt(1), ComparableInt(10))
    int_range2 = Range(ComparableInt(5), ComparableInt(15))
    int_range3 = Range(ComparableInt(20), ComparableInt(25))

    print(f"   Range 1: {int_range1}")
    print(f"   Range 2: {int_range2}")
    print(f"   Range 3: {int_range3}")
    print(f"   Длина Range 1: {int_range1.length}")
    print(f"   5 в Range 1? {ComparableInt(5) in int_range1}")
    print(f"   15 в Range 1? {ComparableInt(15) in int_range1}")
    print(f"   Range 1 и Range 2 пересекаются? {int_range1.overlaps(int_range2)}")
    print(f"   Пересечение Range 1 и Range 2: {int_range1.intersection(int_range2)}")

    # 2. Работа с вещественными числами
    print("\n2. Диапазоны вещественных чисел:")
    float_range1 = Range(ComparableFloat(1.5), ComparableFloat(5.5))
    float_range2 = Range(ComparableFloat(3.0), ComparableFloat(7.0))

    print(f"   Float Range 1: {float_range1}")
    print(f"   Float Range 2: {float_range2}")
    print(f"   3.14 в Float Range 1? {ComparableFloat(3.14) in float_range1}")
    print(f"   Пересечение: {float_range1.intersection(float_range2)}")

    # 3. Сравнение диапазонов
    print("\n3. Сравнение диапазонов:")
    print(
        f"   Range [1, 5) < Range [2, 6)? {Range(ComparableInt(1), ComparableInt(5)) < Range(ComparableInt(2), ComparableInt(6))}"
    )
    print(
        f"   Range [1, 5) == Range [1, 5)? {Range(ComparableInt(1), ComparableInt(5)) == Range(ComparableInt(1), ComparableInt(5))}"
    )

    # 4. Работа с контейнером
    print("\n4. Работа с контейнером диапазонов:")
    container = RangeContainer("TestContainer")
    container.add_ranges(int_range1, int_range2, int_range3)

    print(container)
    print(f"   Всего диапазонов: {len(container)}")

    # 5. Поиск в контейнере (ИСПРАВЛЕННЫЙ КОД)
    print("\n5. Поиск в контейнере:")
    test_values = [ComparableInt(3), ComparableInt(12), ComparableInt(22)]
    for val in test_values:
        found = container.find_containing_range(val)
        if found is not None:  # Явная проверка на None
            print(f"   Значение {val} находится в диапазоне {found}")
        else:
            print(f"   Значение {val} не найдено ни в одном диапазоне")

    # 6. Объединение диапазонов
    print("\n6. Объединение пересекающихся диапазонов:")
    merged_container = container.merge_overlapping_ranges()
    print(merged_container)

    # 7. Общий охват и промежутки
    print("\n7. Общий охват и промежутки:")
    total_coverage = container.get_total_coverage()
    print(f"   Общий охват: {total_coverage}")

    gaps = container.get_gaps()
    if gaps:
        print(f"   Промежутки между диапазонами: {gaps}")
    else:
        print("   Промежутков нет")

    # 8. Фильтрация
    print("\n8. Фильтрация диапазонов по значению:")
    value_to_find = ComparableInt(7)
    containing_ranges = container.filter_by_value(value_to_find)
    print(f"   Диапазоны, содержащие {value_to_find}: {containing_ranges}")

    # 9. Разделение диапазона
    print("\n9. Разделение диапазона:")
    try:
        split_result = int_range1.split(ComparableInt(5))
        print(f"   Разделение {int_range1} в точке 5: {split_result}")
    except ValueError as e:
        print(f"   Ошибка при разделении: {e}")

    # 10. Проверка на смежность
    print("\n10. Проверка на смежность:")
    range_a = Range(ComparableInt(1), ComparableInt(5))
    range_b = Range(ComparableInt(5), ComparableInt(10))
    range_c = Range(ComparableInt(10), ComparableInt(15))

    print(f"   {range_a} смежен с {range_b}? {range_a.is_adjacent_to(range_b)}")
    print(f"   {range_a} смежен с {range_c}? {range_a.is_adjacent_to(range_c)}")

    # 11. Объединение смежных диапазонов
    print("\n11. Объединение смежных диапазонов:")
    adjacent_container = RangeContainer("Adjacent")
    adjacent_container.add_ranges(range_a, range_b, range_c)
    print("   До объединения:")
    print(f"   {adjacent_container}")
    print("   После объединения:")
    merged_adjacent = adjacent_container.merge_overlapping_ranges()
    print(f"   {merged_adjacent}")

    # 12. Итерация по целочисленному диапазону
    print("\n12. Итерация по целочисленному диапазону:")
    iter_range = Range(ComparableInt(1), ComparableInt(6))
    print(f"   Значения в диапазоне {iter_range}: ", end="")
    for val in iter_range:
        print(f"{val} ", end="")
    print()

    # 13. Обработка ошибок
    print("\n13. Обработка ошибок:")
    try:
        bad_range = Range(ComparableInt(10), ComparableInt(1))  # start > end
    except ValueError as e:
        print(f"   Ошибка при создании диапазона: {e}")

    try:
        bad_split = int_range1.split(ComparableInt(15))  # точка вне диапазона
    except ValueError as e:
        print(f"   Ошибка при разделении: {e}")

    print("\n=== Демонстрация завершена ===")


if __name__ == "__main__":
    demonstrate_range_operations()
