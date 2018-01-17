from rest_framework import routers
from .views import SutraViewSet, ReelViewSet, PageViewSet
from django.conf.urls import url, include
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'sutra', SutraViewSet)
router.register(r'reel', ReelViewSet)
router.register(r'page', PageViewSet)



schema_view = get_schema_view(
    title='Example API',
    renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer]
)


urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^swagger/$', schema_view)
]