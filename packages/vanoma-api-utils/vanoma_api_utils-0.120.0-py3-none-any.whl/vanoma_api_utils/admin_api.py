from typing import Any, Dict
from django.conf import settings
from rest_framework import status
from vanoma_api_utils.http import client
from vanoma_api_utils.exceptions import BackendServiceException
from vanoma_api_utils.request import stringify_filters


class AdminApiException(BackendServiceException):
    pass


def get_administrators(filters: Dict[str, Any]) -> Dict[str, Any]:
    query = stringify_filters(filters)
    response = client.get(f"{settings.VANOMA_AUTH_API_URL}/v1/administrators?{query}")

    if not response.ok:
        json = response.json()
        raise AdminApiException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            json["error_code"],
            json["error_message"],
        )

    return response.json()


def create_annotation(entity_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    response = client.post(
        f"{settings.VANOMA_AUTH_API_URL}/v1/entities/{entity_id}/annotations", data=data
    )

    if not response.ok:
        json = response.json()
        raise AdminApiException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            json["error_code"],
            json["error_message"],
        )

    return response.json()


def get_admnistrators_dict(filters: Dict[str, Any]) -> Dict[str, Any]:
    return {
        administrator["administrator_id"]: administrator
        for administrator in get_administrators(filters)["results"]
    }
