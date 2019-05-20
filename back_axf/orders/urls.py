from django.urls import path
from rest_framework.routers import SimpleRouter

from orders.views import OrderView

router = SimpleRouter()
router.register('orders', OrderView)

urlpatterns = [

]

urlpatterns += router.urls