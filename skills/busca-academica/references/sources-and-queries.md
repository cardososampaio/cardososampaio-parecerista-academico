# Fontes e consultas

## Ordem de recuperação

Usar OpenAlex, SciELO e DOAJ primeiro. Em seguida, usar Crossref e Semantic Scholar para buscas complementares, referências, citações e conferência. Pesquisar todas as fontes previstas ou registrar individualmente seus impedimentos. Não anunciar busca direta em SciELO quando só foram recuperados registros SciELO pelo OpenAlex.

Não aplicar `is_oa` como critério padrão de inclusão bibliográfica. Prioridade de acesso aberto significa procurar versões abertas e dar atenção às fontes abertas. Um artigo pertinente pode entrar no corpus mesmo sem PDF acessível, com sua condição de leitura identificada.

## OpenAlex

- Base de consulta `https://api.openalex.org/works`.
- Usar `search`, paginação por `cursor` e `per_page` até 100 no adaptador. Não selecionar campos opcionais rígidos no pedido, para evitar falhas quando a API mudar seu esquema.
- A documentação consultada em outubro de 2026 informa consultas básicas sem chave e chave gratuita que amplia a cota. Ler novamente autenticação e custos em buscas grandes. Não depender de um número de chamadas por dia gravado nesta skill.
- Configurar `OPENALEX_API_KEY` se já houver uma chave autorizada. Enviar por cabeçalho e não expor seu valor em logs, planos ou exportações.
- Preservar `abstract_inverted_index`, reconstruir o resumo completo e conservar a resposta original.
- Usar `from_publication_date` e `to_publication_date` para datas. Aplicar afiliação brasileira apenas se o usuário pedir esse recorte específico, via `affiliation_country` no plano. País da afiliação não corresponde a país estudado.
- A consulta ampla pode encontrar textos além do título ou resumo. Registrar o alcance do campo. Para maior controle, verificar os parâmetros atuais de busca por título e resumo na documentação.
- Usar `AND`, `OR`, `NOT` e frases entre aspas conforme documentação. Quebrar consultas muito longas em conjuntos e unir resultados, mantendo a equivalência lógica e o registro das partes.
- Ordem padrão de resultados de busca não é garantia de seleção completa. O teto por consulta limita a coleta e fica registrado.

Documentação oficial

- https://help.openalex.org/api/
- https://help.openalex.org/api/authentication/
- https://help.openalex.org/api/searching/

## SciELO

- A busca temática usa `https://search.scielo.org/`, com `q`, `count`, `from`, `lang` de interface e `output=site`.
- Não confundir idioma da interface com idioma do artigo. O adaptador não aplica idioma do corpus pelo parâmetro `lang`.
- O portal pode devolver um desafio de segurança com HTTP 200. Classificar como bloqueio, nunca como consulta vazia.
- Se o HTML mudar, registrar `unrecognized_scielo_layout`, buscar pelo portal com ferramentas autorizadas ou recuperar candidatos por um conector disponível. Pode completar a descoberta pelo OpenAlex e validar a presença em SciELO por páginas e registros reais, identificando essa recuperação como indireta.
- Conferir título, autores, periódico, ano, DOI, idioma e tipo na página do artigo. Metadados extraídos de resultados de busca são provisórios. Não inferir o ano a partir de uma data mencionada no título.
- O projeto ArticleMeta fornece cliente para metadados. Sua utilização e disponibilidade precisam ser verificadas. Não apresentá-lo como API de busca temática equivalente ao portal e não citar integração como executada apenas porque há uma URL na documentação.
- A presença em SciELO não torna todos os documentos artigos de pesquisa. Verificar editoriais, resenhas, cartas e outros tipos durante a triagem.
- O pacote R easyScieloPack oferece busca e filtros no mesmo portal. Usá-lo como alternativa opcional quando disponível, conforme `easyscielopack.md`. O adaptador Python reconhece também o total em `#TotalHits`, autores individuais e resumos ligados ao ID do resultado. Essas formas foram conferidas no código publicado no CRAN, sem copiar o pacote para esta skill.

Rotas oficiais

- https://search.scielo.org/
- https://www.scielo.br/
- https://github.com/scieloorg/articlemetaapi

## DOAJ

- A busca de artigos usa `https://doaj.org/api/search/articles/{query}`. Codificar a consulta para URL e registrar a string original.
- Usar tamanho de página constante durante a paginação. O número de página combinado com tamanhos variáveis repete ou perde registros.
- O DOAJ recebe metadados de artigos dos periódicos. Um periódico indexado pode não ter todos os artigos depositados. Não usar a cobertura do diretório como sinônimo de exaustividade.
- Aplicar consultas específicas por `title`, `abstract`, `doi` e ISSN conforme o esquema atual.
- Não copiar automaticamente idiomas do periódico para o artigo quando o periódico for multilíngue. Manter idioma não verificado até consultar o documento.
- O adaptador opera a busca pública. Serviços premium de metadados e APIs de escrita são funções distintas e não são necessários ao fluxo padrão.

Documentação e implementação oficial

- https://doaj.org/docs/api/
- https://doaj.org/docs/faq/
- https://github.com/DOAJ/doaj/tree/master/portality/templates-v2/public/api/v4

## Crossref

- Usar `https://api.crossref.org/works` para recuperação adicional e `/works/{doi}` para conferir registros individuais.
- Não exigir chave no uso básico. Se houver contato autorizado, configurar `CROSSREF_EMAIL` para identificação do cliente.
- `query` é busca textual, não um compilador de lógica booleana. Formular consultas curtas por conceitos e combinar resultados localmente. Não copiar a sintaxe de outra base esperando conjuntos equivalentes.
- Preservar título, autoria estruturada, datas de publicação impressa e online, DOI, veículo, ISBN/ISSN, volume, número, páginas, editores quando presentes, licenças e atualizações.
- Data de depósito não é data de publicação. Diferença de um ano pode corresponder a versões, mas exige análise e registro.
- Links de texto ou PDF retornados pelo Crossref não demonstram acesso aberto ou autorização para baixar.
- Ausência de resumo ou DOI não demonstra falta de qualidade. Não existe obrigação de toda produção acadêmica estar no Crossref.
- A consulta individual do script compara títulos e anos e aponta divergências. A autoria, a versão e a sustentação das afirmações ainda precisam ser verificadas pelo agente.

Documentação oficial

- https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- https://api.crossref.org/

## Semantic Scholar

- Usar o endpoint de busca em lote `https://api.semanticscholar.org/graph/v1/paper/search/bulk` para coleta paginada por token.
- Distinguir busca por relevância de busca em lote. Seus parâmetros e lógica textual são diferentes.
- Na busca em lote, usar a sintaxe documentada, incluindo `+` para conjunção, `|` para alternativas, `-` para exclusão e frases entre aspas quando suportadas. Não copiar operadores `AND/OR` indiscriminadamente.
- Configurar `S2_API_KEY` se disponível. Acesso sem chave pode sofrer limite compartilhado ou bloqueio. Registrar HTTP 429 e aplicar espera limitada, sem repetir indefinidamente.
- Resultados de recomendações ou citações podem ampliar a descoberta. Registrar documento semente e rota de recuperação.
- Ausência de `publicationTypes` deixa o tipo não verificado. Não assumir que todo registro seja um artigo de periódico.
- Uma URL `openAccessPdf` é candidata a recuperação posterior. Verificar o conteúdo após download autorizado.

Documentação oficial

- https://api.semanticscholar.org/api-docs/
- https://api.semanticscholar.org/api-docs/snippets
- https://www.semanticscholar.org/product/api

## Google Scholar e busca suplementar

Usar Scholar como complemento assistido, especialmente para versões, citações e documentos difíceis de localizar. Não depender de coleta em massa não verificada. Não contornar CAPTCHA. Uma busca web genérica com `site:scholar.google.com` não demonstra que o Scholar tenha sido pesquisado diretamente. Registrar a modalidade efetivamente utilizada.

Aceitar referências de congressos e capítulos apenas quando sua indexação em uma base acadêmica puder ser identificada. A busca web pode ajudar a encontrar o texto ou conferir a referência depois dessa identificação.

## Planejamento multilíngue

Construir blocos por conceito, usando a terminologia das áreas e da produção brasileira. Executar consultas distintas em português e inglês quando esses idiomas fizerem parte do escopo. Guardar todos os termos e alterações. Usar espanhol e outros idiomas conforme o recorte.

Uma consulta por expressão inglesa não equivale a filtrar o idioma dos documentos. Seleção por idioma deve ser conferida nos metadados ou no texto, com pendências identificadas.

Antes de encerrar, verificar se documentos conhecidos ou documentos-semente pertinentes foram recuperados. Essa verificação avalia a sensibilidade do plano, sem usar a existência de uma semente como garantia de cobertura.
