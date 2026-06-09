Ant-SVD
=======

Ant-SVD é um projeto da disciplina SME0104 - Cálculo Numérico, pelo Prof. Dr. Geovane Augusto Haveroth.

O objetivo é utilizar o método SVD visto em sala de aula para construir uma ferramenta prática capaz de
separar o fundo de um vídeo das partes dinâmicas (objetos se movendo).

## Desenvolvimento

A aplicação foi desenvolvida utilizando a linguagem Python e diversas bibliotecas, incluindo:

 - NumPy
 - SciPy
 - scikit-image
 - scikit-video

## Instruções de uso

Tendo clonado o repositório em sua máquina, é possível usar o gerenciador de pacotes nix
para instalar as demais dependências. Para instalá-lo no Ubuntu, use:

```sh
apt install nix
```

Após isso, apenas execute:

```sh
./devshell.sh
```

e isso colocará o terminal em um shell com todas as dependências instaladas. Feito isso,
o(s) seguinte(s) comando(s) podem ser usados para executar a ferramenta:

```sh
python -m src.ant_svd $OPTIONS $FILE
# ou
uvx . $OPTIONS $FILE
# ou
uv run ant-svd $OPTIONS $FILE
```

Onde `$OPTIONS` é uma lista de opções que podem ser passadas para controlar o comportamento
da ferramenta, cuja documentação pode ser lida ao executar um dos comandos acima com a opção
`-h` ou `--help`.

Por sua vez, `$FILE` deve ser um arquivo de vídeo que será processado.
