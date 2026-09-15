# agents/agent_02_qualification/qualification_agent.py

# ... (Manter importações e inicialização da classe intactas)

    def _score_experience(self, job, profile) -> float:
        """
        Mede a cobertura dos requisitos obrigatórios da vaga comprovados 
        dentro das experiências profissionais descritas no perfil.
        """
        if not job.competencias_obrigatorias:
            return 10.0
            
        reqs_obrigatorios = {req.lower() for req in job.competencias_obrigatorias}
        reqs_comprovados = set()
        
        # Varre o histórico profissional em busca de evidências textuais normalizadas
        for exp in getattr(profile, 'experiencias', []):
            # Analisa o cargo e o texto descritivo/atividades fornecido pelo schema real
            texto_experiencia = f"{getattr(exp, 'cargo', '')} { ' '.join(getattr(exp, 'atividades', [])) }".lower()
            for req in reqs_obrigatorios:
                if req in texto_experiencia:
                    reqs_comprovados.add(req)
                    
        return round((len(reqs_comprovados) / len(reqs_obrigatorios)) * 10.0, 2)

    def _score_responsibilities(self, job, profile) -> float:
        """
        Avalia se os termos de responsabilidades e atribuições da vaga 
        possuem correspondência determinística normalizada no histórico do candidato.
        """
        # Utiliza campos reais existentes em JobOpportunity (ex: descricao_bruta ou atividades_responsabilidades)
        atividades_vaga = getattr(job, 'atividades_responsabilidades', [])
        if not atividades_vaga:
            # Fallback para descricao_bruta caso a lista esteja vazia
            atividades_vaga = [getattr(job, 'descricao_bruta', '')]
            
        texto_vaga_limpo = " ".join(atividades_vaga).lower()
        if not texto_vaga_limpo.strip():
            return 10.0

        # Coleta o bloco textual de evidências do candidato
        texto_candidato = ""
        for exp in getattr(profile, 'experiencias', []):
            texto_candidato += f" {' '.join(getattr(exp, 'atividades', []))}".lower()

        # Conta termos chaves ou correspondência determinística direta de linhas
        termos_encontrados = 0
        total_termos = len(atividades_vaga)
        
        for atividade in atividades_vaga:
            if atividade.lower() in texto_candidato:
                termos_encontrados += 1
                
        if total_termos == 0:
            return 0.0
        return round((termos_encontrados / total_termos) * 10.0, 2)

    def _score_ats(self, job, profile) -> float:
        """
        Estimativa interna de aderência descritiva.
        Aplica peso ponderado de 80% para requisitos obrigatórios e 20% para desejáveis.
        """
        # Concatena todo o perfil do candidato para buscar correspondências (Anti-Alucinação)
        texto_completo_perfil = f"{getattr(profile, 'nome', '')} {getattr(profile, 'senioridade_declarada', '')} " \
                                f"{' '.join(getattr(profile, 'competencias_tecnicas', []))} "
        for exp in getattr(profile, 'experiencias', []):
            texto_completo_perfil += f" {getattr(exp, 'cargo', '')} {' '.join(getattr(exp, 'atividades', []))}"
        texto_completo_perfil = texto_completo_perfil.lower()

        # 1. Avaliação dos Obrigatórios (Peso 80%)
        obrigatorios = getattr(job, 'competencias_obrigatorias', [])
        score_ob = 10.0
        if obrigatorios:
            encontrados_ob = sum(1 for req in obrigatorios if req.lower() in texto_completo_perfil)
            score_ob = (encontrados_ob / len(obrigatorios)) * 10.0

        # 2. Avaliação dos Desejáveis (Peso 20%)
        desejaveis = getattr(job, 'competencias_desejaveis', [])
        score_dj = 10.0
        if desejaveis:
            encontrados_dj = sum(1 for req in desejaveis if req.lower() in texto_completo_perfil)
            score_dj = (encontrados_dj / len(desejaveis)) * 10.0

        # Consolidação ponderada 80/20
        score_ats_final = (score_ob * 0.8) + (score_dj * 0.2)
        return round(score_ats_final, 2)

# ... (Dentro do método principal de cálculo de score)
    # Substituir os espelhamentos antigos pelas chamadas isoladas:
    breakdown.professional_experience = self._score_experience(job, profile)
    breakdown.responsibilities = self._score_responsibilities(job, profile)
    breakdown.ats_compatibility = self._score_ats(job, profile)

    # Inserção obrigatória da cláusula explicativa estipulada
    reasoning_prefix = "Compatibilidade ATS calculada por critérios internos da plataforma como estimativa de aderência descritiva, sem garantia de aprovação em sistemas externos. "
