# PromoScan

### Busque produtos com valores do seu interesse nos 3 maiores e-commerces do país.

> **⚠️ Nota sobre o Estado Atual:**
> Opções de pesquisa: Mercado Livre, Amazon Brasil, Magazine Luiza e ambos juntos.
>
> **Atualmente estou tendo problemas em mascarar o IP da VM (Máquina Virtual) na nuvem.** Por conta disso, no ambiente de produção online, as pesquisas estão retornando resultados consistentemente apenas no **Mercado Livre**. Amazon e Magalu podem apresentar instabilidade devido a bloqueios de região/datacenter.

---

###  Sobre o Projeto

Projeto idealizado e inicializado **3 horas antes do início da Black Friday**.

Peço paciência principalmente com o tempo de execução das tarefas, pois o sistema realiza varreduras em tempo real. Tentarei adiantar o quanto antes uma otimização no sistema de busca (backend).

###  Melhorias Futuras

* **Criação de perfil opcional:** A funcionalidade de notificações (citada abaixo) será exclusiva para contas registradas e autenticadas.
* **Ticket de Interesse:** O usuário poderá criar um alerta de preço. Sempre que surgir uma promoção do produto escolhido com preço abaixo do estipulado, ele receberá uma notificação pelo WhatsApp.
* **Seção de Cupons:** Desenvolver ferramenta para verificar a situação e validade de cupons.
* **Cálculo Automático:** Caso o produto procurado seja compatível com cupons disponíveis, o sistema exibirá o preço já com a dedução do cupom aplicada.

---

###  Tecnologias Utilizadas

**Frontend**
* **HTML5 & CSS3:** Interface responsiva com variáveis CSS para suporte a Tema Escuro (Dark Mode).

**Backend**
* **Python 3.9+:** Linguagem core do sistema.
* **Flask:** Framework web para gerenciamento de rotas e requisições.
* **Selenium WebDriver:** Automação de navegador para extração de dados em sites dinâmicos (SPA).
* **BeautifulSoup4:** Parsing de HTML para extração de metadados.

**Infraestrutura & DevOps**
* **Docker:** Containerização da aplicação (Linux + Python + Chrome).
* **Google Chrome (Headless):** Navegador utilizado pelo robô no servidor.
* **Render:** Plataforma de hospedagem em nuvem.
