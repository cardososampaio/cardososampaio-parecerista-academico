# SciELO com easyScieloPack

## Quando usar

Considerar o pacote como uma rota opcional se R e easyScieloPack já estiverem disponíveis no ambiente. A busca central continua funcionando com Python, conectores ou pesquisa assistida. Não instalar a skill ou dependências automaticamente para tentar essa rota.

O manual e o código da versão CRAN 0.1.1 foram consultados em outubro de 2026. A função pública é `easyScieloPack::search_scielo`. Conferir a versão instalada antes de executar. Há exemplos antigos no README com o nome `easyScieloPak`, que difere do nome publicado no CRAN.

## O que ela acrescenta

Fornece consultas temáticas, paginação e filtros por período, coleção, periódico, idioma e categoria. Na versão consultada, os filtros aceitam um valor por categoria. Para português e inglês, executar consultas separadas e deduplicar seus resultados.

`lang` identifica a interface. `languages` filtra o idioma. `collections="bra"` seleciona a coleção brasileira, sem demonstrar afiliação brasileira ou que o estudo investigue o Brasil. Usar essa coleção em uma consulta adicional de prioridade brasileira, preservando a busca internacional acordada.

Os dois anos devem ser fornecidos juntos. Definir `n_max` explicitamente em vez de depender da recuperação automática de todos os resultados. Registrar o teto como possível truncamento.

## Limites observados na implementação

O pacote faz scraping de `search.scielo.org`. Não é uma API independente, oficial ou um meio garantido de acesso. Pode continuar recebendo HTTP 403 ou uma página de desafio. Não insistir em redes alternativas ou técnicas de contorno de CAPTCHA.

O extrator da versão consultada devolve cinco colunas, `title`, `authors`, `year`, `doi` e `abstract`. Não recupera por si só todos os campos de uma referência, nem uma URL canônica de artigo quando falta DOI. O resumo pode estar em idioma diferente do texto. Conferir periódico, tipo, idioma e URL na página canônica ou em outra base.

A função pode devolver resultados parciais, ou um data.frame vazio, depois de avisos de falha. Não converter esse retorno isolado em busca completa com zero resultados. Guardar avisos, erros, consultas, versão e teto. Verificar a resposta e a cobertura antes de usar `--coverage complete`.

## Exemplo operacional

Executar primeiro um piloto pequeno. Substituir a consulta e os recortes por aqueles definidos para a pesquisa.

```r
if (!requireNamespace("easyScieloPack", quietly = TRUE)) {
  stop("easyScieloPack não está disponível neste ambiente")
}
avisos <- character()
resultado <- withCallingHandlers(
  easyScieloPack::search_scielo(
    query = "democracia digital",
    lang = "pt",
    languages = "pt",
    n_max = 15,
    year_start = 2020,
    year_end = 2026
  ),
  warning = function(w) {
    avisos <<- c(avisos, conditionMessage(w))
  }
)
write.csv(resultado, "scielo_r.csv", row.names = FALSE,
          fileEncoding = "UTF-8", na = "")
writeLines(c(paste("Versão", packageVersion("easyScieloPack")), avisos),
           "avisos_scielo.txt", useBytes = TRUE)
```

Acrescentar `collections="bra"` somente se esse filtro fizer parte da consulta adicional. Repetir com termos em inglês e `languages="en"` quando aplicável. Não usar o mesmo nome de saída para consultas diferentes.

```bash
python scripts/academic_search.py import --input scielo_r.csv --source scielo --format easy_scielo_pack --coverage partial --config plano_busca.json --out scielo_importado
python scripts/academic_search.py merge --inputs resultados/registros.json scielo_importado/registros.json --config plano_busca.json --out consolidado
```

A importação preserva os cinco campos e a procedência. Usa o DOI como URL de resolução quando disponível, sem afirmar que ele foi verificado. Mantém tipo e idioma como desconhecidos. Resolver as pendências antes da seleção final. Guardar também o CSV de entrada e os avisos como anexos da pesquisa.

## Estado de validação

O adaptador de importação e os seletores correspondentes no Python têm testes de regressão. A execução do pacote R não foi validada no ambiente de criação, onde R não estava disponível. Verificar acesso no ambiente de uso e documentar seu resultado, sem apresentar a inspeção do código como teste online bem-sucedido.

## Fontes primárias

- https://CRAN.R-project.org/package=easyScieloPack
- https://cran.r-project.org/web/packages/easyScieloPack/refman/easyScieloPack.html
- https://cran.r-project.org/src/contrib/easyScieloPack_0.1.1.tar.gz
- https://github.com/Programa-ISA/easyScieloPack

O pacote externo mantém sua própria licença e autoria. Esta skill não redistribui seu código ou suas dependências.
