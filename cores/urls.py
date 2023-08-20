from django.urls import *
from cores.apis import api
from cores.views import *


urlpatterns = [
    path("api/", api.urls)
]
