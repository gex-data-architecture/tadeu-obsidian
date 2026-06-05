---
tipo: raw-reuniao
origem: gravação (transcrição colada)
data: 2026-06-04
participantes: [Gabriel (CTO), Tadeu]
destilado_em: "[[2026-06-04 Sessão de trabalho — Estrutura e governança do vault (Gabriel)]]"
tags: [raw, reuniao]
---
# RAW — Sessão Gabriel × Tadeu — Estrutura do Vault (2026-06-04)

> Transcript bruto (verbatim) preservado como fonte. Ata destilada em
> [[2026-06-04 Sessão de trabalho — Estrutura e governança do vault (Gabriel)]].

00:11 Fala, mano. Opa, e aí, Gabriel, beleza? E aí, suave? Suave por aí. Tudo certo. O que você conseguiu evoluir aí?
00:21 Vamos lá? Bora compartilhar a tela aqui. Teve alguma evolução de Odin pra hoje? Oi? Teve alguma evolução de Odin pra hoje aí?
00:32 Teve, mano. Eu tava fazendo algumas coisas agora. Tá vendo aqui minha tela? Tô vendo, agora eu tô. Boa. Então, a estrutura de palma, Ela está assim, tem a parte aqui de conhecimento, então eu deixei as calls aqui, decisões e dossiers.
00:52 Aí beleza, aqui em dashboards eu coloquei todos os nossos dash, então por exemplo aqui o dash de afiliados, tem o link, tem aqui o resumo, quais são as pontos de dados que a que estão alimentando, então é o dashboard de Affiliate Nutra, Affiliate Nutra USD, de onde elas derivam, né?
01:13 Beleza, atualização, qual que é a procedure que está rodando, então tem isso para todos os dashs aqui, legal, Boa, aí, Aqui no Data Lake, deixa eu mostrar aqui primeiro.
01:31 Então, aqui tem todo o catálogo lá da AWS. Então, todos os databases, Develop, Prod, que é o bronze, silver e gold, quantidade de tabelas em cada uma.
01:43 Na bronze, essas são as tabelas. Na silver, Prod Bronze, enfim, vai listando aqui todas as tabelas. Aqui são os jobs de ETL.
01:55 Então, esse daqui por exemplo é o MySQL to Bronze Develop. Então tem todos os jobs aqui. Aí tá linkado com alguma outra referência?
02:06 Tá linkado. Dá pra ver aqui os execuções, tem o script, então tá tudo aqui né, Step Functions que é a orquestração, Bronze to Silver até a próxima.
02:25 Tchau. By Goods Gold, tem tudo aqui, os crawlers, que é o robô que faz a categorização, a catalogação de tudo.
02:36 Os agendamentos. Esse aqui que tá parado, que não tá ativo, esses aqui são os ativos. Então tem bastante coisa aqui pra limpar que não tá rodando.
02:54 Boa, enfim, aqui tem todos os jobs, tem as orquestrações, tá tudo aqui. Tudo que você pôde jogar de informações já está aí?
03:04 Como assim? É tipo, todos os inputs, então o scanning do nosso banco MySQL completo procedures, views, tabelas Uhum Tá tudo aqui VDL, campo, explicação isso no Atina também, os jobs toda a arquitetura medalhão que a gente tem que a gente tem, tipo, tudo que a gente usa a nível de inputs A explicação
03:28 dos campos não, só a explicação das tabelas dos campos, acho que tem só da silver, da gold e da buygoods por enquanto, mas de todas as tabelas não tem.
03:40 Então, por exemplo, quer ver aqui, tem que ter as principais, por exemplo, tipo, abaigudos aqui, né. Vamos pegar aqui a Gold, por exemplo.
03:52 Então aqui tem toda a documentação da Gold, como ela é gerada, particularidades, tem que estar tudo aqui. Chave de agrupamento.
04:01 Legal. Não, mano, não sei porque a formatação do seu vídeo não tá boa não, velho. Que tabela que é essa tabela bugada?
04:09 Oi? Tá bugado, ó. Isso aí era pra ser Se inscreva no canal e ative o sininho. porque está muito diferente do meu, por exemplo.
04:39 Eu sinto que, pelo menos a nível de organização e formatação, o meu está bem acima, saca? Seria legal dar uma checada, porque existem alguns agentes e skills que se instalaram na sua máquina que são agentes que são otimizados por Obsidian.
04:55 É Obsidian Sea Ally, tá ligado? Então isso dá uma diferença considerável. É uma boa, se você dá uma revisada com o Davi, a nível da estrutura, tá ligado?
05:05 Que vai performar mais. Beleza. Entendi, mano. Mas, tá, vai por aí. Tá, aí aqui tem da Silver, eu coloquei também aqui uma amostra da PI, uma amostra do Abiruk, enfim, pra ter o conhecimento aqui, né?
05:19 deixar registrado. Então, o que vem na API? E aqui exemplo. Legal. Você já usou o próprio cloud para extrair essa amostra?
05:30 Ou você imputou mesmo? Não, acho que a amostra eu que imputei. Ah, tá. Será que você poderia ter mandado a credencial e pedido para ele fazer uma É requisição, né?
05:41 É, poderia, poderia. Seria até mais fácil, mas ok. Boa, então, Aí a Carte Poder não tem nada aqui, nem Clickbank por enquanto.
05:50 Aí a nível da documentação, rapidinho, abre a barriga da documentação ali. Amostra Pay by Goods, Amostra B-Rook, dentro de By Goods tem o que?
06:05 Esse é o índice? É, é só descritivo, o índice. Mas você explica, tipo, a lógica da regra de negócios? Porque lembra que a gente foi em paul várias horas?
06:19 Sim, na Silver tem isso. Aqui tá explicando que a gente tá considerando o webhook como fonte da verdade, aí o motivo, aí API que é o complemento, aí como que a gente unifica, a regra, Webhook tem prioridade, parte do sub-IG, essa é a classificação, todo o fluxo aqui de execução.
06:49 É aqui o esquema da silver unificada. Aqui é só o esquema e embaixo tem o dicionário dos campos, campo a campo.
06:59 É aqui que fica bem detalhado com os partilhares da ASIO e o cálculo. Não sei se é conhecimento mais geral da documentação do dado, mas ok, depois a gente pode reformatar ele.
07:27 Mas legal, beleza. Isso aí é basicamente o documento que a gente tinha antes no Google Docs, né? Isso, é basicamente isso.
07:34 Entendi, entendi. pouco mais completo. Eu não sei se você grava, tem aquela call que a gente tinha feito junto que tem 3 ouros, acho que tem bastante contexto ali também que pode ser daora você jogar ai eu vou te mandar eu vou até colocar no meu também mano porque to fazendo alguns projetos de dados
07:50 inclusive já comecei a usar o logbook mano o unico ponto daquela reunião que a gente fez la, que a gente acabou mudando muita coisa depois, não sei se pode atrapalhar é, você pode testar Tá, aí antes de você jogar, Você criou algum skill de transcrição de ligação?
08:06 De qual? Não, acho que não, Eu tô pegando a transcrição e jogando direto no Cloud. Entendi, Tô fazendo isso. Tem jeito mais fácil?
08:15 É, você cria skill. O ideal, Tipo, sempre quando eu vou inputar algum conhecimento, eu inputo de maneira estruturada. Porque, Deixa eu te mostrar aqui até pra te passar a skill.
08:25 Tipo, eu enxergo duas maneiras de jogar conhecimento aqui no Obsidian. A primeira é através de reunião, que a gente tá fazendo agora, que eu tô gravando e que você vai gravar baixo conhecimento.
08:35 E a segunda é através de documento estruturado. Então, sei lá, eu tenho documento do Google Docs, épico, é documento estruturado.
08:43 Ou então, por áudio que eu gravo, Ah, vou por alguma outra fonte, tipo, externa que não seja reunião, tá ligado?
08:50 Então, eu tenho duas skills pra fazer isso. Tem a skill 1, que ela é específica pra transcrição, pra gravação na verdade, e ela pega dois formatos, que é o formato do LUM, que é o que eu costumo usar, e o do PHANTOM, que aí são estruturas diferentes.
09:08 diferentes né, e eu tenho barra poplite, que ele é pra isso aí, pra documento estruturado etc. Aí o obsidian aqui, mano, isso aqui vai ser até ponto que, até de sugestão, que eu tô vendo aí, que na minha visão, a maneira como você fez a organização de passos de governança, eu tô achando pouco confuso
09:24 , desorganizado, mas isso é bem fácil de fazer, de reorganizar, e isso era uma coisa que eu tava me incomodando no começo, que eu fiz o meu também.
09:32 Então, Então, já de cara, o que eu separaria aí? Conhecimento estruturado, conteúdo de sistema. O que eu considero sistema? Tudo aquilo responsável para fazer o VALT rodar.
09:44 Então, por exemplo, Raw Files. Aqui tem camada bronze. Então, todo o conhecimento que eu deixo aqui, ele fica dentro da pasta Raw Files, e ele fica armazenado entre três categorias.
09:57 Aí eu tenho armazenamento de documento, aí que tem pendente processada, né? Então, aqui tem todo o documento que eu deixei ler aqui dentro.
10:04 Então, é exatamente o mesmo conteúdo que eu deixei ler, que tá aqui, tá ligado? Exatamente o mesmo conteúdo. Aí tem as notas, que tem só que foi brainstorming que eu fiz.
10:16 Então, exatamente o conhecimento tá aqui. E as reuniões que o Open Minds tem. Então, tudo junto. Toda reunião que faz, ele vem aqui e ele armazena todo o transcript, tá ligado?
10:25 Então, na hora que você quiser reprocessar, se você quiser fazer qualquer tipo de coisa, tá aqui. Então esse conhecimento não fica perdido, tipo, nas notas, né?
10:33 Porque, por exemplo, se você pegar a call que a gente tá fazendo aqui e jogar o transcript, só pedir pra ele popular o vault, vai dar certo.
10:42 Só que se você quiser reprocessar, por exemplo, exemplo, pra fazer uma reorganização do vault, igual vai fazer agora, você não consegue.
10:49 Então é da hora isso aqui, justamente pra pegar alguma informação que, sei lá, que veio faltando, pra você reorganizar, enfim.
10:57 Aí o seu, não sei se tem essa pasta, mas quando eu criei com o Davi já veio essa pasta template criado, que aí, tipo, isso aqui, acho que é padrão do Obsidian, que ele cria os templates para cada, como ele destila o conhecimento em notas, ele tem que destinar seguindo algum modelo, né?
11:14 Aí tem uns templates, isso aqui é sistema, na prática tem essa pasta também. Aí, mano, que foi o insight que eu peguei ontem, que eu até te mandei o áudio, referente à memória do Cloud, porque você vai perceber, cada dia que passa que você vai conversar, que você vai usando o no Obsidian fica cada vez
11:32 melhor, mas não fica só cada vez melhor porque a sua base de conhecimento do Obsidian está ficando melhor necessariamente, mas porque o seu Cloud Code da sua máquina, da sua conta, ele armazena memória e a memória ele não é destilada pelas pessoas.
11:50 Então, por exemplo, o Gustavo colocou no meu repositório, colocou no PC dele e, mano, estava burro, não estava tão bom quanto quanto o meu, nem de perto, nem de longe, na verdade.
11:59 Então, fui investigar, aí eu descobri que tem essa porra da parada da memória do Claudio, que ele vai criando, tipo, memórias, que são, que o Claudio, toda vez que você dá o prompt, ele lê isso aqui, sempre antes de dar uma resposta.
12:14 Então ele lê primeiro a baixa de conhecimento, e depois ele consulta o Valt, e aí ele te dá a resposta.
12:18 Então, isso aqui é Que são meio que as skills, né, tipo, são as memórias que o Cloud, É como se fosse cada neurônio que o Cloud armazenou de algum conhecimento que ele aprendeu conversando com você, tá ligado?
12:30 E aí, isso aqui é muito bom porque quando eu jogar, eu vou fazer o teste ainda com o Gustavo, eu ainda não cheguei a fazer o teste, mas qual que é a ideia?
12:38 Quando qualquer pessoa conectar, mesmo que seja com a conta zerada do Cloud, que não Se não tem a base de conhecimento que você tem, por exemplo, que você está construindo a parada, ele vai conseguir ter o mesmo resultado que você.
12:49 Então, esse é o objetivo. E aí, essa base de conhecimento do cloud, e o cloud em si, ele é guiado por esse documento aqui, que ele fica na raiz.
12:57 Então, sempre que o cloud vai te responder, ele começa por onde? Por aqui. Essa é a base. Então, isso aqui é a instrução de uso do cloud a raiz.
13:07 respeito do seu VALT, então ele vai primeiro ler esse documento, aí no documento eu aponto, eu falo assim ó, você tem que ler abaixo de conhecimento antes de fazer qualquer coisa, então ler primeiro, então ele vai vir aqui na abaixo de conhecimento, ele vai ler e aí sim ele vai te responder, tá ligado
13:25 ? Aí tem várias instruções aqui, tem a instrução do sistema, tem várias paradinhas, inclusive Eu não sei se o Davi, no templater que ele te mandou, se tá instalado esse superpowers.
13:37 Esse superpowers é tipo plugin, mano, que, velho, ele ajuda muito na estruturação do conhecimento. Fica bizarramente bom. Isso é ponto, também, que não sei se tá instalado, que a gente pode checar junto aí.
13:49 Enfim, então, E como que tá sendo alimentado ali a base de conhecimentos? Já tá meio que automático, tá bom? É, esse daí.
13:56 Mano, isso que eu, Então, o que que pega? Quando eu identifiquei isso, basicamente eu já coloquei ele pra fazer de maneira automática.
14:06 Então assim, toda vez que eu tô conversando com o Claudio, que eu vou fechar uma sessão, ele vai me perguntando ó, cê quer armazenar esse conhecimento aqui cê quer armazenar essa memória aqui no sistema?
14:18 Por quê? Pode ser que agora você uma memória eu queira armazenar, outra memória talvez eu não queira. É a mesma lógica de uma transcrição de reunião.
14:25 Deixa eu ver se eu pego exemplo aqui, que eu joguei algumas reuniões ontem. É ó, ontem, foi exatamente esse chat aqui que eu tava fazendo transcript de reunião.
14:50 Então, é porque aqui não tá pegando tudo, mas eu dei o barra transcript extractor, mandei o link da reunião e o transcript, aí ele processa ó, de maneira estruturada.
15:01 Aí ele identifica ó, Herbrand não tem nota em pessoas. Então pô, é uma pessoa nova, que não tem nota em que a gente precisa estruturar.
15:09 Aí já pegou o contexto claro. Herbrão, contador, assessor de pessoas, não sei o que. Aí algumas coisas ele vai errar.
15:15 Só que antes dele destelar isso aqui no Obsidian, ele me pergunta. Então, ele vai me dar resumo aqui. Então, sei lá.
15:23 Não, o que foi antes aqui? Pera aí. É, aqui ó, tem o quadro completo. Herbran Hermides é igual a contador assessor da estrutura internacional, hoje sem nota em pessoas.
15:33 SK101, nananã, com duas, Infiro duas vozes. Gabriel e Herbran. Gustavo Estado Mais está viajando ausente. Três eixos. Realocação de função.
15:42 Sistema de Family Office. Updates da estrutura tributária. Aí, e a data, aí ele me perguntou a data né, que ele faz algumas perguntas, aí eu respondo, aí eu coloquei a data e tal, aí ele continua escrevendo.
15:54 E aí no final, ele vai destilar, então ele coloca aqui ó, destilar 101, entre você e o Herbrand, o que foi criado atualizado.
16:03 Aí ele já salva por padrão, isso aqui é padrão, então ele já salva no raw files, Ele já destila a nota dentro de pé.
16:10 pessoas, erbran, 101, com a data da call, qual foi o tema da call, já com resumo, discussão, aí ele já identifica entidades novas, já atualiza as entidades que já existem e alguns pontos para revisar.
16:22 Aí eu vou lá e falei que ele citou a minha namorada, ele identificou a Erika, o nome da minha namorada é Maggie, enfim.
16:32 Aí eu fui lá e corri junto com o que tem que corrigir, e depois eu dou o commit e faço o push pro Git.
16:38 Então ele não destila aqui no Vault antes de eu revisar o que ele fez, sacou? Entendi. Então eu jogo o conhecimento de maneira estruturada, e aí quem faz isso é a Skill, e aí a Skill tem as regras.
16:49 Basicamente isso. Enfim, aí à medida que você vai conversando com a sessão, aí tipo, esse contexto que eu te expliquei de como deixar lá a nota de reunião, é a mesma nota lógica para a memória do cloud, porque ao longo da sessão, se ele identifica que tem algum assunto novo que ele aprendeu e que não
17:08 está deste lado do vault, não está registrado na memória aqui, dentro do obsidian, ele vai perguntar, posso atualizar a base de conhecimento da memória do cloud com isso aqui, aí você vai confirmar, isso aqui beleza, porque às vezes, por exemplo, eu posso usar isso aqui para fazer para a minha parte
17:22 pessoal, de alguma forma, como eu tenho uma parte pessoal aqui. E aí tem parte pessoal que eu não quero colocar aqui para todo mundo, então a memória da minha parte pessoal, ou do tom que eu gosto de falar, isso eu não vou deixar lá para o sistema, eu vou deixar dentro da minha memória local.
17:40 Agora tudo relacionado à empresa, não, eu vou deixar lá para o sistema, sacou? Aqui. Várias outras coisas. Aí tem outras Skills que eu tenho, por exemplo, aqui tem catálogo de Skills.
17:51 Então todas as Skills que eu tenho. Aí eu tenho Skill de Catálogo, que toda vez que eu crio uma Skill nova ou atualizo, ele atualiza o catálogo justamente para eu conseguir lembrar as Skills, porque tem muitas.
18:00 Aí tem a Skill de Lucratividade de Produto, que é aquilo que eu te expliquei, que eu fiz lá para o Gustavo.
18:05 Tem Planejar o Dia, Planejar a Semana. E aqui já tem, tem tipo a skill em .md, então posso até te mandar aqui, skill populate, e tem a skill que é o principal, populate e o transcript extractor, e também tem a skill que é o sincronizar o conhecimento, que é da hora.
18:30 Eu vou te mandar essas três, aí você pode adaptar, tipo, fala que você trocou ideia comigo e tal, e que aí você vai implementar algo semelhante, e aí você adapta se você achar que faz sentido também.
18:43 Deixa eu te mandar aí. Beleza. Deixa eu aqui, é, não sei se tem outra forma de mandar, mas foda-se, vai assim mesmo.
18:52 Então eu tenho essa daqui, sincronizar conhecimento. Te mandei as três aí. E aí, mano, sempre que você vê que existe alguma coisa que você precisa fazer de maneira mais estruturada, você cria skill, tá ligado?
19:05 E aí você mesmo pede pro Claudio, ó, eu quero criar skill XPTO. Aí só faz check pra mim, dá Deixa eu ver a sua tela aí, rapidão.
19:14 Ah, já tô compartilhando. Vê se tá com o Super Power instalado, mano. Clica no, Clica em pesquisar ali em cima.
19:23 Super Power. Não. Pô, véi, mano, o Davi tem que te ajudar a instalar. Joga, abre terminal no Cloud. Tinha que fazer uma revisão mano, abre no terminal ai Como é que abre, aqui né?
19:36 Não, do lado, isso No terminal aqui ele fica meio zoado Mano, isso não ta dando direito É só você mover mano Pega a janela do seu terminal e move lá pra cima Isso, acabou, aí executa o cloud Sabe que você pode usar comando que se chama cloud bypass, né?
19:56 E aí ele não vai ficar pedindo permissão o tempo inteiro, esse comando aí ó Que é chatão, é, da barra, É, não é o, Não, não é barra não, tira a barra aí, aperta, acho que é ctrl Contra o C, para você sair, várias vezes, vai dando contra o C, pronto, joga o comando que eu te mandei.
20:30 Você está no 4.6 mano, você tem que mudar o modelo também. ponto oito. É assim? Mano, copia, copia coluna. Não, não vai dar certo não, você tem que você tem que sair de novo.
20:49 Coloca yes, accept. Ele ta bem zoado Aperta 2 Mano, no terminal você não usa mouse Use de novo aqui Caralho, bugou tudo Mano, fecha o terminal e abre outro Ele ta bugado nesse terminal Integri, é.
21:20 Por que que ele abre o celular do lado? Não dá pra ver. Tá. Ótimo. Aí dá a barra model. Cof.
21:39 Caralho, só não tem? Por que será? Só é max gold mil? Que loucura. Sparks libera só pra algumas pessoas. Tá, beleza.
21:48 É, só, Só dar a entra aí pra confirmar. É, joga aí, tipo, É, Deixa eu só ver qual que é o nome, mano.
21:57 Super, Fala assim, pede pelinho. instalar pra você o plugin superpowers superpowers e o obsidian CLI É, acho que é o principal isso daí.
22:43 Tá, só voltando aqui, olha a minha tela aqui de novo, aí tipo assim, então só voltando para a explicação, tipo, no final das contas a IA não vai fazer milagre, né, a gente precisa dar o prompt, tem que saber direcionar.
22:59 Então, só o que eu estou querendo dizer para você, é que dá para melhorar bastante a governança e a estrutura.
23:05 de pastas que cê fez, porque tá muito centralizado, tá ligado? Tipo, é como se tivesse, não sei mano, acho que tá muito centralizado e tem como criar pastas mãe pra que o conhecimento fique destilado de maneira mais estruturada.
23:21 Então por exemplo, tudo que é sistema fica na pasta do sistema, fica armazenado, e fica mais fácil dar até do próprio, da própria árvore.
23:29 ela conseguir acessar a informação. Aqui é o documento do cloud, está na raiz, não dá para tirar, beleza. Aí aqui tem o daily notes, que é umas notas que dá para criar, aí no meu caso tem guia de reunião, enfim, então no seu caso, por exemplo, deixa eu até te mostrar, abre suas pastas, por favor.
23:48 Por exemplo, aí, ó, DBDatatinho. DB Institute Experience, abre os dois, por exemplo, DB Data Team, o que é isso aí?
24:00 Aqui é o novo que eu criei que a gente vai migrar as coisas para cá. Na minha visão, não acho que faz sentido ter duas pastas que têm a mesma natureza, você concorda?
24:15 de dados, estrutura de banco. Por que as duas estão na raiz? O ideal seria colocar na minha visão banco de dados, ou estrutura de banco de dados.
24:29 Aí o que vai ter nessa pasta? Tudo relacionado ao nosso banco? E o que é tudo? São os eventos? São os triggers?
24:38 São as sei lá, a tipagem dos campos, enfim, então tinha que dar uma organizada nisso na minha visão. Então, criar uma pasta Banco de Dados, aí vai ter BancoXPTO mais que L.
24:53 BancoXPTO, nesse caso, vai ser mais que L também, porque a gente tem dois no mais que L. Enfim, aí outro, se a gente vai usar PostgreSQL, no PostgreSQL.
25:01 E aí eles vão ter a mesma estrutura de pastas, porque vai seguir padrão. Então, beleza. Dentro de eventos, qual que é o padrão que a gente vai seguir em eventos?
25:13 E aí ele vai preencher tudo isso seguindo o padrão. Então na hora de fazer a leitura vai ficar muito mais organizado e estruturado, tá ligado?
25:20 Enfim, no geral, eu acredito que dá pra você fazer uma reorganização boa aí na estrutura de pastas. Para que o conhecimento dele fique mais bem estruturado, saca?
25:29 E aí, você acredita também que, por exemplo, o Athena estaria dentro dessa pasta do banco de dados? Então, mano, é uma boa pergunta.
25:38 É porque, velho, Eu não sei te responder isso, assim, agora, porque teria que pensar com a IA, entendeu? Sim. O que que eu sugiro, mano?
25:47 Vamos instalar esses plugins aí, que eu acho que vai dar uma melhor experiência. Melhorada boa pra você, mas o que eu sugiro é você abrir uma sessão e você pedir pra, agora que você tem uma noção já do Obsidian, você pedir pra AI pra te ajudar numa nova arquitetura de pastas, saca?
26:05 Boa, concordo. Então pede pra ele te ajudar a criar novo esqueleto de pastas, fala que você tá achando, aí dá alguns exemplos que você não tá gostando, tipo por exemplo o que eu te falei do banco.
26:13 Que a gente tá com duas pastas, tem a mesma natureza na raiz. A gente não quer fazer isso. Então, porra, como que a gente pode fazer pra estruturar esse conhecimento de uma maneira que fique em uma ordem cronológica melhor, saca?
26:26 Aí, por exemplo, ali, ó. Entrevistas. Entrevistas, é, talvez, Eu não colocaria entrevistas assim, eu colocaria uma aba Pessoas, por exemplo.
26:35 Então, Pessoas. Tá, quem que é o time de dados? Ou então não só o time de dados mano, todo mundo que se, Que em algum instante, É uma boa.
26:45 Todo mundo que em algum instante tem algum tipo de, De contato com vocês. Então você faz uma call com algum cara da área de negócio.
26:54 Aí, na hora que você acionar o, A skill, Ele vai perguntar, você quer que eu crie essa pessoa? que dentro da pasta pessoas, eu acho bom criar, mesmo que não seja da área de dados, porque na hora que você vai fazer uma análise, na hora que você vai fazer uma modelagem e vai criar uma gold, ele já tem
27:11 contexto da área de negócio, quem que é a pessoa, o que que ela faz, por que que ela faz, tá ligado?
27:17 E junto a isso, como você colocar também o seu próprio time, obviamente. Então, o Léo, o que que o Léo faz?
27:22 O que que o Léo tem que melhorar? Você, o que que você faz? O que Você tem que melhorar qual que é a estrutura, aí tem como ter uma subpasta dentro de pessoas que vai ser entrevistas, sei lá, às vezes dentro de entrevista você pode ter o quê?
27:39 Teste técnico, porque entrevista normalmente tem algumas etapas, você tem ali a triagem e você tem o teste técnico, por exemplo, e você tem os aprovados, ou o currículo, sei lá.
27:49 Então, você pode estruturar isso em formato de pastas, aí algumas coisas vão fazer sentido, outras não vão. Então, é bom você ir separando por competência, ir agrupando as coisas, porque pra você enxergar vai ser muito melhor, tá ligado?
28:02 Mas isso aí, tipo assim, a resposta não consegue te dar, mano, aí tá ajudando o caminho, aí você joga na E, aí você vai pensando junto, saca?
28:08 Boa, é, faz isso mesmo. Aí, sei lá, Por exemplo mano, é tipo, porque acho que a gente tem que focar no 8020, o nosso principal problema hoje é a questão do onboarding das fontes de Gatorade, beleza.
28:25 Aí como que a gente, como é que estruturaria isso, né, tem que pensar mano. É, eu acho que Acredito que o on-board tem que ser skill, e quando tiver aqui, por exemplo, documentação fontes de dados, a gente tem a ByGoods aqui que já está praticamente completa.
28:47 Aí a gente vai preencher aqui o clickbank, aí a partir disso a gente cria skill, on-board de novas fontes. que vai ter o conhecimento dessas duas fontes aqui, que estão documentadas, né?
29:01 O que você acha? Sim, de fato. É, tipo, É porque eu acho que você vai ter que pensar de uma maneira mais cronológica.
29:10 Então, por exemplo, quando a gente vai onbordar uma nova fonte, quais são as etapas? Então, o que eu preciso saber para, para abordar uma fonte nova, por exemplo, a BuyGoods.
29:19 Não sei nada de BuyGoods, o que eu tenho que fazer? Então, sei lá, primeira coisa, pegar a amostra, né? Então a gente tem que pegar a amostra dos payloads, a gente tem que conectar o Abirrook em algum local, ou API em algum local, fazer uma requisição e identificar os padrões.
29:33 Beleza, aí fiz isso, aí eu tenho que, tipo, fazer o de para, né? barra, fazer o discovery para entender o que cada campo ali significa e como ele vai se encaixar no nosso padrão hoje que atualmente é o tabelão, beleza?
29:51 Sim. Enfim, aí você vai avançando, aí beleza, identifiquei, tá, aí isso vai entrar na bronze, aí isso aqui vai entrar na silver, aí depois vai entrar na gold, então tipo, tem que dar o máximo de riqueza de detalhes possível.
30:04 Possível, porque a Buy Goods, por exemplo, que a gente já tem estruturado, estando bem feito, dá até para você testar.
30:12 Você pega a Clickbank e você testa. E finge que você vai onboardar a Clickbank do zero. Faz teste, vê se vai desempenhar bem, por exemplo.
30:20 E vai se comparar. E aí, mano, Tem aquele documento base lá também que eu tinha te mostrado. Aquele lá já tem o, meio que por passo a passo para o onboard nova 11, dá para reutilizar aqui.
30:31 É, com certeza, já é mais contexto, com certeza, sem dúvida. E aí, é mano, é porque, velho, na parte dos dados em si, você vai saber mais do todo do que eu, tá ligado, mas, por exemplo, o que eu acho que seria interessante aí é a gente ter uma pasta, talvez, dedicada só para arquitetura.
30:53 Aí tem que jogar com a AI também, mano, pra entender, mas, sei lá, como que funciona a regra que rege o setor de dados hoje?
31:03 Como é que é a arquitetura? Então, a arquitetura, ela funciona nesse formato aqui. A gente tem isso, isso, isso. Atualmente a gente tá com mais que L, só que a gente quer fazer uma migração, quer ir pro lovable, por exemplo, e só tem pra ficar com o S3 mesmo, enfim, então, só que, obviamente, saindo
31:21 nível de detalhe absurdo e quebrando em notas, etc, saca, com pasta, com subpasta, e tipo, e criando uma linha lógica, sacou?
31:31 É porque, por exemplo, agora a minha tela de novo, é porque mano, não tem antes e depois, na real, deve ter no Git, só que eu não sei acessar, mas tipo assim, quando Quando eu criei, estava exatamente igual o seu.
31:40 Eu estava muito descentralizado ao acesso. Te dar exemplo. Qual que foi o meu objetivo aqui? Eu quero criar uma visão estratégica da empresa e uma visão operacional, caso eu queira aprofundar.
31:53 Então, por exemplo, a visão estratégica da empresa, uma visão estratégica do departamento de atendimento. Não, mento. uma visão estratégica do Departamento de Dados, por exemplo.
32:07 Só que, tipo assim, caso eu veja que está com problema no Departamento de Dados, eu queria poder aprofundar naquilo ali para entender o motivo exato, conseguir fazer requisição na API, conseguir ler documentação e o caralho.
32:21 Então, eu meio que estava enxergando em duas camadas. E aí, o que a EAI tinha criado inicialmente? Ela tinha criado, criado aqui uma pasta estratégica, aí dentro dessa pasta estratégica, ela tava dividindo, tava colocando todas as BUs, que são esses aqui, e todos os departamentos dentro dessa pasta estratégica
32:38 , e aí ela criou uma outra pasta na própria raiz, que é essa pasta aqui, e ela repetiu as mesmas BUs, os mesmos departamentos nessa outra pasta, então tipo assim, eu tava com meio que tipo A B.U.
32:50 e o departamento, eles estavam se repetindo duas vezes, e pra visualizar isso, na minha opinião, é uma bosta. Eu prefiro visualizar, tipo, na mesma competência.
32:59 Então hoje, se eu quero saber de algum departamento, tipo, departamento de dados, se eu quero saber do departamento de dados, independentemente se é visão estratégica ou operacional, ele tá na mesma linha cronológica, sacou?
33:11 Então dados, Aqui, mano, tem todas as decisões estratégicas. Então, por exemplo, isso aqui é uma decisão subestratégica. Isso aqui também, que eu nem lembro o que é, mano.
33:19 Isso aqui foi o, Stack Arquitetura de Dados, Ah, tá. Foi da consultoria com o Flávio. Enfim, é uma decisão estratégica também.
33:28 Aí você também, que eu tinha te promovido pra Tech Lead, também é uma decisão estratégica. Aí tem os projetos, que aí são os projetos futuros que a gente tem que desenvolver, etc.
33:38 que, por exemplo, é uma modelagem dimensional. Aí tem as reuniões do time de dados que estão aqui também, que vão alimentar esse stack aqui.
33:46 E aí, dentro da operação, quebra mais, tá ligado? Então, por exemplo, aqui tem indicadores e tem as regras de negócio.
33:54 Então, dicionário de dados, mano, é algo totalmente operacional. Tá lá no chão de fábrica. Só que, tipo, tá na mesma linha.
34:00 Então, tudo que eu tenho do departamento de dados tá aqui, não tá quebrado, tipo, ah, nessa pasta, aí nessa subpasta tem não sei o que, e aí na outra tem dado de novo que tá se repetindo, tipo, não, tá centralizado aqui dentro, sacou?
34:15 E aí só ponto também que é interessante, até pra você colocar como ponto de ajuste pra sua AI, é pra ela não criar pasta de maneira desequilibrada.
34:25 desnecessária, porque por exemplo, ó, área de dados, dentro da parte de operação, pode perceber que tem duas pastas aqui, beleza, aí agora eu vou entrar, sei lá, deixa eu ver qual que tem mais, acho que atendimento, ó, dentro de atendimento já tem três pastas, Aí eu vou entrar no ABU.
34:46 Vou pegar aqui, Vou pegar esse mesmo. Essa aqui eu acho que tem bastante coisa, é, aqui tem três também, aqui vai ter pouca, deixa eu ver a afiliação, é, ou seja, percebe que eu só tenho pasta onde tem conteúdo, porque, tipo, você vai abrir aqui, por exemplo, vai estar cheio de pasta, só que não tem
35:07 conteúdo nenhum, é lixo, não faz sentido, então ele só cria a pasta. quando existe conteúdo para aquele destino, sacou? Então, a parte dos dados aqui, por exemplo, não tem o playbook ainda.
35:19 Só que, quando eu precisar criar o playbook, vai estar aqui. E tudo isso está na raiz do projeto. Então, o próprio cloud, se eu não me engano, Olha lá, o sistema, a estrutura, o maquinário.
35:32 Tá vendo? Sistema of all files, camada bronze imutável, só input externo e genuíno. Aí tem a convenção de nome. Aí tem retenção obrigatória, que eu até te expliquei que toda reunião ou todo input de formação ele salva na camada bronze.
35:45 Aí os templates, as revisões de skills, os superpowers também. Enfim, então, Tipo, essa estrutura do conhecimento aqui, ele ajuda muito, saca?
35:54 Muito, mano. E aí você vai ter que ir ajustando, aí você ajusta e você vai ver, porra, isso aqui vai, Acho que a pergunta que você tem que se fazer é, se você for se guiar pelas pastas, fica fácil?
36:08 Você ir abrindo aqui, você consegue acessar a informação de forma fácil? Se você responder que sim, beleza, então tá bem construído.
36:16 Entendi. É, o principal primeiro vai ser, se alimentar essa pasta cloud aí e criar os sistemas, né? Começar por isso.
36:29 Cara, assim, vamos, Primeiro eu instalaria as duas skills que eu te falei que acho que elas vão ajudar bem. Pelo que o Davi me falou, tipo, ajuda bastante essas skills que ela meio que dá boost na forma como usa o Obsidian.
36:43 Tá ligado? Ela ajuda a planejar melhor, a destilar melhor as notas. Então primeiro eu começaria instalando essas skills, depois eu instalaria as três skills que eu te falei, que é a skill de transcrição de ligação, de call na verdade, a skill de popular, de populate, que é pra popular basicamente com
37:05 documento, então por exemplo você vai devagar. vários documentos que a gente até já tem do time de dados, que é Google Docs e tal, que aí você vai utilizar para popular documento externo, ou fonte externa.
37:14 E a terceira é o de sincronizar conhecimento, que é para pegar o conhecimento da memória do seu Cloud Code via local, e você deixe lá, para dentro em si, do próprio do próprio mecanismo do Obsidian, que é o conhecimento que você vai estar Tchau!
37:31 compartilhando com quem vai colocar no seu repositório, tipo o Léo, que vai trabalhar em conjunto com você, tá ligado? E aí, você vai ter meio que a base.
37:39 Aí, tendo essa base, foi o que eu até te falei, abre uma sessão, pede pra Amanda, ele dá uma, ele age como tech lead de dados pica, aí joga como input a call do Flávio, que a gente teve ontem, joga como input a call do que eu te mandei aqui e pede pra ele reestruturar e te dar uma nova sugestão de esqueleto
38:02 de pastas, aí você dá alguns exemplos de algumas coisas que você não tá gostando, aí vai ter o contexto da minha calça que eu expliquei também, então vai ajudar pra caralho, e aí refaz o esqueleto, que aí você vai ter uma noção do time de dados de uma maneira melhor e mais acertível.
38:14 E aí, depois disso? Na minha visão, é o que mano? Focar em construir skill de on-board. E aí cê vai, cê abre com uma sessão, fala que cê quer construir skill de on-board, eu não sei como que tá aí exatamente, mas se eu não me engano o próprio superpowers ele abre do caralho pra construir skill.
38:31 Porque quando cê pede pra construir skill, ele segue procedimento mano, que ele vai tipo te brainstormando, e ele vai te perguntando todos os porquês, ele vai validando com você.
38:41 E no final a skill fica absurdamente boa, tá ligado? Fica muito boa. E aí, construir a skill de onboarding de dados, de novas fontes, na verdade, de gateway, né?
38:50 Então seria barra, boarding gateway. Porque, na minha visão, pelo menos, posso estar enganado, aí você vai ter que ver. Mas na minha visão, a gente tem que ter skill de onboarding para cada tipo de fonte.
39:02 Então, se for gateway, então vai ser boarding gateway. Se for, sei lá, fontes de custos de publicidade, tipo Meta, Meta, Google, Tabula, tudo a mesma coisa.
39:11 Então, você teria on-board, barra on-board em, sei lá, Traffic Channel, fonte de tráfego. Enfim, e aí, para finalizar, testar, né?
39:22 Testar, porque o nosso objetivo final com tudo isso é o quê? Acelerar o on-board das fontes. E aí, você pega aquele clique bem, que até uma fonte já está integrada.
39:29 Mas você finge que não tá, tipo, ou então tenta reformatar ela do zero, pra gente ver quanto que a gente ganha de tempo, como é que vai ser, se vai ser melhor ou se não vai.
39:37 E aí nesse processo que você for fazendo, você vai, mano, alimentar muito o Obsidian, ele vai ficar muito melhor. Tipo, velho, cada dia que passa fica melhor, é impressionante.
39:46 Cada dia que passa fica melhor. E toda, E aí, E aí, rapidão. E aí, mano, aí é disciplina. Toda reunião, mano.
39:54 Independentemente de qual você vá. Inclusive, você deveria já estar gravando essa reunião que eu tô fazendo com você. Eu tô gravando aqui pra, Eu tô gravando porque eu vou deixar lá no meu.
40:03 Vou te mandar a ligação, beleza. Só que, tipo assim, isso tem que tá fazendo com todo mundo, tá ligado? Porque é tudo conhecimento, mano.
40:09 Sim. Não, boa. Boa. Mano, quando for criar uma skill, Aí eu tenho que pedir para o Super Powers fazer essa criação.
40:19 Não. Por que mano? Não precisa. O plugin já tá na raiz, entendeu? Então, por exemplo, E aí galera? Boa demais?
40:33 Fala. Mano, a gente tá em ligação aqui agora, velho. Daqui a pouco eu troco o negócio aí, mano. Ah não, tranquilo, mas era pra, Ah, com o Tadeu.
40:42 Depois você me chama, Tadeu. Fechou. Mas, por exemplo, tipo assim, tudo que você faz, Tadeu, aqui, mano, você não tem que ativar necessariamente.
40:53 É porque, por exemplo, eu criei skill. Eu criei a skill de fazer o transformar. da reunião e de destilar as notas.
41:03 Eu não necessariamente tenho que vir aqui da barra skill, barra transcript, extractor e colar o transcript aqui. Eu não preciso necessariamente fazer isso.
41:10 Por quê? Porque ele já entende, tá ligado? Então se eu colocar assim, ative a skill de transcrição e popula com as notas pra mim.
41:24 E aí eu venho aqui, eu pego, deixa eu ver se tem alguma call pra destilar aqui enquanto isso. Ah, boa, eu já vou aproveitar, mano.
41:32 Eu já vou destilar aquela call lá dos dados, porque, Acho que vai mais ajudar do que atrapalhar, porque, Cadê, cadê, cadê, Tem mais de mês?
42:01 Aconselhação, Eu tinha visto aqui, velho, Caralho bicho, cadê essa porra? É uma coisa que tem que melhorar esses nomes aqui no Lunga, fica uma merda pra se achar.
42:48 Achei. O que eu gosto de fazer, eu pego o link da reunião, pego o transcript, porque ele, como ele tem os timestamps aqui, ele já referencia pelo link da reunião o horário, o minuto exato que você falou tal coisa, então se você quiser voltar pra rever, você consegue rever.
43:07 Aí joga, Só jogar isso daí. Ele já identifica, ele já vai chamar skill de transcrição, ó lá ó, automaticamente. Ele já sabe o que ele tem que usar.
43:18 Se eu jogasse documento aqui, se eu baixasse documento do Google Docs, se eu jogo aqui, ele não vai ativar esse skill.
43:24 Ele vai ativar a barra populate porque ele já tem isso intrínseco, tá ligado? Tá no sistema. Porque ele consulta antes, sacou?
43:32 Entendi. Aí a mesma coisa se compaure. Então, por exemplo, o Superpowers é plugin que te ajuda a criar skill. Então, quero criar uma skill de análise de dados de afiliação.
43:47 Me ajuda a criar. Olha lá, olha. Chamou os superpowers, brainstorming, tá vendo? Então ele vai me brainstormar Ó lá, vou começar entendendo o contexto que já exige skill de análise Ele vai consultar no vault que já tem Tá mapeando aqui que já exige E aí, não sei se você sabe, mas você pode rodar vários
44:13 terminais ao mesmo tempo, tá? Uhum. Aí, olha o que aconteceu. O mapeamento ficou claro. confirmar o plano de alocação com você, exatamente o que eu te falei, o que entendi da call, tipo sessão de trabalho, eu conduzindo o discovery do payload da buygoods, com o Leo e o Itadeu definindo as regras do negócio
44:46 para modelar a Raw, Silver, Gold, esperando o pipeline da ClickBank. Aí participantes, ele já pegou, ele já viu que sou eu, já viu que é o Leo e já viu que é você.
44:56 Data, 29 de abril, agora são 5h43 da manhã. enquanto checa vendas ao vivo. Olha lá, tá vendo, ele já sabe qual que foi a data, pelo que ele pegou, aí ele vai deixar lá a nota onde, departamento de dados, dentro de reuniões, sessão de trabalho, aí ele já vai salvar isso aqui lá no Raw Files, área primária
45:15 , dados, aonde impacta, filiação final ops, entidade a atualizar, aí ele vai atualizar o rubro de dados, perfil do Léo, o seu, vai jogar os action itens, Obrigado.
45:23 Beijos. vai linkar com o projeto de fundação de dados, com a arquitetura. Alguns pontos. Pontos que valem virar nota própria.
45:30 Espelhamento do riquismo de regras de negócio. Há muita regra reutilizada do time sobre o abrigo da BuyGoods. Padrões de evento, new order, refund, cancel, chargeback.
45:39 Section ID 2, para agrupar upsell. Cálculo de commission com chargeback fee. Fuso GMT-4. Recomendo espelhar isso na base de conhecimento sistema, base de conhecimento cloud.
45:48 e atualizar a memória GX by Goods, já que viaja com o Repo. Olha lá, exatamente, isso daqui, mano, o que é isso aqui?
45:56 A memória do Cloud, que ele ia salvar na minha máquina. Tá vendo que ele já me recomendou salvar? Boa. Ele já pega, tá ligado?
46:04 Aí, beleza, ele faz as perguntas. O seu tem essas perguntinhas assim? Tem, tem. Ah, tá, da hora. Então, beleza, vem lá na loja.
46:22 O que tipo de skill você quer de verdade aqui ó, assistente de análise ad-hoc Então você barra a fio quando o ninja de blood sugar fez e não sei o que Ai ele vai te dar as opções Então se você não quiser responder a pergunta, você dá ask e você dá prompt por fora, por exemplo.
46:42 Então tipo assim, quando você pede pra criar skill, ele já vai ativar o plugin do superpowers que é como se fosse outro skill, que te ajuda a criar skill, pra brainstormar isso daí, tá ligado?
46:52 Ele vai ficar te fazendo pergunta, e aí você vai validando, sacou? E demora, mano. Isso tem que fazer. Dá uma demoradinha.
46:58 É isso aí, gente. Até a 5 etapas, mas fica do caralho, fica absurdo, então mais, é isso ai, ai o catálogo de skills, mas como que ele atualiza, o catálogo de skills ele não é atualizado pelos superpowers, ele foi skill que eu criei, que é o barra catálogo, se eu rodar aqui, perai deixa eu É verdade,
47:22 porque eu tava criando várias skills e falei mano, vai dar merda isso aqui Se eu quiser rever as skills que eu tenho, aonde eu posso ver?
47:28 Não tem lugar Ai eu criei skill que ela já faz isso por natureza, que é o barra catálogo Ai eu posso ativar ela, tanto manual, quanto ela já automatizada Se eu quiser fazer force update aqui, eu posso fazer Mas ela já pega Ai ela vai atualizar o catálogo, que eu tenho todos os mísseis Esses kills aqui
47:45 por exemplo, sacou? Boa, uhum Então mano, é basicamente isso véi Aí assim Acho que com O que a gente já tem nessa call gravada aqui Se você só jogar no cloud, você já vai conseguir instalar Tudo, tá ligado?
47:58 Acho que você vai ter Puta norte, mas começa Pelo que eu te falei, dos superpowers ali Do Obsidian Sea Ally Instala as Skills básicas que eu te falei, reorganiza a arquitetura, sobe mais conhecimento, na minha visão acho que deveria subir esse conhecimento sintacal com o Leo também, que a gente fez junto
48:16 , porque, mas não agora, né? Depois você inserir as minhas Skills lá de transcrição de cópia. Porque vai agregar muita regra de negócio ali, alguns padrões de Discovery que vai ajudar muito a como fazer uma análise exploratória.
48:30 Tá ligado que eu acho que a gente, e vai, e é isso, e correr atrás do objetivo, mano. Pra gente conseguir fazer daquele quebank, das outras plataformas mais rápido.
48:40 Boa, boa. Só não sei porque o seu tá bugado assim, véi. É porque o seu é Windows também, talvez mude alguma coisa.
48:45 É, pode ser, mas o terminal aqui tá meio zoado mesmo. Por isso que eu tava até usando o desktop. Joga no cloud, pergunta.
48:54 Joga no cloud. E aí tem uma outra coisa também que a gente acabou falando, que é a parte de auditoria dos dados no Onboard, criar uma stream para fazer auditoria, isso vai ser super importante.
49:11 Verdade, aí é ponto que eu não tenho conhecimento, porque eu nunca usei o cloud web que conecta no navegador e tal.
49:18 Mas é ponto super relevante, mano. Inclusive, a planilha que você criou lá, porra, é uma puta base, tá ligado? Aí você pode ensinar o Claudio.
49:29 A gente entra na BuyGoods ou na plataforma que for, a gente tem que bater X com Y, pra ter certeza que o dado tá validado e tal.
49:38 Aí a gente cria normalmente essa planilha aqui pra conseguir validar. Aí você vai dando o contexto. Eu posso gravar minha tela e eu narrando o que eu to fazendo e jogar pro Claudio, acho que vai ficar bom.
49:50 E aí ele consegue ler arquivo também, então por exemplo, você baixa sua planilha, preferencialmente é melhor você mandar em MD.
50:02 Mas ele lê planilha também. muito bem, inclusive ele cria planilha, cria planilha de excel igual cria o caos normal, então é ponto da hora para deixar, cria até documento no google, tudo, mano dá para usar 100% a AI pelo terminal ecobizillion, 100%, tipo exatamente igual usa no web, mas enfim, e aí você
50:25 baixa a planilha, o documento que você quer baixar, aí você cria E só passa pra ele o nome do arquivo, então fala assim ó Eu baixei o arquivo, o nome dele é mais ou menos esse aqui Busca na minha máquina que você vai conseguir achar São os últimos downloads, os downloads dos últimos 20 minutos que eu
50:38 fiz Busca pra essa palavra achar que você vai achar Ele vai achar, ele vai ler e ele já vai conseguir identificar Boa Tá ligado?
50:47 Então mano, é mais ou menos isso E aí eu já tô conectando com o Lovabo já mano, já tô testando essa porra É, e tá dando certo?
50:55 Então, é porque eu tô meio que matando dois coelhos em uma caixa dada só Meio que tipo, é, pouco mais ou menos, porque Eu tô fazendo uma análise de comissionamento aqui na empresa E aí eu quero criar uma calculadora pra isso, tá ligado?
51:11 Só que criar essa calculadora no Excel é meio ruim No Google Sheets como todo Aí eu pensei, pô, por que não criar lovable da vida?
51:18 Que fica muito melhor, né? Fica muito mais visual, muito mais bonito. É muito mais interativo do que criar uma planilha.
51:25 Aí eu tô estudando o lovable. Eu tô aproveitando esse momento pra estudar o lovable. E meio que fazer, já meio que matar o problema do, Que eu tenho que fazer, simulador.
51:36 Juntamente com o, Entender como o lovable funciona. Aí eu já entendi. Eu aprendi que tem a questão do Knowledge Base lá, que a gente conversou com o Nakao ontem, que hoje eu tô testando E tá dando certo e tal, só que a parte de conexão com o banco eu não fiz, até porque tem que conectar com o S3, né
51:51 Então conectar com o S3 agora vai dar trabalho, então eu não fiz essa parte ainda não Eu tô mais entendendo como a ferramenta funciona do que necessariamente conectando alguma coisa agora, tá mais manual Mas, véi, é outro dia do caralho assim, vai dar muito bom, é o futuro mesmo velho, não tem ponto
52:11 de correr não é, eu também acho mano, também acho pois é, mas mano, acho que velho, tá bem alinhado aí mano, você sabe o que eu tô te falando, vai dar bom vai, com certeza velho, ou tá, deu mano, escuta o que eu tô te falando mano, foca nisso 100% mano Então, é isso.
52:28 Tudo o que você for fazer, registra, grava, e mano, foque em melhorar o que você tem. Foca, tipo, não fica satisfeito com o que tá aí, fica revisando, mano, fica revisitando o tempo inteiro, porque só vai ficar melhor, e cada dia que passar, você vai se impressionar mais, mano.
52:45 Juro pra você. Eu tô fazendo isso aqui tem menos de uma semana. Vai fazer uma semana, Hoje. Eu fui, A primeira Calcão Davi, semana passada.
52:52 Tô muito satisfeito. é porra nenhuma, nunca tinha rodado cloud code na minha vida e na máquina, e uma semana depois, tipo assim, a quantidade de conhecimento que eu já deixo aí aqui, de produtividade que eu ganhei é bizarro, tá ligado, então, você precisa ser, mano, você tem que gerar hiperfoco fudido
53:08 aí, velho, senão não vai dar certo não, mano, porque não tem milagre, tá ligado, não tem milagre, a ferramenta em si ela é potencializador do caralho, só que não tem milagre, no final das contas quem opera a maquina é o ser humano então você tem que ficar se questionando, tá bom, não tá, Puta, essa necessidade
53:26 aqui que eu não tinha pensado, mano, acho que isso aqui vai dar merda deixa eu criar skill pra isso aqui, deixa eu adaptar pra isso aqui se não souber, se tiver bugado alguma coisa, joga no próprio Cloud, mano que ele vai te falar o próprio Cloud instala automaticamente os plugins que precisa instalar
53:38 às vezes pra rodar Excel, o por exemplo, pra fazer Excel, pra fazer qualquer coisa, mano. Então tipo, é isso, saca?
53:47 Vai dar bom, mano. Se você focar na parada e você for interessado, vai dar bom. E aí vai me perguntando os pontos também, e principalmente, velho, marca uma call, já troca ideia com o Davi aí, já marca essa call amanhã, pra ele dar fazer review das skills que você tem.
54:03 você tem, se tá com todos os plugins instalados, pra ele dar uma checada, se você tá no ponto máximo do que dá pra tá, beleza?
54:12 Beleza, amor. Beleza. Fechou. Mas já de ponto de partida, já instala aí o que eu te falei, o Superpowers e o Obsidiancy Ally, que vai ajudar.
54:21 Boa. Mas, Beleza, amor. Fechou. Então conto com você aí, já desembola isso daí de hoje pra amanhã, e aí amanhã mais no final do dia cê me dá feedback, que aí cê é bem rápido de instalar.
54:36 Fechou mano, combinado. Beleza, então até amanhã aí, cê acha que dá pra gente já entregar essa arquitetura de passas nova?
54:44 Ah, com certeza, dá sim. Então beleza, é isso, valeu, vou te mandar gravar mais Faça aí também, que vai ajudar.
54:49 Falou. Fechou mano, valeu aí. Falou.
