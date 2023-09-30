from __future__ import absolute_import

from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model.annotation.client_annotation import Annotation


def run(client: KognicIOClient, input_uuid: str, annotation_type: str) -> Annotation:
    annotation = client.annotation.get_annotation(input_uuid=input_uuid, annotation_type=annotation_type)
    return annotation


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    input_uuid = "<input-uuid>"
    annotation_type = "<annotation-type>"
    annotation = run(client, input_uuid, annotation_type)
