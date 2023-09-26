# Moorse Python SDK

O moorse sdk surge como solução ao problema que muitos desenvolvedores enfrentam ao necessitar criar suas próprias requisições http aos serviços web da Moorse, com ele, torna-se possível enviar requests à nossa API de forma simplificada, sem a necessidade de configurar todos os requests do início ao fim.

Todos os métodos e rotas aqui citados podem ser encontrados com maiores detalhes na [documentação da Moorse](https://moorse.readme.io/reference/princ%C3%ADpios-b%C3%A1sicos), bem como maiores detalhes sobre nossos produtos.

## Sumário

1. [Início rápido](#1-início-rápido)
2. [Objeto Moorse](#2-objeto-moorse)
3. [Autorização](#3-autorização)
    1. [login](#31-login)
    2. [set_token](#32-set_token)
    3. [get_token](#33-get_token)
    4. [set_email](#34-set_email)
    5. [get_email](#35-get_email)
    6. [set_password](#36-set_password)
    7. [get_password](#37-get_password)
4. [Mensagens](#4-mensagens)
    1. [send_text](#41-send_text)
    2. [send_file](#42-send_file)
    3. [send_template](#43-send_template)
    4. [send_list_menu](#44-send_list_menu)
    5. [send_buttons](#45-send_buttons)
5. [Integrações](#5-integrações)
    1. [get_one](#51-get_one)
    2. [get_all](#52-get_all)
    3. [delete](#53-delete)
    4. [get_status](#54-get_status)
6. [Webhooks](#6-webhooks)
    1. [create](#61-create)
    2. [update](#62-update)
    3. [delete](#63-delete)
    4. [get_one](#64-get_one)
    5. [get_all](#65-get_all)
7. [Templates](#7-templates)
    1. [create](#71-create)
    2. [delete](#72-delete)
    3. [get_one](#73-get_one)
    4. [get_all](#74-get_all)
8. [Relatórios](#8-relatórios)
    1. [get_messages](#81-get_messages)
    2. [get_messages_by_channel](#82-get_messages_by_channel)
    3. [get_messages_by_timeline](#83-get_messages_by_timeline)
9. [Faturamento](#9-faturamento)
    1. [get_credits](#91-get_credits)

## 1. Início Rápido

Antes de tudo, inicie um projeto em python e instale o sdk da Moorse utilizando o comando:

```bash
pip install moorse
```

Após instalada a dependência, crie um objeto Moorse e faça login para estar apto a enviar mensagens utilizando suas integrações.

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'seu-email@email.com',
    'sua-senha-da-moorse-aqui',
    CommunicationChannel.WHATSAPP # <--- Tipo do canal de comunicação
)

moorse.auth.login()

moorse.send_text(
    '5583916233664', # <--- Número do destinatário
    'sua-mensagem',
    'id-da-sua-integração-moorse'
)
```

## 2. Objeto Moorse

A classe **Moorse** é o ponto chave de todo o SDK, criando uma instância dela é possível gerenciar integrações, criar templates, configurar webhooks, enviar mensagens e muito mais!

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'seu-email@email.com',
    'sua-senha-da-moorse-aqui',
    CommunicationChannel.WHATSAPP # <--- Tipo do canal de comunicação
)
```

Acima é criada uma instância **Moorse** que configura e-mail e senha de uma conta bem como o canal de comunicação desejado para enviar mensagens, essas informações serão úteis para que posteriormente seja possível gerar um token de acesso e consigamos realizar chamadas à API.

## 3. Autorização

Para que seja possível acessar todos os recursos da sua conta é necessário obter seu token de acesso. Desse modo, o objeto Moorse provê um atributo público nomeado *auth*, com ele é possível chamar a rota de login da Moorse que possibilita receber o token em troca do e-mail e senha da conta.

### 3.1. login

Após seu email e senha serem configurados, é possível fazer login e obter seu token de acesso.

#### Definição:

```python
def login(self) -> LoginResponse:
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()
```

Aqui, a linha `moorse.auth.login()`, configura o token de acesso da conta no objeto moorse. Posteriormente isso será importante para que sejamos capazes de executar outros métodos que operam sobre informações pessoais da conta do usuário.

### 3.2 set_token

Método setter padrão, serve para definir o token que se deseja usar diretamente e não precisar fazer chamadas à API da Moorse.

#### Definição:

```python
def set_token(self, token: str) -> None:
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.set_token('seu-token-secreto')
```

### 3.3 get_token

Método getter padrão, serve para resgatar o token salvo no SDK.

#### Definição:

```python
def get_token(self) -> str:
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

meu_email: str = moorse.auth.get_token()
```

### 3.4 set_email

Método setter padrão, serve para definir o email que se deseja configurar no SDK para realizar o login.

#### Definição:

```python
def set_email(self, email: str) -> None:
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.set_email('seu-email-moorse')
```

### 3.5 get_email

Método getter padrão, serve para resgatar o email salvo no SDK.

#### Definição:

```python
def get_email(self) -> str:
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

meu_email: str = moorse.auth.get_email()
```

### 3.6. set_password

Método setter padrão, serve para definir a senha que se deseja configurar no SDK para realizar o login.

#### Definição:

```python
def set_password(self, password: str) -> None:
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.set_password('sua-senha-moorse')
```

### 3.7. get_password

Método getter padrão, serve para resgatar a senha salva no SDK.

#### Definição:

```python
def get_password(self) -> str:
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

minha_senha: str = moorse.auth.get_password()
```

## 4. Mensagens

### 4.1. send_text

Método que serve para enviar uma mensagem de texto utilizando o canal de comunicação(WHATSAPP, INSTAGRAM OU SMS) selecionado na instanciação do objeto Moorse.

#### Definição:

```python
def send_text(
    self, 
    to: str, 
    body: str, 
    integration_id: str
) -> MessageSentResponse:
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

moorse.send_text(
    '551175839219', # <-- destinatário
    'mensagem-teste', # <-- corpo da mensagem
    'a7eb547b-9bfc-4307-bac0-92bad46da00f' # <-- integração
)
```

### 4.2. send_file

Método que serve para enviar um arquivo utilizando o canal de comunicação WHATSAPP.

*Esse método não tem implementação para INSTAGRAM nem SMS.*

#### Definição:

```python
def send_file(
    self, 
    to: str, 
    body: str, 
    filename: str, 
    integration_id: str, 
    caption: str = None
) -> MessageSentResponse
```

#### Exemplo:

```python
from moorse import Moorse, CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

moorse.send_file(
    '551175839219', # <-- destinatário
    'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf', # <-- conteudo do arquivo (url ou base64)
    'dummy.pdf', # <-- nome do arquivo
    'a7eb547b-9bfc-4307-bac0-92bad46da00f' # <-- integração
)
```

### 4.3. send_template

Método que serve para enviar um template utilizando o canal de comunicação WHATSAPP.

*Esse método não tem implementação para INSTAGRAM nem SMS.*

#### Definição:

```python
def send_template(
    self, 
    template: TemplateMessageRequest, 
    integration_id: str
) -> MessageSentResponse:
```

#### Exemplo:

```python
# TODO
```

### 4.4. send_list_menu

Método que serve para enviar um menu utilizando o canal de comunicação WHATSAPP.

*Esse método não tem implementação para INSTAGRAM nem SMS.*

#### Definição:

```python
def send_list_menu(
    self, 
    menu: MenuMessageRequest, 
    integration_id: str
) -> MessageSentResponse:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel
from moorse import MenuMessageRequest
from moorse import Action
from moorse import Section
from moorse import Row

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

menu: MenuMessageRequest = MenuMessageRequest(
    '551175839219',
    'titulo-do-menu',
    Action([
        Section('Carnes', [
            Row('1', 'Carne de sol'),
            Row('2', 'Carne de panela'),
            Row('3', 'Carne de churrasco')
        ]),
        Section('Bebidas', [
            Row('4', 'Cerveja'),
            Row('5', 'Refrigerante'),
            Row('6', 'Suco')    
        ])
    ])
)

moorse.send_list_menu(
    menu, 
    'id-integracao'
)
```

### 4.5. send_buttons

Método que serve para enviar botões utilizando o canal de comunicação WHATSAPP.

*Esse método não tem implementação para INSTAGRAM nem SMS.*

#### Definição:

```python
def send_buttons(
    self, 
    buttons: ButtonsMessageRequest, 
    integration_id: str
) -> MessageSentResponse
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel
from moorse import ButtonsMessageRequest
from moorse import Button

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

buttons: ButtonsMessageRequest = ButtonsMessageRequest(
    '551175839219',
    'Teste de botões',
    [
        Button('1', 'botao 1'), 
        Button('2', 'botao 2'), 
        Button('3', 'botao 3')
    ]
)

moorse.send_buttons(
    buttons, 
    'id-integracao'
)
```

## 5. Integrações

Após ter passado da etapa de autorização usando o método login para obtenção do token você está apto a acessar os recursos da sua conta. O que primeiro veremos são as rotas que envolvem integrações Moorse.

### 5.1. get_one

Método responsável por resgatar as informações de uma integração Moorse dado seu id.

#### Definição:

```python
def get_one(self, integration_id: str):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.integration.get_one(
    'id-integracao'
)
```

### 5.2. get_all

Pega a informação de todas as integrações pertencentes à conta, para isso é apenas necessário a configuração do token da conta.

#### Definição:

```python
def get_all(self):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.integration.get_all()
```

### 5.3. delete

Método responsável por deletar um integração dado seu id.

#### Definição:

```python
def delete(self, integration_id: str):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.integration.delete(
    'id-integracao'
)
```

### 5.4. get_status

Método responsável por resgatar o status de uma integração dado seu id.

#### Definição:

```python
def get_status(self, integration_id: str):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.integration.get_status(
    'id-integracao'
)
```

## 6. Webhooks

Assumindo que o leitor já tenha realizado o login e obtido o seu token de acesso, torna-se possível manipular os webhooks da sua conta para receber requests em uma URL específica quando houverem eventos com as suas integrações. A seguir estão listados os métodos capazes de interagir com os webhooks.

### 6.1. create

Método capaz de criar um webhook em uma conta Moorse, dadas as informações necessárias à sua criação.

#### Definição:

```python
def create(self, webhook: WebhookRequest):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel
from moorse import WebhookRequest
from moorse import WebhookMethod
from moorse import Pair

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.webhook.create(
    WebhookRequest(
        'nome-webhook', # <-- nome desejado ao novo webhook
        'https://google.com.br', # <-- url à qual a moorse enviará o webhook
        WebhookMethod.GET, # <-- método http do request do webhook
        True, # <-- o webhook vai estar ativo ao ser criado? s/n
        [
            'integracao-1', # integrações associadas
            'integracao-2'  # ao webhook
        ],
        [
            Pair('src', 'moorse'),      # cabeçalhos personalizados
            Pair('channel', 'whatsapp') # ao webhook
        ],
        False, # <-- o webhook notificará mensagens respondidas? s/n
        True,  # <-- o webhook notificará mensagens recebidas? s/n
        False, # <-- o webhook notificará mensagens enviadas? s/n
        1, # número de retentativas 
        10 # timeout (em segundos)
    )
)
```

### 6.2. update

Método capaz de atualizar um webhook dado seu id, de modo semelhante ao método de cima.

#### Definição:

```python
def update(self, webhook_id: str, webhook: WebhookRequest):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel
from moorse import WebhookRequest
from moorse import WebhookMethod
from moorse import Pair

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.webhook.update(
    'webhook-id', # <-- id do webhook que se deseja atualizar
    WebhookRequest(
        'nome-webhook', # <-- nome desejado ao novo webhook
        'https://google.com.br', # <-- url à qual a moorse enviará o webhook
        WebhookMethod.GET, # <-- método http do request do webhook
        True, # <-- o webhook vai estar ativo ao ser criado? s/n
        [
            'integracao-1', # integrações associadas
            'integracao-2'  # ao webhook
        ],
        [
            Pair('src', 'moorse'),      # cabeçalhos personalizados
            Pair('channel', 'whatsapp') # ao webhook
        ],
        False, # <-- o webhook notificará mensagens respondidas? s/n
        True,  # <-- o webhook notificará mensagens recebidas? s/n
        False, # <-- o webhook notificará mensagens enviadas? s/n
        1, # número de retentativas 
        10 # timeout (em segundos)
    )
)
```

### 6.3. delete

Método capaz de deletar um webhook dado seu id.

#### Definição:

```python
def delete(self, webhook_id: str):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.webhook.delete('webhook-id')
```

### 6.4. get_one

Método capaz de obter a informação de um webhook dado seu id.

#### Definição:

```python
def get_one(self, webhook_id: str):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.webhook.get_one('webhook-id')
```

### 6.5. get_all

Método capaz de obter a informação de todos os webhooks de uma conta, este método não recebe informação como parâmetro, já que apenas necessita do token de acesso do dono da conta com os webhooks, e este é configurado com a utilização do método login.

#### Definição:

```python
def get_all(self):
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.webhook.get_all()
```

## 7. Templates

Nesta seção são apresentados os métodos que permitem a um usuário Moorse manipular seus templates e realizar ações como criação, remoção e obtenção das informações de um template.

### 7.1. create

Método responsável por criar um template na sua conta.

#### Definição:

```python
def create(self, webhook: TemplateRequest) -> TemplateDto:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel
from moorse import TemplateRequest
from moorse import TemplateType
from moorse import TemplateCategory
from moorse import TemplateLanguage
from moorse import TemplateDocumentComponent
from moorse import TemplateComponentType
from moorse import TemplateTextComponent
from moorse import TemplateButtonComponent
from moorse import ButtonQuickReply
from moorse import ButtonUrl

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

# Acessar https://moorse.readme.io/reference/criar-um-novo-template
# Para mais informações sobre criação de templates

response = moorse.template.create(
    TemplateRequest(
        'nome-do-template',
        'descricao-do-template',
        TemplateType.STANDARD, 
        'id-integracao',
        TemplateCategory.AUTO_REPLY,
        TemplateLanguage.PORTUGUESE_BR,
        [
            TemplateDocumentComponent(TemplateComponentType.HEADER),
            TemplateTextComponent(TemplateComponentType.BODY, "Texto do header"),
            TemplateButtonComponent([
                ButtonQuickReply("Texto do botão 1"),
                ButtonQuickReply("Texto do botão 2"),
                ButtonUrl("Texto do botão 3", "https://moorse.io")
            ])
        ]
    )
)
```

### 7.2. delete

Método responsável por deletar um template da sua conta dado o id do template.

#### Definição:

```python
def delete(self, template_id: str) -> TemplateDto:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

moorse.template.delete('template-id')
```

### 7.3. get_one

Método responsável por obter informação de um template específico de uma conta Moorse dado o id do template buscado.

#### Definição:

```python
def get_one(self, template_id: str) -> TemplateDto:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.template.get_one('template-id')
```

### 7.4. get_all

Método responsável por obter informação de todos os templates de uma conta Moorse.

#### Definição:

```python
def get_all(self) -> TemplateList:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.template.get_all()
```

## 8. Relatórios

Com os métodos aqui citados é possível receber informações sobre quantidade, canais e dias que as mensagens da conta foram enviadas. Para que seja possível acessar estes métodos é necessário apenas estar logado na sua conta Moorse e ter obtido o token de acesso com .login().

### 8.1. get_messages

Método que serve para obter informação da quantidade de mensagens enviadas e recebidas e do número de contatos com os quais se manteve contato com alguma integração em um dado período de tempo.

#### Definição:

```python
def get_messages(self, begin: str, end: str) -> MessagesReportDto:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()
moorse.report.get_messages(
    '2019-01-31', # <-- data de início do relatório 
    '2023-01-31'  # <-- data de fim do relatório
)
```

### 8.2. get_messages_by_channel

Método que serve para obter informação da quantidade de mensagens por canal (WHATSAPP, INSTAGRAM ou SMS) com alguma integração em um dado período de tempo.

#### Definição:

```python
def get_messages_by_channel(self, begin: str, end: str) -> MessagesByChannelReportDto:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()
moorse.report.get_messages_by_channel(
    '2019-01-31', # <-- data de início do relatório 
    '2023-01-31'  # <-- data de fim do relatório
)
```

### 8.3. get_messages_by_timeline

Método que serve para obter informação da quantidade de mensagens mês a mês com alguma integração em um dado período de tempo.

#### Definição:

```python
def get_messages_by_timeline(self, begin: str, end: str) -> MessagesByTimelineReportDto:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()
moorse.report.get_messages_by_timeline(
    '2019-01-31', # <-- data de início do relatório 
    '2023-01-31'  # <-- data de fim do relatório
)
```

## 9. Faturamento

Serviço que conta apenas com um método que serve para pegar todos os créditos de uma integração. É necessário que o usuário esteja logado para acessá-lo.

### 9.1. get_credits

Método que serve para resgatar o número de créditos de uma dada integração.

#### Definição:

```python
def get_credits(self, integration_id: str) -> BillingDto:
```

#### Exemplo:

```python
from moorse import Moorse
from moorse import CommunicationChannel

moorse = Moorse(
    'email', 'senha', 
    CommunicationChannel.WHATSAPP
)

moorse.auth.login()

response = moorse.billing.get_credits("id-integracao")
```