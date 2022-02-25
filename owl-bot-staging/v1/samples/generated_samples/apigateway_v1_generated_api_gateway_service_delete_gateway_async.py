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
# Generated code. DO NOT EDIT!
#
# Snippet for DeleteGateway
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-api-gateway


# [START apigateway_v1_generated_ApiGatewayService_DeleteGateway_async]
from google.cloud import apigateway_v1


async def sample_delete_gateway():
    # Create a client
    client = apigateway_v1.ApiGatewayServiceAsyncClient()

    # Initialize request argument(s)
    request = apigateway_v1.DeleteGatewayRequest(
        name="name_value",
    )

    # Make the request
    operation = client.delete_gateway(request=request)

    print("Waiting for operation to complete...")

    response = await operation.result()

    # Handle the response
    print(response)

# [END apigateway_v1_generated_ApiGatewayService_DeleteGateway_async]
