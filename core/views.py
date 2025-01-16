# /core/views.py
# Este arquivo define as views responsáveis pelas páginas e funcionalidades do sistema.
# As views conectam os modelos às páginas HTML, permitindo a interação do usuário com o sistema.
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from .models import EscolhaProfessor, Professor, Escola, Atribuicao
# from core.models import Professor, Escola, Atribuicao #Acrescentei atribuição e comentei a linha de cima
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.shortcuts import redirect
from django.contrib.auth import logout  # Função para encerrar a sessão do usuário
from django.contrib import messages


# View para a página do professor
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EscolhaProfessor, Professor, Escola, Atribuicao

# View para a página exclusiva do professor para expressar desejo de atribuição.
@login_required
def pagina_professor(request):
    try:
        professor = Professor.objects.get(cpf=request.user.username)
    except Professor.DoesNotExist:
        professor = None

    disciplinas_professor = []
    if professor:
        if professor.disciplina_peb:
            disciplinas_professor.extend(professor.disciplina_peb.replace(",", " ").split())
        if professor.disciplina_paeb:
            disciplinas_professor.extend(professor.disciplina_paeb.replace(",", " ").split())

    escolas = Escola.objects.all()
    if professor and professor.id_sede:
        escolas = [professor.id_sede] + list(escolas.exclude(id=professor.id_sede.id))
    for escola in escolas:
        escola.turmas_matutino_lista = (
            [t.strip() for t in escola.turmas_matutino.split(",")] if escola.turmas_matutino else []
        )
        escola.turmas_vespertino_lista = (
            [t.strip() for t in escola.turmas_vespertino.split(",")] if escola.turmas_vespertino else []
        )

    escolhas = EscolhaProfessor.objects.filter(professor=professor)
    escolhas_detalhadas = []
    for escolha in escolhas:
        turmas_lista = [t.strip() for t in escolha.turmas.split(",")] if escolha.turmas else []

        status_turmas = []
        for turma in turmas_lista:
            atribuicao = Atribuicao.objects.filter(
                escola=escolha.escola,
                turma=turma
            ).first()

            if atribuicao:
                status_turmas.append({
                    "turma": turma,
                    "atribuida": True,
                    "disciplina": atribuicao.disciplina,
                    "professor": atribuicao.professor.nome
                })
            else:
                status_turmas.append({
                    "turma": turma,
                    "atribuida": False
                })

        escolhas_detalhadas.append({
            "id": escolha.id,
            "escola": escolha.escola,
            "turmas_status": status_turmas,
            "turmas_lista": turmas_lista,
            "prioridade": escolha.prioridade,
            "periodo": escolha.periodo,
        })

    concorrencia_lista = []
    for escolha in escolhas_detalhadas:
        for turma in escolha["turmas_lista"]:
            concorrentes = EscolhaProfessor.objects.filter(
                escola=escolha["escola"],
                turmas__icontains=turma
            ).exclude(professor=professor)

            concorrentes_disciplinas = {}
            for disciplina in disciplinas_professor:
                concorrentes_disciplinas[disciplina] = sum(
                    1 for concorrente in concorrentes
                    if (
                        (concorrente.professor.disciplina_peb == disciplina) or
                        (concorrente.professor.disciplina_paeb == disciplina)
                    )
                )

 #           atribuicao = Atribuicao.objects.filter(
 #               escola=escolha["escola"],
 #               turma=turma,
 #           ).first()

            if atribuicao:
                concorrencia_formatada = f"<span style='color: red;'>{atribuicao.disciplina} ({atribuicao.professor.nome})</span>"
            else:
                concorrencia_formatada = "; ".join(
                    f"{count} ({disciplina})" for disciplina, count in concorrentes_disciplinas.items()
                )

            concorrencia_lista.append({
                "escola": escolha["escola"].nome,
                "turma": turma,
                "concorrencia": concorrencia_formatada,
            })

    atribuidas = Atribuicao.objects.select_related('escola').filter(
        disciplina__in=disciplinas_professor
    )
    atribuidas_lista = [
        {"escola": atribuicao.escola.nome, "turma": atribuicao.turma, "disciplina": atribuicao.disciplina}
        for atribuicao in atribuidas
    ]

    return render(request, 'pagina_professor.html', {
        'professor': professor,
        'escolas': escolas,
        'prioridades': [1, 2, 3, 4, 5],
        'escolhas': escolhas_detalhadas,
        'concorrencia_lista': concorrencia_lista,
        'atribuidas_lista': atribuidas_lista,
    })











@login_required(login_url='/login/')
def index(request):
    """
    Renderiza a página inicial do sistema, com links para as páginas do professor, gestor e coletiva.
    """
    
    return render(request, 'index.html')







# View para a página exclusiva do gestor realizar atribuições.
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden

@login_required
def pagina_gestor(request):
    if not (request.user.groups.filter(name='Gestor').exists() or request.user.username == 'seu_usuario_dono'):
        return HttpResponseForbidden("Acesso negado. Você não tem permissão para acessar esta página.")

    professores = Professor.objects.all()
    escolas = Escola.objects.all()
    professor_selecionado = None  # Inicializa a variável como None
    disciplina_selecionada = None
    escolhas_detalhadas = []
    aulas_atribuidas = []
    mensagem_erro = None

    # Calcular os rankings
    professores_peb = Professor.objects.filter(cargo__in=['PEB', 'AMBOS']).order_by('-pontuacao_peb', 'cpf')
    professores_paeb = Professor.objects.filter(cargo__in=['PAEB', 'AMBOS']).order_by('-pontuacao_paeb', 'cpf')
    ranking_especifico_peb = {professor.id: idx + 1 for idx, professor in enumerate(professores_peb)}
    ranking_especifico_paeb = {professor.id: idx + 1 for idx, professor in enumerate(professores_paeb)}
    professores_geral = sorted(
        list(professores_peb) + list(professores_paeb),
        key=lambda prof: (-prof.pontuacao_peb if prof.cargo in ['PEB', 'AMBOS'] else -prof.pontuacao_paeb, prof.cpf)
    )
    ranking_geral = {professor.id: idx + 1 for idx, professor in enumerate(professores_geral)}

    # Buscar professor por CPF ou classificação
    cpf = request.GET.get('cpf')
    classificacao_especifica = request.GET.get('classificacao_especifica')
    tipo_classificacao = request.GET.get('tipo_classificacao')
    classificacao_geral = request.GET.get('classificacao_geral')

    if cpf:
        try:
            professor_selecionado = Professor.objects.get(cpf=cpf)
            disciplina_selecionada = professor_selecionado.disciplina_peb
        except Professor.DoesNotExist:
            mensagem_erro = f"Nenhum professor encontrado com o CPF {cpf}."
    elif classificacao_especifica:
        classificacao_especifica = int(classificacao_especifica)
        try:
            professor_id = None
            if tipo_classificacao == 'PEB':
                professor_id = next((id_ for id_, rank in ranking_especifico_peb.items() if rank == classificacao_especifica), None)
            elif tipo_classificacao == 'PAEB':
                professor_id = next((id_ for id_, rank in ranking_especifico_paeb.items() if rank == classificacao_especifica), None)
            professor_selecionado = Professor.objects.get(id=professor_id)
            disciplina_selecionada = professor_selecionado.disciplina_peb
        except (StopIteration, Professor.DoesNotExist):
            mensagem_erro = f"Nenhum professor encontrado para a classificação {classificacao_especifica} ({tipo_classificacao})."
    elif classificacao_geral:
        classificacao_geral = int(classificacao_geral)
        try:
            professor_id = next((id_ for id_, rank in ranking_geral.items() if rank == classificacao_geral), None)
            professor_selecionado = Professor.objects.get(id=professor_id)
            disciplina_selecionada = professor_selecionado.disciplina_peb
        except (StopIteration, Professor.DoesNotExist):
            mensagem_erro = f"Nenhum professor encontrado para a classificação geral {classificacao_geral}."

    # Verifica se o menu de disciplina foi alterado
    disciplina_alterada = request.GET.get('disciplina')
    if disciplina_alterada:
        disciplina_selecionada = disciplina_alterada

    # Carregar as escolhas do professor
    if professor_selecionado:
        escolhas_professor = EscolhaProfessor.objects.filter(professor=professor_selecionado)
        for escolha in escolhas_professor:
            turmas_lista = escolha.turmas.split(",") if escolha.turmas else []
            status_turmas = []

            for turma in turmas_lista:
                atribuicoes_turma = Atribuicao.objects.filter(escola=escolha.escola, turma=turma.strip())
                            
                
                
                disciplinas_atribuidas = [
                    atribuicao.disciplina.split(" (Fora de Campo)")[0].split(" (Substituição)")[0].strip()
                    for atribuicao in atribuicoes_turma
]
                
                   

                status_disciplinas = [
                    {
                        "disciplina": disciplina_selecionada,
                        "atribuida": disciplina_selecionada in disciplinas_atribuidas
                    }
                ]

                status_turmas.append({
                    "turma": turma.strip(),
                    "disciplinas_status": status_disciplinas
                })

            escolhas_detalhadas.append({
                "escola": escolha.escola,
                "turmas_status": status_turmas,
                "periodo": escolha.periodo,
                "prioridade": escolha.prioridade,
            })

        aulas_atribuidas = Atribuicao.objects.filter(professor=professor_selecionado).select_related('escola')

    return render(request, 'pagina_gestor.html', {
        'professores': professores,
        'escolas': escolas,
        'professor_selecionado': professor_selecionado,
        'disciplina_selecionada': disciplina_selecionada,
        'escolhas_detalhadas': escolhas_detalhadas,
        'aulas_atribuidas': aulas_atribuidas,
        'ranking_peb': ranking_especifico_peb,
        'ranking_paeb': ranking_especifico_paeb,
        'ranking_geral': ranking_geral,
        'mensagem_erro': mensagem_erro,
    })








from django.shortcuts import render

def cpf_invalido(request):
    """
    Renderiza uma página para informar que o CPF é inválido.
    """
    mensagem = request.GET.get('mensagem', 'CPF inválido.')
    return render(request, 'cpf_invalido.html', {'mensagem': mensagem})
    
    
    
    

@login_required
def salvar_atribuicao(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            professor_id = data.get('professor_id')
            turmas = data.get('turmas', [])
            disciplina = data.get('disciplina')  # Lê a disciplina enviada pelo frontend
            fora_de_campo = data.get('fora_de_campo', False)
            em_substituicao = data.get('em_substituicao', False)
            licenca = data.get('licenca', False)
            
            
            

            if not professor_id or (not turmas and not licenca) or (not disciplina and not licenca):
                print("Erro: Dados incompletos")  # Log para depuração
                return JsonResponse({'erro': 'Dados incompletos. Verifique os campos preenchidos.'}, status=400)

            professor = Professor.objects.get(id=professor_id)
            gestor = request.user.username  # Nome do gestor logado

            # Verificar se é um caso de licença
            memoria_licenca_key = f"licenca_professor_{professor_id}"
            memoria_licenca = request.session.get(memoria_licenca_key, [])

            if licenca:
                if memoria_licenca:
                    # Desativa licença e restaura atribuições
                    print("Desativando licença e restaurando atribuições...")
                    for atrib in memoria_licenca:
                        escola = Escola.objects.get(id=atrib['escolaId'])
                        Atribuicao.objects.update_or_create(
                            professor=professor,
                            escola=escola,
                            turma=atrib['turma'],
                            defaults={
                                'disciplina': atrib['disciplina'],
                                'gestor_responsavel': gestor,
                            }
                        )
                    del request.session[memoria_licenca_key]
                    return JsonResponse({'mensagem': 'Licença desativada. Atribuições restauradas.'})
                else:
                    # Ativa licença e remove todas as atribuições
                    print("Ativando licença e removendo atribuições...")
                    atribuicoes = Atribuicao.objects.filter(professor=professor)
                    memoria_licenca = [
                        {
                            'escolaId': atrib.escola.id,
                            'turma': atrib.turma,
                            'disciplina': atrib.disciplina,
                        }
                        for atrib in atribuicoes
                    ]
                    request.session[memoria_licenca_key] = memoria_licenca
                    atribuicoes.delete()
                    return JsonResponse({'mensagem': 'Licença ativada. Todas as atribuições foram removidas.'})




 	# Fluxo padrão para atribuições
            for turma_data in turmas:
                escola = Escola.objects.get(id=turma_data['escolaId'])

                # Ajusta a disciplina com os textos adicionais
                disciplina_final = disciplina
                if fora_de_campo:
                    disciplina_final += " (Fora de Campo)"
                if em_substituicao:
                    disciplina_final += " (Substituição)"

                # Criação ou atualização de atribuição
                Atribuicao.objects.update_or_create(
                    professor=professor,
                    escola=escola,
                    turma=turma_data['turma'],
                    defaults={
                        'disciplina': disciplina_final,
                        'gestor_responsavel': gestor
                    }
                )

            return JsonResponse({'mensagem': 'Atribuição salva com sucesso!'})
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
    return JsonResponse({'erro': 'Método não permitido.'}, status=405)









    






@login_required
def pagina_coletiva(request):
    escolas = Escola.objects.all().prefetch_related('atribuicao_set')
    dados_coletivos = []

    for escola in escolas:
        turmas_matutino = escola.turmas_matutino.split(",") if escola.turmas_matutino else []
        turmas_vespertino = escola.turmas_vespertino.split(",") if escola.turmas_vespertino else []
        periodos = [
            {"nome": "Matutino", "turmas": turmas_matutino},
            {"nome": "Vespertino", "turmas": turmas_vespertino},
        ]

        dados_escola = {"nome": escola.nome, "endereco": escola.endereco, "periodos": []}

        disciplinas = ["matematica", "geografia", "ciencias", "historia", "portugues", "arte", "ingles", "educacao_fisica"]

        for periodo in periodos:
            dados_periodo = {"nome": periodo["nome"], "turmas": []}

            for turma in periodo["turmas"]:
                dados_turma = {"nome": turma, "disciplinas": []}

                for disciplina in disciplinas:
                    atribuicao = Atribuicao.objects.filter(escola=escola, turma=turma.strip(), disciplina__icontains=disciplina).first()
                    if atribuicao:
                        fora_de_campo_texto = "(Fora de Campo)" if "fora de campo" in atribuicao.disciplina.lower() else ""
                        substituicao_texto = "(Substituição)" if "substituição" in atribuicao.disciplina.lower() else ""
                        dados_turma["disciplinas"].append({
                            "nome": f"{disciplina.replace('_', ' ').title()} {fora_de_campo_texto}".strip(),
                            "professor": atribuicao.professor.nome,
                            "pontuacao": atribuicao.professor.pontuacao_peb if atribuicao.professor.cargo == "PEB" else atribuicao.professor.pontuacao_paeb,
                            "cargo": atribuicao.professor.cargo,
                            "gestor": atribuicao.gestor_responsavel if hasattr(atribuicao, 'gestor_responsavel') else "N/A"
                        })
                    else:
                        dados_turma["disciplinas"].append({
                            "nome": disciplina.replace("_", " ").title(),
                            "professor": None
                        })

                dados_periodo["turmas"].append(dados_turma)

            dados_escola["periodos"].append(dados_periodo)

        dados_coletivos.append(dados_escola)

    return render(request, 'pagina_coletiva.html', {"dados_coletivos": dados_coletivos})


















def redirecionar_para_index(request):
    return redirect('//')  # Redireciona para a página index.html (página inicial)

# View para logout
def custom_logout(request):
    logout(request)  # Encerra a sessão do usuário
    return redirect('/login/')  # Redireciona para a página de login



@login_required
def atualizar_professor(request):
    if request.method == 'POST':
        try:
            professor = Professor.objects.get(cpf=request.user.username)
        except Professor.DoesNotExist:
            return JsonResponse({'error': 'Professor não encontrado'}, status=400)

        # Atualizar os campos básicos do professor
        professor.nome = request.POST.get('nome', professor.nome)
        professor.celular = request.POST.get('celular', professor.celular)
        professor.cargo = request.POST.get('cargo', professor.cargo)

        # Atualizar disciplinas dependendo do cargo
        disciplina_peb = request.POST.get('disciplina_peb', None)
        disciplina_paeb = request.POST.get('disciplina_paeb', None)

        if professor.cargo in ['PEB', 'AMBOS']:
            professor.disciplina_peb = disciplina_peb

        if professor.cargo in ['PAEB', 'AMBOS']:
            professor.disciplina_paeb = disciplina_paeb

        # Marcar o professor como retificado
        professor.retificado = True

        # Salvar no banco de dados
        professor.save()

        return render(request, 'professor_atualizado.html', {'mensagem': 'Dados atualizados com sucesso!'})

    return redirect('pagina_professor')

@login_required
def atribuir_professor(request):
    if request.method == "POST":
        try:
            professor = Professor.objects.get(cpf=request.user.username)
        except Professor.DoesNotExist:
            return JsonResponse({'error': 'Professor não encontrado'}, status=400)

        escolas_ids = request.POST.getlist("escolas")
        turmas_por_escola = {
            escola_id: {
                "matutino": request.POST.getlist(f"turmas-matutino-{escola_id}[]"),
               "vespertino": request.POST.getlist(f"turmas-vespertino-{escola_id}[]"),

                "prioridade": request.POST.get(f"prioridade-{escola_id}", None),
            }
            for escola_id in escolas_ids
        }

        if len(escolas_ids) > 5:
            return render(request, 'professor_atribuido.html', {'mensagem': 'Erro: Você pode selecionar no máximo 5 escolas.'})

        for escola_id, dados in turmas_por_escola.items():
            try:
                escola = Escola.objects.get(id=escola_id)
                turmas_selecionadas = dados["matutino"] + dados["vespertino"]

                # Verifica se há turmas selecionadas antes de salvar
                if turmas_selecionadas and dados["prioridade"]:
                    EscolhaProfessor.objects.update_or_create(
                        professor=professor,
                        escola=escola,
                        defaults={
                            "turmas": ",".join(turmas_selecionadas),
                            "prioridade": int(dados["prioridade"]),
                         #   "disciplina_peb": professor.disciplina_peb,
			  #  "disciplina_paeb": professor.disciplina_paeb,
			"disciplina_peb": professor.disciplina_peb,
                        "disciplina_paeb": professor.disciplina_paeb,
                            "periodo": "Matutino e Vespertino" if dados["matutino"] and dados["vespertino"] else
                                      "Matutino" if dados["matutino"] else "Vespertino",
                        }
                    )
            except Exception as e:
                return render(request, 'professor_atribuido.html', {'mensagem': f"Erro ao salvar escolhas: {str(e)}"})

        return render(request, 'professor_atribuido.html', {'mensagem': 'Escolhas salvas com sucesso!'})

    return redirect('pagina_professor')
    



@login_required
def remover_escolha(request):
    if request.method == "POST":
        escolha_id = request.POST.get("escolha_id")
        if not escolha_id:
            messages.error(request, 'ID da escolha não fornecido.')
            return redirect('pagina_professor')
        try:
            escolha = EscolhaProfessor.objects.get(id=escolha_id)
            escolha.delete()
            messages.success(request, 'Escolha removida com sucesso!')
            return redirect('pagina_professor')
        except EscolhaProfessor.DoesNotExist:
            messages.error(request, 'Escolha não encontrada.')
            return redirect('pagina_professor')
    messages.error(request, 'Método não permitido.')
    return redirect('pagina_professor')






	
      
from django.db.models import Q
from .models import Professor  # Certifique-se de importar seu modelo corretamente

def calcular_classificacao():
    # Obter todos os professores PEB (incluindo aqueles com cargo 'AMBOS')
    professores_peb = list(
        Professor.objects.filter(Q(cargo='PEB') | Q(cargo='AMBOS')).order_by('-pontuacao_peb', 'cpf')
    )

    # Obter todos os professores PAEB (incluindo aqueles com cargo 'AMBOS')
    professores_paeb = list(
        Professor.objects.filter(Q(cargo='PAEB') | Q(cargo='AMBOS')).order_by('-pontuacao_paeb', 'cpf')
    )

    # Obter todos os professores (independentemente de cargo ou pontuação)
    professores_todos = list(Professor.objects.all())

    # Criar rankings específicos para PEB e PAEB
    ranking_peb = {professor.id: idx + 1 for idx, professor in enumerate(professores_peb)}
    ranking_paeb = {professor.id: idx + 1 for idx, professor in enumerate(professores_paeb)}

    # Criar entidades virtuais para classificação geral
    entidades_gerais = []

    # Adicionar professores PEB à classificação geral
    for professor in professores_peb:
        entidades_gerais.append({
            'professor': professor,
            'tipo': 'PEB',
            'pontuacao': professor.pontuacao_peb if professor.pontuacao_peb is not None else -float('inf'),
        })

    # Adicionar professores PAEB à classificação geral, mesmo que já tenham sido adicionados como PEB
    for professor in professores_paeb:
        entidades_gerais.append({
            'professor': professor,
            'tipo': 'PAEB',
            'pontuacao': professor.pontuacao_paeb if professor.pontuacao_paeb is not None else -float('inf'),
        })

    # Adicionar professores que não estão em PEB nem em PAEB
    for professor in professores_todos:
        if professor not in [entidade['professor'] for entidade in entidades_gerais]:
            entidades_gerais.append({
                'professor': professor,
                'tipo': None,
                'pontuacao': -float('inf'),
            })

    # Ordenar as entidades virtuais para gerar a classificação geral
    entidades_gerais = sorted(
        entidades_gerais,
        key=lambda entidade: (-entidade['pontuacao'], entidade['professor'].cpf)
    )

    # Corrigir duplicações na lista geral (mesmo professor em PEB e PAEB)
    vistos = set()
    entidades_gerais_unicas = []
    for entidade in entidades_gerais:
        if entidade['professor'].id not in vistos:
            entidades_gerais_unicas.append(entidade)
            vistos.add(entidade['professor'].id)

    # Extrair os professores ordenados pela classificação geral
    professores_geral = [entidade['professor'] for entidade in entidades_gerais_unicas]

    # Criar o ranking geral
    ranking_geral = {professor.id: idx + 1 for idx, professor in enumerate(professores_geral)}

    return ranking_peb, ranking_paeb, ranking_geral






    
    
    

@login_required
def deletar_atribuicao(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Recebe os dados da requisição
            atribuicao_id = data.get('atribuicao_id')

            if not atribuicao_id:
                return JsonResponse({'erro': 'ID da atribuição não fornecido.'}, status=400)

            # Busca e remove a atribuição correspondente
            atribuicao = Atribuicao.objects.get(id=atribuicao_id)
            atribuicao.delete()

            return JsonResponse({'mensagem': 'Atribuição excluída com sucesso!'})
        except Atribuicao.DoesNotExist:
            return JsonResponse({'erro': 'Atribuição não encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
    return JsonResponse({'erro': 'Método não permitido.'}, status=405)



# Fim do arquivo views.py

