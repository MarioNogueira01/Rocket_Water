class JetskiCentralPointsCalculator:
    def __init__(self, object_creator):
        self.object_creator = object_creator

    def calcular_ponto_central_jetski(self):
        # Obter o objeto do jetski da instância do ObjectCreator
        jetski = self.object_creator.jetSki  # Corrigido para acessar através de object_creator

        # Obter as coordenadas atuais do jetski
        posicao_x, posicao_y, posicao_z = jetski.get_position()

        # Retornar as coordenadas como ponto central
        return posicao_x, posicao_y, posicao_z
