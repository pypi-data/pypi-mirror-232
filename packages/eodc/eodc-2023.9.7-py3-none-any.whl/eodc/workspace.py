import json
import os
import subprocess as sp
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, TypeVar

from minio import Minio, MinioAdmin
from pydantic import SecretStr

T = TypeVar("T", bound="WorkspaceAdapter")


class StorageType(Enum):
    MINIO = "minio"


class WorkspaceAdapter(ABC):
    @staticmethod
    def create_adapter(
        tenant_url: str = None,
        storage_type: StorageType = StorageType.MINIO,
        parameters: dict[str, Any] = {},
    ) -> T:
        if storage_type == StorageType.MINIO:
            return MinIOAdapter(
                url=tenant_url,
                access_key=parameters["access_key"],
                secret_key=parameters["secret_key"],
                mc_bin_path=parameters["mc_bin_path"],
            )
        else:
            return None

    @abstractmethod
    def register_user(self, user_name) -> dict[str, str]:
        pass

    @abstractmethod
    def remove_user(self, user_name):
        pass

    @abstractmethod
    def create_user_workspace(
        self, workspace_name: str, user_name: str, cwd: str
    ) -> None:
        pass

    @abstractmethod
    def delete_user_workspace(self, workspace_name: str):
        pass

    @abstractmethod
    def workspace_exists(self, workspace_name) -> bool:
        pass

    @abstractmethod
    def list_workspaces(self) -> list[str]:
        pass

    @abstractmethod
    def list_workspace_files(self, workspace_name):
        pass

    @abstractmethod
    def update_workspace(self, workspace_name, **kwargs):
        pass


class MinIOAdapter(WorkspaceAdapter):
    """
    The system on which this is running needs to have the mc (Minio Client)
    CLI tool installed
    """

    alias: str

    minio_client: Minio
    minio_admin_client: MinioAdmin

    def __init__(
        self,
        url: str,
        access_key: SecretStr,
        secret_key: SecretStr,
        mc_bin_path: Any = None,
        alias: str = "MINIO_EODC",
    ):
        self.alias = alias

        self.minio_client = Minio(
            url,
            access_key=access_key.get_secret_value(),
            secret_key=secret_key.get_secret_value(),
            secure=True,
        )

        self.minio_admin_client = MinioAdmin(target=self.alias, binary_path=mc_bin_path)

        sp.run(
            f"mc config host add {self.alias} https://{url}/ \
            {access_key.get_secret_value()} {secret_key.get_secret_value()}",
            capture_output=True,
            shell=True,
        )

    def register_user(self, user_name) -> dict[str, str]:
        generated_secret_key: uuid = uuid.uuid4()
        self.minio_admin_client.user_add(user_name, str(generated_secret_key))
        return {"access_key": user_name, "secret_key": str(generated_secret_key)}

    def remove_user(self, user_name):
        self.minio_admin_client.user_remove(user_name)

    def _create_workspace(self, workspace_name):
        """
        raises S3Error
        """
        self.minio_client.make_bucket(workspace_name)

    def create_user_workspace(
        self, workspace_name: str, user_name: str, cwd: str
    ) -> None:
        self._create_workspace(workspace_name=workspace_name)
        self._grant_workspace_to_user(
            workspace_name=workspace_name, user_name=user_name, cwd=cwd
        )

    def _create_workspace_policy(self, workspace_name: str, cwd: str) -> str:
        policy_name: str = f"BASIC_{workspace_name.upper()}"
        self.minio_admin_client.policy_add(
            policy_name=policy_name,
            policy_file=create_policy(workspace_name=workspace_name, cwd=cwd),
        )
        return policy_name

    def _grant_workspace_to_user(self, workspace_name: str, user_name: str, cwd: str):
        policy_name: str = self._create_workspace_policy(
            workspace_name=workspace_name, cwd=cwd
        )
        self.minio_admin_client.policy_set(policy_name=policy_name, user=user_name)

    def _delete_workspace(self, workspace_name):
        """
        raises S3Error
        """
        self.minio_client.remove_bucket(workspace_name)

    def _remove_workspace_policy(self, workspace_name: str):
        policy_name: str = f"BASIC_{workspace_name.upper()}"
        for user in self.minio_admin_client.user_list():
            if "policyName" in user.keys() and user["policyName"] == policy_name:
                self._revoke_workspace_policy(
                    policy_name=policy_name, user_name=user["accessKey"]
                )
        self.minio_admin_client.policy_remove(policy_name=policy_name)

    def _revoke_workspace_policy(self, policy_name: str, user_name: str):
        self.minio_admin_client.policy_unset(policy_name=policy_name, user=user_name)

    def delete_user_workspace(self, workspace_name: str):
        self._remove_workspace_policy(workspace_name=workspace_name)
        self._delete_workspace(workspace_name=workspace_name)

    def workspace_exists(self, workspace_name) -> bool:
        return self.minio_client.bucket_exists(workspace_name)

    def list_workspaces(self) -> list[str]:
        buckets = self.minio_client.list_buckets()
        return [bucket.name for bucket in buckets]

    def list_workspace_files(self, workspace_name):
        return [
            obj.object_name for obj in self.minio_client.list_objects(workspace_name)
        ]

    def update_workspace(self, workspace_name, **kwargs):
        pass


# Utils


def create_policy(workspace_name: str, cwd: str) -> str:
    filename = workspace_name + "_policy.json"

    abs_path = os.path.abspath(os.path.join("eodc_workspaces", "policies", filename))

    policy_file_content = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                ],
                "Resource": [
                    f"arn:aws:s3:::{workspace_name}",
                    f"arn:aws:s3:::{workspace_name}/*",
                ],
            }
        ],
    }

    with open(abs_path, "w") as f:
        json.dump(policy_file_content, f)

    return abs_path
