---
tipo: entrevista
candidato: Kleriston Moreira
vaga: Analista de Dados / BI (Sênior — pode ajustar p/ Pleno conforme perfil)
entrevistador: Carlos Tadeu Lopes Filho (Instituto Experience)
data: 2026-06-03
duracao_min: 36
gravacao: https://fathom.video/share/tFyRu5Wxewdthty-DAh82wfFbMZS6PLL
case: Looker Studio (unificação Mídia/Lead/Sales)
nota_case: 6.7
nivel_case: Pleno
recomendacao: Não aprovado p/ Sênior (perfil Pleno)
fonte_nota: https://data-talent-quest.lovable.app/
tags: [entrevista, recrutamento, dados]
---
# 🎤 Entrevista — Kleriston Moreira (Data View / BI)

> Transcript bruto da entrevista (Fathom). Resumo/avaliação em seção própria abaixo.
> ⚠️ Nota do case ainda a preencher (fonte: `data-talent-quest.lovable.app`, candidato "Kleriston").

## Action items (da gravação)
- **Fix Looker Studio filter issue** (filtro de Origem não aplicava a todas as bases) — [timestamp 10:00](https://fathom.video/share/tFyRu5Wxewdthty-DAh82wfFbMZS6PLL?timestamp=599.9999)
- **Alinhar com Emília** sobre o Kleriston; Emília retorna no WhatsApp com o resultado — [timestamp 34:36](https://fathom.video/share/tFyRu5Wxewdthty-DAh82wfFbMZS6PLL?timestamp=2075.9999)

---

## 🧭 Resumo / Avaliação do candidato

> Cruzamento da **nota do case (Looker Studio)** com a **performance na entrevista**.
> Nota do case via `data-talent-quest.lovable.app` (candidato "Kleriston").

### Nota do case — **6.7 / 10 → nível Pleno**
| Critério | Nota |
|---|---:|
| Modelagem de Dados | 80 |
| Dashboard / Visualização | **90** |
| Lógica & Atribuição | 75 |
| Integridade de Dados | **40** ⚠️ |

- **Forças do case:** consolidação em *long format* com `record_type` (evita join *many-to-many*), pipeline de validação, documentação metodológica clara. Avaliado como **"o trabalho mais completo do batch"**.
- **Fraquezas críticas do case:** alterou as datas de 2025→2026 só para habilitar o filtro no Looker; exportou dados **financeiros como texto** (não numérico); deixou **37% dos registros de vendas sem atribuição de origem**.
- **Recomendação do avaliador:** **não aprovado para Sênior** — entrega de nível Pleno, apesar do potencial.

### Performance na entrevista — pontos fortes
- **Storytelling / UX forte:** organizou em 3 camadas (Executiva → Detalhada → Histórica) com lógica de funil mídia→lead→receita. Entrevistador **elogiou** a organização e a distribuição das páginas.
- **Boa filosofia de ETL:** prefere tratar a montante (Athena/BigQuery) a usar *blending* do Looker — argumenta controle do código e menor peso do dashboard. Alinhado a como o time trabalha (Athena + Looker Studio).
- **Domínio de ferramentas de viz:** Looker Studio (mais forte), Power BI, Superset, QuickSight.
- **Usa IA no fluxo:** GPT + Codex e Gemini para escopo, código (ETL em Python) e PNGs; fez o case em ~2 dias com apoio de IA. Forte aderência cultural ao viés de IA do time.
- **Case de carreira sólido:** unificou 200+ sites da Stellantis numa só propriedade GA + BigQuery → virou padrão obrigatório p/ outros fornecedores.
- **Maturidade de processo:** participa do escopo do zero, faz mockup em Miro/mind map, prioriza por impacto de negócio.

### Performance na entrevista — pontos de atenção
- **Integridade de dados** (mesma fraqueza do case): a manipulação de datas e os 37% sem origem reforçam um padrão — preocupante para uma vaga **sênior** de dados.
- **Decisões visuais custosas:** um PNG por *big number* (entrevistador apontou que pesa o Looker e dá retrabalho) + alguns desalinhamentos de layout — e *layout/design é algo que o time cobra muito*.
- **SQL "intermediário alto"** (usa CTEs) — pode ficar abaixo do esperado para sênior, a confirmar em teste técnico.
- **Cloud Code:** só começou agora, nunca usou a versão paga — o time tem expectativa alta de automação com Cloud Code.
- **API:** só consumo, nunca participou de criação.

### Conclusão (alinhada ao avaliador)
Candidato **forte em visualização/storytelling e aderente à cultura de IA**, com bom histórico — mas a **integridade de dados** (case 40/100, +37% sem atribuição, financeiro como texto) e a profundidade técnica (SQL, Cloud Code, API) **não sustentam o nível Sênior**. 
- 🔸 **Sênior:** não recomendado.
- 🔹 **Pleno:** candidato viável e provavelmente o melhor do batch — considerar oferta de Pleno (o entrevistador já sinalizou que a vaga pode virar Pleno conforme perfil, com budget ajustado).
- **Próximo passo:** alinhar com Emília o enquadramento (Pleno) e o retorno por WhatsApp.

---

## Transcript

**0:00 — Kleriston Moreira**
Estava passando por migração de cloud do GCP para AWS, aí eu acabei participando também, então eu tenho um destaque assim até bem completa, algumas mais avançadas do que as outras, mas todas as partes de utilizar dados eu já participei. Eu abri praticamente a área de onde eu estava atuando anteriormente, eu fui o primeiro BI, então eu estava num ambiente onde não tinha uma cultura realmente data-driven, as pessoas não utilizavam tanto assim dashboards, no máximo tinha alguns que era para poder apresentar dados para o cliente, e eles não eram tão confiáveis, então eu cheguei num ambiente onde eu tinha que organizar tudo do zero, e eu construí parte por parte, o primeiro foi na área de CS, construindo primeiramente visões para o cliente, conseguir gerar valor do produto para ele, e depois eu espalhei isso. Para áreas de produto, para poder começar a tomar decisões baseadas em dados, para poder melhorar o produto, para áreas de suporte dentro do CRM, criando views para eles dentro do sistema, e no negócio em geral, trazendo indicadores financeiros, indicadores gerais de saúde do cliente, indicadores gerais de performance, no caso do setor automotivo, baseado nos dados da FENABRA, viu quanto a gente participou aquele mês, em relação à venda de carros, e tudo mais. Então, eu consegui espalhar bem essa questão da visão de negócio dentro da empresa, então, foi uma oportunidade bem legal de eu evoluir, eu consegui evoluir ali para a Sênior, com o tempo a área foi crescendo, chegou mais duas pessoas, um gestor bem mais experiente assim, que conseguiu trazer uma nova visão, principalmente voltado para a engenharia também, um júnior abaixo de mim, para eu poder conseguir, conseguir operacionalizar mais, espalhar mais, criar mais dashboards e tudo mais. Então, hoje, eu sou um profissional bem completo com relação a dados. Eu também atuo na parte de Web Analytics, um lado que eu já estou evoluindo para ser realmente mais especialista. Então, a questão de tracking, de sites, criação de eventos e tudo mais. E na parte de Data View, acredito que você deve ter percebido, né, que eu gosto muito de utilizar essa questão visual, né, e também utilizar bastante conceitos de storytelling, conceitos, bons conceitos de UX, né, para tentar realmente entregar ali uma história que faça sentido. Então, resumindo, é basicamente essa a minha trajetória. Você tinha feito alguma outra pergunta?

**2:51 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Legal, legal, legal, legal, era isso mesmo. Eu queria agora que você só mostrasse ali o seu teste, se pudesse passar assim... Não precisa ser muito detalhado ou passar de forma rápida. Queria só ver o raciocínio que você teve para desenvolver, também fazer algumas perguntas mais técnicas. Beleza. Então você já trabalhou com a GCP e também a WS?

**3:15 — Kleriston Moreira**
Sim, trabalhei com a GCP, eu criava o ETL no BigQuery e quando foi para a WS eu utilizava o Atina. Legal. eu criava alguns pipelines lá, eu já recebia os arquivos parquet ou JSON, seja o que fosse, né, e aí eu fazia o ETL em cima deles e enviava para o Atina. Aí do Atina eu criava o ETL para poder criar os relatórios.

**3:40 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E os relatórios, quando os dados estavam no Atina, você utilizava qual ferramenta de visualização?

**3:47 — Kleriston Moreira**
A gente começou utilizando o QuickSight, só que a gente não gostou muito da entrega visual que ele poderia gerar e também a questão de acessos, né, não dava para particionar bem ali. Então, gente mudou para o Apache Super 7, se você conhece. Mas, no geral, eu já trabalhei, inicialmente eu aprendi com o Power BI, né, e o Looker, utilizei muito, mas muito mesmo, então eu diria que é a ferramenta que eu domino mais, o QuickSight e o Apache Super 7. Boa, legal.

**4:25 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Eu perguntei porque aqui a gente também usa o Atina, e todos os nossos relatórios hoje eles estão no Looker Studio, e a gente não consegue conectar nativamente, né, o Atina? É, não dá.

**4:37 — Kleriston Moreira**
Tem que contratar uma ferramenta terceira para poder conectar com o Atina. Boa.

**4:48 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Boa.

**4:48 — Kleriston Moreira**
É, beleza. Aqui é a base. Eu dei uma alterada nela, nem sabia se eu podia, mas eu fiz o ETL unindo. As três bases, separando aqui por uma categoria, Record Type, então os dados de Mídia, de Lead, Mídia, Lead e Sales. E por que eu fiz isso? Eu normalizei algumas colunas para que fossem a mesma em todas as bases, para que eu conseguisse criar os filtros que funcionassem em todas as telas e para todas as bases de dados. Então, para eu conseguir trabalhar os dados juntos na mesma tela, sem ter confusão de filtro. Então, os filtros de Sunset e Medium, eles funcionam para todas as três tabelas. Então, basicamente, foi o que eu fiz. Beleza? Vou usar uma pergunta aqui já.

**5:48 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Beleza, eu entendi o motivo de você ter feito a unificação. Por que você não fez direto no Looker? Por exemplo, usou lá a mesclagem do Looker. Para.

**6:00 — Kleriston Moreira**
Às vezes eu tenho problema com aquela mesclagem do Looker. Eu não sou tão fã de fazer o ETL por lá. Consigo, mas às vezes eu tenho dor de cabeça, às vezes quebra lá e como a gente não tem acesso ao que está acontecendo no código, aí dá um estresse um pouquinho. Eu prefiro fazer o ETL antes e já entregar para o relatório tudo pronto. É o meu costume, né? Por exemplo, trabalhando com a Atina, eu vou criar lá um... eu vou criar o ETL no Atina já com tudo pronto para ir para o dashboard, já tudo tratado. Então, todo o campo que eu preciso, eu já mando tratar, já mando nomeado, tudo bonitinho. E no Looker eu simplesmente só construo o relatório. Então, é questão tanto de eu ter controle sobre o ETL, né? Vendo no código e também para diminuir o peso de carregamento do dashboard, diminuindo o ETL direto no looker e qualquer outro tipo de mesclagem ou criação lá. Por exemplo, lá vai ter vários campos calculados. Eu preferiria fazer direto no ETL. Perfeito, concordo, perfeito. Boa, então aqui sobre a base, eu também alterei a data, né, porque como tinha lá a exigência dos últimos sete dias, né, comparar com os últimos sete dias, aí não ficava muito legal com as datas do ano passado, né, então eu meio que trouxe para a data atual para poder ficar fazendo sentido lá. Eu trabalhei com uma estrutura aqui de storytelling básica, digamos. Até porque eu estava planejando fazer cedo, só que aconteceu alguns imprevistos, eu não consegui fazer tão cedo, então acabei entregando um pouco em cima da hora. Eu basicamente utilizei esses três passos, que digamos que é o meu conforto para conseguir fazer sempre fazendo sentido, independente de qual é o tipo de relatório. que é uma visão executiva, que uma visão resumida, que é para alguém lá de cima da staff bater o olho e saber, está bom ou não está bom, está saudável ou não está saudável. Então é uma visão rápida, digamos assim. Então a gente vai ter um funil de aquisição e vai ter os indicadores principais de receita, basicamente isso. E um gráfico travado nos últimos meses. Eu colocaria aqui sempre os últimos 12 meses, mas como o relator, a base tem um limite ali, eu coloquei só os meses em que tem dados. Essa página, então, você pensa mais como um...

**9:00 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Um report, né? Não é uma página tão interativa com filtros, é assim que você pensa, a página executiva, né?

**9:05 — Kleriston Moreira**
É, basicamente. É pro cara ali, lá de cima, o chefe, o CEO, bate o olho, deixa eu ver como é que tá esse mês, como que fechou o último mês, deixa eu dar uma olhada rápida, né? Então, já consegue bater o olho e ver, né? Mas, por exemplo, ali em cima tem o filtro de data, é o filtro ali, de 1º de junho até dia 2 de junho, 2026?

**9:25 — Carlos Tadeu Lopes Filho (Instituto Experience)**
É, é porque eu coloquei esse mês até agora, como padrão, né?

**9:31 — Kleriston Moreira**
Então, ele acabou agora pegando...

**9:33 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Esse filtro, ele não impacta lá no visão histórico, lá embaixo, né? Não, ele não impacta esse.

**9:39 — Kleriston Moreira**
E aí, como que você fez pra não...

**9:41 — Carlos Tadeu Lopes Filho (Instituto Experience)**
pro filtro não refletir aí?

**9:45 — Kleriston Moreira**
Eu personalizei a data desse gráfico específico, né? Aqui. No automático, ele puxa lá de cima, né? E o personalizado, aí a gente consegue definir onde... Dados específicos só para ele. Perfeito. Mas aí se eu filtrar aqui, ele vai filtrar esses dados daqui de cima, né? Menos esse. E os filtros de origem, eles vão funcionar para todos os dados. Então, se eu colocar a origem Google aqui, opa, era para funcionar. Depois eu olho isso aqui. _(ACTION ITEM: filtro de Origem não aplica a todas as bases)_

**10:35 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Enfim. E, em segundo lugar, análise detalhada.

**10:45 — Kleriston Moreira**
Falando um pouco também sobre detalhes que eu adicionaria se eu tivesse mais tempo. Na visão executiva, eu provavelmente colocaria links para ir para outras páginas, né? Tipo, ah, para poder ir para o detalhe. Dentro do próprio dashboard.

**10:58 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Na análise detalhada... Mas onde você colocaria esse link? Porque a idade já tem o botão em cima? Como você imaginaria isso? Só para entender mesmo. Ah, ok.

**11:08 — Kleriston Moreira**
Por exemplo, impressões... É porque aqui eu só tenho três páginas, né? Mas na análise detalhada, se eu tivesse mais tempo, eu faria isso quebrado. Eu colocaria mais páginas dentro da análise detalhada. Uma só para mídia, uma só para lead, uma só para receita, e cada uma com seus detalhes. Então, dentro do funil, quando eu clicasse aqui, né? parte de mídia, ele iria lá para a página de mídia, né? Então, a de lead iria para a página de lead. Então, eu faria quebrando assim.

**11:58 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Se quiser, pode falar aí...

**12:02 — Kleriston Moreira**
Já na análise detalhada, então coloquei todos os indicadores que são necessários para poder analisar o negócio, então aqui vai ter tudo, essa página é para quem entende, então digamos que é para os analistas ou é para aquela pessoa da área que está à frente e precisa ver esses indicadores no dia a dia, é para a galera da operação de fato. Então tem aqui todos os indicadores que foram exigidos, então investimento em mídia, impressões, cliques, CTR e CPC, são os indicadores principais, aqui embaixo eu trago a média dos últimos sete dias para poder comparar, então se eu quiser colocar aqui só a data de hoje ou de ontem, de dia específico, eu consigo ver se versus a média dos sete dias, se está ok.

**13:09 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Por que você fica D-1 para trás e não D-0 para trás?

**13:14 — Kleriston Moreira**
Porque geralmente, quando a gente utiliza um data lake, geralmente é D-1. Se eu estivesse com certeza tratando com uma base que atualiza, sei lá, de hora em hora, né, de duas em duas horas, eu trabalharia D-0. Beleza. Mas aqui é só um costume mesmo. Desempenho por mídia, né, então eu chamo atenção para os que estão, para o que está custando mais de R$1,00, né, eu vi a média, né, deu uma olhadinha na média, qual era a média, então, tá, vou definir que acima de R$1,00, vai trazer aqui um alertazinho vermelho. Mas aí tem que entender bem do negócio, né, saber realmente quais são as médias. Poder ali definir. Leads, então todos os indicadores principais de leads vão estar aqui, também comparado com a média dos últimos sete dias. Desempenho por origem, parecido com o lá de cima. E um gráficozinho de pizza para ver a quantidade de leads que tem ali por status. Então é bem útil assim para a operação. dados de receita e vendas. Essa informação, ela seria bem legal separada porque se eu entregasse dessa maneira para todo mundo olhar, quem trabalha diretamente com a receita, time financeiro, então a staff, né, para olhar indicadores financeiros, ia querer isso daqui lá em cima, né, enquanto a operação vai preferir o restante. Então, eu coloquei aqui embaixo para poder seguir uma lógica, né, seguir realmente ali uma história, né, onde o usuário vem de mídia. torno um lead e depois a gente vê o impacto na receita, né? Mas talvez para outras pessoas vai ser mais importante ver a receita primeiro. Deixa eu só mudar aqui, eu rendi a data para ficar melhor. Ficou zerado ali os números. É, mês passado ficou melhor. Deixa eu ficar mais bonitinho. Ok, então aqui as informações de receita, bastante campo calculado aqui, né? Então, eu vou ter os indicadores principais, quantidade de pedido, receita total, receita paga. Então, a gente vai ter também o lucro potencial e o lucro efetivo. Então, lucro potencial eu estou levando em consideração aquilo que poderia ter sido efetivado. Então, eu levo em consideração os pendentes também, né? E o que foi de fato efetivado dentro do mês é que eu trago como lucro efetivo. Então, no caso aqui está negativo. Indicadores de rentabilidade e eficiência, né, que a gente vai para ROE, para ROAS, o ticket médio, CPL, CPA. E aqui alguns indicadores só para poder ter uma noção geral de volume.

**16:21 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Você falou que essas métricas aí são a maioria calculado, né? Você pode mostrar ali como é que você fez?

**16:42 — Kleriston Moreira**
Beleza. CPA, que é basicamente, aqui é porque eu acabei alterando o nome do campo COST, né? COST é dividido por quantidade de Order ID, porque nesse caso aqui é uma mesclagem que eu fiz, né? Às vezes eu utilizo só o cálculo. No campo calculado, às vezes eu utilizo mesclagem. No Looker é porque, às vezes, fazer o cálculo diretamente no campo, ele pode confundir a questão de eu querer contar único e somar esses únicos, então, às vezes não fica tão legal, às vezes eu uso mesclagem. Mas, de novo, eu preferiria fazer isso no ETL.

**17:25 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E como está essa mesclagem? Porque você não tinha feito só aquela tabela unificada? Clica ali na mesclagem para eu ver qual está relacionando ali. Isso. Ah, está fazendo a mesclagem entre a mesma tabela, né?

**17:43 — Kleriston Moreira**
Isso, é entre a mesma tabela, porque dessa maneira eu consigo aplicar filtro, fazer uma versão com filtros e uma versão sem filtros para poder fazer a comparação. Então, é uma maneira de se utilizar a mesclagem. No caso aqui...

**18:00 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Só uma dúvida mesmo, por que você não pode criar um campo calculado dentro dessa base unificada e aí você coloca um IF ou um CASE dentro do campo calculado? Na verdade, tem uns que são assim, né?

**18:14 — Kleriston Moreira**
Eu basicamente tô aqui só mostrando maneiras diferentes de fazer.

**18:19 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Beleza.

**18:21 — Kleriston Moreira**
Tanto que vai ter alguns que são dessa maneira, eu uso o CASE. Deixa eu só encontrar. Esse aqui também vai ser mais claro.

**18:39 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Entendi, beleza. Exato, ticket médio.

**18:42 — Kleriston Moreira**
Aí tem aqui, order status pago, né? São as vendas no status pago, ele traz o indicador de receita, aí dividido pela contagem única de order ID no status pago. Boa, beleza, entendi.

**19:03 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Beleza. Cara, essa borda que tá aí no Big Number, ela é uma imagem? É um PNG.

**19:10 — Kleriston Moreira**
É um PNG, entendi. Um PNG sem fundo. Eu gosto assim de utilizar elementos visuais em PNG. Claro que dá pra otimizar, eu não fui atrás de otimizar as imagens pra deixá-las mais leves. Eu só fui criando e colocando aqui no arquivo, mas daria pra deixar um pouco mais leve, pra carregar mais rápido. Entendi.

**19:34 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Aí cada Big Number vai ter um PNG por trás ali. Isso, cada um tem um PNG aqui.

**19:40 — Kleriston Moreira**
Beleza. Às vezes dá pra se aproveitar o mesmo PNG, por exemplo, aqui em cima, daria pra ter feito isso, né? Aproveitar isso pra poder ser o mesmo em todas as telas, né? E acompanhar, ficar integrado no relatório, mas os outros aqui tem que ser um pra cada. Beleza, alguma dúvida aqui nessa tela? Não, tranquilo. Análise histórica é outra que eu gosto de fazer bastante, né, que é onde a gente vê tudo compilado ao longo do tempo, então, indicadores principais de mídias, alguns indicadores eu gosto de colocar eles juntos, porque eles fazem sentido juntos, por exemplo, em mídia eu coloco o investimento e o CPC juntos, então, para saber o total que eu gastei, verso quanto o CPC está eu estou gastando com cada lead, né, aí impressões e cliques também são juntos, eles fazem bastante sentido, aí depois vindo para a parte de leads, coloco leads, leads qualificados, leads convertidos, né, são quantidades que se acompanham aqui, eu só esqueci de colocar uma médiazinha aqui, é, taxa de conversão, Versus Taxa de Qualificação, Invenda e Receita, Receita Paga Versus Lucro, ROE e ROAS, Ticket Médio, CPL e CPA, que são indicadores de eficiência. Legal. Então assim, sempre seguindo uma lógica e uma história.

**21:24 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Cara, eu gostei, eu acho que ficou organizado, eu gostei da distribuição que você fez aí nas páginas, acho que de fato está seguindo o Storytelling. Algumas coisas no visual, assim, só que eu melhoraria, tipo, você colocou lá os PNGs dentro de cada big number, eu não faria assim, tipo, acho que isso é um puta trabalho e deixa o looker pesado. E eu vi que está alguma coisa desalinhada ali, mas são ajustes simples ali, de design mesmo, de layout, que é algo que a gente cobra muito aqui. Mas no geral, assim, eu gostei. Aí eu queria só... Então... Tirar umas dúvidas aqui, eu anotei algumas perguntas, isso aqui você já falou, mas só para confirmar, além do Looker Studio, quais são as outras ferramentas que você trabalhou mesmo, de visualização de dados?

**22:12 — Kleriston Moreira**
Looker Studio, Power BI, Superset e QuickSight.

**22:17 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E se fosse escolher um, qual você escolheria e por quê?

**22:22 — Kleriston Moreira**
Cara, eu trabalhei por muito mais tempo com o Looker, e eu conheço todas as partes dele, então é a ferramenta que eu estou bem mais acostumado. Mas, independente da ferramenta, eu me adapto, porque eu acho que em primeiro lugar é a necessidade do negócio, aí a ferramenta que for, a gente faz o melhor que puder com ela. Beleza.

**22:43 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E você já usou inteligência artificial para montar algum dash? Alguma ferramenta?

**22:49 — Kleriston Moreira**
Cara, para auxiliar sim, tanto que o case foi o caso, para poder montar primeiro o escopo do projeto, quais seriam os indicadores principais, né, para poder montar essa questão do storytelling, qual viria primeiro, então eu sempre fico ponderando, né, e conversando um pouquinho para poder montar primeiro, e depois é que eu crio baseado nisso, então eu primeiro tomo um tempo com inteligência artificial para poder me organizar, e depois eu trabalho em cima disso, né, muitos dos PNGs aqui também foram criados com inteligência artificial, né, vai decodando mesmo o design, né, para poderem me entregar, então assim, eu utilizo bastante para poder dar apoio.

**23:33 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Beleza, boa, e até aproveitando isso do escopo que você comentou, normalmente como é que funciona, assim, as demandas que você entrega, você recebe já a demanda pronta, com tudo que tem que ter no Dash, quais são as métricas, indicadores, e você só entrega, ou você está acostumado também a participar dessa construção do escopo, entender a regra de negócio, enfim, entender as métricas, indicadores, propor análises, como é que você enxerga isso?

**24:00 — Kleriston Moreira**
Cara, eu quase sempre tive que participar do zero, porque não é tão fácil achar um time que seja bem maduro com dados e que saiba pedir exatamente o que ele quer, isso seria maravilhoso, mas no geral eu tenho que participar junto para poder ajudar o time a entender o que ele precisa, que seja entregue, então na maioria das vezes eu tenho que realmente eu fazer anotações, fazer um brainstorm primeiro, o que é importante, o que vocês precisam ver, qual problema, qual dor vocês precisam que seja solucionada, e a partir disso aí eu começo a criar o scope quais seriam os indicadores principais que responderia a pergunta de negócio. Vai ter melhoria constante, claro, então depois de entregar a versão 1, pode esperar que vai vir versão 2, sempre que você entrega algo, o pessoal se anima e pede mais coisas, isso sempre acontece, mas eu sempre participo do processo criativo. Eu acho que quando tem algo já pronto, às vezes é só um relatório específico para situação específica, né? Eu preciso saber sobre tal coisa, né? Tem como me ajudar com isso aí? Tem esse dado aí? Aí, opa, tem sim, né? Eu te devolvo aí em tanto tempo. É basicamente isso. Entendi.

**25:17 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Boa. E você comentou ali da questão da validação, né? Vai ter versão 1, versão 2, versão 3, isso é normal. Mas você costuma fazer o mockup, você faz um protótipo e valida com o demandante antes ou você já desenvolve entrega? Como é que é isso?

**25:33 — Kleriston Moreira**
Quando é urgente, às vezes só desenvolve numa tela entrega, né? Às vezes não tem necessidade de design ou algo do tipo. Quando é para uma situação urgente. Mas quando é um projeto, de fato, né? Onde dá para se aguardar e dá para ter esse tempo de construção, eu gosto de criar um mockup utilizando um mapa mental, né? Então, eu construo num miro, num mind map, seja o que for. Eu escrevo todos os campos da base e quais campos eu utilizaria, aí depois eu passo para a parte do dashboard, onde eu de fato crio como se fosse um mockup de dashboard mesmo, né? Onde eu coloco qual vai ser o tipo de gráfico, qual vai ser a dimensão, qual vai ser a métrica, quais vão ser os filtros, e aí eu vou criando cada tela, desenhando cada tela dentro desse mockup. Legal, legal.

**26:28 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E como que você se organizaria? Você está desenvolvendo um projeto, você está fazendo um dashboard ali, e aí no meio disso chega uma outra demanda ali para fazer um outro dashboard, um outro projeto. Como que você se organiza nesse sentido? Quais são as ações que você toma para parar de fazer, não fazer, recomendar prazo? O que você faria nesse caso?

**26:53 — Kleriston Moreira**
Cara, é a questão da prioridade. Depende de qual é a prioridade e o impacto do negócio, né? Qual dos dois é mais importante. Às vezes eu posso acabar iniciando um dashboard porque, sei lá, a semana está mais tranquila, né? E aí eu pego algo que está ali no backlog e de repente chega uma outra solicitação, né? E aí eu vou ter que avaliar junto com os stakeholders o que é mais importante, o que é mais crítico, né? E aí não tem problema, se tiver que pausar, pausa, se tiver que iniciar, o outro inicia, né? O que é mais importante do que aquele.

**27:22 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Boa, legal. E agora falando um pouco mais da parte técnica, assim, SQL, você já trabalhou com SQL? Qual que é o seu nível de SQL?

**27:35 — Kleriston Moreira**
Sim, o nível de SQL eu posso dizer que é um intermediário alto, né? Já utilizando ali CTEs, né? Para dar uma economizada, para conseguir otimizar, né? Mas eu trabalho bem, utilizei bastante, né? Principalmente ali no Atina. Tá, legal. E você já trabalhou com API alguma vez? Não participando do processo de criação. Mas utilizando, se utilizando da API para poder entregar os dados. Tá, beleza.

**28:09 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Beleza. Estou vendo aqui só se tem uma outra pergunta que eu tenho para fazer. Cara, eu queria que você me desse um exemplo do projeto mais complexo que você tem para fazer ou algum projeto que você ficou contente com a entrega porque teve bastante desafio no caminho e que gerou algum resultado. Quais foram, assim, os desafios que você teve? Qual foi o seu raciocínio? Enfim, queria que você me explicasse, assim, meio que do começo ao fim, sabe? Um case, assim, que você teve. Beleza.

**28:54 — Kleriston Moreira**
Vou tentar pegar do começo porque eu diria que é um case de anos. Ali na minha última experiência de Letterspace, o principal cliente é Stellantis, Stellantis Brasil, dona de Fiat, Jeep, ou Citroën, e eles possuem mais de 200 sites com a Letterspace, e a análise da performance desses sites era feita de maneira separada, indo de um por um, acesso ao dashboard de site A e ver como está, site B e ver como está, ou seja, a gente conseguia dar um feedback para o cliente, saber se cada um individualmente estava bom, mas não tinha uma visão geral de como estava a saúde geral do cliente, das marcas, a gente não conseguia analisar dessa maneira. A fonte de dados principal era o Google Analytics, existem os dados de leads da plataforma também, mas o Google Analytics é o que trazia ali os principais insights relacionados à performance do usuário, performance de mídia, que é muito importante para eles. Eles não sabiam como fazer, tentaram criar soluções de integração com planilha, um negócio nada a ver, né? E foi aí que eu me aprofundei na questão do Web Analytics, para poder criar alguma solução que pudesse resolver isso aí. E eu consegui, a partir disso, criar uma solução onde eu unificava todos os dados e todos os eventos de todos os sites em uma só propriedade do GA, né? E criei propriedades onde categorizava isso, separava por marca, né? Criava as categorias necessárias ali para poder fazer filtros também. E a partir disso, eu criei relatórios unificados, né? O segundo passo disso foi poder otimizar esses relatórios, porque o GA tem limite de tokens ali, e conectei com o BigQuery. Então, tem a conexão nativa, o GA BigQuery, traz os dados brutos para lá, e a partir daí, tive que começar a aprender a trabalhar com esses dados brutos, para poder transformar ele em dados amigáveis de novo e enviar para o Looker de novo para poder trabalhar eles. Então a partir daí comecei a otimizar esses dados também. E foi quando eu comecei a entregar relatórios compilados. Então eles conseguiram ver, passaram a conseguir ver visão geral por marca, começaram a ter mais noção do negócio e para onde estava indo. Tanto que existem outros fornecedores, não só a Letterspace, e eles colocaram como obrigatório para esses fornecedores eles criarem a mesma solução que eu criei. Então eu criei um padrão geral de qualidade de dados para dentro do programa como um todo. E a partir disso foi criado reuniões semanais que era baseada em cima da análise desses relatórios. Então tudo começou a girar em torno de ver os dados gerais da marca, de cada marca. Legal, foi bacana.

**31:53 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Eu me orgulho bastante. Bacana. Cara, só para finalizar aqui agora, a gente está com viés muito forte aqui de inteligência artificial, tipo, a utilizadora está usando, a gente usa muito a Cloud Code, enfim, várias ferramentas, muito dinamismo aqui, e aí eu queria entender de você, como é que você está atualizado em relação a IA, quais são as ferramentas que você conhece, o que você usa, porque a gente precisa de pessoas com esse perfil, porque o que a gente está tendo aqui de performance está absurdo com Cloud Code e outras ferramentas, como é que você se vê nisso?

**32:28 — Kleriston Moreira**
Cara, eu tentei incentivar a implementação da empresa de onde eu estava, eu não consegui verba para isso, então, pessoalmente, eu mesmo me aprofundei, gastei no meu bolso, paguei ali GPT, eu utilizo bastante o Codex, para poder tanto gerar escopo de projeto, como também gerar código, o ETL que eu fiz em Python, utilizei bastante essa ajuda, para poder conseguir aprofundar, acelerar, eu estava com pouco tempo ali para o projeto, então, me ajuda bastante. As IAs que eu mais utilizo é o GPT junto com o Codex, o Gemini, e o Cloud Code eu estou começando a mexer agora, mas eu não tive a oportunidade de utilizar o pago, que eu realmente quero utilizar. Mas assim, cara, de fato eu tenho bastante facilidade. Como eu te expliquei, o case aqui como um todo eu utilizo como base para acelerar a inteligência artificial. Eu tive basicamente dois dias para fazer isso aqui. Eu não consegui fazer utilizando cinco dias. Então, eu estava, sei lá, de manhã eu fiz o escopo, de tarde eu fiz o ETL, no dia seguinte eu fiz a parte visual. E tudo pegando auxílio da IA para poder acelerar. Tanto parte de código, quanto parte de cálculo, como validação dos dados. Então, sempre fazendo essa relação. Seria excelente ter o Cloud Code para poder fazer de maneira automatizada ali no meu lugar, mas eu consegui utilizar como ponte para poder fazer isso. Então, assim, IA é do meu interesse para me aprofundar, isso com certeza, e eu já utilizo. Agora a questão do Cloud Code para utilizar para a automação em si, é só a falta de oportunidade de utilizar ele no pago.

**34:18 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Cara, beleza, o que eu tinha aqui de pergunta é isso. Mas, cara, conforme eu falei, a gente precisa muito de uma pessoa que esteja disposta a aprender a colocar a mão na massa, utilizando bastante IA, que a gente está usando muito, e a nossa performance está evoluindo a ser absurdo. E a gente quer uma pessoa que entra aqui nesse barco junto com a gente e ajuda a gente a remar na mesma direção. Cara, o que eu tinha aqui para falar com você, acho que está ok, gostei, assim, do nosso bate-papo. Eu vou retornar ali com a Emília e, assim que tiver uma resposta, ela te retorna no WhatsApp. Mas agradeço aí bastante o tempo aí.

**34:57 — Kleriston Moreira**
Boa, não, eu que agradeço também, cara. Só uma dúvida que ficou no meu último bate-papo lá com a Emily, é que ela falou que a posição era pleno, mas estava escrito sênior e você confirmou agora que era sênior, aí ficou meio assim.

**35:12 — Carlos Tadeu Lopes Filho (Instituto Experience)**
É uma posição sênior de fato, então. A gente tem a posição sênior, mas a gente está avaliando conforme o perfil do candidato também. Para a entender que o candidato se encaixa no perfil sênior, a gente vai fazer a oferta de sênior, se a gente entender, se a gente não encontrar um perfil sênior, a gente pode reduzir para uma vaga de pleno, por exemplo. Mas é de sênior. Entendi.

**35:32 — Kleriston Moreira**
Então, o budget aí varia também. Varia. Isso.

**35:36 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Show de bola.

**35:37 — Kleriston Moreira**
Era só isso mesmo.

**35:39 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Beleza. Obrigado aí, cara. Muito obrigado aí pelo bate-papo. Tenha um bom dia. Bom dia. Valeu.
