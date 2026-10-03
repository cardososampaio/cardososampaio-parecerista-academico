# Parecerista Acadêmico

Skill em português para agentes de IA produzirem pareceres acadêmicos rigorosos, rastreáveis e construtivos.

## O que faz

A skill orienta a leitura integral de manuscritos e organiza a avaliação em múltiplas passagens. Ela combina critérios adequados ao desenho da pesquisa com quatro lentes transversais de sustentação, inferência, escopo e contribuição.

Depois da avaliação convencional, executa um **stress test adversarial** para procurar contra-argumentos, explicações alternativas, premissas não examinadas, elos inferenciais frágeis e generalizações excessivas. Nenhuma crítica adversarial entra automaticamente no parecer. O agente deve formular a melhor defesa possível do manuscrito e reconciliar as duas leituras antes da recomendação editorial.

Também inclui regras de rastreabilidade, atomicidade das críticas, verificação de alegações de ausência, classificação de gravidade e separação entre comentários aos autores e recomendação confidencial ao editor.

## Arquivo principal

- [`SKILL.md`](SKILL.md) — protocolo completo, versão 2.0.0.

## Instalação

Copie esta pasta para o diretório de skills do seu agente, preservando `SKILL.md` na raiz da skill.

Exemplo:

```text
.agents/skills/parecerista-academico/SKILL.md
```

## Uso

```text
Use a skill parecerista-academico para avaliar integralmente este manuscrito e produzir um parecer aos autores e uma recomendação confidencial ao editor.
```

## Limites

A skill apoia o julgamento humano. Não transforma uma execução de IA em parecer independente, consenso entre especialistas ou validação externa do manuscrito. O uso de IA em revisão por pares pode ser restringido por revistas e editoras.

## Citação

> Sampaio, Rafael Cardoso. *Parecerista Acadêmico*. Skill para agentes de IA. Versão 2.0.0. 2026.

Licença MIT conforme o arquivo [`LICENSE`](../../LICENSE) da raiz do repositório.
