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

            atribuicao = Atribuicao.objects.filter(
                escola=escolha["escola"],
                turma=turma
            ).first()

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







def calcular_classificacao():
    # Obter professores
    professores_peb = Professor.objects.filter(pontuacao_peb__gt=0).order_by('-pontuacao_peb', 'cpf')
    professores_paeb = Professor.objects.filter(pontuacao_paeb__gt=0).order_by('-pontuacao_paeb', 'cpf')
    professores_zero = Professor.objects.filter(pontuacao_peb=0, pontuacao_paeb=0).order_by('nome', 'cpf')

    # Criar lista para classificação geral
    ranking_geral = []

    # Adicionar professores PEB (pontuação > 0)
    for professor in professores_peb:
        ranking_geral.append({
            "id": professor.id,
            "nome": professor.nome,
            "cargo": "PEB",
            "pontuacao": professor.pontuacao_peb,
            "cpf": professor.cpf,
            "disciplina": professor.disciplina_peb,  # Disciplina associada ao cargo PEB
        })

    # Adicionar professores PAEB (pontuação > 0)
    for professor in professores_paeb:
        ranking_geral.append({
            "id": professor.id,
            "nome": professor.nome,
            "cargo": "PAEB",
            "pontuacao": professor.pontuacao_paeb,
            "cpf": professor.cpf,
            "disciplina": professor.disciplina_paeb,  # Disciplina associada ao cargo PAEB
        })

    # Adicionar professores com pontuação zero (ordem alfabética)
    for professor in professores_zero:
        ranking_geral.append({
            "id": professor.id,
            "nome": professor.nome,
            "cargo": "ZERADO",
            "pontuacao": 0,
            "cpf": professor.cpf,
            "disciplina": None,  # Sem disciplina associada
        })

    # Reorganizar pelo critério (PEB > PAEB > ZERADO, com CPF como desempate)
    ranking_geral = sorted(ranking_geral, key=lambda x: (
        x["cargo"] == "ZERADO",  # ZERADO vai para o final
        x["cargo"] == "PAEB",    # PAEB depois de PEB
        -x["pontuacao"],         # Pontuação decrescente
        x["cpf"]                 # Desempate por CPF
    ))

    # Adicionar posições
    ranking_geral_com_posicao = {idx + 1: prof for idx, prof in enumerate(ranking_geral)}

    return ranking_geral_com_posicao


















@login_required
def pagina_gestor(request):
    # Verifica se o usuário tem permissão para acessar a página
    if not (request.user.groups.filter(name='Gestor').exists() or request.user.username == 'seu_usuario_dono'):
        return HttpResponseForbidden("Acesso negado. Você não tem permissão para acessar esta página.")

    # Obter todos os professores e escolas
    professores = Professor.objects.all()
    escolas = Escola.objects.all()
    professor_selecionado = None
    disciplina_selecionada = None
    escolhas_detalhadas = []
    aulas_atribuidas = []
    mensagem_erro = None

    # Calcular os rankings
    professores_peb = Professor.objects.filter(cargo__in=['PEB', 'AMBOS'], pontuacao_peb__gt=0).order_by('-pontuacao_peb', 'cpf')
    professores_paeb = Professor.objects.filter(cargo__in=['PAEB', 'AMBOS'], pontuacao_paeb__gt=0).order_by('-pontuacao_paeb', 'cpf')
    professores_zerados = Professor.objects.filter(pontuacao_peb=0, pontuacao_paeb=0).order_by('nome', 'cpf')

    # Combinar os rankings em uma lista geral
    ranking_geral = []
    for professor in professores_peb:
        ranking_geral.append({
            "id": professor.id,
            "nome": professor.nome,
            "cargo": "PEB",
            "pontuacao": professor.pontuacao_peb,
            "disciplina": professor.disciplina_peb,
            "cpf": professor.cpf,
        })
    for professor in professores_paeb:
        ranking_geral.append({
            "id": professor.id,
            "nome": professor.nome,
            "cargo": "PAEB",
            "pontuacao": professor.pontuacao_paeb,
            "disciplina": professor.disciplina_paeb,
            "cpf": professor.cpf,
        })
    for professor in professores_zerados:
        ranking_geral.append({
            "id": professor.id,
            "nome": professor.nome,
            "cargo": "ZERADO",
            "pontuacao": 0,
            "disciplina": None,
            "cpf": professor.cpf,
        })

    # Ordenar a lista geral
    ranking_geral = sorted(ranking_geral, key=lambda x: (
        x["cargo"] == "ZERADO",  # Professores zerados por último
        x["cargo"] == "PAEB",    # PAEB depois de PEB
        -x["pontuacao"],         # Pontuação decrescente
        x["cpf"]                 # CPF para desempate
    ))

    # Buscar professor por CPF ou classificação
    cpf = request.GET.get('cpf')
    classificacao_especifica = request.GET.get('classificacao_especifica')
    tipo_classificacao = request.GET.get('tipo_classificacao')
    classificacao_geral = request.GET.get('classificacao_geral')

    if cpf:
        try:
            professor_selecionado = Professor.objects.get(cpf=cpf)
            disciplina_selecionada = professor_selecionado.disciplina_peb or professor_selecionado.disciplina_paeb
        except Professor.DoesNotExist:
            mensagem_erro = f"Nenhum professor encontrado com o CPF {cpf}."

    elif classificacao_especifica:
        classificacao_especifica = int(classificacao_especifica)
        try:
            ranking = ranking_geral if tipo_classificacao == 'GERAL' else (
                ranking_especifico_peb if tipo_classificacao == 'PEB' else ranking_especifico_paeb
            )
            professor_id = next((prof["id"] for idx, prof in enumerate(ranking) if idx + 1 == classificacao_especifica), None)
            professor_selecionado = Professor.objects.get(id=professor_id)
            disciplina_selecionada = professor_selecionado.disciplina_peb if tipo_classificacao == 'PEB' else professor_selecionado.disciplina_paeb
        except (StopIteration, Professor.DoesNotExist):
            mensagem_erro = f"Nenhum professor encontrado para a classificação {classificacao_especifica} ({tipo_classificacao})."

    elif classificacao_geral:
        classificacao_geral = int(classificacao_geral)
        try:
            professor_id = ranking_geral[classificacao_geral - 1]["id"]
            professor_selecionado = Professor.objects.get(id=professor_id)
            disciplina_selecionada = professor_selecionado.disciplina_peb or professor_selecionado.disciplina_paeb
        except IndexError:
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
                disciplinas_atribuidas = [atribuicao.disciplina for atribuicao in atribuicoes_turma]

                # Cria status para todas as disciplinas possíveis do professor
                status_disciplinas = [
                    {
                        "disciplina": disciplina,
                        "atribuida": disciplina in disciplinas_atribuidas
                    }
                    for disciplina in [professor_selecionado.disciplina_peb, professor_selecionado.disciplina_paeb]
                    if disciplina
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

    # Renderizar a página do gestor
    return render(request, 'pagina_gestor.html', {
        'professores': professores,
        'escolas': escolas,
        'professor_selecionado': professor_selecionado,
        'disciplina_selecionada': disciplina_selecionada,
        'escolhas_detalhadas': escolhas_detalhadas,
        'aulas_atribuidas': aulas_atribuidas,
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
            disciplina = data.get('disciplina')
            fora_de_campo = data.get('fora_de_campo', False)
            em_substituicao = data.get('em_substituicao', False)
            licenca = data.get('licenca', False)

            # Validações básicas
            if not professor_id or not disciplina:
                return JsonResponse({'erro': 'Dados incompletos. Verifique os campos preenchidos.'}, status=400)

            professor = Professor.objects.get(id=professor_id)
            gestor = request.user.username

            # Memória temporária para gerenciar licenças
            memoria_licenca_key = f"licenca_professor_{professor_id}"
            memoria_licenca = request.session.get(memoria_licenca_key, [])

            if licenca:
                if memoria_licenca:
                    # Desativa licença e restaura as atribuições
                    for atrib in memoria_licenca:
                        escola = Escola.objects.get(id=atrib['escolaId'])
                        Atribuicao.objects.update_or_create(
                            professor=professor,
                            escola=escola,
                            turma=atrib['turma'],
                            defaults={
                                'disciplina': atrib['disciplina'],
                                'gestor_responsavel': gestor
                            }
                        )
                    # Limpa a memória após restaurar
                    del request.session[memoria_licenca_key]
                    return JsonResponse({'mensagem': 'Licença desativada. Atribuições restauradas.'})
                else:
                    # Ativa licença e remove todas as atribuições
                    atribuicoes = Atribuicao.objects.filter(professor=professor)
                    memoria_licenca = [
                        {
                            'escolaId': atrib.escola.id,
                            'turma': atrib.turma,
                            'disciplina': atrib.disciplina
                        }
                        for atrib in atribuicoes
                    ]
                    # Salva as atribuições na memória temporária
                    request.session[memoria_licenca_key] = memoria_licenca
                    atribuicoes.delete()
                    return JsonResponse({'mensagem': 'Licença ativada. Todas as atribuições foram removidas.'})

            # Fluxo padrão para novas atribuições
            for turma_data in turmas:
                escola = Escola.objects.get(id=turma_data['escolaId'])

                # Ajusta a disciplina com textos adicionais
                disciplina_final = disciplina
                if fora_de_campo:
                    disciplina_final += " (Fora de Campo)"
                if em_substituicao:
                    disciplina_final += " (Substituição)"

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
                        em_substituicao_texto = "(Substituição)" if "substituição" in atribuicao.disciplina.lower() else ""
                        
                        dados_turma["disciplinas"].append({
                            "nome": f"{disciplina.replace('_', ' ').title()} {fora_de_campo_texto} {em_substituicao_texto}".strip(),
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
                            "disciplina_peb": professor.disciplina_peb,
			  "disciplina_paeb": professor.disciplina_paeb,
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




	
def calcular_classificacao():
    # Obter todos os professores
    professores_peb = Professor.objects.filter(cargo__in=['PEB', 'AMBOS']).order_by('-pontuacao_peb', 'cpf')
    professores_paeb = Professor.objects.filter(cargo__in=['PAEB', 'AMBOS']).order_by('-pontuacao_paeb', 'cpf')

    # Calcular classificação específica
    ranking_peb = {professor.id: idx + 1 for idx, professor in enumerate(professores_peb)}
    ranking_paeb = {professor.id: idx + 1 for idx, professor in enumerate(professores_paeb)}

    # Calcular classificação geral
    professores_geral = sorted(
        list(professores_peb) + list(professores_paeb),
        key=lambda prof: (-prof.pontuacao_peb if prof.cargo in ['PEB', 'AMBOS'] else -prof.pontuacao_paeb, prof.cpf)
    )
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

