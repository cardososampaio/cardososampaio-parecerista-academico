# Skills Acadêmicas

Coleção pública em português de **skills para agentes de IA voltadas à pesquisa acadêmica**, desenvolvidas por Rafael Cardoso Sampaio.

O repositório reúne protocolos operacionais autocontidos para tarefas acadêmicas específicas. Cada skill fica em sua própria pasta e mantém um único `SKILL.md` como núcleo de execução. A documentação auxiliar existe para navegação, instalação e citação, sem fragmentar as instruções que o agente precisa seguir.

## Skills disponíveis

### Parecerista Acadêmico

Skill para avaliação integral de manuscritos e produção de pareceres acadêmicos rastreáveis e construtivos.

Principais recursos:

- leitura integral e múltiplas passagens analíticas
- quatro lentes transversais: sustentação, inferência, escopo e contribuição
- critérios específicos por desenho de pesquisa
- registro de evidências e críticas atômicas
- verificação rigorosa de alegações de ausência
- stress test adversarial
- melhor defesa possível do manuscrito antes de manter críticas adversariais
- reconciliação e classificação de gravidade
- separação entre parecer aos autores e recomendação confidencial ao editor

**Versão:** 2.0.0  
**Pasta:** [`skills/parecerista-academico/`](skills/parecerista-academico/)  
**Arquivo principal:** [`SKILL.md`](skills/parecerista-academico/SKILL.md)

### Fichamento Acadêmico

Skill para produzir fichamentos densos, verificáveis, rastreáveis e reutilizáveis de artigos, capítulos, livros, teses, relatórios e materiais equivalentes.

Principais recursos:

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

**Versão:** 3.0.0  
**Pasta:** [`skills/fichamento-academico/`](skills/fichamento-academico/)  
**Arquivo principal:** [`SKILL.md`](skills/fichamento-academico/SKILL.md)

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
    └── fichamento-academico/
        ├── SKILL.md
        ├── README.md
        └── CITATION.cff
```

## Instalação

Clone o repositório:

```bash
git clone --depth 1 https://github.com/cardososampaio/skills-academicas.git
```

Depois copie apenas a pasta da skill desejada para o diretório de skills do seu agente.

Exemplo:

```text
.agents/skills/parecerista-academico/
.agents/skills/fichamento-academico/
```

Cada uma dessas pastas deve preservar seu respectivo `SKILL.md`.

O mecanismo exato de descoberta de skills depende do agente utilizado.

## Princípios comuns

As skills desta coleção procuram seguir alguns princípios recorrentes:

- fidelidade ao material fornecido
- rastreabilidade de afirmações
- distinção entre texto, inferência e análise
- adequação ao desenho de pesquisa
- explicitação de incertezas e limitações
- prevenção de fabricação de citações, páginas, dados, métodos e referências
- uso da IA como apoio ao julgamento humano, não como substituto automático dele

Cada skill possui regras próprias. O arquivo `SKILL.md` de cada pasta prevalece para a tarefa correspondente.

## Uso responsável

Antes de enviar manuscritos, documentos inéditos ou materiais confidenciais a qualquer sistema de IA, verifique as políticas institucionais e editoriais aplicáveis e as condições de tratamento dos dados.

As skills organizam o procedimento de trabalho do agente. Elas não transformam uma execução por IA em validação humana, consenso científico ou decisão editorial.

## Como citar

Para citar a coleção:

> Sampaio, Rafael Cardoso. *Skills Acadêmicas*. Coleção de skills para agentes de IA. 2026. https://github.com/cardososampaio/skills-academicas

Para citar uma skill específica, consulte o `CITATION.cff` dentro da pasta correspondente.

## Licença

MIT License. Consulte [`LICENSE`](LICENSE).
