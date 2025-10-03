# cartoes_app/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden

from datetime import date, timedelta
from calendar import monthrange
from decimal import Decimal
from .models import CartaoCredito, Gasto, GastoAnexo
from .forms import CartaoCreditoAdminForm, RegistrarUsuarioComumForm, GastoForm, RecargaSaldoForm


@staff_member_required
def recarregar_cartao_view(request, cartao_id):
    cartao = get_object_or_404(CartaoCredito, id=cartao_id)

    if request.method == "POST":
        form = RecargaSaldoForm(request.POST)
        if form.is_valid():
            valor = form.cleaned_data["valor"]
            cartao.saldo_atual = (cartao.saldo_atual or 0) + valor
            cartao.save()
            messages.success(request, f"Cartão {cartao.nome} recarregado em R$ {valor:.2f}.")
            return redirect("dashboard")
    else:
        form = RecargaSaldoForm()

    return render(request, "cartoes_app/recarregar_cartao.html", {
        "form": form,
        "cartao": cartao
    })


# # ========== Acesso / Login ==========
# def acesso_view(request):
#     """
#     Home pública: lista todos os usuários e mostra botão único de Login.
#     Se já estiver autenticado, redireciona conforme o tipo.
#     """
#     if request.user.is_authenticated:
#         return redirect('dashboard' if request.user.is_staff else 'gastos')

#     usuarios_comuns = User.objects.filter(is_staff=False).order_by('username')
#     return render(request, 'cartoes_app/acesso.html', {
#         'usuarios_comuns': usuarios_comuns,
#     })


class PortalLoginView(LoginView):
    """
    Login unificado. Após autenticar:
      - staff -> dashboard
      - usuário comum -> gastos
    """
    template_name = 'cartoes_app/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        return reverse('dashboard') if user.is_staff else reverse('gastos')


# ========== Dashboard ==========
@login_required
def dashboard_view(request):
    if request.user.is_staff:
        # Admin vê todos os usuários comuns e seus cartões
        usuarios = (
            User.objects.filter(is_staff=False)
            .order_by('username')
            .prefetch_related('cartoes')  # cartoes = related_name no model CartaoCredito(usuario)
        )

        hoje = date.today()
        periodo = request.GET.get('periodo', 'mes_atual')
        if periodo == 'mes_atual':
            start = date(hoje.year, hoje.month, 1)
            end = date(hoje.year, hoje.month, monthrange(hoje.year, hoje.month)[1])
        elif periodo == 'ult_30':
            start = hoje - timedelta(days=30)
            end = hoje
        else:
            start, end = None, None

        date_filter = {}
        if start and end:
            date_filter = {'data__range': (start, end)}

        # Calcula saldo de cada usuário
        for u in usuarios:
            limite_total = CartaoCredito.objects.filter(usuario=u).aggregate(total=Sum('limite'))['total'] or Decimal('0')
            gasto_total = Gasto.objects.filter(usuario=u, **date_filter).aggregate(total=Sum('valor'))['total'] or Decimal('0')
            u.saldo = limite_total - gasto_total
            u.limite_total = limite_total
            u.gasto_total = gasto_total

        total_usuarios = usuarios.count()
        total_cartoes = CartaoCredito.objects.count()
        limite_total = CartaoCredito.objects.aggregate(total=Sum('limite'))['total'] or Decimal('0')

        context = {
            'usuarios': usuarios,
            'total_usuarios': total_usuarios,
            'total_cartoes': total_cartoes,
            'limite_total': limite_total,
            'periodo': periodo,
            'periodo_inicio': start,
            'periodo_fim': end,
        }

    else:
        # Usuário comum
        cartoes = CartaoCredito.objects.filter(usuario=request.user).order_by('nome')

        hoje = date.today()
        periodo = request.GET.get('periodo', 'mes_atual')
        if periodo == 'mes_atual':
            start = date(hoje.year, hoje.month, 1)
            end = date(hoje.year, hoje.month, monthrange(hoje.year, hoje.month)[1])
        elif periodo == 'ult_30':
            start = hoje - timedelta(days=30)
            end = hoje
        else:
            start, end = None, None

        date_filter = {}
        if start and end:
            date_filter = {'data__range': (start, end)}

        limite_total = cartoes.aggregate(total=Sum('limite'))['total'] or Decimal('0')
        gasto_total = Gasto.objects.filter(usuario=request.user, **date_filter).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        saldo = limite_total - gasto_total

        context = {
            'cartoes': cartoes,
            'limite_total': limite_total,
            'gasto_total': gasto_total,
            'saldo': saldo,
            'periodo': periodo,
            'periodo_inicio': start,
            'periodo_fim': end,
        }

    return render(request, 'cartoes_app/dashboard.html', context)


# ========== CRUD de Cartões (admin) ==========
@staff_member_required
def criar_cartao_view(request):
    """
    Página dedicada para o admin criar um novo cartão (com seleção de usuário dono).
    """
    if request.method == 'POST':
        form = CartaoCreditoAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cartão criado e vinculado ao usuário selecionado.')
            return redirect('dashboard')
    else:
        form = CartaoCreditoAdminForm()

    return render(request, 'cartoes_app/cartao_form.html', {'form': form, 'titulo': 'Adicionar Novo Cartão'})


@staff_member_required
def editar_cartao_view(request, cartao_id):
    cartao = get_object_or_404(CartaoCredito, id=cartao_id)
    if request.method == 'POST':
        form = CartaoCreditoAdminForm(request.POST, instance=cartao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cartão atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = CartaoCreditoAdminForm(instance=cartao)
    return render(request, 'cartoes_app/editar_cartao.html', {'form': form})


@staff_member_required
def confirmar_exclusao_view(request, cartao_id):
    cartao = get_object_or_404(CartaoCredito, id=cartao_id)
    if request.method == 'POST':
        nome = cartao.nome
        cartao.delete()
        messages.success(request, f'Cartão "{nome}" foi excluído com sucesso.')
        return redirect('dashboard')
    return render(request, 'cartoes_app/confirmar_exclusao.html', {'cartao': cartao})


# ========== Usuários (admin) ==========
@staff_member_required
def registrar_usuario_view(request):
    """
    Registrar usuário comum (sem listar usuários aqui; listagem fica na página 'usuarios').
    """
    if request.method == 'POST':
        form = RegistrarUsuarioComumForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário comum registrado!")
            return redirect('dashboard')
    else:
        form = RegistrarUsuarioComumForm()

    return render(request, 'cartoes_app/registrar_usuario.html', {
        'form': form,
    })


@staff_member_required
def usuarios_view(request):
    """
    Página para o admin selecionar um usuário comum e visualizar os cartões dele.
    """
    usuarios = User.objects.filter(is_staff=False).order_by('username')
    usuario_id = request.GET.get('usuario')
    usuario_selecionado = None
    cartoes = CartaoCredito.objects.none()
    limite_total = 0

    if usuario_id:
        try:
            usuario_selecionado = usuarios.get(id=int(usuario_id))
            cartoes = CartaoCredito.objects.filter(usuario=usuario_selecionado).select_related('usuario')
            limite_total = cartoes.aggregate(total=Sum('limite'))['total'] or 0
        except (ValueError, User.DoesNotExist):
            usuario_selecionado = None

    context = {
        'usuarios': usuarios,
        'usuario_selecionado': usuario_selecionado,
        'cartoes': cartoes,
        'limite_total': limite_total,
    }
    return render(request, 'cartoes_app/usuarios.html', context)


# ========== Gastos ==========
@login_required
def gastos_view(request):
    # ===== Definição do usuário alvo =====
    if request.user.is_staff:
        usuarios = User.objects.filter(is_staff=False).order_by('username')
        usuario_id = request.GET.get('usuario')

        user_alvo = None
        if usuario_id:
            try:
                user_alvo = usuarios.get(id=int(usuario_id))
            except (ValueError, User.DoesNotExist):
                user_alvo = None

        # Se não veio ?usuario=, seleciona o primeiro usuário comum automaticamente
        if user_alvo is None:
            user_alvo = usuarios.first()
            if user_alvo is None:
                messages.info(request, 'Não há usuários comuns cadastrados ainda. Cadastre um para visualizar/lançar gastos.')
    else:
        usuarios = None
        user_alvo = request.user

    # ===== Período =====
    periodo = request.GET.get('periodo', 'mes_atual')  # mes_atual | ult_30 | todos
    hoje = date.today()
    if periodo == 'mes_atual':
        start = date(hoje.year, hoje.month, 1)
        end = date(hoje.year, hoje.month, monthrange(hoje.year, hoje.month)[1])
    elif periodo == 'ult_30':
        start = hoje - timedelta(days=30)
        end = hoje
    else:
        start, end = None, None

    date_filter = {}
    if start and end:
        date_filter = {'data__range': (start, end)}

    # ===== Dados base =====
    cartoes = CartaoCredito.objects.filter(usuario=user_alvo).order_by('nome') if user_alvo else CartaoCredito.objects.none()
    gastos_qs = Gasto.objects.filter(usuario=user_alvo) if user_alvo else Gasto.objects.none()

    # Totais do usuário
    limite_total_cartoes = cartoes.aggregate(total=Sum('limite'))['total'] or Decimal('0')
    total_gasto_periodo = gastos_qs.filter(**date_filter).aggregate(total=Sum('valor'))['total'] or Decimal('0')

    # Saldo total do período
    saldo_total = limite_total_cartoes - total_gasto_periodo
    saldo_total_negativo = saldo_total < 0
    saldo_total_zero = saldo_total == 0

    # Resumo por cartão
    cartoes_resumo = []
    if user_alvo:
        gastos_por_cartao = (
            gastos_qs.filter(**date_filter)
            .values('cartao_id')
            .annotate(gasto_total=Sum('valor'))
        )
        gasto_map = {row['cartao_id']: (row['gasto_total'] or Decimal('0')) for row in gastos_por_cartao}

        for c in cartoes:
            gasto = gasto_map.get(c.id, Decimal('0'))
            limite = c.limite or Decimal('0')
            saldo = limite - gasto
            cartoes_resumo.append({
                'id': c.id,
                'nome': c.nome,
                'bandeira_display': c.get_bandeira_display(),
                'limite': limite,
                'gasto_total': gasto,
                'saldo_restante': saldo,
                'estourado': gasto > limite,
                'numero_mascarado': getattr(c, 'numero_mascarado', None),
            })

    # ===== POST: registrar gasto (com anexos) =====
    if request.method == 'POST':
        if not user_alvo:
            messages.error(request, 'Selecione/cadastre um usuário para registrar o gasto.')
            return redirect('gastos')

        form = GastoForm(request.POST, request.FILES, user_alvo=user_alvo)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.usuario = user_alvo

            if gasto.cartao.usuario_id != user_alvo.id:
                form.add_error('cartao', 'Este cartão não pertence ao usuário selecionado.')
            else:
                gasto.save()
                files = request.FILES.getlist('anexos')
                for f in files:
                    GastoAnexo.objects.create(gasto=gasto, arquivo=f, nome_original=f.name)

                messages.success(request, 'Gasto registrado com sucesso.')
                # Redireciona preservando filtros e usuário (se admin)
                base = reverse('gastos')
                params = []
                if request.user.is_staff and user_alvo:
                    params.append(f'usuario={user_alvo.id}')
                if periodo:
                    params.append(f'periodo={periodo}')
                url = base + ('?' + '&'.join(params) if params else '')
                return redirect(url)
    else:
        form = GastoForm(user_alvo=user_alvo)

    # Lista de gastos otimizada
    gastos_listados = (
        gastos_qs.filter(**date_filter)
        .select_related('cartao')
        .prefetch_related('anexos')
        .order_by('-data', '-id')
    )

    context = {
        'usuarios': usuarios,
        'user_alvo': user_alvo,
        'cartoes': cartoes,
        'gastos': gastos_listados,
        'limite_total_cartoes': limite_total_cartoes,
        'total_gasto_periodo': total_gasto_periodo,
        'form': form,
        'periodo': periodo,
        'periodo_inicio': start,
        'periodo_fim': end,
        'cartoes_resumo': cartoes_resumo,
        'saldo_total': saldo_total,
        'saldo_total_negativo': saldo_total_negativo,
        'saldo_total_zero': saldo_total_zero,
    }
    return render(request, 'cartoes_app/gastos.html', context)


# ========== Anexos de Gasto ==========
@login_required
def excluir_anexo_gasto(request, anexo_id):
    """
    Remove um anexo de gasto.
    Permissões: admin (staff) ou dono do gasto (gasto.usuario == request.user).
    Apenas via POST.
    """
    an = get_object_or_404(GastoAnexo, id=anexo_id)

    if not (request.user.is_staff or an.gasto.usuario_id == request.user.id):
        return HttpResponseForbidden('Você não tem permissão para remover este anexo.')

    if request.method == 'POST':
        gasto = an.gasto
        an.delete()
        messages.success(request, 'Anexo removido com sucesso.')

        base = reverse('gastos')
        params = []
        if request.user.is_staff:
            params.append(f'usuario={gasto.usuario_id}')
        periodo = request.POST.get('periodo')
        if periodo:
            params.append(f'periodo={periodo}')
        url = base + ('?' + '&'.join(params) if params else '')
        return redirect(url)

    return redirect('gastos')
