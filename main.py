from fastapi import FastAPI, HTTPException, Query  # >> Biblioteca para criar a API e tratar exceções e parâmetros da URL
from pydantic import BaseModel  # >> Essa ajuda a gente a definir o formato dos dados que a API vai receber ou enviar.
from typing import List  # >> Biblioteca usada para definir listas nos atributos (ex: lista de produtos)
from pymongo import MongoClient  # >> Biblioteca para conectar e interagir com o MongoDB

app = FastAPI()

# ======= Conexão com o MongoDBClient Atlas =======
# >> MongoClient: conecta ao banco de dados MongoDB Atlas (substitua com sua string de conexão do Atlas)
client = MongoClient(
    "mongodb+srv://admin:Jeancarlo92@cluster0.jgwd9pk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)



# >> Define o banco e a coleção que serão usados
db = client["Database_Teste"]
colecao = db["AulaMartin"]




# ======= Modelo de dados com Pydantic =======
# >> Classe que define a estrutura do documento que será recebido/enviado
class Documento(BaseModel):
    Nome: str
    Rua: str
    Produtos_Comprados: List[str]  # >> Lista com os nomes dos produtos comprados

# >> Função para transformar o _id do MongoDB em string para poder exibir no JSON
def converter_documento(doc):
    doc["_id"] = str(doc["_id"])
    return doc



# ======= 0º Endpoint: /Rota Raiz=======

@app.get("/")
def raiz():
    return {"message": "API funcionando!"}

# ======= 1º Endpoint: /cadastrar =======
@app.post("/cadastrar")
def cadastrar_documento(doc: Documento):
    # doc.dict() -> o que é? 
    # >> É uma função da biblioteca Pydantic (classe BaseModel) que transforma os dados recebidos em um dicionário comum do Python.
    
    # colecao.insert_one -> O que é?
    # >> Método da biblioteca PyMongo que insere um documento no banco de dados MongoDB
    resultado = colecao.insert_one(doc.dict())
    
    if resultado.inserted_id:
        return {
            "status": "Documento cadastrado com sucesso",
            "id": str(resultado.inserted_id)  # >> Retorna o ID gerado automaticamente pelo MongoDB
        }
    else:
        raise HTTPException(status_code=500, detail="Erro ao cadastrar documento")

# ======= 2º Endpoint: /pesquisar_nome =======
@app.get("/pesquisar_nome")
def pesquisar_por_nome(nome: str = Query(..., description="Nome do cliente a ser pesquisado")):
    # >> Pesquisa documentos onde o campo "Nome" contém o texto passado (sem considerar maiúsculas/minúsculas)
    documentos = colecao.find({"Nome": {"$regex": nome, "$options": "i"}})
    return [converter_documento(doc) for doc in documentos]  # >> Converte cada documento para JSON legível

# ======= 3º Endpoint: /pesquisar_rua =======
@app.get("/pesquisar_rua")
def pesquisar_por_rua(rua: str = Query(..., description="Nome da rua a ser pesquisada")):
    # >> Pesquisa documentos pelo campo "Rua"
    documentos = colecao.find({"Rua": {"$regex": rua, "$options": "i"}})
    return [converter_documento(doc) for doc in documentos]

# ======= 4º Endpoint: /pesquisar_compras =======
@app.get("/pesquisar_compras")
def pesquisar_por_produto(produto: str = Query(..., description="Nome do produto comprado")):
    # >> Pesquisa documentos que contenham o nome do produto na lista de "Produtos_Comprados"
    documentos = colecao.find({"Produtos_Comprados": {"$regex": produto, "$options": "i"}})
    return [converter_documento(doc) for doc in documentos]
