from typing import List

from django.db.models import F
from ninja import Schema

from lands.models import Info, LandInfoUserMapping


class LandPointParams(Schema):
    name: str
    latitude: float
    longitude: float


class InfoSchema(Schema):
    id: int
    group_name: str
    name: str
    like_count: int
    unlike_count: int
    is_like: bool
    is_unlike: bool


class CommentSchema(Schema):
    login_id: str
    comment: str


class LandSchema(Schema):
    id: int
    infos: List[InfoSchema]
    images: List[str]
    comments: List[CommentSchema]

    @classmethod
    def from_instances(cls, user, land):
        info_list = list(Info.objects.values("id", "group_name", "name"))
        info_id_2_names = {}
        for item in info_list:
            info_id_2_names[item['id']] = {
                "group_name": item['group_name'],
                "name": item['name']
            }

        land_info_list = list(land.landinfomapping_set.values("id", "info", "like_count", "unlike_count"))
        info_id_2_counts = {}
        for item in land_info_list:
            info_id_2_counts[item['info']] = {
                "mapping_id": item['id'],
                "like_count": item['like_count'],
                "unlike_count": item['unlike_count']
            }

        user_like_info_id_list = list(user.landinfousermapping_set.filter(
            is_like_event=True
        ).values_list("land_info_mapping__info", flat=True))

        user_unlike_info_id_list = list(user.landinfousermapping_set.filter(
            is_like_event=False
        ).values_list("land_info_mapping__info", flat=True))

        info_schema_list = [
            InfoSchema(
                id=item['id'],
                group_name=info_id_2_names[item['id']]['group_name'],
                name=info_id_2_names[item['id']]['name'],
                like_count=info_id_2_counts[item['id']]['like_count'],
                unlike_count=info_id_2_counts[item['id']]['unlike_count'],
                is_like=True if item['id'] in user_like_info_id_list else False,
                is_unlike=True if item['id'] in user_unlike_info_id_list else False
            ) if item['id'] in info_id_2_counts.keys() else
            InfoSchema(
                id=item['id'],
                group_name=info_id_2_names[item['id']]['group_name'],
                name=info_id_2_names[item['id']]['name'],
                like_count=0,
                unlike_count=0,
                is_like=True if item['id'] in user_like_info_id_list else False,
                is_unlike=True if item['id'] in user_unlike_info_id_list else False
            ) for item in info_list
        ]
        image_list = list(land.landimagemapping_set.values_list("image", flat=True))

        comment_list = list(land.landcommentmapping_set.annotate(
            login_id=F("user__login_id")
        ).order_by("-created").values("login_id", "comment"))

        comment_schemas = [CommentSchema(login_id=item['login_id'], comment=item['comment']) for item in comment_list]

        return cls(
            id=land.id,
            infos=info_schema_list,
            images=image_list,
            comments=comment_schemas
        )


class LandLikeDTO(Schema):
    counts: int
    is_like_event: bool


class LandLikeParams(Schema):
    land_id: int
    info_id: int


class CommentParams(Schema):
    land_id: int
    comment: str


class PresignedUrlDTO(Schema):
    url: str
    filename: str


class PresignedUrlCallbackParams(Schema):
    land_id: int
    filename: str
