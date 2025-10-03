from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    # acesso_view,
    dashboard_view,
    PortalLoginView,
    editar_cartao_view,
    confirmar_exclusao_view,
    registrar_usuario_view,
    usuarios_view,
    gastos_view,
    criar_cartao_view,
    excluir_anexo_gasto,
    recarregar_cartao_view,
)

urlpatterns = [
    # # ✅ Login/Logout unificados    
    path('', PortalLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('dashboard/', dashboard_view, name='dashboard'),

    # path('acesso/', acesso_view, name='acesso'),
    path('cartoes/<int:cartao_id>/recarregar/', recarregar_cartao_view, name='recarregar_cartao'),


    # Cartões
    path('editar-cartao/<int:cartao_id>/', editar_cartao_view, name='editar_cartao'),
    path('excluir-cartao/<int:cartao_id>/', confirmar_exclusao_view, name='excluir_cartao'),
    path('cartoes/novo/', criar_cartao_view, name='criar_cartao'),

    # Usuários
    path('registrar-usuario/', registrar_usuario_view, name='registrar_usuario'),  # admin-only
    path('usuarios/', usuarios_view, name='usuarios'),

    # Gastos
    path('gastos/', gastos_view, name='gastos'),
    path('gastos/anexos/<int:anexo_id>/excluir/', excluir_anexo_gasto, name='excluir_anexo_gasto'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
