// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProofChainConcursos {
    
    // Definição de cada elo da cadeia (cada documento, edital ou escaneamento de folhas)
    struct Etapa {
        bytes32 hashConteudo;   // O hash SHA-256 do arquivo/texto calculado no Python
        uint256 timestamp;     // O momento exato do registro na blockchain (Unix Timestamp)
        string descricao;      // Ex: "Edital de Abertura", "Escaneamento de Folhas - Sala 12"
    }

    // Conta da Banca Examinadora (dona do contrato e única com poder de escrita)
    address public bancaExaminadora;

    // A CADEIA HISTÓRICA: Mapeia o ID do Concurso para uma lista (array) de Etapas.
    // Garante a rastreabilidade completa: novas etapas não apagam o passado.
    mapping(string => Etapa[]) private historicoConcursos;

    // Evento para monitoramento em tempo real e auditoria facilitada
    event EtapaRegistrada(string indexed idConcurso, bytes32 hashConteudo, string descricao);

    // Modificador de segurança que blinda o acesso de escrita
    modifier apenasBanca() {
        require(msg.sender == bancaExaminadora, "Acesso negado: Apenas a banca examinadora pode registrar.");
        _;
    }

    constructor() {
        // Quem faz o deploy do contrato se torna o administrador oficial (a Banca)
        bancaExaminadora = msg.sender;
    }

    // ==========================================================
    // 1. FUNÇÃO DE ESCRITA: Atende ao requisito de "REGISTRAR"
    // ==========================================================
    function registrarEtapa(
        string memory _idConcurso, 
        bytes32 _hashConteudo, 
        string memory _descricao
    ) public apenasBanca {
        require(_hashConteudo != bytes32(0), "O hash do conteudo nao pode ser nulo.");
        
        // Adiciona o novo elo na lista cronológica daquele concurso específico
        historicoConcursos[_idConcurso].push(
            Etapa(_hashConteudo, block.timestamp, _descricao)
        );

        emit EtapaRegistrada(_idConcurso, _hashConteudo, _descricao);
    }

    // ==========================================================
    // 2. FUNÇÃO DE LEITURA: Atende ao requisito "VERIFICÁVEL PUBLICAMENTE"
    // ==========================================================
    // Retorna a linha do tempo COMPLETA de um concurso de forma gratuita e aberta
    function obterCadeia(string memory _idConcurso) public view returns (Etapa[] memory) {
        return historicoConcursos[_idConcurso];
    }
}