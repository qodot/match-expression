from dataclasses import dataclass
from typing import assert_type
import pytest

from match_expression import match, ExhaustiveError


@dataclass
class Animal:
    name: str


class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} barks!"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} meows!"


class Bird(Animal):
    def speak(self) -> str:
        return f"{self.name} chirps!"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Dog("Buddy"), "Buddy barks!"),
        (Cat("Whiskers"), "Whiskers meows!"),
        (Bird("Tweety"), "Tweety chirps!"),
    ],
)
def test__valid_type(value: Animal, expected: str) -> None:
    result = (
        match(value)
        .case(Dog, lambda dog: dog.speak())
        .case(Cat, lambda cat: cat.speak())
        .case(Bird, lambda bird: bird.speak())
        .exhaustive()
    )

    assert_type(result, str)
    assert result == expected


def test__exhaustive__raises_error() -> None:
    cat = Cat("Whiskers")

    with pytest.raises(ExhaustiveError) as exc_info:
        match(cat).case(Dog, lambda dog: dog.speak()).case(
            Bird, lambda bird: bird.speak()
        ).exhaustive()

    assert isinstance(exc_info.value.value, Cat)


def test__otherwise():
    cat = Cat("Whiskers")

    result = (
        match(cat)
        .case(Dog, lambda dog: dog.speak())
        .case(Bird, lambda bird: bird.speak())
        .otherwise("Other")
    )

    assert_type(result, str)
    assert result == "Other"


def test_type_match__returns_class_without_instantiation() -> None:
    dog = Dog("Buddy")

    class DogHandler: ...

    class CatHandler: ...

    class BirdHandler: ...

    result = (
        match(dog)
        .case(Dog, DogHandler)
        .case(Cat, CatHandler)
        .case(Bird, BirdHandler)
        .exhaustive()
    )

    assert result is DogHandler
    assert not isinstance(result, DogHandler)


def test_type_match__no_eval_exhaustive() -> None:
    dog = Dog("Buddy")

    result = (
        match(dog)
        .case(Dog, lambda d: d.speak())
        .case(Cat, lambda c: c.speak())
        .case(Bird, lambda b: b.speak())
        .exhaustive(eval=False)
    )

    # Should return the lambda function itself, not its result
    assert result(dog) == "Buddy barks!"


def test_type_match__no_eval_otherwise() -> None:
    cat = Cat("Whiskers")

    result = (
        match(cat)
        .case(Dog, lambda d: d.speak())
        .case(Bird, lambda b: b.speak())
        .otherwise(lambda: "Unknown animal", eval=False)
    )

    # Should return the default lambda function itself
    assert callable(result)
    assert result() == "Unknown animal"
