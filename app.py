import os
import json
import hashlib
from flask import Flask, request, jsonify, render_template
from web3 import Web3
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o Flask configurado para usar a pasta 'frontend' exigida pela banca
app = Flask(__name__, template_folder="frontend", static_folder="frontend")

# 2. Configurações de Conexão com a Blockchain Sepolia
RPC_URL = os.getenv("WEB3_PROVIDER_URL")
CONTRATO_ADDRESS = os.getenv("CONTRATO_ADDRESS")
PRIVATE_KEY = os.getenv("BANCA_PRIVATE_KEY")

# Inicializa o provedor Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Validação imediata de conexão com a rede
if not w3.is_connected():
    print("❌ ERRO CRÍTICO: Não foi possível conectar ao provedor RPC da Sepolia!")
else:
    print(f"🚀 Conectado com sucesso à Sepolia! Bloco atual: {w3.eth.block_number}")

# 3. Carrega a carteira da Banca Examinadora derivada da Chave Privada
try:
    if PRIVATE_KEY.startswith("0x"):
        banca_account = w3.eth.account.from_key(PRIVATE_KEY)
    else:
        banca_account = w3.eth.account.from_key("0x" + PRIVATE_KEY)
    print(f"🔑 Carteira da Banca carregada: {banca_account.address}")
except Exception as e:
    print(f"❌ ERRO CRÍTICO ao carregar a chave privada: {e}")

# 4. Carrega a ABI e inicializa o Contrato Inteligente
with open("abi.json", "r", encoding="utf-8") as f:
    contrato_abi = json.load(f)

# Garante que o endereço do contrato está no formato correto (Checksum)
contrato_checksum = w3.to_checksum_address(CONTRATO_ADDRESS)
contrato = w3.eth.contract(address=contrato_checksum, abi=contrato_abi)


# ==========================================================
# ROUTE 1: GET / (Renderiza o Painel Frontend Interativo)
# ==========================================================
@app.route("/")
def index():
    return render_template("index.html")


# ==========================================================
# ROUTE 2: POST /registrar (Garante a IMUTABILIDADE e SEGURANÇA)
# ==========================================================
@app.route("/registrar", methods=["POST"])
def registrar():
    try:
        dados = request.get_json()
        id_concurso = dados.get("idConcurso")
        conteudo_texto = dados.get("conteudoTexto")
        descricao = dados.get("descricao")

        if not id_concurso or not conteudo_texto or not descricao:
            return jsonify({"status": "Erro", "mensagem": "Campos obrigatórios faltando!"}), 400

        # GERADOR DE TRUST: Calcula o Hash SHA-256 localmente antes de enviar para a rede
        hash_calculado = hashlib.sha256(conteudo_texto.encode("utf-8")).hexdigest()
        # Converte para bytes32 exigido pelo contrato em Solidity
        hash_bytes32 = w3.to_bytes(hexstr=f"0x{hash_calculado}")

        print(f"📦 Registrando elo para o concurso {id_concurso}...")
        print(f"🔒 Descrição: {descricao} | SHA-256: 0x{hash_calculado}")

        # Constrói a transação de escrita chamando a função exata do Solidity: registrarEtapa
        nonce = w3.eth.get_transaction_count(banca_account.address)
        
        tx = contrato.functions.registrarEtapa(
            id_concurso,
            hash_bytes32,
            descricao
        ).build_transaction({
            "chainId": 11155111,  # ID nativo da rede Sepolia
            "gas": 200000,        # Limite estimado seguro de gás
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce,
        })

        # Assina a transação localmente com a chave privada criptografada
        tx_assinada = w3.eth.account.sign_transaction(tx, private_key=banca_account.key)
        
        # Envia para a rede pública Sepolia
        tx_hash = w3.eth.send_raw_transaction(tx_assinada.raw_transaction)
        
        # Aguarda a confirmação de mineração do bloco de forma síncrona
        print("⏳ Aguardando mineração da transação na Sepolia...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "Sucesso",
            "mensagem": "Informação eternizada na Sepolia com sucesso!",
            "idConcurso": id_concurso,
            "descricao": descricao,
            "hashConteudo": f"0x{hash_calculado}",
            "transactionHash": tx_receipt["transactionHash"].hex()
        }), 200

    except Exception as e:
        return jsonify({
            "status": "Erro",
            "mensagem": "Falha operacional na gravação da Blockchain",
            "detalhes": str(e)
        }), 500


# ==========================================================
# ROUTE 3: GET /consultar/<idConcurso> (Garante a VERIFICAÇÃO PÚBLICA)
# ==========================================================
@app.route("/consultar/<id_concurso>", methods=["GET"])
def consultar(id_concurso):
    try:
        print(f"🔍 Buscando a cadeia de informações para o ID: {id_concurso}...")
        
        # Chamada GRATUITA de leitura (.call()) invocando a função: obterCadeia
        cadeia_blockchain = contrato.functions.obterCadeia(id_concurso).call()

        if not cadeia_blockchain:
            return jsonify({
                "status": "Sucesso",
                "mensagem": "Nenhum histórico encontrado para este ID de concurso.",
                "cadeia": []
            }), 200

        # Formata o Array de structs recebido do Solidity em um JSON limpo
        historico_formatado = []
        for index, elo in enumerate(cadeia_blockchain):
            historico_formatado.append({
                "elo_posicao": index + 1,
                "hashConteudo": f"0x{elo[0].hex()}",
                "timestamp_unix": elo[1],
                "descricao": elo[2]
            })

        return jsonify({
            "status": "Sucesso",
            "idConcurso": id_concurso,
            "total_elos": len(historico_formatado),
            "cadeia": historico_formatado
        }), 200

    except Exception as e:
        return jsonify({
            "status": "Erro",
            "mensagem": "Falha ao consultar a cadeia de informações publica",
            "detalhes": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)