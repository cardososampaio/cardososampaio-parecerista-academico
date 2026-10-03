# Skills Acadêmicas

Coleção pública em português de **skills para agentes de IA voltadas à pesquisa acadêmica**, desenvolvidas por Rafael Cardoso Sampaio.

O repositório reúne protocolos operacionais para tarefas de leitura, escrita, revisão e avaliação acadêmica. Cada skill fica em sua própria pasta e possui um `SKILL.md` como ponto de entrada. Skills simples podem concentrar todo o protocolo nesse arquivo. Skills mais extensas podem incluir módulos de referência, assets, scripts e metadados auxiliares que devem permanecer junto ao pacote.

## Skills disponíveis

| Skill | Finalidade | Versão |
|---|---|---|
| [Parecerista Acadêmico](skills/parecerista-academico/) | Avaliar manuscritos e produzir pareceres rastreáveis e construtivos | 2.0.0 |
| [Fichamento Acadêmico](skills/fichamento-academico/) | Produzir fichamentos densos, verificáveis e reutilizáveis | 3.0.0 |
| [Melhorar Prompts Acadêmicos](skills/melhorar-prompts-academicos/) | Criar, avaliar e reescrever prompts para tarefas acadêmicas | 1.0.0 |
| [Escrita Acadêmica](skills/escritaacademica/) | Planejar, redigir, revisar, reestruturar, traduzir e auditar textos acadêmicos | 1.0.0 |

### Parecerista Acadêmico

Skill para avaliação integral de manuscritos e produção de pareceres acadêmicos rastreáveis e construtivos.

Principais recursos

- leitura integral e múltiplas passagens analíticas
- quatro lentes transversais de sustentação, inferência, escopo e contribuição
- critérios específicos por desenho de pesquisa
- registro de evidências e críticas atômicas
- verificação rigorosa de alegações de ausência
- stress test adversarial
- melhor defesa possível do manuscrito antes de manter críticas adversariais
- reconciliação e classificação de gravidade
- separação entre parecer aos autores e recomendação confidencial ao editor

**Versão** 2.0.0  
**Pasta** [`skills/parecerista-academico/`](skills/parecerista-academico/)  
**Arquivo principal** [`SKILL.md`](skills/parecerista-academico/SKILL.md)

### Fichamento Acadêmico

Skill para produzir fichamentos densos, verificáveis, rastreáveis e reutilizáveis de artigos, capítulos, livros, teses, relatórios e materiais equivalentes.

Principais recursos

- fichamento como base de leitura recuperável
- leitura integral e cobertura por unidades
- ledger interno de cobertura
- localização de conceitos, citações, dados, métodos e resultados
- distinção entre conteúdo explícito, inferência e interpretação
- takeaway, resumão expandido, mapa do argumento e matriz de alegações e evidências
- módulos próprios para diferentes tipos de texto e desenhos de pesquisa
- crítica interna separada de crítica contextual
- registro obrigatório de lacunas, dúvidas e limitações do arquivo
- controle contra fabricação de páginas, citações, referências, dados e métodos

**Versão** 3.0.0  
**Pasta** [`skills/fichamento-academico/`](skills/fichamento-academico/)  
**Arquivo principal** [`SKILL.md`](skills/fichamento-academico/SKILL.md)

### Melhorar Prompts Acadêmicos

Skill para avaliar, criar e reescrever prompts destinados a tarefas de pesquisa, leitura, escrita, revisão, tradução, análise e ensino acadêmico.

Principais recursos

- identifica o resultado desejado antes de reformular a instrução
- preserva contexto, restrições, nomes, recortes e preferências já fornecidos
- corrige apenas problemas que realmente afetem a execução
- evita transformar prompts simples em estruturas desnecessariamente longas
- pergunta somente quando uma lacuna altera materialmente a tarefa
- usa campos editáveis quando for possível avançar sem interromper o usuário
- adapta as instruções ao tipo de tarefa acadêmica
- distingue revisão linguística, reorganização e alteração de conteúdo
- não escolhe silenciosamente teoria, método, período, país, fontes ou periódico
- inclui regras contra fabricação de dados, citações, referências e capacidades inexistentes
- produz, por padrão, avaliação rápida, prompt melhorado e explicação das mudanças

**Versão** 1.0.0  
**Pasta** [`skills/melhorar-prompts-academicos/`](skills/melhorar-prompts-academicos/)  
**Arquivo principal** [`SKILL.md`](skills/melhorar-prompts-academicos/SKILL.md)

### Escrita Acadêmica

Skill para trabalhar escrita acadêmica em Humanidades e Ciências Sociais desde correções locais até manuscritos completos, sem impor um único gênero ou desenho de pesquisa.

Principais recursos

- planejamento, redação, correção, revisão, reescrita, reestruturação, condensação e expansão
- tradução acadêmica e preparação de textos para leitores e publicações internacionais
- distinção entre intervenção formal, editorial, estrutural e desenvolvimento de conteúdo
- preservação de argumento, dados, números, citações, conceitos, qualificadores e voz autoral
- módulos específicos para argumentação, gêneros e seções, literatura, métodos qualitativos e quantitativos, teoria e história
- protocolos próprios para integridade de fontes, textos longos, internacionalização, prosa e auditoria final
- funcionamento com um único agente por padrão, sem exigir orquestração ou pesquisa externa desnecessária
- scripts locais para verificar a integridade do pacote e comparar elementos protegidos entre versões de texto
- casos de avaliação comportamental para manutenção e testes
- regras explícitas contra fabricação de dados, referências, páginas, citações, procedimentos e resultados

**Versão** 1.0.0  
**Pasta** [`skills/escritaacademica/`](skills/escritaacademica/)  
**Arquivo principal** [`SKILL.md`](skills/escritaacademica/SKILL.md)

## Estrutura

```text
skills-academicas/
├── README.md
├── CITATION.cff
├── LICENSE
└── skills/
    ├── parecerista-academico/
    │   ├── SKILL.md
    │   ├── README.md
    │   └── CITATION.cff
    ├── fichamento-academico/
    │   ├── SKILL.md
    │   ├── README.md
    │   └── CITATION.cff
    ├── melhorar-prompts-academicos/
    │   ├── SKILL.md
    │   ├── README.md
    │   └── CITATION.cff
    └── escritaacademica/
        ├── SKILL.md
        ├── README.md
        ├── CITATION.cff
        ├── agents/
        ├── assets/
        ├── references/
        └── scripts/
```

## Instalação

Clone o repositório

```bash
git clone --depth 1 https://github.com/cardososampaio/skills-academicas.git
```

Depois copie a pasta inteira da skill desejada para o diretório de skills do seu agente.

Exemplos

```text
.agents/skills/parecerista-academico/
.agents/skills/fichamento-academico/
.agents/skills/melhorar-prompts-academicos/
.agents/skills/escritaacademica/
```

Não copie apenas o `SKILL.md` quando a pasta contiver `references`, `assets`, `scripts`, `agents` ou outros arquivos utilizados pelo protocolo.

O mecanismo exato de descoberta de skills depende do agente utilizado.

## Princípios comuns

As skills desta coleção procuram seguir alguns princípios recorrentes

- fidelidade ao material fornecido
- rastreabilidade de afirmações
- distinção entre texto, inferência e análise
- adequação ao gênero e ao desenho de pesquisa
- explicitação de incertezas e limitações
- prevenção de fabricação de citações, páginas, dados, métodos e referências
- uso da IA como apoio ao julgamento humano, não como substituto automático dele

Cada skill possui regras próprias. O `SKILL.md` de cada pasta é o ponto de entrada e pode encaminhar o agente a módulos adicionais do próprio pacote.

## Uso responsável

Antes de enviar manuscritos, documentos inéditos ou materiais confidenciais a qualquer sistema de IA, verifique as políticas institucionais e editoriais aplicáveis e as condições de tratamento dos dados.

As skills organizam o procedimento de trabalho do agente. Elas não transformam uma execução por IA em validação humana, consenso científico ou decisão editorial.

## Como citar

Para citar a coleção

> Sampaio, Rafael Cardoso. *Skills Acadêmicas*. Coleção de skills para agentes de IA. 2026. https://github.com/cardososampaio/skills-academicas

Para citar uma skill específica, consulte o `CITATION.cff` dentro da pasta correspondente.

## Licença

MIT License. Consulte [`LICENSE`](LICENSE).
