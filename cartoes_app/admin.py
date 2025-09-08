from django.contrib import admin
from .models import CartaoCredito, Gasto, GastoAnexo

@admin.register(CartaoCredito)
class CartaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'bandeira', 'limite', 'vencimento_formatado', 'usuario')
    search_fields = ('nome', 'numero')
    list_filter = ('bandeira',)

    # # Se quiser evitar expor o número completo no Django Admin:
    # def mostrar_numero(self, obj):
    #     return obj.numero_mascarado()
    # mostrar_numero.short_description = 'Número'

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cartao', 'descricao', 'valor', 'data', 'created_at')
    list_filter = ('data', 'usuario')
    search_fields = ('descricao', 'usuario__username', 'cartao__nome')

@admin.register(GastoAnexo)
class GastoAnexoAdmin(admin.ModelAdmin):
    list_display = ('gasto', 'nome_original', 'uploaded_at')
    search_fields = ('nome_original', 'gasto__descricao', 'gasto__usuario__username')
    list_filter = ('uploaded_at',)