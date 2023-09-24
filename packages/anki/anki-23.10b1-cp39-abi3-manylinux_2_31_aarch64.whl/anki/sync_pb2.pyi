"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class SyncAuth(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HKEY_FIELD_NUMBER: builtins.int
    ENDPOINT_FIELD_NUMBER: builtins.int
    IO_TIMEOUT_SECS_FIELD_NUMBER: builtins.int
    hkey: builtins.str
    endpoint: builtins.str
    io_timeout_secs: builtins.int
    def __init__(
        self,
        *,
        hkey: builtins.str = ...,
        endpoint: builtins.str | None = ...,
        io_timeout_secs: builtins.int | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_endpoint", b"_endpoint", "_io_timeout_secs", b"_io_timeout_secs", "endpoint", b"endpoint", "io_timeout_secs", b"io_timeout_secs"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_endpoint", b"_endpoint", "_io_timeout_secs", b"_io_timeout_secs", "endpoint", b"endpoint", "hkey", b"hkey", "io_timeout_secs", b"io_timeout_secs"]) -> None: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_endpoint", b"_endpoint"]) -> typing_extensions.Literal["endpoint"] | None: ...
    @typing.overload
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_io_timeout_secs", b"_io_timeout_secs"]) -> typing_extensions.Literal["io_timeout_secs"] | None: ...

global___SyncAuth = SyncAuth

@typing_extensions.final
class SyncLoginRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    USERNAME_FIELD_NUMBER: builtins.int
    PASSWORD_FIELD_NUMBER: builtins.int
    ENDPOINT_FIELD_NUMBER: builtins.int
    username: builtins.str
    password: builtins.str
    endpoint: builtins.str
    def __init__(
        self,
        *,
        username: builtins.str = ...,
        password: builtins.str = ...,
        endpoint: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_endpoint", b"_endpoint", "endpoint", b"endpoint"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_endpoint", b"_endpoint", "endpoint", b"endpoint", "password", b"password", "username", b"username"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_endpoint", b"_endpoint"]) -> typing_extensions.Literal["endpoint"] | None: ...

global___SyncLoginRequest = SyncLoginRequest

@typing_extensions.final
class SyncStatusResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _Required:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _RequiredEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[SyncStatusResponse._Required.ValueType], builtins.type):  # noqa: F821
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        NO_CHANGES: SyncStatusResponse._Required.ValueType  # 0
        NORMAL_SYNC: SyncStatusResponse._Required.ValueType  # 1
        FULL_SYNC: SyncStatusResponse._Required.ValueType  # 2

    class Required(_Required, metaclass=_RequiredEnumTypeWrapper): ...
    NO_CHANGES: SyncStatusResponse.Required.ValueType  # 0
    NORMAL_SYNC: SyncStatusResponse.Required.ValueType  # 1
    FULL_SYNC: SyncStatusResponse.Required.ValueType  # 2

    REQUIRED_FIELD_NUMBER: builtins.int
    NEW_ENDPOINT_FIELD_NUMBER: builtins.int
    required: global___SyncStatusResponse.Required.ValueType
    new_endpoint: builtins.str
    def __init__(
        self,
        *,
        required: global___SyncStatusResponse.Required.ValueType = ...,
        new_endpoint: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_new_endpoint", b"_new_endpoint", "new_endpoint", b"new_endpoint"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_new_endpoint", b"_new_endpoint", "new_endpoint", b"new_endpoint", "required", b"required"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_new_endpoint", b"_new_endpoint"]) -> typing_extensions.Literal["new_endpoint"] | None: ...

global___SyncStatusResponse = SyncStatusResponse

@typing_extensions.final
class SyncCollectionRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    AUTH_FIELD_NUMBER: builtins.int
    SYNC_MEDIA_FIELD_NUMBER: builtins.int
    @property
    def auth(self) -> global___SyncAuth: ...
    sync_media: builtins.bool
    def __init__(
        self,
        *,
        auth: global___SyncAuth | None = ...,
        sync_media: builtins.bool = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["auth", b"auth"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["auth", b"auth", "sync_media", b"sync_media"]) -> None: ...

global___SyncCollectionRequest = SyncCollectionRequest

@typing_extensions.final
class SyncCollectionResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _ChangesRequired:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _ChangesRequiredEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[SyncCollectionResponse._ChangesRequired.ValueType], builtins.type):  # noqa: F821
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        NO_CHANGES: SyncCollectionResponse._ChangesRequired.ValueType  # 0
        NORMAL_SYNC: SyncCollectionResponse._ChangesRequired.ValueType  # 1
        FULL_SYNC: SyncCollectionResponse._ChangesRequired.ValueType  # 2
        FULL_DOWNLOAD: SyncCollectionResponse._ChangesRequired.ValueType  # 3
        """local collection has no cards; upload not an option"""
        FULL_UPLOAD: SyncCollectionResponse._ChangesRequired.ValueType  # 4
        """remote collection has no cards; download not an option"""

    class ChangesRequired(_ChangesRequired, metaclass=_ChangesRequiredEnumTypeWrapper): ...
    NO_CHANGES: SyncCollectionResponse.ChangesRequired.ValueType  # 0
    NORMAL_SYNC: SyncCollectionResponse.ChangesRequired.ValueType  # 1
    FULL_SYNC: SyncCollectionResponse.ChangesRequired.ValueType  # 2
    FULL_DOWNLOAD: SyncCollectionResponse.ChangesRequired.ValueType  # 3
    """local collection has no cards; upload not an option"""
    FULL_UPLOAD: SyncCollectionResponse.ChangesRequired.ValueType  # 4
    """remote collection has no cards; download not an option"""

    HOST_NUMBER_FIELD_NUMBER: builtins.int
    SERVER_MESSAGE_FIELD_NUMBER: builtins.int
    REQUIRED_FIELD_NUMBER: builtins.int
    NEW_ENDPOINT_FIELD_NUMBER: builtins.int
    SERVER_MEDIA_USN_FIELD_NUMBER: builtins.int
    host_number: builtins.int
    server_message: builtins.str
    required: global___SyncCollectionResponse.ChangesRequired.ValueType
    new_endpoint: builtins.str
    server_media_usn: builtins.int
    def __init__(
        self,
        *,
        host_number: builtins.int = ...,
        server_message: builtins.str = ...,
        required: global___SyncCollectionResponse.ChangesRequired.ValueType = ...,
        new_endpoint: builtins.str | None = ...,
        server_media_usn: builtins.int = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_new_endpoint", b"_new_endpoint", "new_endpoint", b"new_endpoint"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_new_endpoint", b"_new_endpoint", "host_number", b"host_number", "new_endpoint", b"new_endpoint", "required", b"required", "server_media_usn", b"server_media_usn", "server_message", b"server_message"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_new_endpoint", b"_new_endpoint"]) -> typing_extensions.Literal["new_endpoint"] | None: ...

global___SyncCollectionResponse = SyncCollectionResponse

@typing_extensions.final
class MediaSyncStatusResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ACTIVE_FIELD_NUMBER: builtins.int
    PROGRESS_FIELD_NUMBER: builtins.int
    active: builtins.bool
    @property
    def progress(self) -> global___MediaSyncProgress: ...
    def __init__(
        self,
        *,
        active: builtins.bool = ...,
        progress: global___MediaSyncProgress | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["progress", b"progress"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["active", b"active", "progress", b"progress"]) -> None: ...

global___MediaSyncStatusResponse = MediaSyncStatusResponse

@typing_extensions.final
class MediaSyncProgress(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CHECKED_FIELD_NUMBER: builtins.int
    ADDED_FIELD_NUMBER: builtins.int
    REMOVED_FIELD_NUMBER: builtins.int
    checked: builtins.str
    added: builtins.str
    removed: builtins.str
    def __init__(
        self,
        *,
        checked: builtins.str = ...,
        added: builtins.str = ...,
        removed: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["added", b"added", "checked", b"checked", "removed", b"removed"]) -> None: ...

global___MediaSyncProgress = MediaSyncProgress

@typing_extensions.final
class FullUploadOrDownloadRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    AUTH_FIELD_NUMBER: builtins.int
    UPLOAD_FIELD_NUMBER: builtins.int
    SERVER_USN_FIELD_NUMBER: builtins.int
    @property
    def auth(self) -> global___SyncAuth: ...
    upload: builtins.bool
    server_usn: builtins.int
    """if not provided, media syncing will be skipped"""
    def __init__(
        self,
        *,
        auth: global___SyncAuth | None = ...,
        upload: builtins.bool = ...,
        server_usn: builtins.int | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["_server_usn", b"_server_usn", "auth", b"auth", "server_usn", b"server_usn"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["_server_usn", b"_server_usn", "auth", b"auth", "server_usn", b"server_usn", "upload", b"upload"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["_server_usn", b"_server_usn"]) -> typing_extensions.Literal["server_usn"] | None: ...

global___FullUploadOrDownloadRequest = FullUploadOrDownloadRequest
