from toadr3 import ToadrError
from toadr3.models import Problem


def test_toadr_error() -> None:
    error = ToadrError(
        message="message",
        status_code=500,
        reason="reason",
        headers={"Content-Type": "application/json"},
        json_response={"a": 1, "b": 2},
    )

    assert error.message == "message"
    assert error.status_code == 500
    assert error.reason == "reason"
    assert error.headers == {"Content-Type": "application/json"}
    assert error.json_response == {"a": 1, "b": 2}
    assert not hasattr(error, "__notes__")


def test_toadr_error_with_error_description() -> None:
    error = ToadrError(
        message="message",
        status_code=500,
        json_response={"error_description": "description"},
    )

    assert error.message == "message"
    assert error.status_code == 500
    assert error.reason == ""
    assert error.headers == {}
    assert error.__notes__ == ["description"]


def test_toadr_error_from_problem() -> None:
    problem = Problem(
        title="title",
        status=500,
    )

    error = ToadrError.from_problem(problem)
    assert error.message == "title"
    assert error.status_code == 500


def test_toadr_error_from_problem_with_details() -> None:
    problem = Problem(
        title="title",
        status=500,
        detail="detail",
    )

    error = ToadrError.from_problem(problem)
    assert error.message == "title: detail"
    assert error.status_code == 500
    assert error.json_response == {
        "type": None,
        "title": "title",
        "status": 500,
        "detail": "detail",
        "instance": None,
    }
