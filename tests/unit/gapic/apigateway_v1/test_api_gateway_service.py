# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import mock
import packaging.version

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule


from google.api_core import client_options
from google.api_core import exceptions as core_exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async  # type: ignore
from google.api_core import operations_v1
from google.auth import credentials as ga_credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.apigateway_v1.services.api_gateway_service import (
    ApiGatewayServiceAsyncClient,
)
from google.cloud.apigateway_v1.services.api_gateway_service import (
    ApiGatewayServiceClient,
)
from google.cloud.apigateway_v1.services.api_gateway_service import pagers
from google.cloud.apigateway_v1.services.api_gateway_service import transports
from google.cloud.apigateway_v1.services.api_gateway_service.transports.base import (
    _API_CORE_VERSION,
)
from google.cloud.apigateway_v1.services.api_gateway_service.transports.base import (
    _GOOGLE_AUTH_VERSION,
)
from google.cloud.apigateway_v1.types import apigateway
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
import google.auth


# TODO(busunkim): Once google-api-core >= 1.26.0 is required:
# - Delete all the api-core and auth "less than" test cases
# - Delete these pytest markers (Make the "greater than or equal to" tests the default).
requires_google_auth_lt_1_25_0 = pytest.mark.skipif(
    packaging.version.parse(_GOOGLE_AUTH_VERSION) >= packaging.version.parse("1.25.0"),
    reason="This test requires google-auth < 1.25.0",
)
requires_google_auth_gte_1_25_0 = pytest.mark.skipif(
    packaging.version.parse(_GOOGLE_AUTH_VERSION) < packaging.version.parse("1.25.0"),
    reason="This test requires google-auth >= 1.25.0",
)

requires_api_core_lt_1_26_0 = pytest.mark.skipif(
    packaging.version.parse(_API_CORE_VERSION) >= packaging.version.parse("1.26.0"),
    reason="This test requires google-api-core < 1.26.0",
)

requires_api_core_gte_1_26_0 = pytest.mark.skipif(
    packaging.version.parse(_API_CORE_VERSION) < packaging.version.parse("1.26.0"),
    reason="This test requires google-api-core >= 1.26.0",
)


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert ApiGatewayServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        ApiGatewayServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ApiGatewayServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ApiGatewayServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ApiGatewayServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ApiGatewayServiceClient._get_default_mtls_endpoint(non_googleapi)
        == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [ApiGatewayServiceClient, ApiGatewayServiceAsyncClient,]
)
def test_api_gateway_service_client_from_service_account_info(client_class):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_info"
    ) as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == "apigateway.googleapis.com:443"


@pytest.mark.parametrize(
    "client_class", [ApiGatewayServiceClient, ApiGatewayServiceAsyncClient,]
)
def test_api_gateway_service_client_from_service_account_file(client_class):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == "apigateway.googleapis.com:443"


def test_api_gateway_service_client_get_transport_class():
    transport = ApiGatewayServiceClient.get_transport_class()
    available_transports = [
        transports.ApiGatewayServiceGrpcTransport,
    ]
    assert transport in available_transports

    transport = ApiGatewayServiceClient.get_transport_class("grpc")
    assert transport == transports.ApiGatewayServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ApiGatewayServiceClient, transports.ApiGatewayServiceGrpcTransport, "grpc"),
        (
            ApiGatewayServiceAsyncClient,
            transports.ApiGatewayServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    ApiGatewayServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ApiGatewayServiceClient),
)
@mock.patch.object(
    ApiGatewayServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ApiGatewayServiceAsyncClient),
)
def test_api_gateway_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(ApiGatewayServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(ApiGatewayServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (
            ApiGatewayServiceClient,
            transports.ApiGatewayServiceGrpcTransport,
            "grpc",
            "true",
        ),
        (
            ApiGatewayServiceAsyncClient,
            transports.ApiGatewayServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (
            ApiGatewayServiceClient,
            transports.ApiGatewayServiceGrpcTransport,
            "grpc",
            "false",
        ),
        (
            ApiGatewayServiceAsyncClient,
            transports.ApiGatewayServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    ApiGatewayServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ApiGatewayServiceClient),
)
@mock.patch.object(
    ApiGatewayServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ApiGatewayServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_api_gateway_service_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)

            if use_client_cert_env == "false":
                expected_client_cert_source = None
                expected_host = client.DEFAULT_ENDPOINT
            else:
                expected_client_cert_source = client_cert_source_callback
                expected_host = client.DEFAULT_MTLS_ENDPOINT

            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=expected_host,
                scopes=None,
                client_cert_source_for_mtls=expected_client_cert_source,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                with mock.patch(
                    "google.auth.transport.mtls.default_client_cert_source",
                    return_value=client_cert_source_callback,
                ):
                    if use_client_cert_env == "false":
                        expected_host = client.DEFAULT_ENDPOINT
                        expected_client_cert_source = None
                    else:
                        expected_host = client.DEFAULT_MTLS_ENDPOINT
                        expected_client_cert_source = client_cert_source_callback

                    patched.return_value = None
                    client = client_class()
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=expected_host,
                        scopes=None,
                        client_cert_source_for_mtls=expected_client_cert_source,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                    )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ApiGatewayServiceClient, transports.ApiGatewayServiceGrpcTransport, "grpc"),
        (
            ApiGatewayServiceAsyncClient,
            transports.ApiGatewayServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_api_gateway_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ApiGatewayServiceClient, transports.ApiGatewayServiceGrpcTransport, "grpc"),
        (
            ApiGatewayServiceAsyncClient,
            transports.ApiGatewayServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_api_gateway_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_api_gateway_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.apigateway_v1.services.api_gateway_service.transports.ApiGatewayServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = ApiGatewayServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_list_gateways(
    transport: str = "grpc", request_type=apigateway.ListGatewaysRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListGatewaysResponse(
            next_page_token="next_page_token_value",
            unreachable_locations=["unreachable_locations_value"],
        )
        response = client.list_gateways(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListGatewaysRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListGatewaysPager)
    assert response.next_page_token == "next_page_token_value"
    assert response.unreachable_locations == ["unreachable_locations_value"]


def test_list_gateways_from_dict():
    test_list_gateways(request_type=dict)


def test_list_gateways_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        client.list_gateways()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListGatewaysRequest()


@pytest.mark.asyncio
async def test_list_gateways_async(
    transport: str = "grpc_asyncio", request_type=apigateway.ListGatewaysRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListGatewaysResponse(
                next_page_token="next_page_token_value",
                unreachable_locations=["unreachable_locations_value"],
            )
        )
        response = await client.list_gateways(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListGatewaysRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListGatewaysAsyncPager)
    assert response.next_page_token == "next_page_token_value"
    assert response.unreachable_locations == ["unreachable_locations_value"]


@pytest.mark.asyncio
async def test_list_gateways_async_from_dict():
    await test_list_gateways_async(request_type=dict)


def test_list_gateways_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.ListGatewaysRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        call.return_value = apigateway.ListGatewaysResponse()
        client.list_gateways(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_gateways_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.ListGatewaysRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListGatewaysResponse()
        )
        await client.list_gateways(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_gateways_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListGatewaysResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_gateways(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_gateways_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_gateways(
            apigateway.ListGatewaysRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_gateways_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListGatewaysResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListGatewaysResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_gateways(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_gateways_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_gateways(
            apigateway.ListGatewaysRequest(), parent="parent_value",
        )


def test_list_gateways_pager():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListGatewaysResponse(
                gateways=[
                    apigateway.Gateway(),
                    apigateway.Gateway(),
                    apigateway.Gateway(),
                ],
                next_page_token="abc",
            ),
            apigateway.ListGatewaysResponse(gateways=[], next_page_token="def",),
            apigateway.ListGatewaysResponse(
                gateways=[apigateway.Gateway(),], next_page_token="ghi",
            ),
            apigateway.ListGatewaysResponse(
                gateways=[apigateway.Gateway(), apigateway.Gateway(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_gateways(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, apigateway.Gateway) for i in results)


def test_list_gateways_pages():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_gateways), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListGatewaysResponse(
                gateways=[
                    apigateway.Gateway(),
                    apigateway.Gateway(),
                    apigateway.Gateway(),
                ],
                next_page_token="abc",
            ),
            apigateway.ListGatewaysResponse(gateways=[], next_page_token="def",),
            apigateway.ListGatewaysResponse(
                gateways=[apigateway.Gateway(),], next_page_token="ghi",
            ),
            apigateway.ListGatewaysResponse(
                gateways=[apigateway.Gateway(), apigateway.Gateway(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_gateways(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_gateways_async_pager():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_gateways), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListGatewaysResponse(
                gateways=[
                    apigateway.Gateway(),
                    apigateway.Gateway(),
                    apigateway.Gateway(),
                ],
                next_page_token="abc",
            ),
            apigateway.ListGatewaysResponse(gateways=[], next_page_token="def",),
            apigateway.ListGatewaysResponse(
                gateways=[apigateway.Gateway(),], next_page_token="ghi",
            ),
            apigateway.ListGatewaysResponse(
                gateways=[apigateway.Gateway(), apigateway.Gateway(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_gateways(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, apigateway.Gateway) for i in responses)


@pytest.mark.asyncio
async def test_list_gateways_async_pages():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_gateways), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListGatewaysResponse(
                gateways=[
                    apigateway.Gateway(),
                    apigateway.Gateway(),
                    apigateway.Gateway(),
                ],
                next_page_token="abc",
            ),
            apigateway.ListGatewaysResponse(gateways=[], next_page_token="def",),
            apigateway.ListGatewaysResponse(
                gateways=[apigateway.Gateway(),], next_page_token="ghi",
            ),
            apigateway.ListGatewaysResponse(
                gateways=[apigateway.Gateway(), apigateway.Gateway(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_gateways(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_gateway(
    transport: str = "grpc", request_type=apigateway.GetGatewayRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.Gateway(
            name="name_value",
            display_name="display_name_value",
            api_config="api_config_value",
            state=apigateway.Gateway.State.CREATING,
            default_hostname="default_hostname_value",
        )
        response = client.get_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetGatewayRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, apigateway.Gateway)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.api_config == "api_config_value"
    assert response.state == apigateway.Gateway.State.CREATING
    assert response.default_hostname == "default_hostname_value"


def test_get_gateway_from_dict():
    test_get_gateway(request_type=dict)


def test_get_gateway_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_gateway), "__call__") as call:
        client.get_gateway()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetGatewayRequest()


@pytest.mark.asyncio
async def test_get_gateway_async(
    transport: str = "grpc_asyncio", request_type=apigateway.GetGatewayRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.Gateway(
                name="name_value",
                display_name="display_name_value",
                api_config="api_config_value",
                state=apigateway.Gateway.State.CREATING,
                default_hostname="default_hostname_value",
            )
        )
        response = await client.get_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetGatewayRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, apigateway.Gateway)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.api_config == "api_config_value"
    assert response.state == apigateway.Gateway.State.CREATING
    assert response.default_hostname == "default_hostname_value"


@pytest.mark.asyncio
async def test_get_gateway_async_from_dict():
    await test_get_gateway_async(request_type=dict)


def test_get_gateway_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.GetGatewayRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_gateway), "__call__") as call:
        call.return_value = apigateway.Gateway()
        client.get_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_gateway_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.GetGatewayRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_gateway), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(apigateway.Gateway())
        await client.get_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_gateway_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.Gateway()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_gateway(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_gateway_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_gateway(
            apigateway.GetGatewayRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_gateway_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.Gateway()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(apigateway.Gateway())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_gateway(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_gateway_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_gateway(
            apigateway.GetGatewayRequest(), name="name_value",
        )


def test_create_gateway(
    transport: str = "grpc", request_type=apigateway.CreateGatewayRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateGatewayRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_gateway_from_dict():
    test_create_gateway(request_type=dict)


def test_create_gateway_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_gateway), "__call__") as call:
        client.create_gateway()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateGatewayRequest()


@pytest.mark.asyncio
async def test_create_gateway_async(
    transport: str = "grpc_asyncio", request_type=apigateway.CreateGatewayRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateGatewayRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_gateway_async_from_dict():
    await test_create_gateway_async(request_type=dict)


def test_create_gateway_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.CreateGatewayRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_gateway), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_gateway_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.CreateGatewayRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_gateway), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_gateway_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_gateway(
            parent="parent_value",
            gateway=apigateway.Gateway(name="name_value"),
            gateway_id="gateway_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].gateway == apigateway.Gateway(name="name_value")
        assert args[0].gateway_id == "gateway_id_value"


def test_create_gateway_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_gateway(
            apigateway.CreateGatewayRequest(),
            parent="parent_value",
            gateway=apigateway.Gateway(name="name_value"),
            gateway_id="gateway_id_value",
        )


@pytest.mark.asyncio
async def test_create_gateway_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_gateway(
            parent="parent_value",
            gateway=apigateway.Gateway(name="name_value"),
            gateway_id="gateway_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].gateway == apigateway.Gateway(name="name_value")
        assert args[0].gateway_id == "gateway_id_value"


@pytest.mark.asyncio
async def test_create_gateway_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_gateway(
            apigateway.CreateGatewayRequest(),
            parent="parent_value",
            gateway=apigateway.Gateway(name="name_value"),
            gateway_id="gateway_id_value",
        )


def test_update_gateway(
    transport: str = "grpc", request_type=apigateway.UpdateGatewayRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateGatewayRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_gateway_from_dict():
    test_update_gateway(request_type=dict)


def test_update_gateway_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_gateway), "__call__") as call:
        client.update_gateway()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateGatewayRequest()


@pytest.mark.asyncio
async def test_update_gateway_async(
    transport: str = "grpc_asyncio", request_type=apigateway.UpdateGatewayRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateGatewayRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_gateway_async_from_dict():
    await test_update_gateway_async(request_type=dict)


def test_update_gateway_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.UpdateGatewayRequest()

    request.gateway.name = "gateway.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_gateway), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "gateway.name=gateway.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_gateway_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.UpdateGatewayRequest()

    request.gateway.name = "gateway.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_gateway), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "gateway.name=gateway.name/value",) in kw[
        "metadata"
    ]


def test_update_gateway_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_gateway(
            gateway=apigateway.Gateway(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].gateway == apigateway.Gateway(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_gateway_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_gateway(
            apigateway.UpdateGatewayRequest(),
            gateway=apigateway.Gateway(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_gateway_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_gateway(
            gateway=apigateway.Gateway(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].gateway == apigateway.Gateway(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_gateway_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_gateway(
            apigateway.UpdateGatewayRequest(),
            gateway=apigateway.Gateway(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_gateway(
    transport: str = "grpc", request_type=apigateway.DeleteGatewayRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteGatewayRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_gateway_from_dict():
    test_delete_gateway(request_type=dict)


def test_delete_gateway_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_gateway), "__call__") as call:
        client.delete_gateway()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteGatewayRequest()


@pytest.mark.asyncio
async def test_delete_gateway_async(
    transport: str = "grpc_asyncio", request_type=apigateway.DeleteGatewayRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteGatewayRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_gateway_async_from_dict():
    await test_delete_gateway_async(request_type=dict)


def test_delete_gateway_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.DeleteGatewayRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_gateway), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_gateway_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.DeleteGatewayRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_gateway), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_gateway(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_gateway_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_gateway(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_gateway_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_gateway(
            apigateway.DeleteGatewayRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_gateway_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_gateway), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_gateway(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_gateway_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_gateway(
            apigateway.DeleteGatewayRequest(), name="name_value",
        )


def test_list_apis(transport: str = "grpc", request_type=apigateway.ListApisRequest):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListApisResponse(
            next_page_token="next_page_token_value",
            unreachable_locations=["unreachable_locations_value"],
        )
        response = client.list_apis(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListApisRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListApisPager)
    assert response.next_page_token == "next_page_token_value"
    assert response.unreachable_locations == ["unreachable_locations_value"]


def test_list_apis_from_dict():
    test_list_apis(request_type=dict)


def test_list_apis_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        client.list_apis()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListApisRequest()


@pytest.mark.asyncio
async def test_list_apis_async(
    transport: str = "grpc_asyncio", request_type=apigateway.ListApisRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListApisResponse(
                next_page_token="next_page_token_value",
                unreachable_locations=["unreachable_locations_value"],
            )
        )
        response = await client.list_apis(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListApisRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListApisAsyncPager)
    assert response.next_page_token == "next_page_token_value"
    assert response.unreachable_locations == ["unreachable_locations_value"]


@pytest.mark.asyncio
async def test_list_apis_async_from_dict():
    await test_list_apis_async(request_type=dict)


def test_list_apis_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.ListApisRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        call.return_value = apigateway.ListApisResponse()
        client.list_apis(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_apis_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.ListApisRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListApisResponse()
        )
        await client.list_apis(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_apis_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListApisResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_apis(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_apis_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_apis(
            apigateway.ListApisRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_apis_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListApisResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListApisResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_apis(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_apis_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_apis(
            apigateway.ListApisRequest(), parent="parent_value",
        )


def test_list_apis_pager():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListApisResponse(
                apis=[apigateway.Api(), apigateway.Api(), apigateway.Api(),],
                next_page_token="abc",
            ),
            apigateway.ListApisResponse(apis=[], next_page_token="def",),
            apigateway.ListApisResponse(
                apis=[apigateway.Api(),], next_page_token="ghi",
            ),
            apigateway.ListApisResponse(apis=[apigateway.Api(), apigateway.Api(),],),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_apis(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, apigateway.Api) for i in results)


def test_list_apis_pages():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_apis), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListApisResponse(
                apis=[apigateway.Api(), apigateway.Api(), apigateway.Api(),],
                next_page_token="abc",
            ),
            apigateway.ListApisResponse(apis=[], next_page_token="def",),
            apigateway.ListApisResponse(
                apis=[apigateway.Api(),], next_page_token="ghi",
            ),
            apigateway.ListApisResponse(apis=[apigateway.Api(), apigateway.Api(),],),
            RuntimeError,
        )
        pages = list(client.list_apis(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_apis_async_pager():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_apis), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListApisResponse(
                apis=[apigateway.Api(), apigateway.Api(), apigateway.Api(),],
                next_page_token="abc",
            ),
            apigateway.ListApisResponse(apis=[], next_page_token="def",),
            apigateway.ListApisResponse(
                apis=[apigateway.Api(),], next_page_token="ghi",
            ),
            apigateway.ListApisResponse(apis=[apigateway.Api(), apigateway.Api(),],),
            RuntimeError,
        )
        async_pager = await client.list_apis(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, apigateway.Api) for i in responses)


@pytest.mark.asyncio
async def test_list_apis_async_pages():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_apis), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListApisResponse(
                apis=[apigateway.Api(), apigateway.Api(), apigateway.Api(),],
                next_page_token="abc",
            ),
            apigateway.ListApisResponse(apis=[], next_page_token="def",),
            apigateway.ListApisResponse(
                apis=[apigateway.Api(),], next_page_token="ghi",
            ),
            apigateway.ListApisResponse(apis=[apigateway.Api(), apigateway.Api(),],),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_apis(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_api(transport: str = "grpc", request_type=apigateway.GetApiRequest):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.Api(
            name="name_value",
            display_name="display_name_value",
            managed_service="managed_service_value",
            state=apigateway.Api.State.CREATING,
        )
        response = client.get_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetApiRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, apigateway.Api)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.managed_service == "managed_service_value"
    assert response.state == apigateway.Api.State.CREATING


def test_get_api_from_dict():
    test_get_api(request_type=dict)


def test_get_api_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api), "__call__") as call:
        client.get_api()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetApiRequest()


@pytest.mark.asyncio
async def test_get_api_async(
    transport: str = "grpc_asyncio", request_type=apigateway.GetApiRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.Api(
                name="name_value",
                display_name="display_name_value",
                managed_service="managed_service_value",
                state=apigateway.Api.State.CREATING,
            )
        )
        response = await client.get_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetApiRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, apigateway.Api)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.managed_service == "managed_service_value"
    assert response.state == apigateway.Api.State.CREATING


@pytest.mark.asyncio
async def test_get_api_async_from_dict():
    await test_get_api_async(request_type=dict)


def test_get_api_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.GetApiRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api), "__call__") as call:
        call.return_value = apigateway.Api()
        client.get_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_api_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.GetApiRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(apigateway.Api())
        await client.get_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_api_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.Api()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_api(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_api_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_api(
            apigateway.GetApiRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_api_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.Api()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(apigateway.Api())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_api(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_api_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_api(
            apigateway.GetApiRequest(), name="name_value",
        )


def test_create_api(transport: str = "grpc", request_type=apigateway.CreateApiRequest):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateApiRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_api_from_dict():
    test_create_api(request_type=dict)


def test_create_api_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_api), "__call__") as call:
        client.create_api()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateApiRequest()


@pytest.mark.asyncio
async def test_create_api_async(
    transport: str = "grpc_asyncio", request_type=apigateway.CreateApiRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateApiRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_api_async_from_dict():
    await test_create_api_async(request_type=dict)


def test_create_api_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.CreateApiRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_api), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_api_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.CreateApiRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_api), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_api_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_api(
            parent="parent_value",
            api=apigateway.Api(name="name_value"),
            api_id="api_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].api == apigateway.Api(name="name_value")
        assert args[0].api_id == "api_id_value"


def test_create_api_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_api(
            apigateway.CreateApiRequest(),
            parent="parent_value",
            api=apigateway.Api(name="name_value"),
            api_id="api_id_value",
        )


@pytest.mark.asyncio
async def test_create_api_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_api(
            parent="parent_value",
            api=apigateway.Api(name="name_value"),
            api_id="api_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].api == apigateway.Api(name="name_value")
        assert args[0].api_id == "api_id_value"


@pytest.mark.asyncio
async def test_create_api_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_api(
            apigateway.CreateApiRequest(),
            parent="parent_value",
            api=apigateway.Api(name="name_value"),
            api_id="api_id_value",
        )


def test_update_api(transport: str = "grpc", request_type=apigateway.UpdateApiRequest):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateApiRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_api_from_dict():
    test_update_api(request_type=dict)


def test_update_api_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_api), "__call__") as call:
        client.update_api()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateApiRequest()


@pytest.mark.asyncio
async def test_update_api_async(
    transport: str = "grpc_asyncio", request_type=apigateway.UpdateApiRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateApiRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_api_async_from_dict():
    await test_update_api_async(request_type=dict)


def test_update_api_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.UpdateApiRequest()

    request.api.name = "api.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_api), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "api.name=api.name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_api_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.UpdateApiRequest()

    request.api.name = "api.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_api), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "api.name=api.name/value",) in kw["metadata"]


def test_update_api_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_api(
            api=apigateway.Api(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].api == apigateway.Api(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_api_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_api(
            apigateway.UpdateApiRequest(),
            api=apigateway.Api(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_api_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_api(
            api=apigateway.Api(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].api == apigateway.Api(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_api_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_api(
            apigateway.UpdateApiRequest(),
            api=apigateway.Api(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_api(transport: str = "grpc", request_type=apigateway.DeleteApiRequest):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteApiRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_api_from_dict():
    test_delete_api(request_type=dict)


def test_delete_api_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_api), "__call__") as call:
        client.delete_api()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteApiRequest()


@pytest.mark.asyncio
async def test_delete_api_async(
    transport: str = "grpc_asyncio", request_type=apigateway.DeleteApiRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteApiRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_api_async_from_dict():
    await test_delete_api_async(request_type=dict)


def test_delete_api_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.DeleteApiRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_api), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_api_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.DeleteApiRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_api), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_api(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_api_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_api(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_api_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_api(
            apigateway.DeleteApiRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_api_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_api), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_api(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_api_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_api(
            apigateway.DeleteApiRequest(), name="name_value",
        )


def test_list_api_configs(
    transport: str = "grpc", request_type=apigateway.ListApiConfigsRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListApiConfigsResponse(
            next_page_token="next_page_token_value",
            unreachable_locations=["unreachable_locations_value"],
        )
        response = client.list_api_configs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListApiConfigsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListApiConfigsPager)
    assert response.next_page_token == "next_page_token_value"
    assert response.unreachable_locations == ["unreachable_locations_value"]


def test_list_api_configs_from_dict():
    test_list_api_configs(request_type=dict)


def test_list_api_configs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        client.list_api_configs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListApiConfigsRequest()


@pytest.mark.asyncio
async def test_list_api_configs_async(
    transport: str = "grpc_asyncio", request_type=apigateway.ListApiConfigsRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListApiConfigsResponse(
                next_page_token="next_page_token_value",
                unreachable_locations=["unreachable_locations_value"],
            )
        )
        response = await client.list_api_configs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.ListApiConfigsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListApiConfigsAsyncPager)
    assert response.next_page_token == "next_page_token_value"
    assert response.unreachable_locations == ["unreachable_locations_value"]


@pytest.mark.asyncio
async def test_list_api_configs_async_from_dict():
    await test_list_api_configs_async(request_type=dict)


def test_list_api_configs_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.ListApiConfigsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        call.return_value = apigateway.ListApiConfigsResponse()
        client.list_api_configs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_api_configs_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.ListApiConfigsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListApiConfigsResponse()
        )
        await client.list_api_configs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_api_configs_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListApiConfigsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_api_configs(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_api_configs_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_api_configs(
            apigateway.ListApiConfigsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_api_configs_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ListApiConfigsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ListApiConfigsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_api_configs(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_api_configs_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_api_configs(
            apigateway.ListApiConfigsRequest(), parent="parent_value",
        )


def test_list_api_configs_pager():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListApiConfigsResponse(
                api_configs=[
                    apigateway.ApiConfig(),
                    apigateway.ApiConfig(),
                    apigateway.ApiConfig(),
                ],
                next_page_token="abc",
            ),
            apigateway.ListApiConfigsResponse(api_configs=[], next_page_token="def",),
            apigateway.ListApiConfigsResponse(
                api_configs=[apigateway.ApiConfig(),], next_page_token="ghi",
            ),
            apigateway.ListApiConfigsResponse(
                api_configs=[apigateway.ApiConfig(), apigateway.ApiConfig(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_api_configs(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, apigateway.ApiConfig) for i in results)


def test_list_api_configs_pages():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_api_configs), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListApiConfigsResponse(
                api_configs=[
                    apigateway.ApiConfig(),
                    apigateway.ApiConfig(),
                    apigateway.ApiConfig(),
                ],
                next_page_token="abc",
            ),
            apigateway.ListApiConfigsResponse(api_configs=[], next_page_token="def",),
            apigateway.ListApiConfigsResponse(
                api_configs=[apigateway.ApiConfig(),], next_page_token="ghi",
            ),
            apigateway.ListApiConfigsResponse(
                api_configs=[apigateway.ApiConfig(), apigateway.ApiConfig(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_api_configs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_api_configs_async_pager():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_api_configs), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListApiConfigsResponse(
                api_configs=[
                    apigateway.ApiConfig(),
                    apigateway.ApiConfig(),
                    apigateway.ApiConfig(),
                ],
                next_page_token="abc",
            ),
            apigateway.ListApiConfigsResponse(api_configs=[], next_page_token="def",),
            apigateway.ListApiConfigsResponse(
                api_configs=[apigateway.ApiConfig(),], next_page_token="ghi",
            ),
            apigateway.ListApiConfigsResponse(
                api_configs=[apigateway.ApiConfig(), apigateway.ApiConfig(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_api_configs(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, apigateway.ApiConfig) for i in responses)


@pytest.mark.asyncio
async def test_list_api_configs_async_pages():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_api_configs), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            apigateway.ListApiConfigsResponse(
                api_configs=[
                    apigateway.ApiConfig(),
                    apigateway.ApiConfig(),
                    apigateway.ApiConfig(),
                ],
                next_page_token="abc",
            ),
            apigateway.ListApiConfigsResponse(api_configs=[], next_page_token="def",),
            apigateway.ListApiConfigsResponse(
                api_configs=[apigateway.ApiConfig(),], next_page_token="ghi",
            ),
            apigateway.ListApiConfigsResponse(
                api_configs=[apigateway.ApiConfig(), apigateway.ApiConfig(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_api_configs(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_api_config(
    transport: str = "grpc", request_type=apigateway.GetApiConfigRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api_config), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ApiConfig(
            name="name_value",
            display_name="display_name_value",
            gateway_service_account="gateway_service_account_value",
            service_config_id="service_config_id_value",
            state=apigateway.ApiConfig.State.CREATING,
        )
        response = client.get_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetApiConfigRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, apigateway.ApiConfig)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.gateway_service_account == "gateway_service_account_value"
    assert response.service_config_id == "service_config_id_value"
    assert response.state == apigateway.ApiConfig.State.CREATING


def test_get_api_config_from_dict():
    test_get_api_config(request_type=dict)


def test_get_api_config_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api_config), "__call__") as call:
        client.get_api_config()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetApiConfigRequest()


@pytest.mark.asyncio
async def test_get_api_config_async(
    transport: str = "grpc_asyncio", request_type=apigateway.GetApiConfigRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api_config), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ApiConfig(
                name="name_value",
                display_name="display_name_value",
                gateway_service_account="gateway_service_account_value",
                service_config_id="service_config_id_value",
                state=apigateway.ApiConfig.State.CREATING,
            )
        )
        response = await client.get_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.GetApiConfigRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, apigateway.ApiConfig)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.gateway_service_account == "gateway_service_account_value"
    assert response.service_config_id == "service_config_id_value"
    assert response.state == apigateway.ApiConfig.State.CREATING


@pytest.mark.asyncio
async def test_get_api_config_async_from_dict():
    await test_get_api_config_async(request_type=dict)


def test_get_api_config_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.GetApiConfigRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api_config), "__call__") as call:
        call.return_value = apigateway.ApiConfig()
        client.get_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_api_config_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.GetApiConfigRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api_config), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ApiConfig()
        )
        await client.get_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_api_config_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api_config), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ApiConfig()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_api_config(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_api_config_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_api_config(
            apigateway.GetApiConfigRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_api_config_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_api_config), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = apigateway.ApiConfig()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            apigateway.ApiConfig()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_api_config(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_api_config_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_api_config(
            apigateway.GetApiConfigRequest(), name="name_value",
        )


def test_create_api_config(
    transport: str = "grpc", request_type=apigateway.CreateApiConfigRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateApiConfigRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_api_config_from_dict():
    test_create_api_config(request_type=dict)


def test_create_api_config_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_api_config), "__call__"
    ) as call:
        client.create_api_config()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateApiConfigRequest()


@pytest.mark.asyncio
async def test_create_api_config_async(
    transport: str = "grpc_asyncio", request_type=apigateway.CreateApiConfigRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.CreateApiConfigRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_api_config_async_from_dict():
    await test_create_api_config_async(request_type=dict)


def test_create_api_config_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.CreateApiConfigRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_api_config), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_api_config_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.CreateApiConfigRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_api_config), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_api_config_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_api_config(
            parent="parent_value",
            api_config=apigateway.ApiConfig(name="name_value"),
            api_config_id="api_config_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].api_config == apigateway.ApiConfig(name="name_value")
        assert args[0].api_config_id == "api_config_id_value"


def test_create_api_config_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_api_config(
            apigateway.CreateApiConfigRequest(),
            parent="parent_value",
            api_config=apigateway.ApiConfig(name="name_value"),
            api_config_id="api_config_id_value",
        )


@pytest.mark.asyncio
async def test_create_api_config_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_api_config(
            parent="parent_value",
            api_config=apigateway.ApiConfig(name="name_value"),
            api_config_id="api_config_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].api_config == apigateway.ApiConfig(name="name_value")
        assert args[0].api_config_id == "api_config_id_value"


@pytest.mark.asyncio
async def test_create_api_config_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_api_config(
            apigateway.CreateApiConfigRequest(),
            parent="parent_value",
            api_config=apigateway.ApiConfig(name="name_value"),
            api_config_id="api_config_id_value",
        )


def test_update_api_config(
    transport: str = "grpc", request_type=apigateway.UpdateApiConfigRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateApiConfigRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_api_config_from_dict():
    test_update_api_config(request_type=dict)


def test_update_api_config_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_api_config), "__call__"
    ) as call:
        client.update_api_config()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateApiConfigRequest()


@pytest.mark.asyncio
async def test_update_api_config_async(
    transport: str = "grpc_asyncio", request_type=apigateway.UpdateApiConfigRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.UpdateApiConfigRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_api_config_async_from_dict():
    await test_update_api_config_async(request_type=dict)


def test_update_api_config_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.UpdateApiConfigRequest()

    request.api_config.name = "api_config.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_api_config), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "api_config.name=api_config.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_api_config_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.UpdateApiConfigRequest()

    request.api_config.name = "api_config.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_api_config), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "api_config.name=api_config.name/value",) in kw[
        "metadata"
    ]


def test_update_api_config_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_api_config(
            api_config=apigateway.ApiConfig(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].api_config == apigateway.ApiConfig(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_api_config_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_api_config(
            apigateway.UpdateApiConfigRequest(),
            api_config=apigateway.ApiConfig(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_api_config_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_api_config(
            api_config=apigateway.ApiConfig(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].api_config == apigateway.ApiConfig(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_api_config_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_api_config(
            apigateway.UpdateApiConfigRequest(),
            api_config=apigateway.ApiConfig(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_api_config(
    transport: str = "grpc", request_type=apigateway.DeleteApiConfigRequest
):
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteApiConfigRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_api_config_from_dict():
    test_delete_api_config(request_type=dict)


def test_delete_api_config_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_api_config), "__call__"
    ) as call:
        client.delete_api_config()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteApiConfigRequest()


@pytest.mark.asyncio
async def test_delete_api_config_async(
    transport: str = "grpc_asyncio", request_type=apigateway.DeleteApiConfigRequest
):
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == apigateway.DeleteApiConfigRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_api_config_async_from_dict():
    await test_delete_api_config_async(request_type=dict)


def test_delete_api_config_field_headers():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.DeleteApiConfigRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_api_config), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_api_config_field_headers_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = apigateway.DeleteApiConfigRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_api_config), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_api_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_api_config_flattened():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_api_config(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_api_config_flattened_error():
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_api_config(
            apigateway.DeleteApiConfigRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_api_config_flattened_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_api_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_api_config(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_api_config_flattened_error_async():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_api_config(
            apigateway.DeleteApiConfigRequest(), name="name_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.ApiGatewayServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ApiGatewayServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.ApiGatewayServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ApiGatewayServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.ApiGatewayServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ApiGatewayServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ApiGatewayServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = ApiGatewayServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ApiGatewayServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.ApiGatewayServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.ApiGatewayServiceGrpcTransport,
        transports.ApiGatewayServiceGrpcAsyncIOTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, "default") as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = ApiGatewayServiceClient(credentials=ga_credentials.AnonymousCredentials(),)
    assert isinstance(client.transport, transports.ApiGatewayServiceGrpcTransport,)


def test_api_gateway_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.ApiGatewayServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_api_gateway_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.apigateway_v1.services.api_gateway_service.transports.ApiGatewayServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.ApiGatewayServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "list_gateways",
        "get_gateway",
        "create_gateway",
        "update_gateway",
        "delete_gateway",
        "list_apis",
        "get_api",
        "create_api",
        "update_api",
        "delete_api",
        "list_api_configs",
        "get_api_config",
        "create_api_config",
        "update_api_config",
        "delete_api_config",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


@requires_google_auth_gte_1_25_0
def test_api_gateway_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.apigateway_v1.services.api_gateway_service.transports.ApiGatewayServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.ApiGatewayServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


@requires_google_auth_lt_1_25_0
def test_api_gateway_service_base_transport_with_credentials_file_old_google_auth():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.apigateway_v1.services.api_gateway_service.transports.ApiGatewayServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.ApiGatewayServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_api_gateway_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.apigateway_v1.services.api_gateway_service.transports.ApiGatewayServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.ApiGatewayServiceTransport()
        adc.assert_called_once()


@requires_google_auth_gte_1_25_0
def test_api_gateway_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        ApiGatewayServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@requires_google_auth_lt_1_25_0
def test_api_gateway_service_auth_adc_old_google_auth():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        ApiGatewayServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.ApiGatewayServiceGrpcTransport,
        transports.ApiGatewayServiceGrpcAsyncIOTransport,
    ],
)
@requires_google_auth_gte_1_25_0
def test_api_gateway_service_transport_auth_adc(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])
        adc.assert_called_once_with(
            scopes=["1", "2"],
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.ApiGatewayServiceGrpcTransport,
        transports.ApiGatewayServiceGrpcAsyncIOTransport,
    ],
)
@requires_google_auth_lt_1_25_0
def test_api_gateway_service_transport_auth_adc_old_google_auth(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class(quota_project_id="octopus")
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.ApiGatewayServiceGrpcTransport, grpc_helpers),
        (transports.ApiGatewayServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_gte_1_26_0
def test_api_gateway_service_transport_create_channel(transport_class, grpc_helpers):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        adc.return_value = (creds, None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])

        create_channel.assert_called_with(
            "apigateway.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            scopes=["1", "2"],
            default_host="apigateway.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.ApiGatewayServiceGrpcTransport, grpc_helpers),
        (transports.ApiGatewayServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_lt_1_26_0
def test_api_gateway_service_transport_create_channel_old_api_core(
    transport_class, grpc_helpers
):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        adc.return_value = (creds, None)
        transport_class(quota_project_id="octopus")

        create_channel.assert_called_with(
            "apigateway.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.ApiGatewayServiceGrpcTransport, grpc_helpers),
        (transports.ApiGatewayServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_lt_1_26_0
def test_api_gateway_service_transport_create_channel_user_scopes(
    transport_class, grpc_helpers
):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        adc.return_value = (creds, None)

        transport_class(quota_project_id="octopus", scopes=["1", "2"])

        create_channel.assert_called_with(
            "apigateway.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            scopes=["1", "2"],
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.ApiGatewayServiceGrpcTransport,
        transports.ApiGatewayServiceGrpcAsyncIOTransport,
    ],
)
def test_api_gateway_service_grpc_transport_client_cert_source_for_mtls(
    transport_class,
):
    cred = ga_credentials.AnonymousCredentials()

    # Check ssl_channel_credentials is used if provided.
    with mock.patch.object(transport_class, "create_channel") as mock_create_channel:
        mock_ssl_channel_creds = mock.Mock()
        transport_class(
            host="squid.clam.whelk",
            credentials=cred,
            ssl_channel_credentials=mock_ssl_channel_creds,
        )
        mock_create_channel.assert_called_once_with(
            "squid.clam.whelk:443",
            credentials=cred,
            credentials_file=None,
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            ssl_credentials=mock_ssl_channel_creds,
            quota_project_id=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )

    # Check if ssl_channel_credentials is not provided, then client_cert_source_for_mtls
    # is used.
    with mock.patch.object(transport_class, "create_channel", return_value=mock.Mock()):
        with mock.patch("grpc.ssl_channel_credentials") as mock_ssl_cred:
            transport_class(
                credentials=cred,
                client_cert_source_for_mtls=client_cert_source_callback,
            )
            expected_cert, expected_key = client_cert_source_callback()
            mock_ssl_cred.assert_called_once_with(
                certificate_chain=expected_cert, private_key=expected_key
            )


def test_api_gateway_service_host_no_port():
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="apigateway.googleapis.com"
        ),
    )
    assert client.transport._host == "apigateway.googleapis.com:443"


def test_api_gateway_service_host_with_port():
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="apigateway.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "apigateway.googleapis.com:8000"


def test_api_gateway_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.ApiGatewayServiceGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_api_gateway_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.ApiGatewayServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [
        transports.ApiGatewayServiceGrpcTransport,
        transports.ApiGatewayServiceGrpcAsyncIOTransport,
    ],
)
def test_api_gateway_service_transport_channel_mtls_with_client_cert_source(
    transport_class,
):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = ga_credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(google.auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [
        transports.ApiGatewayServiceGrpcTransport,
        transports.ApiGatewayServiceGrpcAsyncIOTransport,
    ],
)
def test_api_gateway_service_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_api_gateway_service_grpc_lro_client():
    client = ApiGatewayServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_api_gateway_service_grpc_lro_async_client():
    client = ApiGatewayServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_api_path():
    project = "squid"
    api = "clam"
    expected = "projects/{project}/locations/global/apis/{api}".format(
        project=project, api=api,
    )
    actual = ApiGatewayServiceClient.api_path(project, api)
    assert expected == actual


def test_parse_api_path():
    expected = {
        "project": "whelk",
        "api": "octopus",
    }
    path = ApiGatewayServiceClient.api_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_api_path(path)
    assert expected == actual


def test_api_config_path():
    project = "oyster"
    api = "nudibranch"
    api_config = "cuttlefish"
    expected = "projects/{project}/locations/global/apis/{api}/configs/{api_config}".format(
        project=project, api=api, api_config=api_config,
    )
    actual = ApiGatewayServiceClient.api_config_path(project, api, api_config)
    assert expected == actual


def test_parse_api_config_path():
    expected = {
        "project": "mussel",
        "api": "winkle",
        "api_config": "nautilus",
    }
    path = ApiGatewayServiceClient.api_config_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_api_config_path(path)
    assert expected == actual


def test_gateway_path():
    project = "scallop"
    location = "abalone"
    gateway = "squid"
    expected = "projects/{project}/locations/{location}/gateways/{gateway}".format(
        project=project, location=location, gateway=gateway,
    )
    actual = ApiGatewayServiceClient.gateway_path(project, location, gateway)
    assert expected == actual


def test_parse_gateway_path():
    expected = {
        "project": "clam",
        "location": "whelk",
        "gateway": "octopus",
    }
    path = ApiGatewayServiceClient.gateway_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_gateway_path(path)
    assert expected == actual


def test_managed_service_path():
    service = "oyster"
    expected = "services/{service}".format(service=service,)
    actual = ApiGatewayServiceClient.managed_service_path(service)
    assert expected == actual


def test_parse_managed_service_path():
    expected = {
        "service": "nudibranch",
    }
    path = ApiGatewayServiceClient.managed_service_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_managed_service_path(path)
    assert expected == actual


def test_service_path():
    service = "cuttlefish"
    config = "mussel"
    expected = "services/{service}/configs/{config}".format(
        service=service, config=config,
    )
    actual = ApiGatewayServiceClient.service_path(service, config)
    assert expected == actual


def test_parse_service_path():
    expected = {
        "service": "winkle",
        "config": "nautilus",
    }
    path = ApiGatewayServiceClient.service_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_service_path(path)
    assert expected == actual


def test_service_account_path():
    project = "scallop"
    service_account = "abalone"
    expected = "projects/{project}/serviceAccounts/{service_account}".format(
        project=project, service_account=service_account,
    )
    actual = ApiGatewayServiceClient.service_account_path(project, service_account)
    assert expected == actual


def test_parse_service_account_path():
    expected = {
        "project": "squid",
        "service_account": "clam",
    }
    path = ApiGatewayServiceClient.service_account_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_service_account_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "whelk"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = ApiGatewayServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "octopus",
    }
    path = ApiGatewayServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "oyster"
    expected = "folders/{folder}".format(folder=folder,)
    actual = ApiGatewayServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "nudibranch",
    }
    path = ApiGatewayServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "cuttlefish"
    expected = "organizations/{organization}".format(organization=organization,)
    actual = ApiGatewayServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "mussel",
    }
    path = ApiGatewayServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "winkle"
    expected = "projects/{project}".format(project=project,)
    actual = ApiGatewayServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "nautilus",
    }
    path = ApiGatewayServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "scallop"
    location = "abalone"
    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = ApiGatewayServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "squid",
        "location": "clam",
    }
    path = ApiGatewayServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = ApiGatewayServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.ApiGatewayServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = ApiGatewayServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.ApiGatewayServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = ApiGatewayServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
