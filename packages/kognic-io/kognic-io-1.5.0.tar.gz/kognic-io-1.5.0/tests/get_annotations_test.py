from __future__ import absolute_import, annotations

import pytest

import examples.get_annotation as get_annotation_example
import kognic.io.client as IOC
from kognic.io.model.annotation.client_annotation import Annotation


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestGetAnnotations:
    def test_get_annotation(self, client: IOC.KognicIOClient):
        annotation = get_annotation_example.run(client=client, input_uuid="e1229546-f447-4c07-8f6d-1347f067d14a", annotation_type="signs")
        assert isinstance(annotation, Annotation)

    def test_get_annotation_incorrect_at(self, client: IOC.KognicIOClient):
        with pytest.raises(Exception) as exception_info:
            get_annotation_example.run(client=client, input_uuid="e1229546-f447-4c07-8f6d-1347f067d14a", annotation_type="od")

        assert "404 Client Error: Not Found for url:" in exception_info.value.args[0]
