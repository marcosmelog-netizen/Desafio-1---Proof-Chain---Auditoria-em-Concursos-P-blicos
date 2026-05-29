# ProofChain — Auditoria e Rastreabilidade de Concursos Públicos 🔗

O **ProofChain** é uma solução de software completa (End-to-End) voltada a assegurar a integridade, a transparência e a imutabilidade cronológica das etapas de Concursos Públicos. Através da fusão de criptografia simétrica local e contratos inteligentes em redes Blockchain (Ethereum Sepolia Testnet), o ecossistema mitiga de forma definitiva fraudes comuns em certames, tais como a adulteração retroativa de gabaritos, a substituição fraudulenta de folhas de resposta pós-prova e a quebra de isonomia institucional.

---

## 1. O Problema Real Enfrentado 🚨

Concursos públicos movimentam interesses de milhares de candidatos e demandam uma cadeia de custódia impecável. Historicamente, os principais pontos de vulnerabilidade e fraudes internas concentram-se em:
* 🔴 **Alteração Retroativa de Atas:** Modificação de documentos internos para favorecimento ou inclusão de candidatos após prazos preestabelecidos.
* 🔴 **Substituição de Cartões-Resposta:** Troca física de cartões-resposta digitalizados ou substituição das strings de dados no banco de dados centralizado da banca examinadora antes da publicação oficial.
* 🔴 **Incerteza Cronológica (Timestamping):** Falta de uma evidência pública matemática e incontestável de *quando* determinada folha de resposta ou edital foi oficialmente congelado e homologado.

Sistemas centralizados tradicionais baseados exclusivamente em bancos de dados relacionais (como PostgreSQL ou MySQL) são vulneráveis a ataques internos. Qualquer usuário com privilégios de administrador (*root*) ou credenciais obtidas via engenharia reversa pode alterar registros históricos diretamente na tabela, sem deixar rastros auditáveis publicamente.

---

## 2. Por que a Blockchain é Adequada para este Problema? 🧠

A tecnologia Blockchain atua como um **Livro-Razão Distribuído e Imutável**. No contexto do ProofChain, ela substitui a "confiança cega" na instituição organizadora por "verificação matemática" e descentralizada. 

A arquitetura justifica-se pelos seguintes pilares:
1. 🟢 **Imutabilidade Temporal:** Uma vez minerada e inserida em um bloco da rede pública Ethereum, nenhuma entidade (nem mesmo os diretores da banca examinadora) possui o poder computacional de apagar ou alterar retroativamente as informações registradas.
2. 🟢 **Carimbo de Tempo Nativo (*On-Chain Timestamping*):** O horário de registro de cada etapa é gerado pela própria rede através da propriedade `block.timestamp` do Solidity, impedindo a retroatividade ou o adiantamento fraudulento de horários.
3. 🟢 **Auditoria Pública e Independente:** Qualquer cidadão, órgão de controle (como o Ministério Público e Tribunais de Contas) ou o próprio candidato pode auditar de forma autônoma a validade da cadeia através de nós públicos, sem requerer autorizações formais da banca.

---

## 3. Arquitetura da Solução e Fluxo de Dados 🏗️

Para garantir alta performance, economia com taxas de rede (*gas fees*) e a privacidade de dados sensíveis, o ProofChain adota uma **Arquitetura Híbrida** segregando os dados de forma estratégica:

### 📁 Dados Off-Chain (Fora da Blockchain)
O conteúdo textual integral (os textos longos dos editais, o teor descritivo das atas de encerramento de sala, as respostas detalhadas dos gabaritos colhidos) permanece no ambiente operacional local ou em servidores da banca. Armazenar textos volumosos diretamente na rede blockchain tornaria as transações financeiramente inviáveis devido ao custo de armazenamento em estado global (*SSTORE*).

### ⛓️ Dados On-Chain (Dentro da Blockchain)
Apenas as seguintes propriedades de controle técnico e criptográfico são gravadas no Contrato Inteligente:
* **`idConcurso` (string):** Identificador exclusivo do certame público indexado no mapeamento.
* **`hashConteudo` (bytes32):** A impressão digital criptográfica gerada localmente via algoritmo SHA-256 a partir do texto integral.
* **`timestamp` (uint256):** O horário exato da mineração em Unix Timestamp fornecido pelo validador do bloco.
* **`descricao` (string):** Metadado descritivo de rótulo para identificação ágil da etapa (ex: "Edital de Abertura v1.0").

## 4. Tecnologias, Ferramentas e Ambientes Utilizados 🛠️

Para viabilizar a interoperabilidade, a execução distribuída e a transparência do ecossistema, o ProofChain integra as seguintes tecnologias:

### 💻 Ambientes de Desenvolvimento e Editores
* **Visual Studio Code (VS Code):** Editor de código integrado utilizado para o desenvolvimento do ecossistema local, estruturação das rotas da API em Python (Flask) e scripts de interface.
* **Remix IDE:** Ambiente de desenvolvimento integrado web utilizado para a escrita, compilação, testes unitários primários e deploy dos contratos inteligentes em Solidity.

### 🌐 Infraestrutura Blockchain e Web3
* **Sepolia Testnet:** Rede de testes pública baseada em Proof-of-Stake (PoS) da Ethereum, utilizada como infraestrutura descentralizada para a simulação real, mineração de blocos e validação imutável das etapas dos concursos.
* **MetaMask:** Carteira digital baseada em extensão de navegador utilizada como interface de custódia de chaves privadas e assinatura criptográfica das transações enviadas via Frontend.
* **Etherscan (Sepolia):** Explorador de blocks oficial utilizado para auditoria pública, rastreamento de hashes de transação (`transactionHash`), verificação de contratos e monitoramento dos logs de eventos emitidos pela EVM.

### 🤖 Declaração de Uso de Inteligência Artificial Generativa
Em estrita conformidade com as diretrizes de transparência e uso adequado de ferramentas tecnológicas do evento:
* **Gemini (Google):** Modelo de inteligência artificial generativa de linguagem utilizado ativamente durante o certame como assistente de codificação para o refinamento da arquitetura da API REST, suporte na lógica de mitigação de duplicidade de dados no Smart Contract em Solidity e revisão de segurança contra vetores de ataque em sistemas distribuídos.

```text
  [Texto Integral Off-Chain] ──> (Algoritmo SHA-256) ──> [Hash bytes32]
                                                               │
  [Painel Web Frontend] ─── (API Flask via Web3.py) ───────────┼──> [Contrato Inteligente Sepolia]
                                                                      (Registra e concatena linearmente)

