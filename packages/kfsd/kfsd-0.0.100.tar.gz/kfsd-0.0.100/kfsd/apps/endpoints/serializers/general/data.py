from rest_framework import serializers
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
)

from kfsd.apps.models.constants import MAX_LENGTH, MIN_LENGTH
from kfsd.apps.endpoints.serializers.model import BaseModelSerializer
from kfsd.apps.models.tables.general.data import Data
from kfsd.apps.endpoints.serializers.base import get_serializer_val


class DataModelSerializer(BaseModelSerializer):
    name = serializers.CharField(
        validators=[
            MinLengthValidator(MIN_LENGTH),
            MaxLengthValidator(MAX_LENGTH),
        ]
    )
    is_template = serializers.BooleanField(default=False)
    is_json = serializers.BooleanField(default=True)
    txt_body = serializers.CharField(
        required=False,
        validators=[
            MinLengthValidator(MIN_LENGTH),
        ],
    )
    json_body = serializers.JSONField(default=dict)

    def validate(self, data):
        is_json = get_serializer_val(self, data, "is_json")
        if not is_json and not get_serializer_val(self, data, "txt_body"):
            raise serializers.ValidationError(
                "txt_body field need to be set if is_json is false"
            )

        if is_json and not get_serializer_val(self, data, "json_body"):
            raise serializers.ValidationError(
                "json_body field need to be set if is_json is true"
            )

        return data

    class Meta:
        model = Data
        fields = "__all__"


class DataViewModelSerializer(DataModelSerializer):
    id = None
    created = None
    updated = None

    class Meta:
        model = Data
        exclude = ("created", "updated", "id")
