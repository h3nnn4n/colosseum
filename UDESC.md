# Colosseum
## Introdução

Colosseum é uma plataforma automatizada de competições de agentes autônomos. O
projeto tem como principal objetivo o incentivo dos estudos em Inteligência
Artificial e disciplinas relacionadas atravéz de competição e premem em
dinheiro. Alternativamente, o projeto também oferece aos envolvidos uma
oportunidade de trabalhar e desenvolver utilizando tecnologias frequentemente
encontradas no mercado de trabalho.

O projeto conta com um sistema modular, onde multiplos jogos podem ser
integrados ao sistema e participantes podem registrar agentes para competir
nestes jogos. Os agentes competem uns contra os outros de maneira autonoma em
torneios periodicos. Premiações podem ser oferecidas aos vencedores de
torneiros específicos, ou com base nos rankings dos agents.

## Timeline

- Janeiro:
  - Testes internos
  - Correção de bugs
  - Desenvolvimento das features necessárias
- Fevereiro:
  - Competição interna entre voluntários
  - Divulgação da pre temporada
- Março:
  - Fim do semestre 2021/2
  - Pré temporada (testes)
  - Inicio da divulgação da temporada começando em abril
- Abril:
  - Início do semestre 2022/1
  - Início dos torneios
- Maio:
- Junho:
  - Fim dos torneios

## Recursos necessários

Para o desempenho do projeto multiplos recursos são desejáveis e/ou necessários:

Necessários:
- Servidores (físicos ou virtuais)
  - Bancos de dados (postgres, redis)
  - Web (gunicorn, nginx)
  - Execução das partidas
- Dinheiro para premiação

Desejáveis:
- Dinheiro para bug bounties (ou feature bounties)
  - Pagar alunos pela descoberta de bugs
  - Pagar alunos por corrigir bugs ou implementar features
- Beta testers
- Voluntários para tirar dúvidas dos participantes

## Papel do bolsista

- Testar o sistema
- Tirar dúvidas
- Documentação do sistema
- Manutenção do sistema
- Adiministração da infraestrutura
- Correção de bugs
- Implementação de novas funcionalizades
- Divulgação
- Criação de conteúdo
  - Tutoriais
  - Exemplos de agentes

## Estado atual do projeto

O projeto conta atualmente com um sistema completamente funcional e autonomo
hospedado em atualmente hospedado em
[https://colosseum.website](https://colosseum.website).
Dois jogos estão disponíveis. O primeiro deles sendo xadrez. O segundo jogo
consiste em um cenário multi-agente, onde os agentes competem por comida e
devem capturar mais comida que os adversários para ganhar.

Os seguintes repositórios contem o projeto:
- [Colosseum](https://github.com/h3nnn4n/colosseum): Motor de torneios e os
  modulos de jogos / problemas.
- [Website](https://github.com/h3nnn4n/colosseum_website): Site com placar e
  API utilizada pelo motors de torneios.
- [Agentes](https://github.com/h3nnn4n/colosseum_agents): Agentes de exemplo
  para os games implementados na engine.
- [SDK](https://github.com/h3nnn4n/colosseum_sdk): SDK para os games. Todos os
  jogos contam com uma interface padronizada que permite agentes em qualquer
  linguagem. Este repositorio contem bibliotecas para facilitar a implementação
  em lingaguens específicas.
- [Infraestrutura](https://github.com/h3nnn4n/colosseum_infra): Codigo
  utilizado para gerenciamento de recursos, servidores, releases, etc.
- [Vizualizadores](https://github.com/h3nnn4n/colosseum_renderer): Contem
  vizualizadores modulares para executar replays dos games. Pode auxiliar a
  depuração dos agentes, monitoramento ou vizualização para fins de
  entreterimento (exemplo: Fazer streaming das finais de uma temporada).
