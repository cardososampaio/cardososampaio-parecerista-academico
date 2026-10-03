# Escrita Acadêmica

Skill em português para planejar, redigir, corrigir, revisar, reescrever, reestruturar, condensar, expandir, traduzir e auditar textos acadêmicos em Humanidades e Ciências Sociais.

## O que faz

A skill foi desenhada para tarefas que vão de uma frase ou seção isolada a manuscritos completos. Ela distingue o grau de intervenção editorial da base de trabalho disponível e procura usar o menor nível de alteração suficiente para cumprir o pedido.

O núcleo preserva argumento, dados, citações, conceitos, qualificadores e voz autoral. Os módulos auxiliares acrescentam protocolos específicos para argumentação, gêneros e seções, integridade de fontes, revisão de literatura, pesquisa qualitativa, pesquisa quantitativa, teoria e história, prosa e estilo, tradução, internacionalização, textos longos e auditoria final.

A skill não impõe IMRaD, hipóteses, saturação, acordo entre codificadores ou outros critérios incompatíveis com o desenho do trabalho. Pesquisa externa, múltiplos agentes e ferramentas auxiliares não são exigidos por padrão.

## Estrutura

- [`SKILL.md`](SKILL.md) contém o protocolo principal e o roteamento entre módulos.
- [`references/`](references/) contém módulos especializados carregados conforme a tarefa.
- [`assets/modelos.md`](assets/modelos.md) reúne modelos de apoio.
- [`assets/casos-avaliacao.json`](assets/casos-avaliacao.json) contém casos para avaliação comportamental.
- [`scripts/check_package.py`](scripts/check_package.py) verifica estrutura, links e regressões determinísticas.
- [`scripts/compare_text.py`](scripts/compare_text.py) auxilia a detectar alterações em números, citações e fragmentos protegidos.
- [`agents/openai.yaml`](agents/openai.yaml) fornece metadados de interface para ambientes compatíveis.

## Instalação

Copie a pasta inteira para o diretório de skills do agente. Não copie apenas o `SKILL.md`, porque o protocolo referencia módulos, assets e scripts do próprio pacote.

Exemplo

```text
.agents/skills/escritaacademica/
```

O mecanismo exato de descoberta depende do agente utilizado.

## Uso

```text
Use $escritaacademica para revisar este artigo preservando argumento, dados, citações e voz autoral.
```

Também é possível pedir operações delimitadas, como correção de um parágrafo, reestruturação de uma seção, tradução acadêmica, revisão para leitores internacionais ou auditoria de um manuscrito completo.

## Verificação do pacote

O pacote inclui testes locais sem dependências externas. A partir da raiz da skill

```bash
python scripts/check_package.py --root . --self-test
```

O verificador cobre integridade estrutural, referências internas e regressões do comparador textual. Ele não substitui validação científica ou semântica do conteúdo produzido pelo agente.

## Limites

A skill não autoriza inventar dados, referências, páginas, citações, procedimentos, resultados, documentos ou regras editoriais. Quando uma afirmação externa exige verificação e a tarefa não autoriza ou não permite pesquisa, o limite deve permanecer visível.

## Citação

> Sampaio, Rafael Cardoso. *Escrita Acadêmica*. Skill para agentes de IA. Versão 1.0.0. 2026.

Licença MIT conforme o arquivo LICENSE da raiz do repositório.
