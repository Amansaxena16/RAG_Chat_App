from django.urls import path
from .views import AskLLM


urlpatterns = [
     path('ask/', AskLLM.as_view(), name='ask_llm'),
]