# Revisão aprofundada

## Perguntas antes da execução

Solicitar informações apenas quando sua ausência altera a investigação. Obter ou confirmar pergunta, período, região ou perspectiva internacional, idiomas, áreas, tipos documentais e preferência entre artigos empíricos, teóricos ou ambos. Perguntar também sobre exclusões que o usuário considere relevantes.

Não impor PICO a uma pergunta teórica ou interpretativa. Usar PCC, SPIDER ou uma formulação conceitual quando fizer sentido, sem exigir rótulos metodológicos para iniciar uma busca bem delimitada.

## Planejar e executar

Registrar a pergunta no plano. Formular consultas por conceitos e idioma, adaptar à base e fazer piloto. Conservar versão inicial, mudanças e justificativas. Repetir consulta alterada apenas quando a mudança puder recuperar outra literatura ou corrigir um problema demonstrado.

Não iniciar por nomes de autores apenas porque o agente os conhece. Usar autores e documentos-semente identificados na busca ou fornecidos pelo usuário para ampliar recuperação e acompanhar referências.

O plano padrão permite artigos e revisões. Quando forem solicitados papers de congressos ou capítulos, acrescentar `conference-paper` ou `book-chapter`. A mudança vale para coleta, triagem, relatório e referências.

## Redigir o relatório

Escrever de 2.000 a 5.000 palavras analíticas, incluindo resumo executivo. A contagem exclui bibliografia, tabelas e anexos técnicos. Aproximar-se de 2.000 em perguntas delimitadas com corpus menor, e de 5.000 em perguntas complexas com debates e métodos diversificados.

Começar pelo resumo executivo. Identificar a pergunta, as conclusões permitidas, o tamanho do corpus, a participação brasileira, o nível de leitura e os limites. Uma página é uma aproximação editorial. Usar normalmente 350 a 600 palavras, adaptando à formatação solicitada.

Incluir tabela resumo com registros recuperados, únicos, incluídos, pendentes e textos consultados. Não inventar contagens de triagem para preencher uma tabela. Calcular a tabela diretamente dos registros anotados e do manifesto.

Construir top 20 por pertinência ao problema, consistência do estudo, cobertura de posições e função na revisão. Priorizar artigos. Registrar ID, referência, URL, justificativa, tipo de estudo e nível de leitura. Quando o corpus tiver menos de 20 documentos pertinentes, listar todos os adequados e explicar a quantidade.

O estado da arte deve comparar estudos e argumentos. Não redigir apenas uma sequência de resumos. Diferenciar contextos brasileiros e internacionais, conceitos, desenhos, evidências, divergências e condições de aplicação.

Apresentar interpretações iniciais e tendências com linguagem proporcional à leitura. Identificar inferências do agente e hipóteses de aprofundamento. Não atribuir causalidade ao crescimento bibliográfico.

## Visualizações

Utilizar `visualize_corpus.py` após anotar o corpus. O padrão de população é `included`. Para uma exploração inicial, escolher `candidates` explicitamente e nomear essa população nas legendas. `all` inclui registros fora de escopo e serve a diagnóstico, não à descrição da literatura analisada.

- Barras por ano mostram contagens discretas.
- Linhas ajudam a comparar evolução quando há vários períodos.
- Mapas de calor podem cruzar fontes e anos, ou temas atribuídos na leitura e anos.
- Temas dependem de classificação explícita. O script não infere categorias de pesquisa a partir de títulos.
- Categorias e fontes podem se sobrepor. Um documento pode participar de mais de uma célula sem constituir estudos diferentes.
- Tratar ano ausente e ano em curso separadamente. Não desenhar uma tendência com números inventados.

Os SVGs são figuras exatas e portáveis. Cada figura tem dados em CSV. Se o ambiente oferecer Matplotlib, R ou ferramenta equivalente, pode produzir PNG/PDF a partir desses mesmos dados, preservando contagens e legendas. Não usar geração de imagem para gráficos quantitativos.

## Bibliografia e produtos

Incluir todas as referências únicas encontradas, no estilo escolhido e com URLs. Manter a separação entre documentos usados na revisão e registros recuperados fora do escopo. Todos permanecem nas exportações, com motivos e estados.

Finalizar revisão, CSV, BibTeX, JSON, CSL JSON, matriz de evidências, figuras e dados, manifesto e pendências. O pedido de PDFs vem depois dessas entregas.

## Desenhos especiais

Quando o usuário solicitar revisão sistemática ou revisão de escopo, definir protocolo e critérios adequados, registrar decisões, avaliar limites da automação e utilizar diretrizes de relato correspondentes. Não declarar revisão sistemática apenas por pesquisar várias bases.

PRISMA-S ajuda a relatar consultas, fontes e procedimentos. PRISMA 2020 ajuda a relatar a seleção e o trabalho de revisão. Nenhum deles substitui o desenho, e não há mínimo universal de três bases aplicável a toda pergunta.

- https://www.prisma-statement.org/prisma-search
- https://www.prisma-statement.org/prisma-2020-statement

## Retomar ou encerrar

Salvar plano, registros, matriz e decisões. Retomar consultas incompletas e etapas pendentes, sem repetir buscas já concluídas no mesmo recorte. Ao mudar plano ou período, criar uma execução identificada como atualização.

Se a busca não puder sustentar o relatório, entregar diagnóstico verificável e síntese limitada. Preservar arquivos e indicar exatamente o que falta. Não apresentar essa entrega como revisão aprofundada concluída.
