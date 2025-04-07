from toadr3.models import ObjectOperation, ObjectTypes, OperationTypes, Subscription


def test_subscription() -> None:
    data = {
        "objectType": "SUBSCRIPTION",
        "clientName": "clientName",
        "programID": "programId",
        "objectOperations": [
            {
                "objects": [ObjectTypes.EVENT],
                "operations": [OperationTypes.POST],
                "callbackUrl": "url://callback",
            },
            ObjectOperation(
                objects=[ObjectTypes.PROGRAM, ObjectTypes.REPORT],
                operations=[OperationTypes.PUT, OperationTypes.DELETE],
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
    assert op_0.objects == [ObjectTypes.EVENT]
    assert op_0.operations == [OperationTypes.POST]
    assert op_0.callback_url == "url://callback"
    assert op_0.bearer_token is None

    op_1 = subscription.object_operations[1]
    assert op_1.objects == [ObjectTypes.PROGRAM, ObjectTypes.REPORT]
    assert op_1.operations == [OperationTypes.PUT, OperationTypes.DELETE]
    assert op_1.callback_url == "url://callback2"
    assert op_1.bearer_token == "token"

    assert subscription.targets is not None
    assert len(subscription.targets) == 1
