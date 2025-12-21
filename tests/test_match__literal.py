from typing import Literal, assert_type

import pytest

from match_expression import match, ExhaustiveError


type Platform = Literal["instagram", "tiktok", "youtube"]


class InstagramManager: ...


class TiktokManager: ...


class YoutubeManager: ...


@pytest.mark.parametrize(
    ("platform", "expected_type"),
    [
        ("instagram", InstagramManager),
        ("tiktok", TiktokManager),
        ("youtube", YoutubeManager),
    ],
)
def test__valid_literal(platform: Platform, expected_type: type) -> None:
    result = (
        match(platform)
        .case("instagram", InstagramManager())
        .case("tiktok", TiktokManager())
        .case("youtube", YoutubeManager())
        .exhaustive()
    )

    assert_type(result, InstagramManager | TiktokManager | YoutubeManager)
    assert isinstance(result, expected_type)


def test__exhaustive__raises_error() -> None:
    platform: Platform = "youtube"

    with pytest.raises(ExhaustiveError) as exc_info:
        match(platform).case("instagram", "IG").case("tiktok", "TT").exhaustive()

    assert exc_info.value.value == "youtube"


def test_literal_match_with_otherwise() -> None:
    platform: Platform = "youtube"

    result = (
        match(platform).case("instagram", "IG").case("tiktok", "TT").otherwise("Other")
    )

    assert_type(result, str)
    assert result == "Other"


def test_literal_match__returns_class_without_instantiation() -> None:
    platform: Platform = "instagram"

    result = (
        match(platform)
        .case("instagram", InstagramManager)
        .case("tiktok", TiktokManager)
        .case("youtube", YoutubeManager)
        .exhaustive()
    )

    assert result is InstagramManager
    assert not isinstance(result, InstagramManager)


def test_literal_match__no_eval_exhaustive() -> None:
    platform: Platform = "instagram"

    result = (
        match(platform)
        .case("instagram", lambda: "IG")
        .case("tiktok", lambda: "TT")
        .case("youtube", lambda: "YT")
        .exhaustive(eval=False)
    )

    # Should return the lambda function itself, not its result
    assert callable(result)
    assert result() == "IG"


def test_literal_match__no_eval_otherwise() -> None:
    platform: Platform = "youtube"

    result = (
        match(platform)
        .case("instagram", lambda: "IG")
        .case("tiktok", lambda: "TT")
        .otherwise(lambda: "Other", eval=False)
    )

    # Should return the default lambda function itself
    assert callable(result)
    assert result() == "Other"
