# Banco do Brasil

![Static Badge](https://img.shields.io/badge/status-em_progresso-blue)

Uma biblioteca que realiza algumas operações no site do banco do brasil.

Lib muito útil para empresas que não possuem acesso a API oficial.

O projeto não está finalizado, e em breve irá fornecer um auxilio integral nos seus projetos.

# Como roda a aplicação

No terminal, clone o projeto:
```
git clone https://github.com/ruan-albuquerque204/Banco-do-Brasil-Scrap.git
```

Ao finalizar o projeto, você poderá utilizar a biblioteca livremente, caso queria instalar em alguma venv de um projeto específico, também é possível instalar da seguinte forma

```py
# Instalação de modo estático
pip install "caminha/da/biblioteca/brasil"
```
ou
```py
# Caso queira editar a biblioteca e manter todos os seus projetos que a utilizam atualizados.
pip install -e "caminha/da/biblioteca/brasil"
```

# Funcionalidades

`bb = Brasil(usuario, senha, echo=True, headless=False)` - cria o nosso objeto inicial. Também é possivel utilizar com o comando `with`.

`bb.close` - desloga do banco e finaliza a janela aberta.

`bb.consult_boleto(chave)` - retorna um dicionário com algumas informações do boleto

`bb.void_boleto(chave, valor)` - realiza a baixa do boleto informado, retorna um dicionário com status e mensagem.

`bb.descount_boleto` - realiza o abatimento do boleto informado, retorna um dicionário com status e mensagem

`bb.register_boleto` - registra o uma chave de boleto. ⚠ Incompleto ⚠



# Tecnologias
- `Python`

# Autor
[Ruan de Albuquerque Santos](https://github.com/ruan-albuquerque204)

![Imagem Ruan](https://avatars.githubusercontent.com/u/119131595?v=4)