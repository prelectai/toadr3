from pydantic import HttpUrl

from toadr3.models import Problem


def test_problem() -> None:
    problem_data = {
        "type": "https://problem/type",
        "title": "title",
        "status": 400,
        "detail": "detail",
        "instance": "https://instance/",
    }
    problem = Problem.model_validate(problem_data)
    assert problem is not None
    assert problem.type == HttpUrl("https://problem/type")
    assert problem.title == "title"
    assert problem.status == 400
    assert problem.detail == "detail"
    assert problem.instance == HttpUrl("https://instance/")


def test_problem_minimum() -> None:
    problem = Problem(title="Minimum", status=400)
    assert problem.title == "Minimum"
    assert problem.status == 400
