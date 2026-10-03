# MCPs, plugins e conectores

## Descobrir capacidades

Inspecionar o catálogo de ferramentas ou usar a ferramenta de descoberta do ambiente. Procurar serviços acadêmicos e as operações disponíveis, incluindo Consensus, Scite, SciSpace, OpenAlex, Semantic Scholar e Zotero. Não inferir acesso por nomes mencionados pelo usuário ou por exemplos desta skill.

Não imprimir credenciais nem o catálogo inteiro. Registrar apenas as integrações pertinentes e seus estados de acesso. Se uma integração estiver exposta e servir ao pedido, executar ao menos uma operação pertinente, em vez de apenas recomendá-la.

## Atribuir tarefas

| Serviço disponível | Uso preferencial | Conferência posterior |
|---|---|---|
| Consensus ou serviço de busca por pergunta | Descobrir estudos adicionais e testar formulações da pergunta | Documento original, tipo de estudo e correspondência da referência |
| Scite ou serviço de contexto de citações | Recuperar contextos de apoio, oposição ou menção em estudos citantes | Trecho citante, desenho do estudo e limite da classificação automática |
| SciSpace ou serviço de leitura acadêmica | Obter metadados, localizar texto e consultar passagens | Texto realmente acessível, localização e versão |
| Conector oficial de base | Executar consultas e recuperar registros | Cobertura do endpoint, paginação e campos retornados |
| Zotero | Importação, referência, leitura e exportação quando autorizado | Metadados importados e duplicatas |

Não tratar a classificação de uma citação como avaliação automática da validade de um estudo. Não transformar a síntese de um serviço em evidência primária. Usar serviços de leitura apenas para documentos realmente recuperados.

## Preservar procedência

Converter cada resultado bibliográfico para o formato de `assets/record-example.json`, substituindo integralmente seu conteúdo de exemplo. Preencher `sources`, `source_ids` e `provenance` com serviço, consulta, data, URL do registro e modalidade de recuperação. Conservar a resposta original quando o ambiente permitir.

Utilizar a rota de importação dos scripts e depois consolidar com as outras bases. Exportar registros suficientes para identificar título, autoria, ano, veículo e URL. Um texto de resposta sem referências identificáveis não pode gerar entradas bibliográficas por suposição.

Registrar limites de cobertura e acesso. Não somar respostas de serviços sobrepostos como se fossem estudos diferentes. Não classificar todos os resultados de um serviço como brasileiros com base no idioma da pergunta.

## Comportamento em falhas

Se uma ferramenta exigir autenticação inexistente ou não responder, registrar o impedimento e continuar com fontes acessíveis. Não contratar serviços ou pedir autorização para instalar plugins como condição para concluir uma busca já executável.

Se o usuário quiser configurar uma integração ausente, tratar isso como tarefa separada. Seguir as regras do ambiente para qualquer operação externa. Esta skill autoriza pesquisa e processamento bibliográfico, sem envio de mensagens, compartilhamento de bibliotecas, alteração de coleções pessoais ou ativação de custos não solicitados.
