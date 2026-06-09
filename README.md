Ant-SVD
=======

Ant-SVD é um projeto da disciplina SME0104 - Cálculo Numérico, pelo Prof. Dr. Geovane Augusto Haveroth.

O objetivo é utilizar o método SVD visto em sala de aula para construir uma ferramenta prática capaz de
separar o fundo de um vídeo das partes dinâmicas (objetos se movendo).

## Desenvolvimento

A aplicação foi desenvolvida utilizando a linguagem Python e diversas bibliotecas, como NumPy e Scipy.

## Rodar Localmente

Tendo clonado o repositório em sua máquina, a primeira dependência é ter o gerenciador de pacotes Nix. Para instalá-lo no Ubuntu, use:

`apt install nix`

Após isso, apenas execute:

`./devshell.sh`

e isso colocará o terminal em um shell com os pacotes corretamente funcionando. Para executar o programa:

`python3 src/main.py input/ants-concrete.webm`
