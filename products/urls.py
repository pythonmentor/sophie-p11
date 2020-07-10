from django.urls import path
from . import views


urlpatterns = [
    path('results', views.results, name='results'),
    path('product/<product_id>/', views.detail, name='product'),
    path('product/<int:comment_id>/comment/', views.add_comment, name='add_comment'),
    #path('product/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    #path('product/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    path('my_substitutes/', views.my_substitutes, name='my_substitutes'),
    path('results/save_in_db/', views.save_in_db, name='save_in_db'),
    path('autocomplete/', views.autocompleteModel, name='autocomplete'),
    path('legal_notice/', views.legal_notice, name='legal_notice'),
    # path('results/save_in_db/<substitute_id>/<product_id>/', views.save_in_db, name='save_in_db')
]
