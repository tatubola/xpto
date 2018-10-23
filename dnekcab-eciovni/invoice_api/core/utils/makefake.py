from django.utils import timezone
from invoice_api.core.models import *


class Makefakedata(object):
    def __init__(self):
        self.template_pt = "<b>INSTRUMENTO PARTICULAR DE CONTRATO</b></p>\r\n<p>Pelo presente instrumento particular de um lado, <b>NÚCLEO DE INFORMAÇÃO E COORDENAÇÃO DO PONTO BR - NIC.br</b>, inscrito no CNPJ/MF sob nº 05.506.560/0001-36, com sede na Av. das Nações Unidas, n° 11.541, 7º andar, Brooklin Novo, São Paulo/SP, CEP: 04578-000, denominado <b>NIC.br</b>, neste ato representado por Demi Getschko e, de outro lado, {razao_social}, inscrito no CNPJ/MF sob nº {cnpj}, com sede na {endereco_rua}, {endereco_numero} - {endereco_complemento}, cidade {endereco_cidade}, estado {endereco_estado}, CEP: {endereco_cep}, denominado <b>PARTICIPANTE</b>, neste ato representado por {responsavel};</p>\r\n<p>Considerando que:</p>\r\n<p>&#183; O NIC.br foi criado para implementar as decisões e os projetos do Comitê Gestor da Internet no Brasil - CGI.br, que é o responsável por coordenar e integrar as iniciativas e serviços da Internet no País;</p>\r\n<p>&#183 ; Entre os objetivos estatutários do NIC.br está o desenvolvimento de projetos que visam melhorar a qualidade da Internet no Brasil e disseminar seu uso, com especial atenção para seus aspectos técnicos e de infraestrutura;</p>\r\n<p>&#183; Em observância a seus objetivos o NIC.br vem trabalhando, há mais de 10 anos, na implantação da iniciativa PTTmetro do Comitê Gestor da Internet do Brasil (CGI.br), atualmente nomeada IX.br, que cuida da criação e operação de pontos de troca de tráfego Internet no Brasil;</p>\r\n<p>&#183; IX.br é o nome dado à iniciativa do Comitê Gestor da Internet no Brasil (CGI.br) que promove, cria e opera a infraestrutura necessária para interligação direta entre as redes que compõem a Internet Brasileira em regiões metropolitanas que apresentam grande potencial para troca de tráfego Internet;</p>\r\n<p>&#183; À infraestrutura para a interligação direta entre as redes dá-se o nome de Ponto de Troca de Tráfego Internet (PTT) ou, em inglês, ”Internet Exchange Point,” (IX ou IXP);</p>\r\n<p>&#183; As redes que em conjunto compõem a Internet são os Sistemas Autônomos, em inglês “Autonomous Systems” (ASs);</p>\r\n<p>&#183; A interligação entre Sistemas Autônomos em uma área metropolitana, através do IX.br, se dá por meio da utilização de um ou mais Pontos de Interligação (PIXs), que em conjunto formam uma única matriz de troca de tráfego Internet da localidade. A utilização dos PIXs possibilita uma melhor cobertura geográfica e eficiência na utilização dos recursos disponíveis;</p>\r\n<p>&#183; O modelo de interligação de Sistemas Autônomos por meio de Pontos de Troca de Tráfego Internet (PTT) promove a racionalização dos custos, uma vez que os balanços de tráfego são resolvidos direta e localmente e não através de redes de terceiros, muitas vezes fisicamente distantes;</p>\r\n<p>&#183; O modelo também promove uma melhor organização da infraestrutura da Internet, e um maior controle de cada Sistema Autônomo sobre a entrega de seu tráfego, possibilitando que seja feita o mais próximo possível do destino, o que em geral resulta em melhor desempenho e qualidade e em uma operação mais eficiente da Internet como um todo;</p>\r\n<p>&#183; Uma localidade do IX.br é uma interligação em área metropolitana de Pontos de Interligação de Redes (PIXs), comerciais, governamentais e/ou acadêmicos, sob uma gerência centralizada, tendo como características: neutralidade (independência de provedores comerciais), qualidade (troca de tráfego eficiente com menor latência), baixo custo das alternativas e alta disponibilidade, constituindo uma matriz de troca de tráfego regional única, ou seja, um único Internet Exchange ou Ponto de Troca de Tráfego Internet;</p>\r\n<p>&#183; A coordenação do IX.br, a cargo do NIC.br, e sua operação em parceria com organizações tecnicamente habilitadas, estabelecem os requisitos de arquitetura e gerência das interligações e garantem as características de neutralidade e qualidade do IX.br;</p>\r\n<p>&#183; A hospedagem dos Pontos de Interligação (PIXs) em instalações com padrão adequado de segurança e infraestrutura é condição para obtenção das características de qualidade, baixo custo das alternativas e alta disponibilidade;</p>\r\n<p>&#183; O NOC do IX.br é um centro de operação de redes que coordena os trabalhos de gerenciamento das localidades, sendo responsável pela manutenção da estabilidade das matrizes de troca de tráfego internet, bem como de toda a infraestrutura de recursos utilizados na operação das localidades do IX.br;</p>\r\n<p>&#183; O PARTICIPANTE, para fins deste instrumento, é o administrador de um Sistema Autônomo (AS) de acordo com o significado dado na BCP6/RFC 4271, “A Border Gateway Protocol BGP4” (vide IETF - The Internet Engineering Task Force em https://tools.ietf.org/html/rfc4271);</p>\r\n<p>&#183; O PARTICIPANTE acessou o portal do participante do IX.br (https://meu.ix.br) e escolheu o pacote de funcionalidades e recursos que considerou mais adequado;</p>\r\n<p>&#183; O PARTICIPANTE é identificado no portal do participante do IX.br (https://www.meu.ix.br) como o Sistema Autônomo (AS) nº <?= asn ?>.</p>\r\n<p>As partes têm entre si, certo e ajustado, o presente contrato, que se regerá pelas seguintes cláusulas e condições.</p>\r\n<p></p>\r\n<p><b>CLÁUSULA PRIMEIRA - DO OBJETO</b></p>\r\n<p></p>\r\n<p>1.1. O objeto do presente contrato é a atividade, disponibilizada pelo NIC.br nas localidades do IX.br, de Interligação de Sistemas Autônomos (ASs), que se dará através da utilização de um ou mais Pontos de Interligação de Redes (PIXs).</p>\r\n<p></p>\r\n<p><b>CLÁUSULA SEGUNDA - REQUISITOS PARA ADESÃO AO  IX.br</b></p>\r\n<p></p>\r\n<p>2.1. São requisitos para adesão de um PARTICIPANTE ao IX.br:</p> \r\n<p>&#183; Ter um Número de Sistema Autônomo, ou ASN (Autonomous System Number): possuir e operar um Sistema Autônomo devidamente cadastrado nos organismos de registro de números e nomes da Internet;</p>\r\n<p>&#183; Participar do acordo multilateral de tráfego via Servidor de Rotas (RS - Route Server), ou estabelecer relações bilaterais diretas: estabelecer acordos de troca de tráfego Internet com outros Sistemas Autônomos que participam do IX.br;</p>\r\n<p>&#183; BGP-4: Utilizar o protocolo de roteamento externo BGP-4 (Border Gateway Protocol, conforme padronizado pelo IETF), para interligar seu AS a outros;</p>\r\n<p>&#183; Seguir a Política de Requisitos Técnicos e a Política de Uso Aceitável do IX.br: que podem ser encontradas no portal do IX.br (http://www.ix.br), em suas últimas versões. </p>\r\n<p>2.2. A comunicação entre o PARTICIPANTE e o NIC.br se dará por meio do portal do participante do IX.br (https://meu.ix.br), no qual o PARTICIPANTE deverá criar um login para ter acesso às funcionalidades disponibilizadas.</p>\r\n<p>2.2.1. Por meio do portal do participante do IX.br, o PARTICIPANTE terá acesso a todas as informações necessárias sobre sua conta, tais como recursos utilizados para a interligação do seu AS aos Pontos de Interligação de Redes (PIXs) e localidades do IX.br que melhor lhe convirem, valores, forma de pagamento, como realizar o cancelamento ou acréscimo de recursos, bem como a outras informações pertinentes.</p>\r\n<p>2.2.2. Por meio do portal do participante do IX.br, o PARTICIPANTE poderá solicitar o cancelamento da interligação ao IX.br, desde que observado o descrito na cláusula quinta do presente instrumento.</p>\r\n<p>2.2.3. A liberação dos novos recursos tratados na cláusula 2.2.1 está condicionada a análise prévia de viabilidade, cujo resultado será informado ao PARTICIPANTE em até 5 dias úteis, com a aceitação imediata da solicitação, previsão de disponibilidade do recurso, ou aviso de impossibilidade de atendimento.</p>\r\n<p>2.2.3.1. Havendo disponibilidade dos recursos solicitados, os mesmos serão alocados e configurados por meio de interações realizadas no portal do participante do IX.br, entre a equipe do NIC.br e o  PARTICIPANTE, sendo que o NIC.br irá interagir em no máximo 5 (cinco) dias úteis, sempre que o processo estiver em atividade sob sua responsabilidade.</p>\r\n<p>2.3. A data base para o levantamento dos recursos utilizados para o cálculo da cobrança será o último dia corrido de cada mês. Recursos que tenham utilização iniciada durante o mês, serão calculados “pro-rata temporis”.</p>\r\n<p></p>\r\n<p><b>CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES DAS PARTES</b></p>\r\n<p></p>    \r\n<p>3.1. O NIC.br se obriga a:</p>\r\n<p>I. Continuar aportando recursos no projeto IX.br;</p>\r\n<p>II. Gerenciar a infraestrutura de rede, utilizando recursos técnicos e as melhores práticas disponíveis para a operação e manutenção de Pontos de Troca de Tráfego Internet;</p>\r\n<p>III. Realizar investimentos para a melhoria do atendimento ao PARTICIPANTE;</p>\r\n<p>IV. Definir os equipamentos, tecnologias e práticas adotadas nas localidades do IX.br;</p>\r\n<p>V. Analisar e, se for o caso, disponibilizar os recursos de infraestrutura de rede solicitados pelo PARTICIPANTE por meio do portal do IX.br, em até 30 (trinta) dias corridos após o aviso de disponibilidade dos recursos;</p>\r\n<p>VI. Atender, no prazo de 24 (vinte e quatro) horas, 7 (sete) dias da semana, chamados de suporte técnico realizados pelo PARTICIPANTE, com exceção da solicitação pertinente a novos recursos descrita na cláusula 2.2.1;  </p>\r\n<p>VII. Cobrar contribuição financeira por parte do  PARTICIPANTE, conforme pacote de recursos utilizados;</p>\r\n<p>VIII. Cumprir todas as demais cláusulas, obrigações e condições previstas neste contrato.</p>\r\n<p></p>\r\n<p>3.2. O PARTICIPANTE se obriga a:</p>\r\n<p>I. Atender aos requisitos para adesão a uma localidade do IX.br, descritas na cláusula 2.1;</p>\r\n<p>II. Efetuar o pagamento de acordo com o valor cobrado pelo pacote de funcionalidades e recursos escolhidos no IX.br;</p>\r\n<p>III. Indicar, caso entender necessário, contato para realização do pagamento de acordo com o valor das funcionalidades e recursos escolhido;</p>\r\n<p>IV. Seguir, criteriosamente, a Política de Uso Aceitável (http://ix.br/pua) e a Política de Requisitos Técnicos do IX.br (http://ix.br/requisitos);</p>\r\n<p>V. Acompanhar eventuais atualizações da Política de Uso Aceitável e da Política de Requisitos Técnicos do IX.br;</p>\r\n<p>VI. Envidar esforços para melhorar a qualidade de sua rede, conectando-se a outros ASs da Internet por um meio físico que não seja o mesmo utilizado para se interligar ao IX.br, com capacidade suficiente, conforme recomendação da RFC 1930 (https://tools.ietf.org/html/rfc1930), colaborando assim também para a robustez e a resiliência da Internet como um todo;</p>\r\n<p>VII. Não assumir qualquer obrigação em nome do NIC.br ou, por qualquer forma ou condição, obrigá-lo perante terceiros;</p>\r\n<p>VIII. Comunicar, por meio de chamado no portal do participante, indisponibilidades ou problemas técnicos enfrentados no IX.br;</p>\r\n<p>IX. Cumprir todas as demais cláusulas, obrigações e condições previstas neste contrato.</p>\r\n<p></p>\r\n<p><b>CLÁUSULA QUARTA - DO PAGAMENTO</b></p>\r\n<p></p>\r\n<p>4.1. O PARTICIPANTE pagará pelo pacote de recursos utilizados na Interligação do AS, escolhido no portal do participante do IX.br (https://meu.ix.br).</p>\r\n<p>4.1.1 Pagamentos oriundos do exterior serão acrescidos das despesas, taxas e impostos adicionais para sua efetivação, sendo certo que eventuais despesas serão suportadas pelo PARTICIPANTE.</p></p>\r\n<p>4.2. O PARTICIPANTE, por meio do seu login, irá acessar o portal do participante do IX.br e gerar cópia da fatura, boleto ou outro meio de  pagamento do pacote escolhido.</p>\r\n<p>4.2.1 O PARTICIPANTE, caso entender necessário, poderá indicar por meio do portal um contato para realização de pagamento.</p>\r\n<p>4.3. A fatura, boleto ou outro meio de pagamento e demais informações relativas à cobrança, estarão disponíveis no portal do participante do IX.br até o dia 5 (cinco) do mês subsequente, sendo certo que o PARTICIPANTE deverá acessar o portal para acessar a forma de pagamento. O prazo de pagamento será até o 15 (quinze) do mês da emissão da fatura.</p>\r\n<p>4.4. Eventuais problemas técnicos que venham a ocorrer na estrutura do AS, tais como problemas com o provedor de serviço de transporte até o IX.br, com o data center onde o AS está hospedado, ou problemas técnicos na infraestrutura do IX.br, mesmo que resultem em interrupções na interligação entre os ASs promovida pelo IX.br, não gerarão descontos nos valores devidos pelo PARTICIPANTE.</p>\r\n<p>4.5. A tabela de preços para os recursos disponibilizados pelo IX.br da localidade, publicada no portal do IX.br (http://www.ix.br), poderá ser reajustada anualmente, com data base 01/07/2017, reajuste este que não poderá ser superior ao IGP-M publicado pelo Instituto Brasileiro de Economia da Fundação Getúlio Vargas (IBRE/FGV).</p>\r\n<p></p>\r\n<p><b>CLÁUSULA QUINTA - DA VIGÊNCIA E EXTINÇÃO</b></p>\r\n<p></p>\r\n<p>5.1. O presente contrato entra em vigor na data de sua assinatura e vigorará por prazo indeterminado.</p>\r\n<p>5.2. As partes poderão rescindir o presente contrato, a qualquer tempo, desde que a parte interessada comunique a outra com 30 (trinta) dias de antecedência.\r\n<p></p>\r\n<p><b>CLÁUSULA SEXTA - DAS RESPONSABILIDADES</b></p>\r\n<p></p>\r\n<p>6.1. O PARTICIPANTE assume em relação aos profissionais envolvidos na execução direta e indireta das atividades decorrentes deste contrato, exclusiva responsabilidade pelo cumprimento das leis trabalhistas, previdenciárias, seguros,  acidentes  de  trabalho  e  das  demais   obrigações   legais   ou regulamentares decorrentes de relação de emprego ou qualquer outra forma  de contratação que mantiverem com suas equipes de trabalho, eximindo  o  NIC.br de qualquer responsabilidade, vínculo ou obrigação.</p>\r\n<p>6.2. Em todas e quaisquer reclamações trabalhistas, ações judiciais ou autos de infração de qualquer natureza, que versem e digam respeito sobre vínculo trabalhista, relacionada aos empregados do PARTICIPANTE  ou de seus subcontratados, e que o NIC.br eventualmente venha a fazer parte sendo intimado, interpelado, notificado ou citado, ficará o PARTICIPANTE  obrigado a realizar todos os procedimentos necessários a fim de isentar o NIC.br de qualquer responsabilidade patrimonial dessas ações ou atuações, bem como ressarcir o NIC.br de qualquer condenação e/ou despesas advindas dessas reclamações.</p>\r\n<p>6.3. O PARTICIPANTE é o único responsável pela estrutura necessária para que o mesmo se torne um AS (Sistema Autônomo), devendo seguir as regras dos organismos de registro de números e nomes da Internet para poder operá-lo.</p>\r\n<p>6.4. O NIC.br não se responsabiliza pela configuração ou operação do AS (Sistema Autônomo) do PARTICIPANTE,  ou por qualquer consequência decorrente dessa configuração e operação.</p> \r\n<p>6.5. O presente contrato não ensejará qualquer vínculo trabalhista entre o NIC.br e o PARTICIPANTE, podendo o NIC.br exercer livremente seus serviços, sem apresentar exclusividade para com o PARTICIPANTE.</p>\r\n<p>6.6. O NIC.br não será responsável por perdas ou danos de qualquer natureza que possam advir da utilização dos recursos de infraestrutura do IX.br, seja por problemas de funcionamento ou por questões relacionadas ao conteúdo e dados trafegados.</p> \r\n<p>6.6.1 O NIC.br não tem controle sobre as rotas disponibilizadas por cada Sistema Autônomo no IX.br. Estas podem ser anunciadas ou retiradas a qualquer tempo, por decisão de cada Sistema Autônomo, implicando no acesso ou não a determinados sites e conteúdos da Internet via IX.br.</p>\r\n<p></p>\r\n<p><b>CLÁUSULA SÉTIMA - DO INADIMPLEMENTO E DO  DO DESCUMPRIMENTO</b></p>\r\n<p></p>\r\n<p>7.1. Em caso de inadimplemento por parte do PARTICIPANTE  quanto ao pagamento do pacote de recursos escolhido para Interligação de Sistemas Autônomos em área metropolitana, o PARTICIPANTE  estará automaticamente em mora, facultado ao NIC.br após 60 (sessenta) dias o bloqueio do PARTICIPANTE no IX.br e a rescisão do contrato, sem prejuízo da cobrança do débito pela via executiva judicial.</p>\r\n<p>7.2. O NOC do IX.br poderá, em caso de observar o descumprimento da Política de Uso Aceitável ou da Política de Requisitos Técnicos do IX.br, fazer de forma imediata a sua desconexão lógica ou movimentação para um ambiente de testes, por tempo indeterminado, até que o problema seja resolvido.</p>\r\n<p>7.3. Em caso de descumprimento da Política de Uso Aceitável ou da Política de Requisitos Técnicos do IX.br, em mais de uma ocasião, ou por evidente má-fé, fica facultado ao NIC.br o bloqueio imediato do PARTICIPANTE no IX.br e a rescisão do contrato, sem prejuízo da cobrança de débitos existentes, inclusive por via judicial executiva.</p>\r\n<p></p>\r\n<p><b>CLÁUSULA OITAVA - CONSIDERAÇÕES GERAIS</b></p>\r\n<p></p>\r\n<p>8.1. Fica expressamente vedado ao PARTICIPANTE ceder ou transferir, a qualquer título, os direitos e obrigações assumidos através do presente instrumento, sem a prévia e expressa anuência do NIC.br.</p>\r\n<p>8.2. Este contrato, em nenhuma hipótese, cria relação de parceria ou de representação comercial entre as partes, sendo cada uma responsável por seus atos e obrigações.</p>\r\n<p>8.3. O presente contrato somente poderá sofrer alterações em seu conteúdo mediante aditivo contratual, assinado por ambas as partes, que passará a fazer parte integrante do mesmo.</p>\r\n<p>8.4. Este contrato constitui a totalidade do acordo entre os signatários com relação às matérias aqui previstas e supera, substitui e revoga eventuais entendimentos, negociações e acordos anteriores.</p>\r\n<p>8.5. O PARTICIPANTE compromete-se, por si, seus empregados e prepostos, a manter o mais absoluto sigilo, a não reproduzir, disponibilizar, transferir ou ceder qualquer informação, material e/ou documentos do NIC.br que, por ventura, vier a ter acesso por força do cumprimento do objeto deste contrato, sob pena de arcar com as perdas e danos a que der causa, por infração às disposições desta cláusula.</p>\r\n<p>8.6. O NOC do IX.br poderá, em caso de observar problemas técnicos na ligação do PARTICIPANTE à rede do IX.br que possam provocar instabilidade na rede, fazer a sua desconexão lógica ou movimentação para um ambiente de testes, a fim de mitigar o problema.</p>\r\n<p>8.7. O NIC.br poderá monitorar o tráfego do PARTICIPANTE, incluindo informações como Sistema Autônomo de origem e destino, quantidade de dados trafegados, e protocolos de camada 3 e 7 utilizados, com o objetivo único e exclusivo de obter informações que permitam melhor gerenciar tecnicamente o IX.br.</p>\r\n<p>8.8. Fica permitido ao NIC.br divulgar publicamente no portal do IX.br e por outros meios, gráficos e estatísticas baseados nos dados coletados no monitoramento citado no item 8.7, desde que estejam anonimizados e agregados, não permitindo a identificação de Sistemas Autônomos individuais.</p>\r\n<p>8.9. Ao NIC.br fica permitido realizar testes e provas de segurança, incluindo tentativas de acesso ao equipamento do PARTICIPANTE diretamente ligado ao IX.br sem senha ou usando senhas comuns, bem como a verificação ativa ou passiva de protocolos e serviços ativos que descumpram a Política de Uso Aceitável ou da Política de Requisitos Técnicos.</p>\r\n<p></p>\r\n<p><b>CLÁUSULA NONA - DO FORO</b></p>\r\n<p></p>\r\n<p>9.1. Para dirimir quaisquer dúvidas em relação ao presente contrato, elegem as partes o Foro Central da Comarca de São Paulo, Estado de São Paulo, renunciando a qualquer outro por mais privilegiado que seja, como único competente para dirimir qualquer dúvida ou eventual controvérsia, oriundas do presente contrato.</p>\r\n<p></p><p>Contrato - Interligação de Sistemas Autônomos Rev. 1.0 - 30/06/2017</p>\r\n<p></p>\r\n\r\n"
        self.template_en = "\r\n\r\n<p><b>PRIVATE CONTRACTUAL INSTRUMENT</b></p>\r\n<p></p> \r\n<p>By the present Private Instrument, on the one hand the <b>Brazilian Network Information Center (NÚCLEO DE INFORMAÇÃO E COORDENAÇÃO DO PONTO BR - NIC.br)</b>, registered on the Brazilian Corporate Taxpayer Register of the Ministry of Finance (CNPJ/MF) under No. 05.506.560/0001-36, with head office established at Av. das Nações Unidas, n° 11,541, 7th floor, Brooklin Novo, São Paulo, State of São Paulo, Brazil, postcode 04578-000, hereinafter <b>NIC.br</b>, here represented by the person of Demi Getschko, and, on the other hand, {razao_social}, registered on the Brazilian Corporate Taxpayer Register of the Ministry of Finance (CNPJ/MF) under No. {cnpj}, with head office established at {endereco_rua}, {endereco_numero} - {endereco_complemento}, city {endereco_cidade}, state {endereco_estado}, postcode: {endereco_cep}, denominado <b>PARTICIPANTE</b>, hereafter the <b>PARTICIPANT</b>, here represented by the person of {responsavel};</p>\r\n<p>Whereas:</p>\r\n<p>&#183; The NIC.br was established to implement the decisions and the projects asset out by the Brazilian Internet Steering Committee - CGI.br, the party responsible for the co-ordination and the integration of Internet initiatives and services in the country;</p>\r\n<p>&#183; Among the statutory aims of the NIC.br, we have the development of projects aiming to improve the quality of the Internet in Brazil and also to disseminate its use, giving special attention to its technical aspects and infrastructure;</p>\r\n<p>&#183; In compliance with its aims and goals as proposed, NIC.br has, for the past 10 years or so, been working towards the implementation of the PTTmetro initiative of the Brazilian Internet Steering Committee (CGI.br), currently known by the name of IX.br, which takes care of the creation and operation of points of exchange of Internet traffic in Brazil;</p>\r\n<p>&#183; IX.br is the name given to the initiative by the Brazilian Internet Steering Committee (CGI.br) which promotes, creates and operates the infrastructure that is necessary for there to be direct interconnection between the different networks that make up the Brazilian Internet in metropolitan areas which show significant potential for the exchange of Internet traffic;</p>\r\n<p>&#183; The infrastructure for the direct interconnection between the networks is known as an Internet Exchange Point (IX or IXP) or, in Portuguese,  Ponto de Troca de Tráfego Internet (PTT);</p>\r\n<p>&#183; The networks which, together, make up the Internet are known as Autonomous Systems (ASs);</p>\r\n<p>&#183; The interconnection between Autonomous Systems within a metropolitan area, through IX.br, occurs through the use of one or more interconnection points (PIXs) which, together, form one single matrix for exchange of Internet traffic in this location. The use of the PIXs allows better geographical coverage and greater efficiency in the use of the available resources;</p>\r\n<p>&#183; The model for the interconnection of the Autonomous System through Internet Exchange Points (IXPs) allows the rationalisation of costs, as the balances of traffic are directly and locally solved rather than through third-party networks which, in many cases, are physically distant;</p>\r\n<p>&#183; The model also promotes better organisation of the Internet infrastructure and also a better control of each Autonomous System over the delivery of its traffic, thereby allowing this to be carried out as close as possible to the destination, which, in general, results in better performance and quality, and also in a more efficient operation of the Internet as a whole;</p>\r\n<p>&#183; A locality of IX.br is an interconnection, within a metropolitan area, of Internet Exchange Points (IXPs), be they commercial, Governmental and/or academic, under centralised management, with the following main characteristics: neutrality (independence of commercial providers), quality (efficient exchange of traffic with lower rate of latency); low cost of options, and high availability, thereby establishing a unique matrix for exchange of local traffic; in other words, one single Internet Exchange Point;</p>\r\n<p>&#183; The coordination of IX.br, which is the responsibility of NIC.br, and its operation in partnership with technically accredited organisations, establishes the requirements with regard to architecture and management of the interconnections, and also ensure the characteristics of neutrality and quality of IX.br;</p>\r\n<p>&#183; The hosting of Internet Exchange Points (IXPs) in installations with appropriate standard of security and infrastructure is an essential condition for obtaining the basic characteristics of quality, low cost of options, and high availability;</p>\r\n<p>&#183; The NOC of IX.br is an operational centre for networks, that co-ordinates the work of management of the locations, also being responsible for maintaining stability of the matrices for exchange of Internet traffic, as also the whole infrastructure of resources used in the operation of the different locations of IX.br;</p>\r\n<p>&#183; For the purposes set forth in this Instrument, the PARTICIPANT is the manager of an Autonomous System (AS), according to the meaning assigned to the term by BCP6/RFC 4271, “A Border Gateway Protocol BGP4” (see The Internet Engineering Task Force (IETF) on the Internet at https://tools.ietf.org/html/rfc4271);</p>\r\n<p>&#183; The PARTICIPANT has accessed the participant’s portal of IX.br (https://meu.ix.br) and has also duly selected the package of features and resources that they have considered most appropriate;</p>\r\n<p>&#183; The PARTICIPANT is identified on the participant’s portal of IX.br (https://www.meu.ix.br) as Autonomous System (AS) No. <?= asn ?>.</p>\r\n<p>The Parties have, between themselves, agreed and accepted the terms of the present Contract, which shall be governed by the clauses and conditions as follow hereunder.</p>\r\n<p></p>\r\n<p><b>CLAUSE ONE - THE OBJECT</b></p>\r\n<p></p>\r\n<p>1.1.\tThe object of the present Contract is the activity of interconnection of Autonomous Systems (ASs), as made available by NIC.br, at the locations of IX.br. This shall occur through the use of one or more Network Interconnection Points (PIXs).</p>\r\n<p></p>\r\n<p><b>CLAUSE TWO - REQUIREMENTS FOR JOINING  IX.br</b></p>\r\n<p></p>\r\n<p>2.1. The requirements for a PARTICIPANT to become part of IX.br are the following:</p>\r\n<p>&#183; Having an Autonomous System Number (ASN): the Participant must possess and operate an Autonomous System duly registered on the organisations responsible for the registration of Internet names and numbers;</p>\r\n<p>&#183; Participation in the multilateral agreement regarding traffic, through a Route Server (RS), or establishment of direct bilateral relations:  establishment of agreements for exchange of Internet traffic with other Autonomous Systems (ASs) that participate in IX.br;</p>\r\n<p>&#183; BGP-4: Use of the BGP-4 external routing (Border Gateway Patrol, as standardised by the IETF) to link their own AS to others;</p>\r\n<p>&#183; Follow the Policy for Technical Requirements and Acceptable Use set by IX.br: these policies can be found on the IX.br portal (http://www.ix.br), in its most recent versions.</p>\r\n<p>2.2. Communication between the PARTICIPANT and NIC.br shall take place through the participant’s portal within the IX.br website (https://meu.ix.br), where the PARTICIPANT should create a username to be able to login, gaining access to the features thus made available. </p>\r\n<p>2.2.1. Through the participant’s portal on IX.br, the PARTICIPANT shall have access to all the necessary information about their account, such as the resources used for the interconnection of their own AS with the Network Interconnection Points (PIXs) and also with locations of IX.br as suit them best; prices and methods of payment; how to cancel or add resources; as also any other relevant information.</p>\r\n<p>2.2.2. Also through the participant’s portal on IX.br, the PARTICIPANT may also request the cancellation of the link up to IX.br, provided there is observance of the terms and conditions as set out in Clause Five of this Instrument.</p>\r\n<p>2.2.3. The release of the new resources as mentioned in Clause 2.2.1 depends on a prior feasibility analysis, whose result shall be informed to the PARTICIPANT within a time frame of 5 business days, with the immediate acceptance of the request, forecast as to the availability of the resources sought, or a notification informing that it shall be impossible to meet the request.</p>\r\n<p>2.2.3.1. If the resources sought are indeed available, then these shall be allocated and configured through interactions made on the participant’s portal within the IX.br site, between the NIC.br team and the PARTICIPANT, and in this case NIC.br shall interact within a time frame of five (5) business days, whenever the process is active under their responsibility.</p>\r\n<p>2.3. The base date for harnessing the resources used for the calculation of debt collection shall be the last calendar day of each month. Resources which start being used during the month shall be calculated on a pro rata temporis basis.</p>\r\n<p></p>\r\n<p><b>CLAUSE THREE - OBLIGATIONS OF THE PARTIES</b></p>\r\n<p></p>\r\n<p>3.1. NIC.br shall have the following obligations:</p>\r\n<p>I. To continue to invest resources in the IX.br project;</p>\r\n<p>II. To manage the network infrastructure, making use of technical resources and also the best practices available for the operation and the maintenance of Internet Exchange Points;</p>\r\n<p>III. To make investments with a view to improving the service provided to the PARTICIPANT;</p>\r\n<p>IV. To define the equipment, technologies and practices taken up at the IX.br locations;</p>\r\n<p>V. To analyse and, if the case warrants it, make available the resources of network infrastructure as requested by the PARTICIPANT through the IX.br portal, within a period of thirty (30) calendar days after the notification that the said resources are available;</p>\r\n<p>VI. To answer, within a time frame of twenty-four (24) hours, seven days a week, any technical support calls as made by the PARTICIPANT, with the exception of any request relative to new resources as described in Clause 2.2.1;</p>\r\n<p>VII. To demand financial contributions from the PARTICIPANT, according to the package of resources that has been used;</p>\r\n<p>VIII. To comply with all other clauses, obligations and conditions as set forth in this Contract.</p>\r\n<p>3.2. The PARTICIPANT has the following obligations:</p>\r\n<p>I. To respond to all requests for joining an IX.br location, as described in Clause 2.1 above;</p>\r\n<p>II. To make payment, according to the price charged for the package of features and resources as chosen at IX.br;</p>\r\n<p>III. To name, if deemed necessary, a contact for making the due payment according to the value of the features and the resources as chosen;</p>\r\n<p>IV. To strictly follow the Policy of Acceptable Use (http://ix.br/pua) and the Policy of Technical Requirements of IX.br (http://ix.br/requisitos);</p>  \r\n<p>V. To follow possible updates to the Policy of Acceptable Use and the Policy of Technical Requirements of IX.br;</p>\r\n<p>VI. To make efforts towards the improvement of the quality of their network, by linking up to other ASs of the Internet through a physical medium which is not the same one used to interconnect to IX.br, with sufficient capacity, in line with the recommendations made by RFC 1930 (https://tools.ietf.org/html/rfc1930), thereby also collaborating to the robustness and resilience of the Internet as a whole;</p>\r\n<p>VII. Not to take on any obligations in the name of NIC.br or bind this latter institution before third parties, under any conditions or in any manner;\r\n<p>VIII. To inform any unavailability or technical problems faced in IX.br, through making a notification on the participant’s portal;</p>\r\n<p>IX. To comply with all other clauses, obligations and conditions as established in this Contract.</p>\r\n<p></p>\r\n<p><b>CLAUSE FOUR - PAYMENT</b></p>\r\n<p></p>\r\n<p>4.1. The PARTICIPANT shall pay for the package of resources used in the Interconnection of the AS, as chosen in the participant’s portal of IX.br (https://meu.ix.br).</p>\r\n<p>4.1.1 Any payments originating from abroad shall have the addition of any expenses, fees and taxes as may be additionally charged for the effectuation thereof, it also being agreed that the cost of such expenses shall be borne by the PARTICIPANT.</p>\r\n<p>4.2. The PARTICIPANT, through his/her username, shall access the participant’s portal of IX.br and generate a copy of the invoice, bank docket, or other means of payment for the package chosen.</p>\r\n<p>4.2.1 Should this party deem it necessary, the PARTICIPANT may appoint a contact, through the portal, so that the payment may be made.</p>\r\n<p>4.3. The invoice, bank docket, or other means of payment, as also any other information regarding the debt collection, shall be available on the participant’s portal at IX.br by the fifth (5th) day of the subsequent month, it also being here agreed that the PARTICIPANT shall access the portal to gain access to the method of payment. The time frame for payment shall be up to the fifteenth (15th) day of the month the invoice is issued.</p>\r\n<p>4.4. Any technical problems as may occur within the structure of the AS, such as problems with the provider of transport to IX.br, with the data centre where the AS is hosted, or any technical problems with IX.br infrastructure, even should they lead to interruptions of the interconnections between the ASs as promoted by IX.br, shall not generate any deductions on the sums due by the PARTICIPANT.</p>\r\n<p>4.5. The price list for resources made available by the IX.br of the location, as published on the IX.br portal (http://www.ix.br) may be readjusted every year, with a base date of 7/1/2017. This readjustment must not be more than the variation in the IGP-M as published by the Brazilian Economics Institute of the Getúlio Vargas Foundation (IBRE/FGV).</p>\r\n<p></p>\r\n<p><b>CLAUSE FIVE - VALIDITY AND TERMINATION</b></p>\r\n<p></p>\r\n<p>5.1. The present Contract takes effect on the date of the signing thereof, and shall remain in effect for an indefinite period.</p>\r\n<p>5.2. The Parties may terminate the present Contract at any moment, provided the interested party informs the other party thirty (30) days in advance.</p>\r\n<p></p>\r\n<p><b>CLAUSE SIX - RESPONSIBILITIES</b></p>\r\n<p></p>\r\n<p>6.1. The PARTICIPANT does hereby take on, with regard to those professional people involved in the direct and indirect execution of the activities arising from this Contract, the exclusive responsibility for compliance with the labour laws, pension laws, insurance, labour accidents, and any other legal or regulatory obligations arising from the relationship of employment or any other type of contract as they may maintain with their work teams, with NIC.br being exempt from any responsibilities, ties, or obligations.</p>\r\n<p>6.2. In any labour claims, court action or infringement notifications of any type, as may apply to the relationship of employment regarding the employees of the PARTICIPANT or of its subcontracted parties, where NIC.br may be a party being notified, called upon, summoned or called, then the PARTICIPANT shall be required to carry out all procedures as necessary so that NIC.br may be exempted from any asset responsibilities arising from such lawsuits or notifications, as also reimburse NIC.br for any sentencing and/or expenses as may arise from such claims.</p>\r\n<p>6.3. The PARTICIPANT is the only party responsible for the structure that is necessary for this party to become an Autonomous System (AS), and hence must follow the rules applicable to organisations for registration of Internet names and numbers, to be able to operate it.</p>\r\n<p>6.4. NIC.br shall not be held responsible for the configuration or operation of the Autonomous System (AS) of the PARTICIPANT, or for any other consequences as may arise from this configuration and operation.</p>\r\n<p>6.5. The present Contract shall not mean any relationship of employment between NIC.br and the PARTICIPANT, meaning that NIC.br shall have the right to freely exercise its services, without any presentation of exclusivity to the PARTICIPANT.</p>\r\n<p>6.6. NIC.br shall not be held responsible for losses or damages of any kind as may arise from the use of the infrastructure resources of IX.br, be it through operational problems or due to issues concerning the content and data as transported.</p>\r\n<p>6.6.1 NIC.br does not have any control over the routes made available by each Autonomous System in IX.br. These can be announced or withdrawn at any time, by decision made by each Autonomous System, meaning granting or denial of access to certain Internet sites and content, through IX.br.</p>\r\n<p></p>\r\n<p><b>CLAUSE SEVEN - DEFAULT AND NON-COMPLIANCE</b></p>\r\n<p></p>\r\n<p>7.1. In the event of non-compliance by the PARTICIPANT with regard to payment for the resource package chosen for the Interconnection of Autonomous Systems within a metropolitan area, then the PARTICIPANT shall be automatically declared as in default, and this means that, after a period of sixty (60) days, NIC.br shall then have the right to block the PARTICIPANT on IX.br and terminate the contract, regardless of the collection of the debt through the Courts.</p>\r\n<p>7.2. The NOC of IX.br may, should there be confirmation of non-compliance with the terms of the Policy for Acceptable Use or the Policy for Technical Requirements of IX.br, immediately proceed with the logical disconnection or transfer to a test environment, for an indefinite period, until the problem is solved. </p>\r\n<p>7.3. In the case of failure to comply with the terms of the Policy for Acceptable Use or the Policy for Technical Requirements of IX.br, on more than one occasion, or in any case where malicious intent is evident, then NIC.br shall have the right to immediately block the participation of the PARTICIPANT on IX.br and terminate the corresponding contract, regardless of the collection of any outstanding debts, also through the Courts.</p>\r\n<p></p>\r\n<p><b>CLAUSE EIGHT - MISCELLANEOUS</b></p>\r\n<p></p>\r\n<p>8.1. It shall be strictly forbidden for the PARTICIPANT to assign or transfer, for any reason, the rights and obligations taken on by means of the present Instrument, without the prior express authorisation from NIC.br.</p>\r\n<p>8.2. Under no circumstances whatsoever shall this Contract be construed as establishing a partnership or a relationship of commercial representation between the Parties, with each such Party being responsible for its own acts and obligations.</p>\r\n<p>8.3. The present Contract may only have changes made to its content by means of a contractual addendum, signed by both Parties, and this Addendum shall then become a constituent part of the present Contract.</p>\r\n<p>8.4. This Contract brings the total terms of the agreement between the signatories with regard to the issues here addressed, and does also hereby supersede, replace and repeal any possible prior understandings, negotiations and agreements.</p>\r\n<p>8.5. The PARTICIPANT does also agree, for self and also for their employees and representatives, to maintain utmost secrecy and not to reproduce, make available, transfer or otherwise assign any information, materials and/or documents from NIC.br to which they may have access by force of compliance with the purpose of this Contract, lest they shall foot the costs of any losses and damages which they may have caused through the violation of the terms of this Clause.</p>\r\n<p>8.6. Should there be any observed technical problems with the connection between the PARTICIPANT and the IX.br network that could lead to instability of the network, then the NOC of IX.br may proceed with the logical disconnection or transfer to a test environment, in order to mitigate the problem.</p>\r\n<p>8.7. NIC.br may monitor the traffic of the PARTICIPANT, including information such as the Autonomous System of origin and destination; the quantity of data that has been transported; and Layer 3 and Layer 7 protocols used, with the sole and exclusive purpose of obtaining information that could allow a better technical management of IX.br.</p>\r\n<p>8.8. NIC.br shall be allowed to publicly disclose, on the IX.br portal or by other means, any graphs and statistics based on the data collected through the monitoring mentioned in item 8.7, provided the data is made anonymous and grouped together. The identification of individual Autonomous Systems (ASs) shall not be permitted.</p>\r\n<p>8.9. NIC.br shall also be allowed to conduct tests and security trials, including attempts to access the PARTICIPANT’s equipment directly connected to IX.br without a password or using common passwords, and also to actively or passively check protocols and active services that do not comply with the Policy for Acceptable Use or the Policy for Technical Requirements.</p>\r\n<p></p>\r\n<p><b>CLAUSE NINE - THE FORUM</b></p>\r\n<p></p>\r\n<p>9.1. To sort out any doubts as may arise with regard to the present Contract, the Parties do hereby appoint the Central Law Courts of the Judicial District of São Paulo, State of São Paulo, with the renouncement of any other, however privileged it may be, as the only competent party to solve any doubts or possible controversies arising from the present Contract.</p>\r\n<p></p>\r\n<p>In agreement.</p>\r\nContract - Interconnection of Autonomous Systems\r\nRev. 1.0 - 30/06/2017\r\n<p></p>\r\n</body>\r\n"

        self.hoje = timezone.now()

        self.IX_SP_10 = IX.objects.create(
            cidade="Sao Paulo",
            codigo="sp1",
            estado="SP",
            ix_id=10,
            nome_curto="saopaulo.sp",
            nome_longo="Sao Paulo - SP"
        )

        self.IX_RIA_20 = IX.objects.create(
            cidade="Santa Maria",
            codigo="ria",
            estado="RS",
            ix_id=20,
            nome_curto="santamaria.rs",
            nome_longo="Santa Maria - RS"
        )

        self.Perfil_generico = PerfilParticipante.objects.create(
            fator_de_desconto=0.0,
            tipo="Generico",
        )
        self.Perfil_PCC = PerfilParticipante.objects.create(
            fator_de_desconto=50.0,
            tipo="PCC",
        )

        self.ASN_22548_SP = Participante.objects.create(
            asn=22548,
            cnpj='05506560000136',
            endereco_bairro='Brooklin Paulista',
            endereco_cep='04578000',
            endereco_cidade='São Paulo',
            endereco_complemento='7º andar',
            endereco_estado='SP',
            endereco_numero='11541',
            endereco_rua='Avenida das Nações Unidas',
            ix_id=self.IX_SP_10,
            razao_social='Núcleo de Inf. e Coord. do Ponto BR - NIC.BR',
            responsavel='Demi Getschko',
            telefone_ddd='11',
            telefone_numero='55093500',
            telefone_ramal='3527',
            perfil=self.Perfil_PCC,
        )
        self.ASN_22548_RIA = Participante.objects.create(
            asn=22548,
            cnpj='05506560000136',
            endereco_bairro='Brooklin Paulista',
            endereco_cep='04578000',
            endereco_cidade='São Paulo',
            endereco_complemento='7º andar',
            endereco_estado='SP',
            endereco_numero='11541',
            endereco_rua='Avenida das Nações Unidas',
            ix_id=self.IX_RIA_20,
            razao_social='Núcleo de Inf. e Coord. do Ponto BR - NIC.BR',
            responsavel='Demi Getschko',
            telefone_ddd='11',
            telefone_numero='55093500',
            telefone_ramal='3527',
            perfil=self.Perfil_generico,
        )

        self.ASN_10500 = Participante.objects.create(
            asn=10500,
            cnpj='68253654000160',
            endereco_bairro='Nossa Senhora de Lourdes',
            endereco_cep='97050650',
            endereco_cidade='Santa Maria',
            endereco_complemento='',
            endereco_estado='RS',
            endereco_numero='11541',
            endereco_rua='Rua Romeu Pereira Brenner',
            ix_id=self.IX_RIA_20,
            razao_social='Patetas SA',
            responsavel='Fulano da Silva',
            telefone_ddd='14',
            telefone_numero='55093500',
            telefone_ramal='3527',
            perfil=self.Perfil_generico,
        )

        Contrato.objects.create(
            assinado=True,
            ix=self.IX_SP_10,
            participante=self.ASN_22548_SP,
            template_pt=self.template_pt,
            template_en=self.template_en,
            tipo="Generico",
            vigente=True,
            usuario="fulano"
        )
        Contrato.objects.create(
            assinado=True,
            ix=self.IX_RIA_20,
            participante=self.ASN_22548_RIA,
            template_pt=self.template_pt,
            template_en=self.template_en,
            tipo="Generico",
            vigente=True,
            usuario="demilovato"
        )
        Contrato.objects.create(
            assinado=True,
            ix=self.IX_RIA_20,
            participante=self.ASN_10500,
            template_pt=self.template_pt,
            template_en=self.template_en,
            tipo="Generico",
            vigente=True,
            usuario="jayZ"
        )

    def createServicosEmFaturaCancelada(self):

        Servico_ASN_22548_SP_01 = Servico.objects.create(
            data_expiracao=self.hoje.replace(
                month=self.hoje.month - 2,
                day=28
            ),
            hash="aaaaa",
            ix=self.IX_SP_10,
            participante=self.ASN_22548_SP,
            preco=100.00,
            recorrente=True,
            tipo="porta_100g"
        )
        Servico_ASN_22548_SP_02 = Servico.objects.create(
            data_expiracao=self.hoje.replace(
                month=self.hoje.month - 2,
                day=28
            ),
            hash="aaaab",
            ix=self.IX_SP_10,
            participante=self.ASN_22548_SP,
            preco=10.00,
            recorrente=True,
            tipo="porta_50g"
        )
        Servico_ASN_10500_RIA = Servico.objects.create(
            data_expiracao=self.hoje.replace(
                month=self.hoje.month - 1,
                day=28
            ),
            hash="aaaac",
            ix=self.IX_RIA_20,
            participante=self.ASN_10500,
            preco=50.00,
            recorrente=True,
            tipo="porta_10g"
        )

        fat_01 = Fatura.objects.create(
            boleto_gerado=True,
            boleto_url="http://localhost:2000/home/boleto.pdf",
            encerrada=True,
            estado="CANCELADA",
            id_financeiro=51234,
            participante=self.ASN_22548_SP,
            valor=(
                Servico_ASN_22548_SP_02.preco + Servico_ASN_22548_SP_01.preco
            ),
            vencimento=self.hoje.replace(day=self.hoje.day - 3)
        )
        fat_01.servicos.add(Servico_ASN_22548_SP_01, Servico_ASN_22548_SP_02)

        fat_02 = Fatura.objects.create(
            boleto_gerado=True,
            boleto_url="http://localhost:2000/home/boleto.pdf",
            encerrada=True,
            estado="CANCELADA",
            id_financeiro=10000,
            participante=self.ASN_10500,
            valor=Servico_ASN_10500_RIA.preco,
            vencimento=self.hoje.replace(day=self.hoje.day - 3)
        )
        fat_02.servicos.add(Servico_ASN_10500_RIA)

    def createServicosEmFaturaPaga(self):
        Servico_ASN_22548_SP_01 = Servico.objects.create(
            data_expiracao=self.hoje.replace(
                month=self.hoje.month - 2,
                day=28
            ),
            hash="aaaad",
            ix=self.IX_SP_10,
            participante=self.ASN_22548_SP,
            preco=10.00,
            recorrente=True,
            tipo="porta_50g"
        )
        Servico_ASN_22548_SP_02 = Servico.objects.create(
            data_expiracao=self.hoje.replace(
                month=self.hoje.month - 2,
                day=28
            ),
            hash="aaaae",
            ix=self.IX_SP_10,
            participante=self.ASN_22548_SP,
            preco=100.00,
            recorrente=True,
            tipo="porta_100g"
        )
        Servico_ASN_10500_RIA = Servico.objects.create(
            data_expiracao=self.hoje.replace(
                month=self.hoje.month - 1,
                day=28
            ),
            hash="aaaaf",
            ix=self.IX_RIA_20,
            participante=self.ASN_10500,
            preco=50.00,
            recorrente=True,
            tipo="porta_10g"
        )

        fat_01 = Fatura.objects.create(
            boleto_gerado=True,
            boleto_url="http://localhost:2000/home/boleto.pdf",
            encerrada=True,
            estado="PAGA",
            id_financeiro=51234,
            participante=self.ASN_22548_SP,
            valor=(
                Servico_ASN_22548_SP_02.preco + Servico_ASN_22548_SP_01.preco
            ),
            vencimento=self.hoje.replace(day=self.hoje.day - 3)
        )
        fat_01.servicos.add(Servico_ASN_22548_SP_01, Servico_ASN_22548_SP_02)

        fat_02 = Fatura.objects.create(
            boleto_gerado=True,
            boleto_url="http://localhost:2000/home/boleto.pdf",
            encerrada=True,
            estado="PAGA",
            id_financeiro=10000,
            participante=self.ASN_10500,
            valor=Servico_ASN_10500_RIA.preco,
            vencimento=self.hoje.replace(day=self.hoje.day - 3)
        )
        fat_02.servicos.add(Servico_ASN_10500_RIA)

    def createServicoComExpiracaoFutura(self):
        Servico_ASN_22548_SP_01 = Servico.objects.create(
            data_expiracao=self.hoje + timezone.timedelta(days=30*3),
            hash="aaaag",
            ix=self.IX_SP_10,
            participante=self.ASN_22548_SP,
            preco=10.00,
            recorrente=True,
            tipo="porta_50g"
        )

        Servico_ASN_22548_SP_02 = Servico.objects.create(
            data_expiracao=self.hoje + timezone.timedelta(days=30*2),
            hash="aaaah",
            ix=self.IX_SP_10,
            participante=self.ASN_22548_SP,
            preco=100.00,
            recorrente=True,
            tipo="porta_100g"
        )
        fat_01 = Fatura.objects.create(
            boleto_gerado=True,
            boleto_url="http://localhost:2000/home/boleto.pdf",
            encerrada=True,
            estado="PAGA",
            id_financeiro=51234,
            participante=self.ASN_22548_SP,
            valor=(
                Servico_ASN_22548_SP_02.preco + Servico_ASN_22548_SP_01.preco
            ),
            vencimento=self.hoje.replace(day=self.hoje.day - 3)
        )
        fat_01.servicos.add(Servico_ASN_22548_SP_01, Servico_ASN_22548_SP_02)

        Servico.objects.create(
            data_expiracao=self.hoje + timezone.timedelta(days=30*2),
            hash="aaaai",
            ix=self.IX_RIA_20,
            participante=self.ASN_22548_RIA,
            preco=100.00,
            recorrente=True,
            tipo="porta_100g"
        )

        Servico.objects.create(
            data_expiracao=self.hoje + timezone.timedelta(days=30*1),
            hash="aaaaj",
            ix=self.IX_RIA_20,
            participante=self.ASN_10500,
            preco=50.00,
            recorrente=True,
            tipo="porta_10g"
        )
