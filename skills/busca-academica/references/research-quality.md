# Qualidade da pesquisa e das evidências

## Corpus e rastreabilidade

Conservar todos os registros únicos recuperados nos arquivos. Separar estados `candidate`, `included`, `outside_scope`, `needs_verification` e `excluded`. Registrar motivo para exclusões e distinguir fora de escopo documental de exclusão por conteúdo após leitura.

Campos ausentes não constituem resultados negativos. Idioma desconhecido não é outro idioma. Ano desconhecido não permite afirmar inclusão em um período. Resolver pendências quando possível e informar as restantes.

O total anunciado por uma base pode ser estimado e pode ultrapassar a coleta. Não somar totais de bases sobrepostas como um número de estudos. Teto por consulta e paginação incompleta impedem alegação de recuperação exaustiva.

## Deduplicação e versões

1. Unir registros com o mesmo DOI normalizado, conservando fontes e conflitos de metadados.
2. Não unir automaticamente DOIs diferentes, mesmo com títulos idênticos.
   Identificadores canônicos iguais dentro da mesma base permitem consolidar a mesma entrada, mas não se sobrepõem a DOIs conflitantes.
3. Sem DOI conflitante, unir apenas quando título normalizado, ano, autoria e tipo forem compatíveis.
   Sobrenome compartilhado não confirma autoria. Usar nomes completos, e não consolidar automaticamente veículos conhecidos diferentes. Abreviações e iniciais ambíguas exigem conferência.
4. Tratar similaridade textual como indicação para conferência, nunca como identidade suficiente.
5. Preservar preprint, paper de congresso e artigo ampliado como versões ou documentos relacionados quando necessário. Não apagar diferenças de conteúdo nem contar automaticamente versões como estudos independentes.

## Nível de leitura e afirmações

| Estado | O que permite |
|---|---|
| `metadata` | Identificar publicação, pertinência provável e necessidade de leitura |
| `abstract` | Relatar o que o resumo declara, com a atribuição e o limite explícitos |
| `partial_text` | Sustentar apenas afirmações localizadas nos trechos realmente consultados |
| `full_text` | Analisar o texto recuperado, identificando método, resultados e limites que foram examinados |

Não preencher metodologia pelo título ou pela área do periódico. Não presumir empirismo, teoria, método qualitativo ou amostra porque o documento usa uma palavra frequente. Não transformar resumo em leitura integral.

Para cada afirmação importante, registrar documento, nível de leitura e localização recuperável. Citação direta exige transcrição conferida. Para texto sem páginas, usar seção, subtítulo, parágrafo ou trecho pesquisável com URL.

## Robustez em humanas e sociais

Avaliar critérios adequados ao desenho. Não impor uma hierarquia universal de ensaios clínicos a pesquisas qualitativas, teóricas ou documentais.

- Estudos empíricos quantitativos. Conferir mensuração, amostragem, desenho, análise, inferência e tratamento da incerteza.
- Estudos qualitativos. Conferir adequação entre pergunta e abordagem, seleção de participantes ou documentos, percurso analítico, reflexividade, sustentação por evidências e limites contextuais.
- Estudos teóricos. Conferir definições, diálogo com a literatura, coerência argumentativa, pressupostos, objeções e alcance da proposição.
- Estudos documentais e históricos. Conferir constituição do corpus, crítica das fontes, contexto e limites de interpretação.
- Revisões. Conferir escopo, fontes, seleção, acesso aos textos, síntese e possibilidade de rastrear as conclusões.

Uma literatura pode ter muitos documentos e pouca convergência metodológica. Um tema recente pode ter poucos trabalhos de boa sustentação. Descrever essas diferenças sem criar pontuações de qualidade arbitrárias ou equiparar citação a validade.

Quando a avaliação se apoiar principalmente em resumos, classificar a robustez como preliminar e apontar quais documentos precisam de leitura integral.

## Tendências e lacunas

Distinguir crescimento de publicações recuperadas, mudança temática, mudança de método e mudança de resultados. Não inferir tendência temporal com um único ano nem queda do campo com ano em curso ou atraso de indexação.

Anotar temas após leitura e justificar a atribuição. Não usar palavras-chave de base como se fossem categorias analíticas já validadas. Uma análise de palavras-chave pode ser apresentada com esse nome e seus limites.

Formular lacunas como observações do corpus pesquisado. Expressões como nenhum estudo existe exigem evidência de cobertura muito mais forte do que ausência em consultas limitadas.

## Referências e estilo

Conferir cada referência nos metadados e na página canônica. Confirmar a correspondência entre DOI e documento, não apenas a existência do identificador. Resolver conflitos de título, autoria e data sem apagar o histórico.

Usar os dados de autoria estruturada, quando existentes. Não adivinhar sobrenomes compostos brasileiros. O BibTeX e o CSL JSON preservam nomes completos quando a fonte não oferece a divisão.

A lista produzida automaticamente pelos scripts é uma base para revisão. Para capítulos, recuperar editores, livro, páginas, editora e edição quando presentes. Para congressos, recuperar título dos anais, evento, páginas, editora e identificadores. Para ABNT, conferir os requisitos da versão e do veículo solicitado, incluindo acesso a documentos online quando aplicável. Para APA, conferir autores, datas, tipos de documento, títulos e apresentação de DOI.

Não gerar referências usando a memória do modelo. Utilizar o JSON e a resposta original para preservar campos não expostos nos modelos de exportação.
