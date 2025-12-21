from dataclasses import dataclass
from typing import Literal, assert_type

import pytest

from match_expression import ExhaustiveError, match


type Platform = Literal["instagram", "tiktok", "youtube"]
type Status = Literal["success", "error"]


@dataclass
class Animal:
    name: str


class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} barks!"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} meows!"


class Car:
    def drive(self) -> str:
        return "Driving!"


class Bike:
    def ride(self) -> str:
        return "Riding!"


def test__value_tuple_match() -> None:
    status: Status = "success"
    platform: Platform = "instagram"

    result = (
        match((status, platform))
        .case(("success", "instagram"), "success on instagram")
        .case(("success", "tiktok"), "success on tiktok")
        .case(("success", "youtube"), "success on youtube")
        .case(("error", "instagram"), "error on instagram")
        .case(("error", "tiktok"), "error on tiktok")
        .case(("error", "youtube"), "error on youtube")
        .exhaustive()
    )

    assert_type(result, str)
    assert result == "success on instagram"


def test__value_tuple_with_callable() -> None:
    status: Status = "error"
    platform: Platform = "tiktok"

    result = (
        match((status, platform))
        .case(("success", "instagram"), lambda: "IG success")
        .case(("success", "tiktok"), lambda: "TT success")
        .case(("success", "youtube"), lambda: "YT success")
        .case(("error", "instagram"), lambda: "IG error")
        .case(("error", "tiktok"), lambda: "TT error")
        .case(("error", "youtube"), lambda: "YT error")
        .exhaustive()
    )

    assert result == "TT error"


def test__value_tuple_exhaustive_raises() -> None:
    status: Status = "error"
    platform: Platform = "youtube"

    with pytest.raises(ExhaustiveError):
        (
            match((status, platform))
            .case(("success", "instagram"), "ok")
            .case(("error", "tiktok"), "fail")
            .exhaustive()
        )


def test__value_tuple_otherwise() -> None:
    status: Status = "error"
    platform: Platform = "youtube"

    result = (
        match((status, platform))
        .case(("success", "instagram"), "matched")
        .otherwise("not matched")
    )

    assert result == "not matched"


def test__type_tuple_match() -> None:
    dog = Dog("Buddy")
    car = Car()

    result = (
        match((dog, car))
        .case((Dog, Car), lambda d, c: f"{d.speak()} {c.drive()}")
        .case((Dog, Bike), lambda d, b: f"{d.speak()} {b.ride()}")
        .case((Cat, Car), lambda c, car: f"{c.speak()} {car.drive()}")
        .case((Cat, Bike), lambda c, b: f"{c.speak()} {b.ride()}")
        .exhaustive()
    )

    assert_type(result, str)
    assert result == "Buddy barks! Driving!"


def test__type_tuple_with_value_return() -> None:
    cat = Cat("Whiskers")
    bike = Bike()

    result = (
        match((cat, bike))
        .case((Dog, Car), "dog+car")
        .case((Dog, Bike), "dog+bike")
        .case((Cat, Car), "cat+car")
        .case((Cat, Bike), "cat+bike")
        .exhaustive()
    )

    assert result == "cat+bike"


def test__type_tuple_exhaustive_raises() -> None:
    cat = Cat("Whiskers")
    car = Car()

    with pytest.raises(ExhaustiveError):
        (
            match((cat, car))
            .case((Dog, Car), "dog+car")
            .case((Dog, Bike), "dog+bike")
            .exhaustive()
        )


def test__type_tuple_otherwise() -> None:
    cat = Cat("Whiskers")
    car = Car()

    result = (
        match((cat, car))
        .case((Dog, Car), "dog+car")
        .case((Dog, Bike), "dog+bike")
        .otherwise("other")
    )

    assert result == "other"


def test__mixed_value_and_type() -> None:
    platform: Platform = "instagram"
    dog = Dog("Buddy")

    result = (
        match((platform, dog))
        .case(("instagram", Dog), lambda p, d: f"IG: {d.speak()}")
        .case(("instagram", Cat), lambda p, c: f"IG: {c.speak()}")
        .case(("tiktok", Dog), lambda p, d: f"TT: {d.speak()}")
        .case(("tiktok", Cat), lambda p, c: f"TT: {c.speak()}")
        .case(("youtube", Dog), lambda p, d: f"YT: {d.speak()}")
        .case(("youtube", Cat), lambda p, c: f"YT: {c.speak()}")
        .exhaustive()
    )

    assert_type(result, str)
    assert result == "IG: Buddy barks!"


def test__mixed_type_and_value() -> None:
    cat = Cat("Whiskers")
    status: Status = "success"

    result = (
        match((cat, status))
        .case((Dog, "success"), lambda d, s: f"{d.speak()} - ok")
        .case((Dog, "error"), lambda d, s: f"{d.speak()} - fail")
        .case((Cat, "success"), lambda c, s: f"{c.speak()} - ok")
        .case((Cat, "error"), lambda c, s: f"{c.speak()} - fail")
        .exhaustive()
    )

    assert result == "Whiskers meows! - ok"


def test__mixed_exhaustive_raises() -> None:
    platform: Platform = "youtube"
    cat = Cat("Whiskers")

    with pytest.raises(ExhaustiveError):
        (
            match((platform, cat))
            .case(("instagram", Dog), "IG dog")
            .case(("tiktok", Cat), "TT cat")
            .exhaustive()
        )


def test__mixed_otherwise() -> None:
    platform: Platform = "youtube"
    dog = Dog("Buddy")

    result = (
        match((platform, dog))
        .case(("instagram", Dog), "IG dog")
        .case(("tiktok", Cat), "TT cat")
        .otherwise("other")
    )

    assert result == "other"


def test__tuple_no_eval_exhaustive() -> None:
    status: Status = "success"
    platform: Platform = "instagram"

    result = (
        match((status, platform))
        .case(("success", "instagram"), lambda: "IG success")
        .case(("success", "tiktok"), lambda: "TT success")
        .case(("success", "youtube"), lambda: "YT success")
        .case(("error", "instagram"), lambda: "IG error")
        .case(("error", "tiktok"), lambda: "TT error")
        .case(("error", "youtube"), lambda: "YT error")
        .exhaustive(eval=False)
    )

    assert callable(result)
    assert result() == "IG success"


def test__tuple_no_eval_otherwise() -> None:
    status: Status = "error"
    platform: Platform = "youtube"

    result = (
        match((status, platform))
        .case(("success", "instagram"), lambda: "matched")
        .otherwise(lambda: "not matched", eval=False)
    )

    assert callable(result)
    assert result() == "not matched"
