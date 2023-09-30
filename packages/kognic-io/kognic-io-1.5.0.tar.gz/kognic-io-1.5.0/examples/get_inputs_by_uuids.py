from typing import List

import kognic.io.client as IOC
from kognic.io import model as IAM


def run(client: IOC.KognicIOClient, input_uuids: List[str]) -> List[IAM.Input]:
    print("Listing inputs...")
    return client.input.get_inputs_by_uuids(input_uuids=input_uuids)


if __name__ == "__main__":
    client = IOC.KognicIOClient()

    input_uuids = ["input-identifier"]
    run(client, input_uuids)
