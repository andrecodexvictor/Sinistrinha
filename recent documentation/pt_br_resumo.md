# Resumo das Mudanças e Integração Realizada

Nossa missão foi transformar a aplicação de um "protótipo visual" em um **sistema full-stack 100% funcional, integrado e pronto para produção**. 

1. **Correção de Erro Fatal (Backend):** O servidor Django estava quebrando ao iniciar (`ImportError`) porque as rotas chamavam `FreeSpinView` e `LevelProgressView` que não existiam. Ambas foram devidamente programadas em `apps/game/views.py`.
2. **Fim das Simulações (Mocks) no React:** Removemos todas as funções `setTimeout` falsas do frontend. Agora, o botão de "Girar", "Depositar" e "Login" se comunicam de verdade com o banco de dados via API.
3. **Autenticação JWT End-to-End:** Implementamos o cliente Axios (`api.ts`) que agora injeta automaticamente os tokens JWT em todas as requisições privadas e possui inteligência para renovar o token automaticamente se ele expirar.
4. **Mapeamento de Contratos de Dados:** Havia uma incompatibilidade enorme: o React esperava variáveis como `totalWin`, e o Django enviava `payout`. Refatoramos os tipos no frontend (`game.types.ts`) para casar exatamente com o formato do backend.
5. **Comunicação em Tempo Real Ativada:** O `casinoStore.ts` agora se conecta via WebSocket (`ws/casino/`) ao Django Channels. Se o jogador 1 ganhar um Jackpot, o jogador 2 vê a notificação subir na tela na mesma hora.
6. **Pipeline de CI/CD (GitHub Actions):** Criamos a automação que testa o código Python, compila o TypeScript do frontend e faz um teste de sanidade com Docker sempre que você envia código para o repositório.
7. **Documentação de Arquitetura:** Criamos o `ARCHITECTURE.md` para mapear visualmente todas as portas, bancos e rotas.

---

# Características e Impacto dos Frameworks Utilizados

Para entender o poder da sua arquitetura moderna, veja como cada tecnologia está desempenhando seu papel no ecossistema do **Sinistrinha**:

### 🟢 Django & Django REST Framework (A Base de Regras de Negócio)
*   **A Característica:** O Django é "baterias inclusas", altamente seguro e estruturado em aplicativos (`apps`). O Django REST Framework (DRF) transforma modelos do banco em JSON.
*   **Impacto no Projeto:** Ele garante que ninguém consiga burlar o sistema de saldos.
*   **Exemplo Prático:** O Django usa **Views Baseadas em Classes** (como a classe `SpinView` em `apps/game/views.py`). Nela, usamos um decorador `@transaction.atomic`. Isso significa que se o jogador girar a roleta, a aposta for descontada do saldo, mas o servidor cair antes de dar o prêmio, **toda a operação é desfeita**. O saldo do jogador fica completamente protegido contra quedas de energia no servidor.

### ⚛️ React + Vite (A Camada de Experiência do Usuário)
*   **A Característica:** O React cria interfaces dinâmicas usando "Componentes", enquanto o Vite é o motor de desenvolvimento que constrói os arquivos finais para a web numa velocidade impressionante.
*   **Impacto no Projeto:** Permite transições suaves sem que a tela do navegador pisque ou recarregue.
*   **Exemplo Prático:** O Vite usa o arquivo `vite.config.ts`. Nele, configuramos um recurso de **Proxy**. Quando estamos desenvolvendo localmente, o Vite intercepta requisições feitas para `/api/` e as envia silenciosamente para a porta `:8000` (Django). Isso impede que o navegador bloqueie a aplicação com o famoso "Erro de CORS" (Cross-Origin Resource Sharing).

### 🐻 Zustand (Gerenciamento de Estado Global)
*   **A Característica:** Em vez de usar contextos pesados do React ou o temido Redux, o Zustand cria "Lojas" (Stores) globais em memória com baixíssimo impacto de performance.
*   **Impacto no Projeto:** Componentes completamente diferentes conseguem compartilhar informações.
*   **Exemplo Prático:** O `useAuthStore` guarda quem está logado. Quando um usuário faz login na página de autenticação, tanto a barra de navegação superior (`Header`, que mostra a foto) quanto a página interna do jogo (`GamePage`, que mostra o saldo) são atualizadas em tempo real, lendo exatamente da mesma variável global no Zustand.

### 🌐 Axios (Mensageiro HTTP)
*   **A Característica:** Uma biblioteca de requisições web com suporte a **Interceptadores** (Middlewares).
*   **Impacto no Projeto:** Evita repetição de código em toda a aplicação.
*   **Exemplo Prático:** Em vez de você programar em cada página "pegue o token do localStorage e adicione no cabeçalho", o arquivo `api.ts` usa um interceptador: toda requisição HTTP, antes de sair do navegador, passa por um pedágio invisível que insere o crachá de identificação `Authorization: Bearer <token>`.

### 🚀 FastAPI (Probability Engine / Motor de Sorte)
*   **A Característica:** Um microserviço assíncrono em Python focado exclusivamente em operações de alta velocidade e matemática pesada.
*   **Impacto no Projeto:** Isola o processamento lógico da roleta do servidor principal.
*   **Exemplo Prático:** O Django envia o nível do jogador para a porta `:8001` (FastAPI). O FastAPI realiza cálculos de Teoria de Probabilidades (RTP dinâmico) para montar o visual da roleta sem tocar em banco de dados, e retorna os símbolos instantaneamente. Isso impede que picos de usuários girando a roleta ao mesmo tempo travem as funções de saque/depósito do Django.

### ⚡ Django Channels + Redis (Notificações Instantâneas)
*   **A Característica:** O protocolo HTTP clássico só funciona quando o usuário pergunta algo. O WebSockets (gerenciado pelo Channels) permite que o servidor mande informações sem ninguém perguntar. O Redis atua como o "correio" interno.
*   **Impacto no Projeto:** Fator FOMO (Fear Of Missing Out). O cassino parece "vivo".
*   **Exemplo Prático:** Quando alguém ganha um prêmio alto, a view do Django publica uma mensagem no canal "casino_live" no Redis. O Channels, que está escutando esse canal, dispara um pacote de dados para o `useCasinoStore` no React. Imediatamente, uma janela pop-up de "Fulano ganhou R$500 na roleta!" aparece na barra lateral de todos os usuários conectados no mundo inteiro simultaneamente.
