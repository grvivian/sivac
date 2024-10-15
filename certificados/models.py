from django.contrib.auth.backends import UserModel
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from .validators import validate_file_extension
import datetime
from django.utils.timezone import get_current_timezone 

class Certificado(models.Model):
    ST_APROVADO = 1
    ST_PENDENTE = 2
    ST_REPROVADO = 3
    ST_ERRO = 4
    SITUACAO_CHOICES = [
       (ST_APROVADO, 'Aprovado'),
       (ST_PENDENTE, 'Em análise'),
       (ST_REPROVADO, 'Recusado'),
       (ST_ERRO, 'Erro')
    ]
    titulo = models.CharField(max_length=150,verbose_name = 'Título', help_text="Informe o título completo da atividade conforme o certificado")
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    horas = models.IntegerField(verbose_name="Carga Horária")
    observacao = models.CharField(max_length=200, blank=True)
    situacao = models.SmallIntegerField(default = ST_PENDENTE, choices = SITUACAO_CHOICES)
    data_emissao = models.DateTimeField(verbose_name="Data da atividade", help_text="Se a atividade aconteceu em múltiplos dias informe apenas a data inicial")
    data_envio = models.DateTimeField(default=timezone.now)
    imagem = models.FileField(
        upload_to = 'certificados/',
        verbose_name = 'Certificado',
        validators=[validate_file_extension], help_text="Certifique-se de enviar o certificado alinhado, com boa resolução e no máximo 10MB (Preferencialmente em PDF)"
    )
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo + " (" + str(self.id) + ")"

    def tamanho_titulo(self):
        t = len(self.titulo)

        if t <= 120:
            return self.titulo[0:120]
        else:
            return self.titulo[0:117] + "..."
    
    def tamanho_autor(self):
        a = len(self.usuario.first_name + " " + self.usuario.last_name)

        if a <= 100:
            return (self.usuario.first_name + " " + self.usuario.last_name)[0:100]
        else:
            return (self.usuario.first_name + " " + self.usuario.last_name)[0:97] + "..."
        
    def pdf(self):
        return self.imagem.name.endswith('.pdf')
    
class Categoria(models.Model):
    nome = models.CharField(max_length=170)
    limite_horas = models.IntegerField()
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)
    
    def __str__(self):
        if self.limite_horas >= 999:
            return self.nome
        else:
            return self.nome + " (Até " + str(self.limite_horas) + "h)"

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    quantidade_horas = models.IntegerField()
    semestres = models.IntegerField()

    def anos(self):
        return int(self.semestres/2)

    def __str__(self):
        return self.nome + " (" + str(self.quantidade_horas) + "h de ACC)"


class Perfil(models.Model):
    TURMA_CHOICES = [(r, r) for r in range(2019, (datetime.datetime.now().year+1))]

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    matricula = models.IntegerField()
    turma = models.IntegerField(choices=TURMA_CHOICES)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)
    redefinir_senha = models.BooleanField(default=True) 

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def horas_concluidas(self):
        total = 0 
        horas_por_categoria = self.horas_concluidas_categorias() 

        for c in horas_por_categoria:
            total+= c["horas"]
            
        return total    

    def horas_pendentes(self):
        total = Certificado.objects.filter(usuario=self.user, situacao=Certificado.ST_PENDENTE).aggregate(Sum('horas'))['horas__sum'] or 0
        return total 

    def num_certificados_pendentes(self):
        total = Certificado.objects.filter(usuario=self.user, situacao=Certificado.ST_PENDENTE).count()
        return total 

    
    def horas_concluidas_categorias(self):
        horas_por_categoria = []

        categorias = Categoria.objects.filter(curso=self.curso)
        for c in categorias:
            #Todas as atividades aprovadas do usuário na categoria c
            atividades = Certificado.objects.filter(usuario=self.user, categoria=c, situacao=Certificado.ST_APROVADO)

            #Calcula o total de ch realizada na categoria
            total_categoria = atividades.aggregate(Sum('horas'))['horas__sum'] or 0

            #Calcula o total de ch remota durante o período de atividades remotas no IFFAr (17/03/2020 a 31/01/2022) 
            total_remoto = 0
            dt_inicio = datetime.datetime(2020,3,17,tzinfo=get_current_timezone())
            dt_fim = datetime.datetime(2022,1,31,tzinfo=get_current_timezone())
            total_remoto = atividades.filter(data_emissao__range = (dt_inicio, dt_fim)).aggregate(Sum('horas'))['horas__sum'] or 0
            #Calcula o total de ch presencial 
            total_presencial = total_categoria - total_remoto

            #Adiciona no total apenas a quota remota e presencial que não ultrapasse, individualmente, o limite da categoria
            total = min(total_presencial, c.limite_horas) + min(total_remoto, c.limite_horas)
            horas_por_categoria.append({'categoria': c.nome, 'horas': total, 'limite_horas': c.limite_horas})

        return horas_por_categoria

    def horas_faltando(self):
        return max(self.curso.quantidade_horas-self.horas_concluidas(),0)

    def ano_conclusao_estimado(self):
        ano_atual = datetime.datetime.now().year
        ano_estimado = self.turma + self.curso.anos()-1
        if ano_estimado < ano_atual:
            ano_estimado = ano_atual
        return ano_estimado

    
    def horas_faltando_por_ano(self):
        ano_atual = datetime.datetime.now().year
        anos_faltando = self.ano_conclusao_estimado()-ano_atual+1 #considera o ano atual como faltante
        return int(self.horas_faltando()/anos_faltando+0.5)

    def situacao(self):
        h = self.horas_faltando_por_ano()
        media = int(self.curso.quantidade_horas/self.curso.anos())
        if h == 0:
            return "integralizado"
        elif h <= media:
            return "regular"
        elif h > media*2:
            return "muito atrasado"
        else:
            return "atrasado"

    def percentual_integralizado(self):
        return int((min(self.horas_concluidas(),self.curso.quantidade_horas)/self.curso.quantidade_horas)*100)




