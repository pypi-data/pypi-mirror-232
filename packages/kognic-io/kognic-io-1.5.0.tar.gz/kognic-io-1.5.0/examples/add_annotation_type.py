import kognic.io.client as IOC


def run(client: IOC.KognicIOClient, input_uuid: str, annotation_type: str):
    print("Adding annotation types to input...")

    client.input.add_annotation_type(input_uuid=input_uuid, annotation_type=annotation_type)


if __name__ == "__main__":
    client = IOC.KognicIOClient()

    input_uuid = "<input-identifier>"
    annotation_type = "annotation-type"
    run(client, input_uuid, annotation_type)
