from typing import List

import kognic.io.client as IOC
import kognic.io.model as IAM


def run(client: IOC.KognicIOClient, input_uuid: str, invalidated_reason: IAM.SceneInvalidatedReason) -> List[IAM.Input]:
    print("Invalidating inputs...")
    return client.input.invalidate_inputs(input_uuids=[input_uuid], invalidated_reason=invalidated_reason)


if __name__ == "__main__":
    client = IOC.KognicIOClient()

    # Input-identifier - Available via `client.input.get_inputs()`
    input_uuid = "Input-identifier"
    invalidated_reason = IAM.SceneInvalidatedReason.INCORRECTLY_CREATED
    run(client, input_uuid, invalidated_reason)
