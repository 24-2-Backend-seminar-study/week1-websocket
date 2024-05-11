from django.urls import path
from .views import SignUpView


app_name = "account"
urlpatterns = [
    # CBV url path
    path("signup/", SignUpView.as_view()),
]