from datetime import datetime

from django.db.models import F
from django.shortcuts import render

from cores.apis import api
from cores.enums import ApiTagEnum
from cores.utils import generate_presigned_url
from lands.models import Land, Info, LandInfoMapping, LandCommentMapping, LandInfoUserMapping, LandImageMapping
from lands.schemas import LandPointParams, LandSchema, LandLikeDTO, LandLikeParams, CommentSchema, CommentParams, \
    PresignedUrlDTO, PresignedUrlCallbackParams


# Create your views here.


# 지도 조회 (데이터 없으면 생성)
@api.get(
    path="land/",
    response={200: LandSchema},
    tags=[ApiTagEnum.lands]
)
def get_lands(request, name: str, latitude: float, longitude: float):
    user = request.user

    try:
        land = Land.objects.get(name=name)
    except Land.DoesNotExist:
        land = Land.objects.create(
            name=name,
            latitude=latitude,
            longitude=longitude
        )

    return LandSchema.from_instances(user, land)


# 토지 정보 좋아요, 싫어요 생성
@api.post(
    path="land/like/",
    response={200: LandLikeDTO},
    tags=[ApiTagEnum.lands]
)
def land_like(request, params: LandLikeParams):
    user = request.user
    land_id = params.land_id
    info_id = params.info_id

    try:
        land_info_user_mapping = user.landinfousermapping_set.get(
            land_info_mapping__info_id=info_id,
            land_info_mapping__land_id=land_id
        )
        land_info_mapping = land_info_user_mapping.land_info_mapping

        if land_info_user_mapping.is_like_event:
            # 선택된 버튼을 like 누를 때
            land_info_mapping.like_count = land_info_mapping.like_count - 1 if land_info_mapping.like_count != 0 else 0
            land_info_user_mapping.is_like_event = False
            user.landinfousermapping_set.filter(
                land_info_mapping__info_id=info_id,
                land_info_mapping__land_id=land_id
            ).delete()
        else:
            # 선택되지 않은 버튼을 like 누를 때
            land_info_mapping.like_count = land_info_mapping.like_count + 1
            land_info_mapping.unlike_count = land_info_mapping.unlike_count - 1 if land_info_mapping.unlike_count != 0 else 0
            land_info_user_mapping.is_like_event = True
            land_info_user_mapping.save()

        land_info_mapping.save()
    except LandInfoUserMapping.DoesNotExist:
        try:
            land_info_mapping = LandInfoMapping.objects.get(info_id=info_id, land_id=land_id)
        except LandInfoMapping.DoesNotExist:
            land_info_mapping = LandInfoMapping.objects.create(
                info_id=info_id,
                land_id=land_id,
                like_count=1,
                unlike_count=0
            )

        land_info_user_mapping = LandInfoUserMapping.objects.create(
            land_info_mapping=land_info_mapping,
            user=user,
            is_like_event=True
        )

    return LandLikeDTO(counts=land_info_mapping.like_count, is_like_event=land_info_user_mapping.is_like_event)


@api.post(
    path="land/unlike/",
    response={200: LandLikeDTO},
    tags=[ApiTagEnum.lands]
)
def land_unlike(request, params: LandLikeParams):
    user = request.user
    land_id = params.land_id
    info_id = params.info_id

    try:
        land_info_user_mapping = user.landinfousermapping_set.get(
            land_info_mapping__info_id=info_id,
            land_info_mapping__land_id=land_id
        )
        land_info_mapping = land_info_user_mapping.land_info_mapping

        if land_info_user_mapping.is_like_event:
            # 선택되지 않은 버튼으로 unlike 누를 때
            land_info_mapping.like_count = land_info_mapping.like_count - 1 if land_info_mapping.like_count != 0 else 0
            land_info_mapping.unlike_count = land_info_mapping.unlike_count + 1
            land_info_user_mapping.is_like_event = False

            land_info_user_mapping.save()
        else:
            # 선택된 버튼으로 unlike 누를 때
            land_info_mapping.unlike_count = land_info_mapping.unlike_count - 1 if land_info_mapping.unlike_count != 0 else 0
            land_info_user_mapping.is_like_event = True

            user.landinfousermapping_set.filter(
                land_info_mapping__info_id=info_id,
                land_info_mapping__land_id=land_id
            ).delete()

        land_info_mapping.save()
    except LandInfoUserMapping.DoesNotExist:
        try:
            land_info_mapping = LandInfoMapping.objects.get(info_id=info_id, land_id=land_id)
        except LandInfoMapping.DoesNotExist:
            land_info_mapping = LandInfoMapping.objects.create(
                land_id=land_id,
                info_id=info_id,
                like_count=0,
                unlike_count=1
            )

        land_info_user_mapping = LandInfoUserMapping.objects.create(
            land_info_mapping=land_info_mapping,
            user=user,
            is_like_event=False
        )

    return LandLikeDTO(counts=land_info_mapping.unlike_count, is_like_event=land_info_user_mapping.is_like_event)


# 토지 이미지 생성
@api.get(
    path="land/presigned_url/",
    response={200: PresignedUrlDTO},
    tags=[ApiTagEnum.lands]
)
def get_presigned_url(request):
    bucket = 'junction-landwiki'
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"image-{timestamp}"
    presigned_url = generate_presigned_url(
        bucket, filename
    )
    return PresignedUrlDTO(url=presigned_url, filename=filename)


@api.post(
    path='land/presigned_url/callback',
    response={200: None},
    tags=[ApiTagEnum.lands]
)
def presigned_url_callback(request, params: PresignedUrlCallbackParams):
    bucket = 'junction-landwiki'

    land_id = params.land_id
    filename = params.filename

    land = Land.objects.get(id=land_id)
    image = f"https://{bucket}.s3.ap-northeast-2.amazonaws.com/{filename}"
    LandImageMapping.objects.create(land=land, image=image)


# 토지 댓글 생성
@api.post(
    path="land/comment/",
    response={200: None},
    tags=[ApiTagEnum.lands]
)
def create_comment(request, params: CommentParams):
    user = request.user
    land_id = params.land_id
    comment = params.comment

    LandCommentMapping.objects.create(
        user=user,
        land=land_id,
        comment=comment
    )
