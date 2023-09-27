import json

class LebryDB:
    def __init__(self, nome_arquivo):
        self.nome_arquivo = nome_arquivo
        self.data = self.carregar_dados()

    def carregar_dados(self):
        if not self.nome_arquivo:
            return {}
        try:
            with open(self.nome_arquivo, 'r') as arquivo:
                return json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def salvar_dados(self):
        if self.nome_arquivo:
            with open(self.nome_arquivo, 'w') as arquivo:
                json.dump(self.data, arquivo, indent=4)

    def inserir(self, chave, documento):
        if chave in self.data:
            raise KeyError("Chave já existe na base de dados")
        self.data[chave] = documento
        self.salvar_dados()

    def atualizar(self, chave, novos_dados):
        if chave in self.data:
            self.data[chave].update(novos_dados)
            self.salvar_dados()
        else:
            raise KeyError("Chave não encontrada na base de dados")

    def consultar(self, filtro):
        resultados = []
        for chave, documento in self.data.items():
            if all(documento.get(k) == v for k, v in filtro.items()):
                resultados.append((chave, documento))
        return resultados
