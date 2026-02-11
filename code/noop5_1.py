#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from dataclasses import dataclass, field
from typing import List
from enum import Enum


class Position(Enum):
    """Перечисление для амплуа игроков"""

    GOALKEEPER = "вратарь"
    DEFENDER = "защитник"
    MIDFIELDER = "полузащитник"
    FORWARD = "нападающий"


@dataclass
class Player:
    """Датакласс для представления игрока"""

    name: str
    position: Position
    goals: int = 0

    def __post_init__(self):
        """Проверка корректности данных после инициализации"""
        if self.goals < 0:
            raise ValueError("Количество голов не может быть отрицательным")


@dataclass
class Team:
    """Контейнер для хранения и управления игроками команды"""

    name: str
    players: List[Player] = field(default_factory=list)

    def add_player(self, player: Player) -> None:
        """Добавить игрока в команду"""
        self.players.append(player)

    def add_players(self, *players: Player) -> None:
        """Добавить несколько игроков в команду"""
        for player in players:
            self.add_player(player)

    def get_players_by_position(self, position: Position) -> List[Player]:
        """Получить игроков указанного амплуа"""
        return [player for player in self.players if player.position == position]

    def get_top_scorers(
        self, position: Position = None, limit: int = None
    ) -> List[Player]:
        """
        Получить игроков, отсортированных по голам по убыванию

        Args:
            position: фильтр по амплуа (опционально)
            limit: ограничение количества результатов (опционально)
        """
        # Фильтруем по амплуа если указано
        if position:
            filtered_players = self.get_players_by_position(position)
        else:
            filtered_players = self.players.copy()

        # Сортируем по голам по убыванию
        sorted_players = sorted(filtered_players, key=lambda p: p.goals, reverse=True)

        # Ограничиваем количество если указано
        if limit:
            return sorted_players[:limit]
        return sorted_players

    def get_total_goals(self) -> int:
        """Получить общее количество голов команды"""
        return sum(player.goals for player in self.players)

    def get_goals_by_position(self) -> dict:
        """Получить количество голов по амплуа"""
        result = {}
        for position in Position:
            players = self.get_players_by_position(position)
            result[position.value] = sum(p.goals for p in players)
        return result

    def get_best_scorer(self) -> Player:
        """Получить лучшего бомбардира команды"""
        if not self.players:
            raise ValueError("В команде нет игроков")
        return max(self.players, key=lambda p: p.goals)

    def __len__(self) -> int:
        """Количество игроков в команде"""
        return len(self.players)

    def __str__(self) -> str:
        """Строковое представление команды"""
        return f"Команда '{self.name}' ({len(self)} игроков, голов: {self.get_total_goals()})"


def demonstrate_team_operations():
    """Демонстрация работы с командой и игроками"""
    team = Team("Молния")
    print(f"Создана {team}\n")

    players = [
        Player("Алексей Иванов", Position.FORWARD, 15),
        Player("Игорь Петров", Position.FORWARD, 10),
        Player("Сергей Сидоров", Position.FORWARD, 8),
        Player("Дмитрий Козлов", Position.MIDFIELDER, 5),
        Player("Антон Николаев", Position.MIDFIELDER, 3),
        Player("Владимир Михайлов", Position.MIDFIELDER, 7),
        Player("Артем Федоров", Position.DEFENDER, 2),
        Player("Павел Сергеев", Position.DEFENDER, 1),
        Player("Евгений Васильев", Position.DEFENDER, 0),
        Player("Константин Алексеев", Position.GOALKEEPER, 0),
    ]

    team.add_players(*players)
    print(f"Добавлено игроков: {len(team)}\n")

    print("Все игроки команды:")
    for i, player in enumerate(team.players, 1):
        print(f"   {i}. {player.name} - {player.position.value}, голов: {player.goals}")

    print("\nНападающие (FORWARD):")
    forwards = team.get_players_by_position(Position.FORWARD)
    for i, player in enumerate(forwards, 1):
        print(f"   {i}. {player.name}, голов: {player.goals}")

    print("\nВсе игроки, отсортированные по голам (по убыванию):")
    top_scorers = team.get_top_scorers()
    for i, player in enumerate(top_scorers, 1):
        print(f"   {i}. {player.name} ({player.position.value}) - {player.goals} голов")

    print("\nНападающие, отсортированные по голам (по убыванию):")
    top_forwards = team.get_top_scorers(Position.FORWARD)
    for i, player in enumerate(top_forwards, 1):
        print(f"   {i}. {player.name} - {player.goals} голов")

    print("\nТОП-3 бомбардира команды:")
    top_3 = team.get_top_scorers(limit=3)
    for i, player in enumerate(top_3, 1):
        print(f"   {i}. {player.name} ({player.position.value}) - {player.goals} голов")

    print("\nГолы по амплуа:")
    goals_by_position = team.get_goals_by_position()
    for position, goals in goals_by_position.items():
        print(f"   {position}: {goals} голов")

    print("\nЛучший бомбардир команды:")
    try:
        best = team.get_best_scorer()
        print(f"   {best.name} ({best.position.value}) - {best.goals} голов")
    except ValueError as e:
        print(f"   Ошибка: {e}")

    print(f"\nОбщая статистика команды:")
    print(f"    Всего игроков: {len(team)}")
    print(f"    Всего голов: {team.get_total_goals()}")
    print(f"    Среднее голов на игрока: {team.get_total_goals() / len(team):.1f}")

    print("\nПолузащитники (MIDFIELDER), отсортированные по голам:")
    midfielders = team.get_top_scorers(Position.MIDFIELDER)
    if midfielders:
        for i, player in enumerate(midfielders, 1):
            print(f"   {i}. {player.name} - {player.goals} голов")
    else:
        print("   Полузащитников нет в команде")

    print("\nСоздание новой пустой команды:")
    empty_team = Team("Новички")
    print(f"   {empty_team}")

    try:
        empty_team.get_best_scorer()
    except ValueError as e:
        print(f"   Попытка получить лучшего бомбардира: {e}")

    print(
        f"   Нападающие в новой команде: {len(empty_team.get_players_by_position(Position.FORWARD))} игроков"
    )


if __name__ == "__main__":
    demonstrate_team_operations()
