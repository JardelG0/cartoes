# cartoes_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CartaoCredito, Gasto

class CartaoCreditoForm(forms.ModelForm):
    """Form padrão (sem o campo usuário). Útil para edições quando não se troca o dono."""
    class Meta:
        model = CartaoCredito
        fields = ['nome', 'numero', 'mes_vencimento', 'ano_vencimento', 'limite', 'bandeira']

class CartaoCreditoAdminForm(forms.ModelForm):
    """Form para ADMIN: inclui o campo 'usuario' para vincular o cartão a um usuário comum."""
    usuario = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label='Usuário',
        help_text='Selecione o dono deste cartão',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CartaoCredito
        fields = ['usuario', 'nome', 'numero', 'mes_vencimento', 'ano_vencimento', 'limite', 'bandeira']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apenas usuários comuns (não staff) como opções
        self.fields['usuario'].queryset = User.objects.filter(is_staff=False).order_by('username')

class RegistrarUsuarioComumForm(UserCreationForm):
    """Cadastro de usuário comum (is_staff=False). Regras de senha seguem settings.AUTH_PASSWORD_VALIDATORS."""
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user

# ✅ Widget para múltiplos arquivos
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class GastoForm(forms.ModelForm):
    cartao = forms.ModelChoiceField(
        queryset=CartaoCredito.objects.none(),
        label='Cartão',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data'
    )
    # ✅ Campo de anexos (múltiplos)
    anexos = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        label='Comprovantes (PDF/Imagens)'
    )

    class Meta:
        model = Gasto
        fields = ['cartao', 'descricao', 'valor', 'data']  # "anexos" é campo extra (não-model)
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, user_alvo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_alvo = user_alvo
        if user_alvo is not None:
            self.fields['cartao'].queryset = CartaoCredito.objects.filter(usuario=user_alvo).order_by('nome')
        else:
            self.fields['cartao'].queryset = CartaoCredito.objects.none()

    def clean_cartao(self):
        cartao = self.cleaned_data.get('cartao')
        if cartao and self.user_alvo and cartao.usuario_id != self.user_alvo.id:
            raise forms.ValidationError('Este cartão não pertence ao usuário selecionado.')
        return cartao

    def clean_anexos(self):
        # ✅ pega lista de arquivos mesmo sem 'multiple' no HTML (widget já permite)
        files = self.files.getlist('anexos') if hasattr(self.files, 'getlist') else []
        if not files:
            return files

        allowed = {
            'application/pdf',
            'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'
        }
        max_size = 10 * 1024 * 1024  # 10MB

        for f in files:
            if f.content_type not in allowed:
                raise forms.ValidationError('Tipos permitidos: PDF, PNG, JPG, GIF, WEBP.')
            if f.size > max_size:
                raise forms.ValidationError('Cada arquivo deve ter no máximo 10 MB.')
        return files
