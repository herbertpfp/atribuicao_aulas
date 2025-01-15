# /core/models.py
# Este arquivo define os modelos do banco de dados para o sistema Django.

from django.db import models


# Modelo para representar os professores.
class Professor(models.Model):
    CARGO_CHOICES = [
        ('PEB', 'Professor de Educação Básica'),
        ('PAEB', 'Professor Adjunto de Educação Básica'),
        ('AMBOS', 'Ambos os Cargos'),
    ]

    nome = models.CharField(max_length=255, help_text="Nome completo do professor.")  # Nome completo do professor.
    cpf = models.CharField(max_length=11, unique=True, help_text="CPF do professor (usado como login).")  # CPF único.
    celular = models.CharField(max_length=15, help_text="Número de telefone para contato.")  # Telefone para contato.
    cargo = models.CharField(max_length=5, choices=CARGO_CHOICES, help_text="Cargo do professor: PEB, PAEB ou AMBOS.")  # Cargo do professor.
    id_sede = models.ForeignKey(
        'Escola', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="professores_sede", 
        help_text="Escola sede do professor, caso aplicável."
    )

    # Novos campos para disciplinas e pontuações separadas
    disciplina_peb = models.CharField(max_length=255, null=True, blank=True, help_text="Disciplina para o cargo PEB.")
    disciplina_paeb = models.CharField(max_length=255, null=True, blank=True, help_text="Disciplina para o cargo PAEB.")
    pontuacao_peb = models.IntegerField(null=True, blank=True, help_text="Pontuação do professor no cargo PEB.")
    pontuacao_paeb = models.IntegerField(null=True, blank=True, help_text="Pontuação do professor no cargo PAEB.")

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"

    def __str__(self):
        return self.nome  # Representação textual do professor.

        
        

# Modelo para representar as escolas.
class Escola(models.Model):
    id_escola = models.CharField(max_length=255, help_text="Identificação da escola.")  # ID da escola.
    nome = models.CharField(max_length=255, help_text="Nome da escola.")  # Nome da escola.
    endereco = models.CharField(max_length=255, help_text="Endereço da escola.")  # Endereço da escola.
    turmas_matutino = models.TextField()  # Lista de turmas matutino separadas por vírgula
    turmas_vespertino = models.TextField()  # Lista de turmas vespertino separadas por vírgula
    status_matutino = models.TextField()  # Lista de status matutino separadas por vírgula
    status_vespertino = models.TextField()  # Lista de status vespertino separadas por vírgula

    def __str__(self):
        return self.nome  # Representação textual da escola.

# Modelo para representar as atribuições de aulas.
class Atribuicao(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, help_text="Professor atribuído.")  # Professor vinculado à atribuição.
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, help_text="Escola onde a atribuição foi feita.")  # Escola vinculada à atribuição.
    turma = models.CharField(max_length=10, help_text="Turma atribuída (ex.: 6A, 7B).")  # Turma específica.
    disciplina = models.CharField(max_length=50, help_text="Disciplina atribuída (ex.: Matemática, Português).")  # Disciplina atribuída.
    gestor_responsavel = models.CharField(max_length=100, null=True, blank=True)  # Adiciona o campo
    fora_de_campo = models.BooleanField(default=False, help_text="Indica se a atribuição foi feita fora da especialidade do professor.")  # Se a atribuição foi fora da especialidade.
    
    class Meta:
        verbose_name = "Atribuição"
        verbose_name_plural = "Atribuições"
    
    def __str__(self):
        return f"{self.professor.nome} - {self.disciplina} ({self.turma})"  # Representação textual da atribuição.
        
# Modelo para representar as escolhas feitas pelos professores.
class EscolhaProfessor(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, help_text="Professor que fez a escolha.")  # Professor vinculado à escolha.
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, help_text="Escola escolhida.")  # Escola escolhida.
    turmas = models.CharField(max_length=255, help_text="Lista de turmas escolhidas separadas por vírgula.")  # Turmas escolhidas.
    prioridade = models.PositiveIntegerField(help_text="Prioridade atribuída à escola.")  # Prioridade para a escola (1 a 5).
    periodo = models.CharField(max_length=20, choices=[('Matutino', 'Matutino'), ('Vespertino', 'Vespertino')], help_text="Período de interesse (Matutino ou Vespertino).")  # Período da escolha.
    disciplina_peb = models.CharField(max_length=255, null=True, blank=True, help_text="Disciplina para o cargo PEB")  # Adicionado
    disciplina_paeb = models.CharField(max_length=255, null=True, blank=True, help_text="Disciplina para o cargo PAEB")  # Adicionado
    data_escolha = models.DateTimeField(auto_now_add=True, help_text="Data e hora em que a escolha foi feita.")  # Data de registro da escolha.

    class Meta:
        verbose_name = "Escolha do Professor"
        verbose_name_plural = "Escolhas dos Professores"
        unique_together = ('professor', 'escola', 'prioridade')  # Evita duplicação de prioridades para a mesma escola e professor.

    def __str__(self):
        return f"{self.professor.nome} - {self.escola.nome} (Prioridade {self.prioridade})"


# Fim do arquivo models.py

