import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver


class CartaoCredito(models.Model):
    BANDEIRAS = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('elo', 'Elo'),
        ('outros', 'Outros'),
    ]

    MESES = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
        (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
        (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
        (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ]

    def ano_opcoes():
        ano_atual = datetime.date.today().year
        return [(ano, ano) for ano in range(ano_atual, ano_atual + 15)]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cartoes')
    nome = models.CharField(max_length=100)
    numero = models.CharField(max_length=16)
    mes_vencimento = models.IntegerField(choices=MESES)
    ano_vencimento = models.IntegerField(choices=ano_opcoes())
    limite = models.DecimalField(max_digits=10, decimal_places=2)
    bandeira = models.CharField(max_length=20, choices=BANDEIRAS)

    def __str__(self):
        return f'{self.nome} - {self.bandeira.upper()}'

    def vencimento_formatado(self):
        return f'{self.mes_vencimento:02d}/{self.ano_vencimento}'

    def numero_mascarado(self):
        """Retorna o número no formato **** **** **** 1234"""
        if not self.numero:
            return ''
        return f"**** **** **** {self.numero[-4:]}"

    def bandeira_static_filename(self) -> str:
        mapping = {
            'visa': 'visa.png',
            'mastercard': 'mastercard.png',
            'amex': 'amex.png',
            'elo': 'elo.png',
            'outros': 'outros.png',
        }
        filename = mapping.get(self.bandeira, 'outros.svg')
        return f'cartoes_app/img/bandeiras/{filename}'


class Gasto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gastos')
    cartao = models.ForeignKey('CartaoCredito', on_delete=models.CASCADE, related_name='gastos')
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-id']

    def __str__(self):
        return f'{self.usuario.username} - {self.descricao} - R$ {self.valor}'


class GastoAnexo(models.Model):
    gasto = models.ForeignKey('Gasto', on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='gastos/%Y/%m/')
    nome_original = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        base = self.nome_original or (self.arquivo.name.split('/')[-1] if self.arquivo else 'arquivo')
        return f'Anexo de {self.gasto_id} - {base}'


@receiver(post_delete, sender=GastoAnexo)
def delete_file_on_anexo_delete(sender, instance, **kwargs):
    # Apaga o arquivo do storage quando o registro de anexo é deletado
    if instance.arquivo:
        instance.arquivo.delete(save=False)
