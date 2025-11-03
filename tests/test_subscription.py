import datetime

from testdata import create_subscription

from toadr3.models import ObjectType, OperationType, Subscription


def test_subscription() -> None:
    data = create_subscription(sid="1", pid="7")

    subscription = Subscription.model_validate(data)

    assert subscription.id == "1"
    assert subscription.created is not None
    assert isinstance(subscription.created, datetime.datetime)
    assert subscription.modified is not None
    assert isinstance(subscription.modified, datetime.datetime)

    assert subscription.object_type == "SUBSCRIPTION"
    assert subscription.client_name == "YAC"
    assert subscription.program_id == "7"
    assert len(subscription.object_operations) == 2
    op_0 = subscription.object_operations[0]
    assert op_0.objects == [ObjectType.EVENT]
    assert op_0.operations == [OperationType.POST]
    assert op_0.callback_url == "url://callback"
    assert op_0.bearer_token is None

    op_1 = subscription.object_operations[1]
    assert op_1.objects == [ObjectType.PROGRAM, ObjectType.REPORT]
    assert op_1.operations == [OperationType.PUT, OperationType.DELETE]
    assert op_1.callback_url == "url://callback2"
    assert op_1.bearer_token == "token"

    assert subscription.targets is not None
    assert len(subscription.targets) == 1
