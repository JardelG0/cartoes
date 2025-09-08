from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path('', views.acesso_view, name='acesso'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # ✅ Login/Logout prontos do Django
    path('login/', auth_views.LoginView.as_view(
        template_name='cartoes_app/login.html',
        redirect_authenticated_user=True   # se já estiver logado, não fica preso no login
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='acesso'), name='logout'),

    path('editar-cartao/<int:cartao_id>/', views.editar_cartao_view, name='editar_cartao'),
    path('excluir-cartao/<int:cartao_id>/', views.confirmar_exclusao_view, name='excluir_cartao'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.registrar_view, name='registrar'),  # visual público (placeholder)
    path('registrar-usuario/', views.registrar_usuario_view, name='registrar_usuario'),  # admin-only
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('gastos/', views.gastos_view, name='gastos'),
    path('cartoes/novo/', views.criar_cartao_view, name='criar_cartao'),
    path('gastos/anexos/<int:anexo_id>/excluir/', views.excluir_anexo_gasto, name='excluir_anexo_gasto'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)