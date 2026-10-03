# Fichamento Acadêmico

Skill em português para produzir fichamentos acadêmicos densos, verificáveis, rastreáveis e reutilizáveis.

## O que faz

A skill trata o fichamento como uma **base de leitura recuperável**, não como um resumo curto. O protocolo foi pensado para permitir que o pesquisador retorne posteriormente ao argumento, aos conceitos, às evidências, às citações, ao método e aos possíveis usos acadêmicos sem precisar reler imediatamente todo o documento.

Ela exige leitura global e por unidades, ledger interno de cobertura, localização recuperável, distinção entre conteúdo explícito, inferência e interpretação do fichamento, matriz de alegações e evidências e módulos específicos conforme o tipo de texto.

O protocolo contempla trabalhos empíricos quantitativos e qualitativos, métodos mistos, experimentos, análise computacional ou textual, trabalhos teóricos, metodológicos, revisões de literatura, ensaios e documentos técnicos.

No fichamento completo, a densidade mínima é de 2 mil palavras quando o material comportar esse nível de detalhe sem repetição artificial.

## Arquivo principal

- [`SKILL.md`](SKILL.md) — protocolo completo, versão 3.0.0.

## Instalação

Copie esta pasta para o diretório de skills do seu agente, preservando `SKILL.md` na raiz da skill.

Exemplo:

```text
.agents/skills/fichamento-academico/SKILL.md
```

## Uso

```text
Use a skill fichamento-academico para produzir um fichamento completo e rastreável deste texto.
```

É possível pedir apenas partes do protocolo, como mapa do argumento, conceitos, citações, método ou crítica interna.

## Limites

A skill não autoriza completar metadados, páginas, referências, citações, métodos ou resultados por suposição. Quando o documento não sustentar uma informação, o fichamento deve registrar a ausência, incerteza ou impossibilidade de verificação.

## Citação

> Sampaio, Rafael Cardoso. *Fichamento Acadêmico*. Skill para agentes de IA. Versão 3.0.0. 2026.

Licença MIT conforme o arquivo [`LICENSE`](../../LICENSE) da raiz do repositório.
