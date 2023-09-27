"""Creators for s3 secrets"""
import configparser
from pathlib import Path
from typing import Callable, List, Optional

from mcli.models import SecretType
from mcli.objects.secrets import MCLIS3Secret
from mcli.objects.secrets.create.base import SecretCreator, SecretValidationError
from mcli.objects.secrets.create.generic import FileSecretFiller, FileSecretValidator
from mcli.utils.utils_interactive import file_prompt
from mcli.utils.utils_string_functions import validate_existing_filename


class S3SecretFiller(FileSecretFiller):
    """Interactive filler for s3 secret data
    """

    @staticmethod
    def fill_file(prompt: str, validate: Callable[[str], bool]) -> str:
        return file_prompt(prompt, validate=validate)

    @classmethod
    def fill_config(cls, validate: Callable[[str], bool]) -> str:
        return cls.fill_file(
            'Where is your S3 config file located?',
            validate,
        )

    @classmethod
    def fill_credentials(cls, validate: Callable[[str], bool]) -> str:
        return cls.fill_file(
            'Where is your S3 credentials file located?',
            validate,
        )


class S3SecretValidator(FileSecretValidator):
    """Validation methods for secret data

    Raises:
        SecretValidationError: Raised for any validation error for secret data
    """

    @staticmethod
    def validate_file_exists(path: str) -> bool:

        if not validate_existing_filename(path):
            raise SecretValidationError(f'File does not exist. File path {path} does not exist or is not a file.')
        return True


class S3SecretCreator(S3SecretFiller, S3SecretValidator):
    """Creates s3 secrets for the CLI
    """

    def create(self,
               name: Optional[str] = None,
               mount_directory: Optional[str] = None,
               credentials_file: Optional[str] = None,
               config_file: Optional[str] = None,
               profile: str = 'default') -> MCLIS3Secret:

        # Validate mount directory and files
        if mount_directory:
            self.validate_mount_absolute(mount_directory)

        if credentials_file:
            self.validate_file_exists(credentials_file)

        if config_file:
            self.validate_file_exists(config_file)

        base_creator = SecretCreator()
        secret = base_creator.create(SecretType.s3, name=name)
        assert isinstance(secret, MCLIS3Secret)

        if not config_file:
            config_file = self.fill_config(self.validate_file_exists)

        if not credentials_file:
            credentials_file = self.fill_credentials(self.validate_file_exists)

        if not mount_directory:
            mount_directory = self.get_mount_path(secret.name)
        secret.mount_directory = mount_directory

        profiles = self._parse_aws_profiles(credentials_file)
        if profile not in profiles:
            profile = self.fill_file(
                f'[{profile}] profile does not exist in the profiles in s3 credentials, please choose among {profiles}',
                lambda p: p in profiles)
        secret.profile = profile

        with open(Path(config_file).expanduser().absolute(), 'r', encoding='utf8') as fh:
            secret.config = fh.read()

        with open(Path(credentials_file).expanduser().absolute(), 'r', encoding='utf8') as fh:
            secret.credentials = fh.read()

        return secret

    def _parse_aws_profiles(self, credential_file_path: str) -> List[str]:
        config = configparser.ConfigParser()
        # The aws config(config_file_path) has been validated before written into the database.
        # Therefore, it should have a valid format for configparser to parse and at least one
        # profile should exist
        config.read(credential_file_path)

        # return the set of aws profiles in the credential file
        return config.sections()
