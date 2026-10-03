# Execução e arquivos

## Recursos necessários

Usar Python 3.10 ou superior para os scripts. As buscas, exportações, gráficos SVG, auditoria e testes não exigem bibliotecas externas. `pypdf` é opcional para validar a estrutura dos PDFs. Sem ele, o script verifica assinatura e término do arquivo e registra essa validação limitada.

Não executar instaladores nem instalar a skill como parte de uma busca. Os scripts são portáveis e funcionam por caminhos absolutos a partir da pasta já disponibilizada no ambiente.

## Preparar o plano

Copiar `assets/search-plan.json` para a pasta da pesquisa. Substituir pergunta, recortes, conceitos e consultas. Não usar seus termos de exemplo como se fossem o tema do usuário.

`config.types` aceita `article`, `review`, `conference-paper`, `book-chapter` e tipos explicitamente pedidos. Artigos e revisões são o padrão. `config.languages` contém códigos de idioma, enquanto o idioma anotado em cada consulta descreve a formulação, sem filtrar automaticamente os documentos.

`max_per_query` é um teto de recuperação por combinação fonte e consulta. O padrão simples é 60 e o aprofundado 200. Ajustar ao tamanho do tema, cobertura e limites das bases. Sempre informar truncamento. Isso não é um número obrigatório de referências na revisão.

Variáveis opcionais de acesso

```text
OPENALEX_API_KEY
CROSSREF_EMAIL
S2_API_KEY
UNPAYWALL_EMAIL
```

Não inventar contato pessoal, copiar chaves para os arquivos nem pedir chaves que não sejam necessárias. Não ativar custos pagos para executar o plano.

## Comandos

```bash
python scripts/academic_search.py search --plan plano_busca.json --out resultados
python scripts/academic_search.py search --plan plano_busca.json --out resultados --resume
python scripts/academic_search.py search --query "democracia digital" --languages pt,en --year-start 2020 --year-end 2026 --out piloto
python scripts/academic_search.py doctor --out diagnostico
```

O atalho `--query` usa a mesma expressão textual nas bases e serve a pilotos simples. Para booleanos, sinônimos e busca aprofundada, usar consultas próprias por fonte no plano.

Saída 0 significa conclusão das operações programáticas, sem garantir leitura ou exaustividade. Saída 2 significa que ao menos uma busca falhou ou foi parcial, com preservação das exportações. Saída 1 significa erro de configuração ou execução. Não ignorar o manifesto quando a saída for 0, pois pode haver truncamento pelo teto.

O diagnóstico executa uma consulta pequena em cada base e testa acesso e forma da resposta. Ele não substitui a busca temática nem demonstra qualidade da recuperação. BDTD só é testada com `--bdtd`, após o pedido explícito.

## Importar e consolidar

```bash
python scripts/academic_search.py import --input registros.json --source consensus --format canonical --coverage partial --languages pt,en --out importados
python scripts/academic_search.py import --input resposta_openalex.json --source openalex --format openalex --out importados_oa
python scripts/academic_search.py import --input scielo_r.csv --source scielo --format easy_scielo_pack --coverage partial --config plano_busca.json --out importados_scielo
python scripts/academic_search.py merge --inputs resultados/registros.json importados/registros.json --config plano_busca.json --out consolidado
python scripts/academic_search.py enrich --input consolidado/registros.json --out enriquecido --style apa
```

Aceitar listas JSON, envelopes de respostas suportadas e CSV exportado por esta skill. Para importação de resultados nativos, selecionar `openalex`, `crossref`, `doaj` ou `semantic_scholar`. Para conectores, navegação e SciELO assistida, converter os resultados reais ao esquema canônico.

Para o CSV de cinco colunas produzido por easyScieloPack, usar `easy_scielo_pack`. Tipo documental, idioma integral e veículo ficam pendentes até conferência. O manifesto identifica o formato e a entrada, e os metadados conservam os campos importados.

A consolidação mantém a procedência dos registros. Preservar também os manifestos das execuções originais, porque cada um contém consultas e cobertura. O manifesto de consolidação não transforma uma coleta parcial em completa.

O enriquecimento consulta DOI no Crossref, completa campos ausentes e registra conflitos. Ele não verifica a sustentação de afirmações, nem considera DOI fora do Crossref inexistente. Conferir autores e versões antes de promover o estado de verificação.

`--config` aceita um objeto de configuração ou um plano contendo `config`, nos comandos de importação, consolidação e enriquecimento. O enriquecimento preserva o manifesto original encontrado ao lado da entrada e o recorte do plano. Para registros vindos de uma consolidação ou de outro diretório, passar `--config plano_busca.json` explicitamente.

## Anotar o corpus

Editar uma cópia de `registros.json`, preservando IDs, referências e procedência. Preencher `selection`, `study_kind`, `themes`, `reading_level`, `method`, `main_finding`, `supports`, `contradicts`, `limitations` e `locator` somente com base no material recuperado.

Reexportar o corpus anotado em uma pasta final, mantendo os manifestos originais como anexos.

```bash
python scripts/academic_search.py merge --inputs corpus_anotado.json --config plano_busca.json --out entrega
python scripts/visualize_corpus.py --input entrega/registros.json --population included --out entrega/figuras
python scripts/audit_delivery.py --directory entrega --report entrega/relatorio.md --mode deep
```

Não alterar o estado para `full_text` apenas porque existe uma URL ou porque um PDF foi baixado. Registrar quais partes foram efetivamente examinadas.

## Arquivos produzidos

| Arquivo | Função |
|---|---|
| `referencias.csv` | Todos os registros, metadados, seleção, URLs e procedência |
| `referencias.bib` | Referências completas disponíveis em BibTeX, com chaves estáveis |
| `registros.json` | Registros estruturados e metadados originais por fonte |
| `referencias.csl.json` | Dados para processamento bibliográfico por CSL |
| `bibliografia_completa.md` | Lista completa preliminar para conferência de estilo |
| `matriz_evidencias.csv` | Campos de extração, decisões e leitura |
| `manifesto_busca.json` | Consultas, limites, contagens e falhas |
| `pendencias_metadados.json` | Campos ausentes e divergências |
| `duplicatas_provaveis.json` | Pares que exigem conferência |
| `raw/` | Respostas originais e estados HTTP |
| `checkpoint.json` | Estado de consultas para retomada |
| `figuras/` | SVGs, dados CSV e manifesto das figuras |
| `auditoria_entrega.json` | Verificações estruturais e pendências |

Escrever a revisão final em `relatorio.md`. Pode criar DOCX ou PDF se solicitado e se houver ferramentas adequadas, preservando o conteúdo e verificando a apresentação. Não apresentar o modelo ou o texto preliminar de referências como entrega concluída.

## Conferir a entrega

A auditoria compara registros, CSV, BibTeX, CSL, bibliografia e estrutura do relatório. No modo aprofundado, conta o texto entre marcadores `narrative`, verifica resumo executivo, tabela resumo, IDs do top 20 e arquivos de figuras. Os marcadores são comentários invisíveis em Markdown e estão nos modelos.

As figuras omitem a linha quando só existe um ano verificado. Para séries com mais de 70 anos ou mapas de calor com dimensões excessivas, o manifesto registra o limite. Agregar por década ou reduzir categorias a partir dos mesmos dados quando isso fizer sentido, sem ocultar os registros originais.

Conferir manualmente pertinência, apoio das afirmações, classificações temáticas e estilo das referências. O script não avalia a validade das conclusões científicas.

Para diagnóstico de investigação insuficiente, usar `--insufficient-reason` com o impedimento concreto. Essa opção registra a entrega como incompleta e flexibiliza apenas o comprimento e o tamanho do corpus, sem dispensar consistência das exportações. Não usá-la para evitar uma análise executável.

## PDFs após aceite

```bash
python scripts/academic_search.py download --input entrega/registros.json --out entrega/pdfs --approved --maximum 20
```

Passar `--approved` somente depois da aceitação do usuário. Para baixar apenas documentos destacados, preparar uma lista com esses registros e usá-la como entrada. O script tenta URLs de PDFs recuperadas e, se houver contato configurado, Unpaywall. Ele não contorna páginas bloqueadas, não lê o conteúdo para análise e não executa Content APIs pagas.

Se não houver URL direta, usar ferramentas autorizadas para procurar versões abertas e atualizar a lista de candidatos. Sempre validar o arquivo, registrar falhas e respeitar o escopo autorizado. Um arquivo com HTML não conta como PDF.

## Testes

```bash
python -m unittest discover -s tests -v
python scripts/academic_search.py doctor --out teste_acesso
```

Os testes unitários usam exemplos declaradamente sintéticos e não realizam buscas online. O diagnóstico é um teste real pequeno de acesso e esquema. Seus estados dependem da rede, das bases e das credenciais no momento de execução.
