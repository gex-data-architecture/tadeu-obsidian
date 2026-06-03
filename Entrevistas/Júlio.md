---
tipo: entrevista
candidato: Júlio Gabriel Queiroz
vaga: Analista de Dados / BI (Sênior — pode ajustar p/ Pleno conforme perfil)
entrevistador: Carlos Tadeu Lopes Filho (Instituto Experience)
data: 2026-06-03
duracao_min: 34
gravacao: https://fathom.video/share/tEPYvJ_teQAD_jtnqe9cJFYDs6YPz62b
case: Looker Studio (unificação Mídia/Lead/Sales)
nota_case: 6.4
nivel_case: Pleno
recomendacao: Não aprovado p/ Sênior (perfil Pleno I)
fonte_nota: https://data-talent-quest.lovable.app/
tags: [entrevista, recrutamento, dados]
---
# 🎤 Entrevista — Júlio Gabriel Queiroz (Data View / BI)

> Transcript bruto da entrevista (Fathom). Resumo/avaliação em seção própria abaixo.
> Nota do case via `data-talent-quest.lovable.app` (candidato "Júlio Queiroz").

## Action items (da gravação)
- **Alinhar com Amy + Gabriel (CTO)** sobre o Júlio; enviar decisão até **5/jun** (ou 8/jun se necessário) — [timestamp 32:22](https://fathom.video/share/tEPYvJ_teQAD_jtnqe9cJFYDs6YPz62b?timestamp=1942.9999)
- Retorno ao candidato por WhatsApp (Amy) até **sexta-feira**, no máximo segunda.

---

## 🧭 Resumo / Avaliação do candidato

> Cruzamento da **nota do case (Looker Studio)** com a **performance na entrevista**.
> Nota do case via `data-talent-quest.lovable.app` (candidato "Júlio Queiroz").

### Nota do case — **6.4 / 10 → nível Pleno**
| Critério | Nota |
|---|---:|
| Identidade Visual | 60 |
| Organização da Informação | **75** |
| Experiência do Usuário | 65 |
| Storytelling dos Dados | 60 |
| Visualização dos Indicadores | 65 |
| Maturidade Executiva | 60 |

- **Forças do case:** identidade visual consistente, boa separação/organização da informação (página financeira × página de tráfego), funil construído manualmente para contornar a distorção do gráfico nativo.
- **Fraquezas do case:** excesso de elementos visuais reduzindo a hierarquia; **falta de storytelling crítico dos dados** — não deu destaque ao **ROI de −51%** nem ao **prejuízo de −R$ 565k**; métricas de funil exibidas de forma inadequada (valores zerados por limite de casas decimais).
- **Recomendação do avaliador:** *"Dashboard funcional de nível Pleno I; sem maturidade executiva sênior."* **Não recomendado** para a vaga (que pede perfil sênior).

### Performance na entrevista — pontos fortes
- **Forte viés técnico / engenharia de dados:** prefere Python (Pandas) e SQL; pensa em **granularidade da tabela "grande"** (1 linha por dia × campanha) como base para flexibilidade de filtros — bom instinto de modelagem para BI.
- **ETL a montante:** montou as duas tabelas finais (financeiro consolidado + dataset de funil) num script Python; reconhece que **em produção faria em SQL** ligado ao banco. Alinhado a como o time trabalha.
- **Resolução criativa de limitação:** construiu o funil empilhando barras e removendo eixos/elementos ("Frankenstein") porque o gráfico nativo distorcia o salto 16M→168 — pragmático.
- **Boa cabeça de cloud/DW:** fã declarado de **BigQuery** (custo previsto por query, conexão nativa com Looker, pipelines), experiência com **Redshift** (mais júnior) — *mas o time usa AWS + MySQL, não GCP/BigQuery*.
- **API dos dois lados:** já **criou** API (servir modelo de ML de leitura de gabaritos por visão computacional, Arco Educação) e **consumiu** (Mixpanel, com dor no limite de 20 min). Diferencial vs. Kleriston (só consumo).
- **Maturidade de processo:** entende contexto/perguntas do negócio primeiro, faz **entregas parciais com roadmap** para não ser gargalo; confortável com múltiplas demandas em paralelo.
- **Autoconsciência:** aponta "aprender a dizer não" como ponto de crescimento; quer pivotar para **engenharia de analytics** em ~1 ano.

### Performance na entrevista — pontos de atenção
- **Maturidade executiva (mesma fraqueza do case):** não destacou o prejuízo/ROI negativo — para sênior, faltou *insight de negócio* além da boa execução técnica.
- **Stack desalinhada:** experiência mais forte é **GCP/BigQuery**; aqui é **AWS + Athena/MySQL**. Redshift foi uso "mais júnior". Curva de adaptação ao ecossistema do time.
- **Identidade visual / hierarquia:** o próprio avaliador apontou excesso de elementos visuais — *layout/design é algo que o time cobra muito*.
- **Cloud Code:** só começou a testar agora, **apenas em projetos pessoais**, nunca em produção/pago (mesmo gap do Kleriston) — o time é "AI first" e cobra automação com Cloud Code.
- **Contratação PJ:** nunca trabalhou como PJ; precisaria estruturar isso (disponibilidade ~1 semana / 15 dias).

### Conclusão (alinhada ao avaliador)
Candidato com **perfil mais técnico/engenharia** (Python, modelagem por granularidade, BigQuery, criação de API) e boa cabeça de processo — porém o case entrega **nível Pleno I**, sem a **maturidade executiva** (leitura crítica do negócio, destaque do prejuízo) que a vaga sênior exige; soma-se a **stack centrada em GCP** (vs. AWS/MySQL do time) e Cloud Code ainda incipiente.
- 🔸 **Sênior:** não recomendado.
- 🔹 **Pleno:** viável, com destaque para o **viés de engenharia de analytics** — interessante se a vaga puder enquadrar como Pleno com trilha p/ data eng.
- **Próximo passo:** alinhar com Amy + Gabriel (CTO) e dar retorno ao candidato até 5/jun (máx. 8/jun).

> **Comparativo rápido com Kleriston** (mesmo batch): Kleriston **6.7** — mais forte em **visualização/storytelling/UX**; Júlio **6.4** — mais forte em **engenharia/modelagem/API**. Ambos Pleno, ambos com gap em Cloud Code pago e integridade/maturidade executiva. Perfis complementares.

---

## Transcript

**0:02 — Júlio Gabriel Queiroz**
Aqui, foi assim, aqui, foi assim mesmo. Deixa eu compartilhar. Opa, tá, opa, tá mostrando? Desculpa. Sim, sim, tudo bem. Pronto, beleza. Pronto, então aqui, esse é o script que eu usei, no caso, ele carrega tanto as três bases, certo? E aí, pra cada, tá, aí ele carrega essas três bases e cria as duas tabelas finais que eu criei, que eu utilizei. Uma das tabelas é esse financeiro aqui, que é de, esse financeiro consolidado. Essa aqui é a tabela final total que eu comentei, que pra cada dia de referência, pra cada ID de campanha, eu tenho todos os valores de receita, de custo. E todas as outras métricas também de tráfego, que são impressões, cliques, conversões, quantidade de leads, de vendas. Então, nessa tabela grande aqui que a gente chama, eu tenho todas as métricas com referência de cada idade de campanha e de cada dia. Então foi essa aqui que eu criei. Aí na próxima página, lá do dashboard, eu criei uma outra que é essa aqui, depois eu posso comentar melhor. Mas foi, assim, é um script bem básico, porque ele só junta, assim, os arquivos CSV, faz um join ali usando o Pandas e cria esses arquivos finais ali. Assim, teria como fazer isso em SQL? Também. Na verdade, seria até o mais recomendável, mas como não tem essa conexão ali com o Luka ou com o Banco de Dados, que é o que aconteceria se a gente, se a gente tivesse trabalhando, digamos assim, daria para fazer bem tranquilo também. Tá, boa. Boa, legal.

**1:53 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Beleza, velho. Pode voltar lá. E, então, vocês, por favor, parte ou sabe... O SQL, qual você gosta mais? Qual você usa mais aí?

**2:03 — Júlio Gabriel Queiroz**
Cara, assim, a gente usa Python para alguns problemas e SQL a gente usa sempre, né? Acho que o SQL é a linguagem que você tem que dominar, porque em vídeo médico você vai ter que trabalhar com banco de dados, vai ter que fazer conexão e, assim, até você chegar no Python, você vai ter que ter usado muito SQL, né? Tanto para juntar todos os dados, para tratar eles e eles você levar para o seu script Python, mas o que eu mais gosto mesmo é o Python. Acho que o Python é meio que essa natureza de conseguir fazer muita coisa com pouco recurso ali, acho que é primordial, assim, para analisar dados mesmo. Boa, concordo, né?

**2:45 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Concordo. Não, legal, mano. Bacana demais. Pode voltar lá no look? Eu queria que você clicasse ali no botão de edição, eu queria ver como que você montou ali, como que foi feito.

**2:56 — Júlio Gabriel Queiroz**
Vou abrir aqui de novo, compartilhar. Dá pra ver, né?

**3:11 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Isso, dá pra ver. Certo.

**3:13 — Júlio Gabriel Queiroz**
Qual item você queria ver?

**3:15 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Eu quero ver o que você criou aí de campo calculado, como é que você fez. Ah, tá. Por exemplo, o ROAS ali, ou o ROE. Certo. Beleza.

**3:23 — Júlio Gabriel Queiroz**
O ROAS aqui, como eu falei, a tabela que ele tá consumindo é aquela tabela grande, que tem todos os dados destrinchados por dia e por dia de campanha, de todos os períodos que a gente tem ali os dados. E aí, o jeito que eu calculei foi isso aqui. No caso, aqui eu calculei toda a receita das ordens que estava com o status de pago. Então, é toda a receita que foi de fato consolidada. O dinheiro que realmente entrou ali é dividido pelo custo. Então, esse aqui foi o eu calculei o ROAS e o ROE eu calculei. No caso, foi a receita líquida, né? o que foi de fato pago menos o custo em relação ao... todo o curso ali.

**4:03 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Boa, legal. Beleza. Cara, Fletcher, quer mostrar outra página ali? Ah, sim. Bora.

**4:10 — Júlio Gabriel Queiroz**
Deixa eu tirar aqui a edição. Pronto. Então, essa primeira página, como eu falei, eu mostro todas as métricas financeiras, né? Eu acho que até por isso eu coloquei como primeira página, que no final das contas, né? Acho que o que você dá destaque é realmente tudo que está, tudo que envolve dinheiro ali, A receita em si. E aí, em segundo plano, eu coloquei essa outra página que trata mesmo da parte de tráfego, né? Então, começando pelo fim de conversão. Aqui é bem interessante, porque os números, eu até fiquei um pouco chocado, porque tem uma discrepância bem grande, né? Entre as impressões, cliques, leads e vendas. Dá para ver que é uma queda bem brusca. E o gráfico nativo do Looker não dava para você ter uma visão muito detalhada desses números. Porque você sai de um... Sobre de 16 milhões para 168, aí o gráfico fica bastante distorcido, né? Aí eu acabei criando esse Frankenstein aqui no look, mas é só para poder ter visibilidade. Mas ficou bom, mano, eu gostei, eu gostei. Mas deu um pouquinho de trabalho, assim. Assim, eu confesso que como eu não tinha noção prática, assim, dos números dessa parte de marketing digital, eu confesso que foi um pouco, assim, eu até estava achando que estava errado, né? Mas não, depois que eu fiz uma pesquisa ali no mercado, eu vi que é bem comum ter esses números, assim, né? Essa ordem, né? Decrescente. E aí, beleza.

**5:39 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Mas aí, como é que você fez esse gráfico aí, esse funil? Você colocou vários gráficos de barra que você foi colocando embaixo do outro?

**5:46 — Júlio Gabriel Queiroz**
Isso, exatamente. Eu coloquei vários gráficos de barra. No caso, primeiro, eu criei o conjunto de dados, em que eu tinha cada uma dessas etapas ali com o número pré-calculado. Então, assim, eu até queria... Outra fonte de dados, usando aquele mesmo script Python, e a partir dessa única fonte de dados, eu criei esse único, desculpa, esse gráfico de barras só com os dados de cada uma das etapas do funil. Então, por exemplo, esse gráfico de barra, eu removi todos os eixos, todas as dentes grátis, todos os outros elementos que não fossem a barra em si e o rótulo dela, e aí eu só fui empilhando aqui. É, o Luke, ele tem esses, caramba, tem uns dois anos que eu não, tem um ano que eu não mexo no Luke e ele continua com os mesmos erros, assim, o cara é impressionante. Verdade, tem uns bugzinhos muito estranhos, né? Cara, muito, muito, muito louco isso, Ele até mudou de nome, Era Luke, agora virou Data Studio, né? Ele já foi Data Studio, mudou para o Luke, agora é Data Studio de novo. É realmente retrocesso. Exatamente. que é a melhor palavra para ele. Então, foi exatamente isso que você viu. Solto grafos de barras empilhados e aí eu tirei todos os elementos para ficar mais nítido e... Foi assim, porque o grafo nativo dele ficou bem ruim com esses valores. E aqui é boa taxa de passagem.

**7:09 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E aí esses percentuais que você colocou ali, a taxa de passagem que você chamou e taxa global, são campos calculados também?

**7:18 — Júlio Gabriel Queiroz**
Isso, exatamente. Isso, são campos calculados colocando cada valor de cada etapa, no caso a divisão, fazendo a divisão de cada número, de cada etapa, pela etapa inicial, para a taxa global e para a taxa de passagem, só os valores relativos de uma etapa para a outra. Essas daqui ficaram realmente zero, porque são números muito, muito pequenos. E aí eu fiz de tudo para aumentar essa pressão decimal aqui, mas o look realmente não consegue mostrar valores tão pequenos assim. Mas eu acredito que são bem comuns nessa área, porque como é uma conversão muito baixa ali, Não dá para ter essa precisão, mas é isso, a gente tem essa diferença de taxa de passagem e taxa global de cada etapa em relação à primeira etapa ali. E aqui são as métricas, Claro, dá para a gente filtrar também tanto o funil quanto as métricas, inclusive lá na primeira página também, por cada filtro aqui. E é até importante a arquitetura que eu usei para a tabela grande, que quanto maior a granulidade que você tem dessa tabela, mais filtros você consegue colocar no seu dashboard. Então, mais detalhada ainda, a sua visão fica no dashboard. Acho que o bom de usar uma tabela que nem aquela é isso.

**8:42 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E aqui tem as métricas, né?

**8:45 — Júlio Gabriel Queiroz**
ali tem o custo por aquisição e o custo por lead. E aqui tem, no caso, aqui, essas visões eu coloquei mais para a gente ter uma ideia da performance, né? Que lá no desafio... Pedir para ver uma janela dos últimos sete dias. Só que assim, aí eu fiquei confuso porque os últimos sete dias sempre de uma data fixa ou sempre de uma janela? Eu achei que sempre uma janela de sete dias faria mais sentido. Então, qualquer que seja o mês, se você filtrar aqui o mês, você vai ver sempre uma janela de um dia e os últimos sete dias corridos antes deles. Então, acho que essa foi a visão que eu tentei passar aqui. E aqui você consegue ver, né? Cada métrica de tráfego e, claro, de vendas em relação à sua média. Então, dá para você comparar tanto ela com ela mesma, ou seja, cada métrica com sua média, como ela com cada uma das outras métricas, né? Desempenho. Sim, boa. Legal. Eu até pensei em colocar uma visão também cumulativa, mas aí eu achei que, sei lá, talvez numa próxima fase eu fizesse essa visão um pouco mais detalhada. Mas me tira uma dúvida.

**9:53 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Ali no primeiro gráfico, o de impressões, você tem impressões ali na coluna e tem a média ali na linha. E essa média seria a média desse intervalo de sete dias, dessa janela. Exatamente, exatamente.

**10:05 — Júlio Gabriel Queiroz**
Tá.

**10:06 — Carlos Tadeu Lopes Filho (Instituto Experience)**
É porque a linha ficou muito baixa, eu acho que é por conta do eixo, deve ser os dois, um esquerdo e direito, talvez.

**10:14 — Júlio Gabriel Queiroz**
É, e também acho que por causa da variabilidade também, assim, você tem dados que vai de 34 a 240 mil em cerca de dois dias, sabe? Aí acho que a média, ela tem um pouco a acompanhar esse número. Agora, só um coisa que você falou, deixa eu só ter certeza, tá? É, a média, não, perdão, a média, ela é a média geral de todo o conjunto de gráfico, tá? Ah, Pra corrigir, perdão, perdão.

**10:42 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Perdão, imaginei mesmo, porque se fosse a média desse intervalo de sete dias, ela ia ter que Ela iria mais rápido. É, e teria que ser uma constante, né? Que é a média desses dias.

**10:54 — Júlio Gabriel Queiroz**
Sim, sim. Assim, o que faria sentido seria adicionar uma média móvel. No caso, como o Looker não tem esse recurso, ou pelo menos talvez tenha para séries temporais, eu teria que dar uma analisada, seria um tipo de campo que você conseguiria calcular no Python, ou mais fácil ainda no SQL, você calcular, então para cada método que você tem, você cria uma média móvel, seja de 7 dias, seja de 14, qualquer período que for, que fizer mais sentido, facilmente a consegue calcular, e seria aqui. Boa. E aqui, assim como na primeira página, tem a calculada, desculpa, tem a visão detalhada, né, de todos esses dados de tráfego para cada campanha, para cada canal, para cada plataforma, e a gente consegue ordenar eles de acordo com o que fizer mais sentido, né, seja, pode ter crescente do curso por lead ou do curso por aquisição, né, ou até questão de impressões também, e é isso, assim, claro, dá para adicionar também outras métricas, mas eu acho que essas foram aqui, aqui, ao meu ver, fizeram mais sentido.

**12:04 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Eu gostei do seu dash, do seu case, aí eu acho que ficou bem fluídas as informações, deu um storytelling legal, achei que ficou bem organizado ali os visuais, deu para entender, não ficou tipo o número sobreposto, as cores acho que ficam boas também. Ah, legal, tá legal. Legal, e aí me tiro uma dúvida, em relação a ferramentas de visualização de dados, quais que você já trabalhou, além do Luca?

**12:32 — Júlio Gabriel Queiroz**
Certo, eu trabalhei com a ferramenta que talvez não seja tão conhecida, que era o Clicksense, não sei se você ouviu falar, também trabalhei com, ai caramba, agora esqueci o nome, é uma da Apache, que é toda por Python, então você cria todo o código para criar esse dashboard, você sobe ele no servidor e tal, e aí as pessoas entram no site para ver o seu dashboard, e também trabalhei com o Power BI, mas o Power BI é bem... Pouco, assim, porque como ele era muito caro na época, aí justamente eu optei por usar o Looker pela facilidade que ele tem, questão de curso, questão de acesso também, mas é isso, acho que se fosse destacar seria o Looker, principalmente, seria esse Clicksense e seria essa outra ferramenta da parte que agora eu não sei porquê, me fugiu o nome disso, e o FHBR também. Então, boa.

**13:24 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E falando do Looker especificamente, tem alguma coisa nele que você não gosta? Alguma limitação que você acha que atrapalha? E eu queria saber também, se você tivesse mais tempo para fazer esse teste, o você mudaria nele? Certo. Bom, pergunta.

**13:40 — Júlio Gabriel Queiroz**
O Looker, eu acho que ele tem, sim, algumas limitações, por exemplo, a gente tem poucas opções de gráfico, você vê, desde a última vez, assim, desde que eu comecei a trabalhar com o Looker, a gente tem exata mesma quantidade de gráfico, então, assim, são quatro anos trabalhando com ela e... Aqui ele não traz nada de novo, então a gente tem uma limitação bem grande em questão de número de gráficos, a questão visual também, eu vi que ele tem uma funcionalidade nova, que você cria um dashboard que ele se adapta ao tamanho da tela, isso é bom, só que eu vi que ele é muito rígido, por exemplo, eu não conseguiria criar esse funil aqui usando esse recurso dele, eu tive que criar essa página de tamanho fixo justamente para poder criar esse funil alternativo. Então, eu acho que ele tem uma limitação visual grande, agora em questão de código e de performance, eu acho que ele desempenha bastante bem, eu já trabalhei com bases de dados bem grandes, mais de 50 milhões de linhas conectadas diretamente com ele através de uma consulta SQL e trabalhou bem, principalmente quando a gente trabalha com o banco de dados do próprio Google, do próprio ecosystem do Google, que é o Big Query. É, ele, o Big Query e o Google Ads. É perfeito, claro, tinha que ser, era um serviço pago, que era com eles, no mínimo tinha que ser, né? E é, de fato, eu já trabalhei com um concorrente, né? Que é o da AWS, o Redshift, e ele tem bem mais limitações em questão de performance. Então, acho que é isso sobre o Luca. E sobre o Dash, eu acredito que eu tentaria trazer um pouco mais insights sobre, por exemplo, sobre as vendas, né? Sobre como foi um problema que me chamou muita atenção, eu tentaria cruzar com mais informações, claro, se tivesse esses dados disponíveis, eu tentaria trazer mais informações sobre as vendas que foram canceladas e as vendas ficaram pendentes, assim, o tempo que a ordem ficou ali em negociação, qual o tipo de cliente que acabou cancelando, qual foi o motivo de cancelamento, eu acho que eu criaria uma visão mais detalhada aqui sobre essa sessão, porque são informações que, em que a ação para contornar elas é bem clara, assim, ah, se o... teve várias ordens que foram canceladas porque o motivo de pagamento foi cartão de crédito, foi boleto, vamos tentar mudar essa forma de pagamento para cartão de crédito, então é uma informação que é fácil de mostrar, ela é bem clara e a ação que você tem por causa dela é bem rápida, você bate o olho e fala, não, peraí, vamos fazer uma campanha para mudar a forma de pagamento, já que a está deixando 30%, quase 40% da receita só por causa disso, entende? Então acho que eu tentaria entrar em detalhes mais nesse tipo de dado, assim, que o esforço é menor e o resultado que você pode gerar através dele é bem grande.

**16:38 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Tá legal, boa. Você comentou anteriormente que o Lucre funciona muito bem trabalhando com bases grandes, né, você comentou 50 milhões de linhas, principalmente no Big Query. Qual foi a sua experiência com o Big Query? Conta um pouquinho como que você usou, como que foi. Perfeito.

**16:56 — Júlio Gabriel Queiroz**
Cara, eu realmente gosto bastante do Big Query, então, é... Principalmente assim, a linguagem dele que ele usa é muito semelhante ao Postgres, que é um dialeto SQL que eu tenho mais familiaridade. Não que tenha muita diferença com os outros, mas é um que eu gosto bastante, porque ele é bem performático. E o BigQuery eu gosto porque, primeiro, se a empresa já trabalha com o próprio ecossistema do Google, isso facilita muito a questão de conexão, a questão de acesso. Para acessar o dashboard, se você é dentro do ecossistema do Google, basta o seu e-mail Google. Então, pronto, você não tem aquela dificuldade do RBI, pelo menos na época que eu trabalhei com ele, você não tem a questão do custo. Então, assim, e a própria conexão do BigQuery com o Looker, ela consegue ser otimizada. Se eu não me engano, tem um pacote que você consegue comprar, que a conexão, eles sempre colocam no servidor próximo aonde o dashboard vai ser visualizado, sabe? Cara, isso, nossa, isso é muito... Muito bom, assim. E a visibilidade também. Eu lembro que o próprio Big Query, você tem uma plataforma que você consegue escrever as suas consultas SQL para visualizar os dados e no próprio console você tem a previsão de curso que aquela consulta vai trazer. Isso é muito bom porque para times de dados e tal que tem essa limitação, você saber o curso provisionado ali da sua pipeline de dados ou da sua consulta, da sua análise, é muito bom, assim. Eu acho que é um recurso bem interessante. Então, é isso. Acho que o Big Query foi o melhor, assim, que eu já trabalhei, tá? O serviço de nuvem, de banco de dados, fora todos os outros recursos que ele tem também, que eu dou. Ele tem, por exemplo, a execução de script Python, de script SQL, que você pode fazer toda uma pipeline para criar tabelas analíticas. Cara, é bem bom, assim, o Big Query. Cara, eu também sou muito fã do Big Query.

**18:59 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Eu usei... Bastante já em diversos projetos. Aqui na AGEX a gente não usa o BigQuery nem a GSP. O que a gente usa da Google é só o Looker mesmo. A gente usa a AWS e o MySQL aqui com o banco de dados. Mas enfim, é isso. O BigQuery realmente é muito bom.

**19:20 — Júlio Gabriel Queiroz**
Sim, nossa.

**19:21 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Você comentou ali do Redshift, se não me engano, Também conhece com ele?

**19:26 — Júlio Gabriel Queiroz**
Sim, sim. Eu trabalhei com ele, só que assim, eu ainda estava meio que na posição um pouco júnior ali, mas eu trabalhei bem com ele. Ele é bem performático, tá? Ele é um dashboard, desculpa, ele é um banco de dados. Se não me engano, ele é um data warehouse, eu acho. Isso, isso aí. Ele é bem, assim, ele tem uma performance muito boa, o dialeto dele não tem muita diferença, ele tem bastantes funções também, que você consegue criar views, criar views materializados de forma automática. Isso é bem bom para você otimizar pipelines, mas eu... Eu trabalhei até um pouco, eu trabalhei um pouco distante dele, sabe? Eu trabalhei fazendo algumas consultas. No BigQuery não, no BigQuery eu acabei trabalhando com o pipeline inteiro, Ponto a ponto. Mas o Artificial é bom também. Se eu não me engano, a própria AWS tem uma plataforma de visoração de dados, eu não lembro agora o nome, mas acho que no começo dela era bem limitado, assim, né? Acho que o Luca é da Begazep. Se ele é, ele ainda ganha isso aqui. Não, legal demais, legal demais.

**20:32 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E você já trabalhou com API alguma vez? Já puxou dados de API de algum lugar?

**20:37 — Júlio Gabriel Queiroz**
Sim, já tanto puxei quanto eu criei, assim, APIs, né? No primeiro trabalho que eu tive com o desenvolvedor back-end Python, eu acabei criando uma API para servir o modelo de machine learning que um outro integrante do meu time criou, né? Só para dar um contexto, ele criou uma leitura de gabaritos, utilizando visão computacional. E aí, esse produto de dados... Acabou sendo um produto da empresa que a trabalhou, que é a Arco Educação. Então, era uma letra de gabaritos em que o modelo de machine learning lia as respostas e aí enviava todas essas respostas digitalizadas para a nossa plataforma, nosso banco de dados. E aí, a API que eu criei disponibilizava esse modelo de machine learning para o site, para a plataforma sites, se comunicar com o modelo, enviando as imagens e aí todo o back-end da API processava as imagens. Isso dava para o modelo fazer ali a leitura. Então, trabalhei, assim, não só criando, como também consumindo. No meu último emprego, tinha várias ferramentas que o de serviços utilizava que forneciam dados via API. Então, acho que o Mixpanel, ele é bem famoso, é uma plataforma de product analytics e, assim, a API deles é bem limitada, eu tive bastante dor de cabeça com isso. Eu tentava puxar muitos dados, mas sempre batia no limite de 20 minutos. Eu tinha que acionar os focos deles para poder puxar mais linhas e tal, mas é bem tranquilo. Principalmente com Python, acho que a API tem bastante experiência. Legal, bacana.

**22:15 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E como é que você está em relação à inteligência artificial? Quais ferramentas que você conhece? Qual que você usa? Me dá um panorama disso daí.

**22:23 — Júlio Gabriel Queiroz**
Cara, atualmente eu utilizo o Gemini, mas eu estou migrando aos poucos para o código, porque o Gemini eu já usava ele na outra empresa, então eu usei bastante ele, Gemini, porque como eu falei, lá tinha esse ecossistema do Google. Eu uso bastante, eu ainda sinto que tem muita evolução, tá? Parte do código, parte das análises, porque dados por dados, números por números é uma coisa, mas se não tiver nenhum contexto ali por trás das análises... Se você não tem uma curadoria do que você está pedindo, que você quer receber ali da IA, acho que acaba ficando um pouco viesado, sabe? Eu sinto um pouco de falha ali ainda, sabe? Mas assim, o ganho de produtividade é real, cara, isso aí é inegável, assim, acho que não importa o que os breves falarem, que, né, enfim, o ganho de produtividade é muito alto, cara, porque você deixa de fazer todas essas tarefas repetitivas, ou então um código que você sabe usar, só que, pô, você vai gastar 30 minutos escrevendo ele e a IA está em 10 segundos, por que não usar, entendeu? Então, pô, é tipo assim, você negar isso é meio que ser muito imprático, né? Então, eu uso e atualmente eu estou migrando para o Cláudio só para testar mesmo, assim, mas é mais para projetos pessoais, né? Cara, mas você demorou a migrar para o Cláudio.

**23:53 — Carlos Tadeu Lopes Filho (Instituto Experience)**
O Cláudio é um milhão de vezes melhor.

**23:55 — Júlio Gabriel Queiroz**
Cara, então, eu até usei ele no começo, assim, bem no começo, mesmo, porque ele não tinha cliente para o Windows, aí eu tive que migrar para o Linux para instalar ele, para ele, né, para entrar ali no terminal e tal, e aí quando eu fiz tudo isso, ele lançou para o Windows, fiquei muito, ah, mentira, cara, depois de fazer toda a migração para o Linux, e aí, mas eu voltava, voltava. O Diminar é muito bom para fazer pesquisa também, então, como eu estava, nesse projeto que eu estava, eu estava estudando e, né, fazendo código e tudo mais, aí eu acabei usando o Diminar, porque tem conexão com o notebook LM, que do Google, então, ficava tudo dentro de um sistema só, assim, aí foi por isso, mas eu vou migrar, vou migrar.

**24:37 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Não, perguntei porque aqui, a gente tem um viés muito forte de IA, tipo, muito forte mesmo, gente é AI first, e a gente usa bastante o Cloud Code, e com o nosso ganho, assim, de produtividade, de eficiência, velocidade, é absurdo, depois a gente começa a usar o Cloud Code e plugar ele nas nossas ferramentas aqui. Então, o nosso grande desafio... O desafio hoje é esse mesmo que você falou, da gente organizar, estruturar os dados, documentar, ter essa governança, para que a gente consiga utilizar o máximo potencial que a IA tem.

**25:12 — Júlio Gabriel Queiroz**
Nossa, isso é perfeito.

**25:14 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Então, isso é perfeito, porque para trabalhar aqui tem que usar o Cloud Code para tudo, tem que ser assim. Então, por isso que eu perguntei. Cara, boa, acho que da parte técnica, assim, legal, bacana, deu para ter um bom panorama aqui. Eu queria só entender agora, em relação ao seu modelo de trabalho, por exemplo, como você vai desenvolver um dashboard de Nuluker Studio. Normalmente, como é que funciona? A demanda já chega pronta para você, num documento, e você só desenvolve? Você também tem esse costume de ir até área de negócio, entender aquele escopo, mapear junto com a área de negócio, definir ali quais são as portas, definir, enfim, as páginas do Dash. Como é que funciona o processo de validação do dashboard? Você monta protótipo? Monta um mockup? Ou se você entrega direto? Como é que é o seu modelo de trabalho? Perfeito.

**26:11 — Júlio Gabriel Queiroz**
Assim, tá, acho que eu posso dar um exemplo, um exemplo um pouco mais prático. Na outra empresa que eu trabalhava, o que a gente fazia? Primeiro, eu tentava entender ao máximo qual que era o contexto em que aquele dashboard vai ser utilizado. Então, todas as perguntas que os times iriam responder usando o dashboard. Isso, para mim, acho que era o mais importante, assim. E, segundo, o que eu tentava fazer sempre era criar uma versão do dashboard que já entregasse algum tipo de resultado de forma parcial. Então, por exemplo, eu fazia uma parte do dashboard para ele já entregar alguma coisa para que a gente não fosse nunca o gargalo dessa operação, desse projeto, né? Principalmente nessa outra empresa, porque eu era o time de uma pessoa só. Então, eu tinha, não era um dashboard ou uma análise que eu tinha que fazer. Tinha que fazer várias no mesmo tempo. Então, eu sempre me policiava para fazer entregas parciais e prazos bem definidos. Então, uma vez que eu entendia qual era o contexto, qual era a análise que tinha que ser feita por meio do dashboard, eu criava um roadmap de entregas. Então, eu jamais segurava o dashboard para ser entregue como produto final. Eu sempre entregava ele de formas parciais, até porque enquanto a área ia validando a primeira entrega, eu já trabalhava na segunda. Então, de certa forma, a conseguia fazer esse trabalho paralelo, que tinha um ganho, assim, foi o que proporcionou o maior ganho de performance, assim, do meu time, né, das mesas entregas. Então, acho que eu poderia dizer que esse seria o framework que eu acho mais relevante, assim.

**27:47 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Então, você acha que você tem facilidade em trabalhar com mais de uma demanda de uma vez só?

**27:54 — Júlio Gabriel Queiroz**
Sim, sim, com certeza, com certeza. Tá, boa.

**27:59 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Boa, legal.

**28:01 — Júlio Gabriel Queiroz**
Acho que como um time de dados, isso é bem comum, você ter várias demandas, você ter vários processos, você nunca tem um projeto só que você está trabalhando, porque dados é algo que é consumido por vários times ao mesmo tempo, então acho que é muito difícil você estar focado em um projeto só, é bem difícil. Boa.

**28:24 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Cara, bom demais. Deixa eu ver aqui se tem mais alguma coisa que eu tinha notado, mas... Cara, uma ótima pergunta aqui. O que você acha que você tem que aprender e desenvolver aí nos próximos seis meses?

**28:47 — Júlio Gabriel Queiroz**
Tá, você fala da parte técnica ou de outras frentes?

**28:52 — Carlos Tadeu Lopes Filho (Instituto Experience)**
O que você quiser.

**28:54 — Júlio Gabriel Queiroz**
Tá, acho que da parte técnica, eu diria... Eu diria... Toda essa área que surgiu agora de agentes, eu acho que essa parte, pelo que eu tenho lido, isso tem sido bastante importante, esses agentes autônomos, desenvolver eles, eu acho que seria bem legal, principalmente para projetos em que eu tenha que fazer várias extrações de dados, várias tarefas repetitivas. Eu vi que é uma área que tem crescido muito e que, assim, é uma área que você não tem conhecimento até você realmente pegar para estudar, não é como se você tivesse uma premissa ali, porque eu sei isso, isso aqui vai ser mais fácil. Não, acho que é toda uma área nova, então acho que é bem importante saber ela. E da parte, assim, comportamental, acho que diria dizer não, assim, eu acho que ao longo da minha carreira eu acabava me empolgando muito e ficando, né, ficando muito cheio de demanda e acabava me prejudicando um pouco porque eu queria realmente entregar. Então, a... Como aprender a dizer não foi algo que me fez crescer, por mais que seja contra intuitivo, é uma coisa que não é muito natural para mim, porque eu gosto de entregar, quero fazer, eu acabo empolgando bastante, mas às vezes é muito para uma pessoa só, e aí acho que no meu último emprego eu acabei deixando isso levar um pouco mais, mas é isso, acho que eu tenho aprendido bastante, e foi o que mais me proporcionou esse crescimento, escolher bem as demandas que você quer trabalhar, os projetos que você quer se envolver, acho que é isso. Tá, legal.

**30:35 — Carlos Tadeu Lopes Filho (Instituto Experience)**
E como que você se vê assim daqui a um ano?

**30:38 — Júlio Gabriel Queiroz**
Cara, daqui a um ano, eu acho que eu me veria no papel mais de engenheiro de analytics, sabe, por mais que eu goste da parte visual do dashboard, da parte de fazer as análises mais, assim, eu gosto bastante mesmo, eu acho que a minha predisposição à parte técnica, à parte de código, parte de levantar infraestrutura. Criar, scripts e tudo mais, acho que levaria a dar um passo um pouco, a pivotar um pouco assim para a área de engenharia de data, engenharia de analytics, né? E eu acabo conversando muito assim, né? Nos outros empresas que eu tive, eu sempre desempenhei essa parte, né? Eu não ficava só na ponta de análise ou de visualização, eu sempre trabalhava como um todo. E aí eu tenho percebido que eu tenho muito mais afinidade a toda a parte de construção, né? do banco de dados e estruturação de pipelines, de dados e tudo mais. Embora eu goste bastante da análise, né? Toda a parte estatística, ciência de dados eu gosto bastante também. Mas é isso, acho que eu me vejo mais voltado para a parte técnica do código do que da análise visual. Acho que eventualmente eu vou acabar fazendo essa transição, assim.

**31:46 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Cara, eu acho que é o caminho mesmo, eu acho que é a decisão boa, assim, a tomar. E eu acho que, pô, a maioria das pessoas de dados vão ter que acabar se adaptando para saber de engenharia.

**31:58 — Júlio Gabriel Queiroz**
Mas, pô, bom demais.

**32:00 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Gostei do bate-papo aí. E uma dúvida, você tem disponibilidade para começar quando?

**32:07 — Júlio Gabriel Queiroz**
Cara, assim, eu teria que ver toda aquela parte da contratação PJ, né? Porque como eu nunca tinha trabalhado como PJ antes, aí eu teria que, assim, para dar um prazo... Não, isso aí é de boa, isso aí é de boa. Ah, então, acho que o quanto antes, assim, eu não tenho, assim, nada, assim, eu não tenho nenhum impeditivo, por exemplo, se for na semana que vem ou daqui a 15 dias, para mim é tranquilo. _(ACTION ITEM: alinhar com Amy + Gabriel; retorno ao Júlio até 5/jun, máx. 8/jun)_ Tá bom, beleza.

**32:33 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Aí, para ser bem transparente aí com você, eu conversei com você, conversei com outra pessoa hoje mais cedo também, tem essas duas pessoas aí por enquanto, eu vou conversar hoje lá com a Amy também, vou conversar aqui com o CTO, e o mais breve possível aí eu já devo dar um retorno, até sexta-feira, provavelmente. Certo.

**32:53 — Júlio Gabriel Queiroz**
Beleza? São quantas pessoas no time? Então, o time, ele é bem...

**33:00 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Eu entrei aqui na GX em fevereiro, para você ter noção, vai fazer quatro meses aqui agora, e eu entrei no mesmo cargo que você, eu entrei como um Data View, aí depois de, aí recentemente agora em maio, o Gabriel, que é o nosso CTO aqui, ele fez essa promoção aí para a Tech Lead, então eu estou como Tech Lead e tenho engenheiro de dados, então por enquanto o time é só nós dois, aí a gente está agora aumentando, contratando mais um Data View.

**33:30 — Júlio Gabriel Queiroz**
Perfeito, massa, massa, massa, é, tá, tá, tá, crescendo bem, bem rápido então, né, posso?

**33:36 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Tá, e pô, o que não falta aqui é trabalho, muita coisa, a empresa está crescendo muito, a empresa está crescendo muito, e a gente está precisando muito de alguém aí para chegar aqui, colocar a mão na massa, ajudar, aprender, e remar junto com a gente aí.

**33:54 — Júlio Gabriel Queiroz**
Bom demais, nossa, é isso mesmo, tá, então já contrata os dois logo de vez. Isso aí, velho, isso aí, tá certo.

**34:02 — Carlos Tadeu Lopes Filho (Instituto Experience)**
Mas boa, Júlio, muito obrigado aí pelo bate-papo, aí a M ele te dá um retorno aí até, provavelmente até sexta-feira, no máximo segunda-feira.

**34:10 — Júlio Gabriel Queiroz**
Tranquilo, combinado, cara. Obrigado mesmo. Valeu, até mais.

---

## Relacionados
[[Kleriston]] · _(mesmo batch de entrevistas — Data View / BI)_
