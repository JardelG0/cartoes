# cartoes_app/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User 
from .models import CartaoCredito, Gasto, GastoAnexo
from .forms import CartaoCreditoForm, CartaoCreditoAdminForm, RegistrarUsuarioComumForm, GastoForm
# from .forms import CartaoCreditoAdminForm
from django.db.models import Sum, Q
from datetime import date, timedelta
from calendar import monthrange
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import logout
from django.http import HttpResponseForbidden


def login_view(request):
    return render(request, 'cartoes_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def registrar_view(request):
    # Se o registro público NÃO deve existir, deixe apenas um placeholder visual
    return render(request, 'cartoes_app/registrar.html')

@login_required
def dashboard_view(request):
    # Admin vê TODOS os cartões; usuário comum vê apenas os seus
    if request.user.is_staff:
        cartoes = CartaoCredito.objects.select_related('usuario').all().order_by('usuario__username', 'nome')
    else:
        cartoes = CartaoCredito.objects.filter(usuario=request.user).order_by('nome')

    form = None
    if request.user.is_staff:
        # Admin pode criar e escolher o usuário dono
        if request.method == 'POST':
            form = CartaoCreditoAdminForm(request.POST)
            if form.is_valid():
                form.save()  # já salva com o 'usuario' selecionado no form
                messages.success(request, "Cartão criado e vinculado ao usuário selecionado.")
                return redirect('dashboard')
        else:
            form = CartaoCreditoAdminForm()
    # >>> NÚMEROS DO PAINEL ADMIN (visível só para staff no template)
    total_usuarios = User.objects.filter(is_staff=False).count()   # apenas usuários comuns
    total_cartoes = CartaoCredito.objects.count()                  # todos os cartões
    limite_total = CartaoCredito.objects.aggregate(
        total=Sum('limite')
    )['total'] or Decimal('0')

     # ------- Filtro de período para resumos (somente admin) -------
    periodo = request.GET.get('periodo', 'mes_atual')  # mes_atual | ult_30 | todos

    hoje = date.today()
    if periodo == 'mes_atual':
        start = date(hoje.year, hoje.month, 1)
        end = date(hoje.year, hoje.month, monthrange(hoje.year, hoje.month)[1])
    elif periodo == 'ult_30':
        start = hoje - timedelta(days=30)
        end = hoje
    else:  # 'todos'
        start = None
        end = None

    # helper para filtro de data
    date_filter = {}
    if start and end:
        date_filter = {'gastos__data__range': (start, end)}

    # ------- Números do painel admin (que já usamos) -------
    total_usuarios = User.objects.filter(is_staff=False).count()
    total_cartoes = CartaoCredito.objects.count()
    limite_total = CartaoCredito.objects.aggregate(total=Sum('limite'))['total'] or Decimal('0')

    # ------- Resumo por USUÁRIO -------
    usuarios_resumo = User.objects.filter(is_staff=False).annotate(
        gasto_total=Sum('gastos__valor', filter=Q(**date_filter))
    ).order_by('username')

    # ------- Resumo por CARTÃO + alerta de limite -------
    cartoes_resumo = CartaoCredito.objects.select_related('usuario').annotate(
        gasto_total=Sum('gastos__valor', filter=Q(**date_filter))
    ).order_by('usuario__username', 'nome')

    # cartões em ALERTA: gasto_total > limite
    cartoes_alerta = []
    for c in cartoes_resumo:
        gt = c.gasto_total or Decimal('0')
        if gt > (c.limite or Decimal('0')):
            cartoes_alerta.append(c.id)

    cartoes_alerta = []
    for c in cartoes_resumo:
        gasto = c.gasto_total or Decimal('0')
        limite = c.limite or Decimal('0')
        if gasto > limite:
            cartoes_alerta.append(c.id)
        # ✅ saldo restante para o período selecionado
        c.saldo_restante = limite - gasto

    context = {
        'cartoes': cartoes,
        'form': form,
        'total_usuarios': total_usuarios,
        'total_cartoes': total_cartoes,
        'limite_total': limite_total,
        # resumos
        'periodo': periodo,
        'usuarios_resumo': usuarios_resumo,
        'cartoes_resumo': cartoes_resumo,
        'cartoes_alerta': set(cartoes_alerta),
        # datas (opcional mostrar no template)
        'periodo_inicio': start,
        'periodo_fim': end,
    }
    return render(request, 'cartoes_app/dashboard.html', context)


# ---- CRUD de cartões restrito a admins ----
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


# ---- Registrar usuário comum (apenas admin) ----
@staff_member_required
def registrar_usuario_view(request):
    if request.method == 'POST':
        form = RegistrarUsuarioComumForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário comum registrado!")
            return redirect('registrar_usuario')
    else:
        form = RegistrarUsuarioComumForm()
    # Pode listar usuários existentes também (visual)
    usuarios = User.objects.filter(is_staff=False).order_by('username')
    return render(request, 'cartoes_app/registrar_usuario.html', {
        'form': form,
        'usuarios': usuarios
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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from datetime import date, timedelta
from calendar import monthrange
from decimal import Decimal
from .models import CartaoCredito, Gasto, GastoAnexo   # ✅ certifique-se deste import
from .forms import GastoForm

@login_required
def gastos_view(request):
    # Define usuário alvo
    if request.user.is_staff:
        usuarios = User.objects.filter(is_staff=False).order_by('username')
        usuario_id = request.GET.get('usuario')
        user_alvo = None
        if usuario_id:
            try:
                user_alvo = usuarios.get(id=int(usuario_id))
            except (ValueError, User.DoesNotExist):
                user_alvo = None
    else:
        usuarios = None
        user_alvo = request.user

    # Período
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

    # Dados base
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

    # POST: registrar gasto (com anexos)
    if request.method == 'POST':
        if not user_alvo:
            messages.error(request, 'Selecione um usuário para registrar o gasto.')
            return redirect('gastos')

        form = GastoForm(request.POST, request.FILES, user_alvo=user_alvo)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.usuario = user_alvo

            if gasto.cartao.usuario_id != user_alvo.id:
                form.add_error('cartao', 'Este cartão não pertence ao usuário selecionado.')
            else:
                gasto.save()
                # ✅ ALTERAÇÃO: pegue TODOS os arquivos enviados (multi input ou vários inputs)
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

@staff_member_required
def criar_cartao_view(request):
    """
    Página dedicada para o admin criar um novo cartão
    (com seleção de usuário dono).
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

def acesso_view(request):
   # ✅ Se já estiver logado, redireciona automaticamente
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        else:
            return redirect('gastos')

    # Só mostra a página de acesso se não estiver autenticado
    usuarios_comuns = User.objects.filter(is_staff=False).order_by('username')
    return render(request, 'cartoes_app/acesso.html', {
        'usuarios_comuns': usuarios_comuns,
    })

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

        # Redireciona de volta à tela de gastos preservando (se possível) o usuário/periodo
        base = reverse('gastos')
        params = []
        # Para admin, mantemos o mesmo usuário alvo
        if request.user.is_staff:
            params.append(f'usuario={gasto.usuario_id}')
        # Preservar período vindo como hidden no form
        periodo = request.POST.get('periodo')
        if periodo:
            params.append(f'periodo={periodo}')
        url = base + ('?' + '&'.join(params) if params else '')
        return redirect(url)

    # Se não for POST, apenas retorna para a listagem
    return redirect('gastos')