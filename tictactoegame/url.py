from django.urls import path,include
from . import views

urlpatterns = [  
 	path('', views.entry, name="entry"),
	path('entry/', views.entry, name="entry"),
	path('game/', views.game, name="game"),
	path('poll/', views.poll, name="poll"),
	path('clear/', views.clear, name="clear"),
	path('reset/', views.reset, name="reset"),
]
