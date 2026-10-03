# BDTD mediante pedido explícito

## Escolher a busca

Consultar BDTD somente quando o usuário pedir teses, dissertações ou a base pelo nome. O pedido de valorizar pesquisa brasileira não autoriza incluir automaticamente essa produção.

Definir período de defesa, idiomas, tema, área e tipo de trabalho. Incluir `thesis` em `config.types` e ativar `bdtd_requested=true` no plano. Preservar os demais tipos quando o usuário quiser artigos e teses juntos.

## Rota preferencial

1. Usar o portal de busca BDTD e sua busca avançada. Formar consultas por termos em português, variantes e, quando necessário, inglês. Não aplicar toda a busca apenas ao título quando a pergunta exigir conceitos presentes no resumo.
2. Consultar filtros efetivamente disponíveis na interface. Guardar a consulta, filtros, data e quantidade recuperada. Não inventar parâmetros de áreas ou instituições.
3. Seguir os registros até o repositório da instituição. Conferir autoria, título, orientador, instituição, programa, grau, data de defesa, resumo, palavras-chave e identificador persistente.
4. Distinguir ano de defesa, data de depósito e atualização do registro. A data de um feed pode corresponder à indexação.
5. Exportar todos os registros encontrados, com seleção e procedência. Não presumir que um link de registro seja um PDF.

## Rota programática contingente

O adaptador incluído tenta a interface RSS do VuFind com `lookfor`, `type=AllFields`, `view=rss`, `page` e tamanho de página constante. Essa interface pode ser desativada, alterar formato ou retornar bloqueio de segurança. O script identifica XML inválido ou página de desafio como falha, não como consulta vazia.

Não anunciar esta rota como validada universalmente. Executar `doctor --bdtd` somente se a base já tiver sido solicitada. Se a rota falhar, usar pesquisa assistida no portal e importação de metadados efetivamente recuperados.

## OAI-PMH

A interface publicada pela BDTD utiliza o servidor `https://bdtd.ibict.br/vufind/OAI/Server`.

Verificar disponibilidade com `Identify` e formatos com `ListMetadataFormats`. Quando já houver identificador, `GetRecord` pode recuperar um registro. `ListRecords` permite colheita por datas de atualização e conjuntos, com `resumptionToken` quando necessário.

OAI-PMH não fornece busca temática arbitrária por palavras-chave. Datas de colheita não equivalem a período de defesa. Não baixar o catálogo inteiro para responder a uma pergunta delimitada. Para coleta ampla, definir um plano específico, limites e identificação das condições de cobertura.

## Referência e PDF

Confirmar dissertação ou tese e o grau antes de escolher a entrada BibTeX. Sem confirmação, usar entrada genérica e registrar a pendência, em vez de inventar doutorado. Recuperar PDF apenas após a oferta e aceite aplicáveis a todo o fluxo.

Fontes oficiais

- https://bdtd.ibict.br/
- https://bdtd.ibict.br/vufind/Search/Home
- https://bdtd.ibict.br/vufind/oai
- https://bdtd.ibict.br/vufind/faq/home
