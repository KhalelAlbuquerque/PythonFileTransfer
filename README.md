# 📁 PythonFileTransfer
Trabalho feito por Ramon e Khalel.

## 🚀 Instalação das Dependências
Para instalar as dependências necessárias para o projeto, execute o comando abaixo no terminal:

```bash
pip install -r requirements.txt
```



## 🛠️ Como Executar o Projeto
Este projeto requer a execução de três processos em paralelo. Para isso, abra três terminais na pasta do projeto:

1. No primeiro terminal inicie o serviço de nomes do Pyro4:
```bash
python -m Pyro4.naming
```


2. No segundo terminal inicie o servidor:
```bash
python ./server.py
```

2. No terceiro terminal inicie a interface do cliente:
```bash
python ./terminal.py
```
