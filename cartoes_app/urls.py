from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    acesso_view,
    dashboard_view,
    PortalLoginView,
    editar_cartao_view,
    confirmar_exclusao_view,
    # registrar_view,
    registrar_usuario_view,
    usuarios_view,
    gastos_view,
    criar_cartao_view,
    excluir_anexo_gasto,
)

urlpatterns = [
    path('', acesso_view, name='acesso'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # ✅ Login/Logout unificados
    path('login/', PortalLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='acesso'), name='logout'),

    # Cartões
    path('editar-cartao/<int:cartao_id>/', editar_cartao_view, name='editar_cartao'),
    path('excluir-cartao/<int:cartao_id>/', confirmar_exclusao_view, name='excluir_cartao'),
    path('cartoes/novo/', criar_cartao_view, name='criar_cartao'),

    # Usuários
    # path('registrar/', registrar_view, name='registrar'),  # placeholder
    path('registrar-usuario/', registrar_usuario_view, name='registrar_usuario'),  # admin-only
    path('usuarios/', usuarios_view, name='usuarios'),

    # Gastos
    path('gastos/', gastos_view, name='gastos'),
    path('gastos/anexos/<int:anexo_id>/excluir/', excluir_anexo_gasto, name='excluir_anexo_gasto'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
