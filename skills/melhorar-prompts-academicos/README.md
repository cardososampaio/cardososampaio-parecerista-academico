# Melhorar Prompts Acadêmicos

Skill em português para avaliar, criar e reescrever prompts voltados à pesquisa acadêmica.

## O que faz

A skill ajuda a transformar pedidos acadêmicos em instruções claras, contextualizadas, executáveis e verificáveis, preservando a intenção, o recorte e as exigências do usuário.

Ela foi desenhada para tarefas como pesquisa e revisão de literatura, leitura e síntese, fichamento, escrita e revisão de textos, tradução acadêmica, pesquisa empírica, análise de dados, pareceres, avaliação acadêmica e preparação de aulas.

O protocolo evita dois extremos. Não trata todo prompt como se precisasse de uma estrutura longa e rígida, mas também não aceita instruções vagas quando faltam elementos que afetam diretamente a execução.

Entre as regras centrais estão:

- identificar primeiro o resultado desejado e o tipo de tarefa acadêmica
- recuperar contexto e restrições já informados pelo usuário
- corrigir apenas problemas que realmente prejudiquem a tarefa
- perguntar somente quando a informação ausente alterar materialmente o resultado
- usar campos editáveis quando for possível avançar sem interromper o usuário
- não escolher silenciosamente teoria, método, período, país, fontes ou periódico
- adaptar o prompt ao tipo de tarefa acadêmica
- distinguir instruções do material que será analisado
- solicitar evidências e procedimentos verificáveis quando necessário
- não pedir exposição integral do raciocínio interno do modelo
- não inventar referências, dados, recursos ou capacidades inexistentes
- preservar o que já funciona em rodadas posteriores de refinamento

## Saída padrão

Quando o usuário não especificar outro formato, a skill entrega:

1. avaliação rápida do prompt
2. uma única versão melhorada pronta para uso
3. explicação breve das alterações realizadas

Pedidos específicos prevalecem. Se o usuário quiser apenas o prompt final, apenas a avaliação ou outra forma de saída, a skill deve respeitar essa instrução.

## Arquivo principal

- [`SKILL.md`](SKILL.md) — protocolo completo, versão 1.0.0.

## Instalação

Copie esta pasta para o diretório de skills do seu agente, preservando `SKILL.md` na raiz da skill.

Exemplo:

```text
.agents/skills/melhorar-prompts-academicos/SKILL.md
```

## Uso

```text
Use a skill melhorar-prompts-academicos para avaliar e reescrever este prompt acadêmico.
```

Também é possível fornecer apenas uma ideia ou objetivo para que o agente construa o prompt a partir do contexto disponível.

## Base

A skill foi elaborada a partir dos princípios e exemplos de *Prompts (Infalíveis!) para Pesquisa Acadêmica com Inteligência Artificial*, de Rafael Cardoso Sampaio e Dalson Figueiredo, publicado pela EDUFPI em 2025, e das instruções originais do GPT de análise e melhoria de prompts fornecidas pelo autor.

## Citação

> Sampaio, Rafael Cardoso. *Melhorar Prompts Acadêmicos*. Skill para agentes de IA. Versão 1.0.0. 2026.

Licença MIT conforme o arquivo [`LICENSE`](../../LICENSE) da raiz do repositório.
