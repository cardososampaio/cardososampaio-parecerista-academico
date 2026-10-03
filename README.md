# Parecerista Acadêmico

Skill pública em português para produzir **pareceres acadêmicos rigorosos, rastreáveis e construtivos com agentes de IA**.

O pacote foi desenhado para apoiar a avaliação de artigos, capítulos, teses, dissertações, working papers, relatórios científicos e manuscritos revisados. A skill exige leitura integral, múltiplas passagens analíticas, avaliação adequada ao desenho da pesquisa, rastreabilidade das críticas e uma rodada adversarial antes da redação do parecer.

## O que a skill faz

- exige leitura integral do manuscrito antes da recomendação editorial
- separa compreensão global, avaliação metodológica e análise argumentativa em passagens sucessivas
- constrói um mapa interno do estudo com pergunta, objetivos, desenho, dados, análise, resultados e conclusões
- avalia o manuscrito por quatro lentes transversais de sustentação, inferência, escopo e contribuição
- adapta os critérios ao tipo de trabalho, incluindo pesquisas quantitativas, qualitativas, métodos mistos, revisões, estudos de caso e artigos teóricos ou conceituais
- registra cada crítica com localização, evidência, consequência e correção possível
- exige que críticas compostas sejam decompostas em problemas atômicos
- trata alegações de ausência com checagem explícita das partes do manuscrito onde a informação deveria aparecer
- executa um stress test adversarial com melhor contra-argumento, explicação alternativa, premissa não examinada, salto inferencial e generalização vulnerável
- obriga o agente a formular a melhor defesa possível do manuscrito antes de manter uma crítica adversarial
- reconcilia a leitura principal e a rodada adversarial antes de classificar os problemas
- separa comentários destinados aos autores da recomendação confidencial ao editor
- diferencia problemas estruturais, reparáveis e secundários
- inclui protocolos para primeira rodada, reavaliação de manuscrito revisado e resposta a pareceristas
- inclui controle final contra alucinação de páginas, linhas, citações, métodos, dados e referências

A rodada adversarial não funciona como um segundo parecerista fictício. Ela é uma etapa de teste do mesmo agente e nenhuma objeção entra automaticamente no parecer. A crítica precisa sobreviver à melhor defesa possível do manuscrito e permanecer sustentada por evidência rastreável.

## Princípios de funcionamento

A skill parte de alguns compromissos simples.

O manuscrito é a fonte primária. Conhecimento externo só deve ser utilizado quando o usuário solicitar pesquisa, checagem ou comparação externa.

O agente deve avaliar o estudo que os autores efetivamente fizeram. Não deve transformar o trabalho em outro projeto nem impor sua teoria ou método preferido.

Afirmações positivas e negativas exigem sustentação. Uma crítica tecnicamente sofisticada não recebe maior peso apenas pela forma como foi escrita.

A gravidade de um problema depende de seu efeito sobre validade, interpretação ou contribuição. O tom adversarial não autoriza inflar a gravidade de uma crítica.

Uma qualidade em determinada dimensão não compensa automaticamente uma falha que comprometa outra dimensão central do estudo.

## Fluxo de avaliação

A execução completa segue, em termos gerais, este fluxo.

1. leitura integral do manuscrito
2. construção do mapa do estudo
3. primeira passagem de compreensão global
4. segunda passagem centrada em método, dados e inferência
5. terceira passagem centrada em argumento, interpretação e apresentação
6. avaliação pelas quatro lentes transversais
7. avaliação específica conforme o tipo de manuscrito e desenho de pesquisa
8. registro atômico das evidências e críticas
9. verificação de inconsistências internas
10. stress test adversarial
11. melhor defesa possível do manuscrito contra cada crítica adversarial
12. reconciliação entre avaliação principal e rodada adversarial
13. classificação das prioridades de revisão
14. redação do parecer aos autores
15. recomendação confidencial ao editor
16. controle de qualidade antes da entrega

## Quatro lentes transversais

### Sustentação

Pergunta se as evidências apresentadas sustentam as afirmações feitas pelo manuscrito.

### Inferência

Examina o caminho entre evidência, resultado, interpretação e conclusão e procura saltos lógicos, causalidade indevida ou pressupostos não demonstrados.

### Escopo

Compara população, corpus, casos, período e contexto efetivamente analisados com o alcance atribuído às conclusões.

### Contribuição

Examina se o manuscrito demonstra com clareza o que acrescenta ao problema estudado e se a contribuição declarada corresponde ao que o trabalho efetivamente entrega.

## Stress test adversarial

Depois da avaliação convencional, a skill exige uma rodada deliberadamente adversarial. O agente procura a melhor objeção possível ao argumento central e testa cinco frentes.

- melhor contra-argumento
- explicação alternativa mais plausível
- premissa não examinada
- maior salto inferencial
- generalização mais vulnerável

A rodada adversarial produz candidatos a críticas, não conclusões automáticas.

Cada candidato precisa passar por reconciliação. O agente deve formular a melhor defesa possível dos autores, verificar novamente o manuscrito e manter a crítica apenas quando ela continuar sustentada.

Esse desenho procura reduzir dois riscos opostos. O primeiro é o parecer excessivamente complacente. O segundo é o hipercriticismo produzido por uma instrução genérica para ser rigoroso.

## Tipos de manuscrito contemplados

A skill inclui critérios específicos para

- pesquisas quantitativas
- pesquisas qualitativas
- métodos mistos
- revisões sistemáticas, scoping reviews, meta-análises e outras sínteses
- artigos teóricos e conceituais
- estudos de caso
- análises de conteúdo
- estudos de políticas públicas

Os critérios só devem ser aplicados quando forem pertinentes ao desenho do trabalho.

## Estrutura do repositório

- `SKILL.md` contém o protocolo completo de execução
- `README.md` apresenta objetivos, funcionamento e instalação
- `CITATION.cff` fornece os metadados de citação
- `LICENSE` contém a licença MIT

A skill foi deliberadamente mantida em um único arquivo principal. O objetivo é reduzir dependências internas e aumentar a chance de o agente executar o protocolo completo sem ignorar arquivos auxiliares.

## Instalação

Clone ou copie este repositório para o diretório de skills do agente, preservando `SKILL.md` na raiz da pasta.

```bash
git clone --depth 1 https://github.com/cardososampaio/cardososampaio-parecerista-academico.git
```

Em ambientes que usam uma pasta local de skills, copie o diretório resultante para o caminho correspondente. Um exemplo comum é

```text
.agents/skills/parecerista-academico/
```

O mecanismo exato de descoberta depende do agente utilizado.

## Uso básico

Depois de instalar a skill, forneça o manuscrito ao agente e solicite um parecer acadêmico completo.

Exemplo

```text
Use a skill parecerista-academico para avaliar integralmente este manuscrito e produzir um parecer para os autores e uma recomendação confidencial ao editor.
```

Para reavaliar uma nova versão, forneça também o parecer anterior e a carta de resposta dos autores.

## Limites

A skill não transforma um modelo de linguagem em parecerista humano independente.

Uma execução por IA não equivale a consenso entre especialistas, avaliação editorial real ou validação metodológica externa.

O agente não deve afirmar que verificou elementos que não estavam acessíveis no manuscrito.

A rodada adversarial não deve criar críticas apenas para demonstrar rigor.

A avaliação de originalidade frente ao estado da literatura exige pesquisa externa quando isso não puder ser demonstrado pelo próprio manuscrito.

Questões que dependam de conhecimento estatístico, metodológico ou substantivo especializado podem exigir revisão humana adicional.

## Ética e confidencialidade

O uso de IA em revisão por pares pode ser restrito ou proibido por periódicos, editoras e associações científicas. Antes de enviar um manuscrito confidencial a qualquer sistema de IA, verifique a política editorial aplicável e as condições de tratamento dos dados.

Esta skill foi concebida como apoio ao julgamento humano. Ela não substitui a responsabilidade do parecerista pela leitura, avaliação e decisão sobre o conteúdo do parecer.

Para uma discussão sobre uso ético e responsável de IA na pesquisa acadêmica, consulte

> SAMPAIO, Rafael Cardoso. SABBATINI, Marcelo. LIMONGI, Ricardo. *Diretrizes para o uso ético e responsável da Inteligência Artificial Generativa. Um guia prático para pesquisadores*. São Paulo. Editora Intercom. 2024.

## Como citar

> Sampaio, Rafael Cardoso. *Parecerista Acadêmico*. Skill para agentes de IA. Versão 2.0.0. 2026. https://github.com/cardososampaio/cardososampaio-parecerista-academico

Consulte também `CITATION.cff`.

## Licença

MIT License. Consulte [`LICENSE`](LICENSE).