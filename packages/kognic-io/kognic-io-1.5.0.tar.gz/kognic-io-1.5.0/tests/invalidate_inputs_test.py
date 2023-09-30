from __future__ import absolute_import

import time
from typing import List

import pytest

import examples.cameras as cameras_example
import examples.get_inputs_by_uuids as get_inputs_example
import examples.invalidate_inputs as invalidate_inputs_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from kognic.io.model import SceneInvalidatedReason
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestCameras:
    @staticmethod
    def filter_cameras_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_invalidate_inputs(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        scene_response = cameras_example.run(client=client, project=project, dryrun=False)
        scene_uuid = scene_response.scene_uuid

        assert isinstance(scene_uuid, str)

        inputs = None
        for _ in range(6):
            inputs = get_inputs_example.run(client=client, input_uuids=[scene_uuid])
            if len(inputs) == 1 and inputs[0].status == "created":
                print("Input created")
                break
            time.sleep(1)

        assert isinstance(inputs, list)
        assert len(inputs) == 1
        assert inputs[0].status == "created", f"Input has not been created, has status {inputs[0].status}"

        invalidate_inputs_example.run(client=client, input_uuid=scene_uuid, invalidated_reason=SceneInvalidatedReason.BAD_CONTENT)

        invalidated_inputs = None
        for _ in range(3):
            invalidated_inputs = get_inputs_example.run(client=client, input_uuids=[scene_uuid])
            if len(invalidated_inputs) == 1 and inputs[0].status != "created":
                print("Input un-created")
                break
            time.sleep(1)

        assert invalidated_inputs[0].status == "invalidated:broken-input"
