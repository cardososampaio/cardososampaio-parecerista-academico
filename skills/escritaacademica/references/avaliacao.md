# Avaliação e manutenção da skill

Usar este recurso ao desenvolver, alterar ou testar a skill. Não aplicá-lo como formulário obrigatório ao usuário final.

## Validar o pacote

Executar `python3 scripts/check_package.py --self-test` a partir da pasta da skill. O programa usa somente a biblioteca padrão, confere arquivos, frontmatter, links internos, esquema dos casos e comportamento determinístico do comparador. Não mede a qualidade da escrita produzida pelo modelo.

Validar metadados da plataforma quando houver ferramenta específica. A skill textual não depende dela em uso normal.

## Ensaiar comportamento

Usar pedidos e materiais em `assets/casos-avaliacao.json`. Apresentar ao executor somente pedido, material e a skill. Não fornecer os critérios esperados ou conclusões prévias. Avaliar a saída usando critérios do caso depois da execução.

Testar operações diferentes, correção, redação, desenvolvimento, condensação, reestruturação, tradução, projeto, teoria, método, fontes e internacionalização. Não exigir execução de todos os casos a cada correção de baixa consequência.

Uma passagem independente pode revelar problemas que a autoavaliação não encontra. Usar somente quando a complexidade ou alteração justificar. Isso é avaliação da skill, não um requisito de múltiplos agentes no procedimento de escrita.

## Julgar resultados observáveis

Verificar se houve produto real, fidelidade, adequação ao gênero, uso pertinente de materiais e cumprimento de formato ou extensão. Usar critérios concretos.

- Citação protegida permanece literal em edição.
- Associação, relato e possibilidade conservam estatuto.
- Notas se tornam argumento sem ganhar origem empírica inventada.
- Condensação mantém ressalva e contraevidência materiais.
- Projeto não simula pesquisa realizada.
- Tradução conserva negação, escopo, atribuição e conceito.
- Conflito não é normalizado sem base.
- Ausência de fonte não gera referência plausível.
- Preparação internacional não inventa método ou contribuição.
- Texto solicitado é efetivamente escrito, sem substituição por conselho.

Não exigir frase idêntica a uma resposta de referência quando várias formulações são fiéis. Distinguir falha material de preferência estilística. Não usar comprimento variável ou presença de uma palavra como indicador isolado de qualidade.

## Tratar falhas

Registrar pedido, saída e trecho problemático. Identificar a regra insuficiente ou contraditória. Corrigir a instrução no recurso canônico, evitando duplicá-la por todo o pacote. Repetir o caso afetado e um caso diferente que possa revelar regressão.

Não afirmar que comportamento foi testado porque os casos existem. Não afirmar que um script verificou semântica. Não afirmar completude universal a partir de ensaios curtos.

## Manter economia e portabilidade

Conferir se cada recurso resolve decisão não atendida pelo núcleo. Não acrescentar dependências, APIs ou agente especializado obrigatório apenas porque estão disponíveis. Conservar caminho textual para uso sem ferramentas. Atualizar links e metadados ao reorganizar arquivos.

O pacote deve continuar sendo uma única skill instalável a partir de sua pasta. Instruções, recursos e scripts usam caminhos relativos. Não incluir caminhos da máquina de desenvolvimento, chaves, logs com material confidencial ou saídas temporárias.
