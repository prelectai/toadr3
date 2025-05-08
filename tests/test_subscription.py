from toadr3.models import ObjectOperation, ObjectType, OperationType, Subscription


def test_subscription() -> None:
    data = {
        "objectType": "SUBSCRIPTION",
        "clientName": "clientName",
        "programID": "programId",
        "objectOperations": [
            {
                "objects": [ObjectType.EVENT],
                "operations": [OperationType.POST],
                "callbackUrl": "url://callback",
            },
            ObjectOperation(
                objects=[ObjectType.PROGRAM, ObjectType.REPORT],
                operations=[OperationType.PUT, OperationType.DELETE],
                callback_url="url://callback2",
                bearer_token="token",
            ),
        ],
        "targets": [{"type": "VEN", "values": ["venId"]}],
    }

    subscription = Subscription.model_validate(data)

    assert subscription.id is None
    assert subscription.created is None
    assert subscription.modified is None

    assert subscription.object_type == "SUBSCRIPTION"
    assert subscription.client_name == "clientName"
    assert subscription.program_id == "programId"
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
