# PetFinder

Projeto de Engenharia de Software que envolve a aplicação de uma coleira inteligente pra monitoramento de pets.

A proposta é uma coleira híbrida de identificação e localização, que combina tecnologia NFC e QR Code a um custo acessível e sem mensalidade:

Qualquer pessoa pode se aproximar da coleira e escanear o código pode acessar as informações do tutor e enviar sua localização, sem necessidade de aplicativos.

---

A equipe é composto por:

- Giovana Campos: gcampos.2025@alunos.utfpr.edu.br
- Eliseu Camargo: eliseucamargo@alunos.utfpr.edu.br
- Thais Santos: thaissantos.1997@alunos.utfpr.edu.br
- João Alberto: joaotrassi@alunos.utfpr.edu.br

---

# Como testar o projeto (Docker)

## Iniciar o servidor
Antes de qualquer coisa é necessário que o docker esteja instalado em sua maquina: 

www.docker.com/products/docker-desktop/

Após baixar é necessario que ele esteja executando, caso contrário não é possivel chamar o docker no terminal.

Abra o terminal **dentro da pasta do seu clone local** (se não estiver nela, use `cd [diretório onde o projeto está salvo]`). Não é possível iniciar o Docker a partir de um repositório remoto, só da cópia local.

```bash
docker compose up --build
```

Esse comando cria a imagem do projeto e sobe o servidor e o banco de dados. Ao terminar, o terminal mostra possíveis erros.

Com o servidor iniciado, abra no navegador:

```
localhost:8081
```

Você será direcionado para a tela de login caso não esteja autenticado. Existe um usuário padrão de teste:

- **E-mail:** `tutor@teste.com`
- **Senha:** `teste1234`

Para parar o servidor, use `Ctrl+C` no terminal. Para derrubar os containers, use `docker compose down`.

## Ver as alterações no navegador

O `docker-compose.yml` monta a pasta do projeto dentro do container (`volumes: - .:/app`). Na prática, o container enxerga os arquivos do seu VS Code em tempo real, e **não é preciso rodar o `--build` a cada alteração**:

| O que você mudou | O que fazer |
|---|---|
| HTML, CSS, JavaScript ou imagens | Salvar o arquivo e atualizar o navegador com `Ctrl+F5` (limpa o cache) |
| Arquivos `.py` (views, forms, urls) | Salvar o arquivo. O servidor reinicia sozinho; depois, atualizar o navegador |
| `requirements.txt` ou `Dockerfile` | `docker compose up --build` |
| `Banco_de_dados.sql` | Recriar o banco (veja abaixo) |

Se o servidor não atualizar sozinho depois de salvar, pare com `Ctrl+C` e rode `docker compose up --build` de novo, que sempre funciona.

## Banco de dados

O arquivo `Banco_de_dados.sql` só é executado quando o banco é criado pela primeira vez. Se ele for alterado, o banco antigo **não** é atualizado sozinho. Para recriar o banco a partir do arquivo:

```bash
docker compose down -v
docker compose up --build
```

O `-v` apaga os dados do banco, incluindo cadastros de teste. O usuário padrão é recriado junto, porque faz parte do `.sql`.

Cada pessoa tem o seu próprio banco, na sua máquina. Os dados cadastrados em um computador não aparecem em outro.

Para ver o que foi cadastrado:

```bash
docker compose exec db mysql -uroot -proot coleira_pet --default-character-set=utf8mb4 -e "select * from pet;"
```

(troque `pet` pelo nome da tabela que quiser ver)

---

# Recomendações para o front

Este projeto usa Django. Você não precisa saber Python para mexer nas telas, mas precisa seguir algumas regras nos arquivos HTML.

## Onde ficam os arquivos

Cada tela pertence a um app (`pet`, `tutor`, `emergencia`, `endereco`...). Dentro de cada app:

```
pet/
  templates/pet/cadastro_pet.html   <- HTML
  static/css/pet.css                <- CSS
  static/js/pet.js                  <- JavaScript
  static/img/                       <- imagens
```

Dentro de `templates/` existe outra pasta com o nome do app. Isso é obrigatório: o Django procura `pet/cadastro_pet.html`.

## CSS, JS e imagens

No topo do HTML, uma vez só:

```html
{% load static %}
```

Nunca use caminho solto como `href="style.css"`, porque não funciona. Use:

```html
<link rel="stylesheet" href="{% static 'css/pet.css' %}">
<script src="{% static 'js/pet.js' %}"></script>
<img src="{% static 'img/PetFinder-Logo.png' %}" alt="PetFinder">
```

O texto entre aspas é o caminho a partir da pasta `static/`. Para conferir se um arquivo está sendo servido, abra no navegador `localhost:8081/static/css/pet.css`: se mostrar o conteúdo do arquivo, o caminho está certo.

Arquivos de apps diferentes com o mesmo caminho dentro de `static/` entram em conflito. Por isso, prefira nomes únicos ou uma subpasta com o nome do app.

## Links e formulários

- **Links entre telas:** `{% url 'tutor:login' %}`, no formato `app:nome_da_rota`. Os nomes das rotas estão no `urls.py` de cada app.
- **Formulários:** todo `<form method="POST">` precisa de `{% csrf_token %}` logo depois da tag de abertura. Sem ele, o envio dá erro 403.
- **Campos:** o atributo `name` de cada `<input>` precisa ser igual ao nome do campo no `forms.py` do backend. Se o nome estiver diferente, o campo chega vazio e o formulário não salva.

## Erros comuns

| Mensagem | O que significa |
|---|---|
| `TemplateDoesNotExist: pet/x.html` | O nome no `render(...)` da view não bate com o nome do arquivo, ou o arquivo não está em `templates/<app>/`. |
| `NoReverseMatch: Reverse for 'x'` | O nome usado em `{% url %}` não existe. Confira o `urls.py` e o prefixo `app:`. |
| Página aparece sem estilo | Falta `{% static %}` no link do CSS, ou o arquivo não está em `static/`. |
| Mudei o arquivo e nada mudou | O navegador usou cache (`Ctrl+F5`), ou a pasta `volumes` não está no `docker-compose.yml`. |
| `403 CSRF verification failed` | Falta `{% csrf_token %}` no formulário. |

Quando algo dá errado, o Django mostra uma página amarela com o erro. Ela indica o arquivo e a linha do problema. Ao pedir ajuda ao backend, mande o texto da linha `Exception Value`.