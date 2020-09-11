from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3

#path /hoteis?cidade=Rio-de-Janeiro&estrelas_min=4&diaria_max=400

def normalize_path_params(cidade = None, estrelas_min = 0, estrelas_max = 5, diaria_min = 0, diaria_max = 10000, limit = 5, offset = 0, **dados):
    if cidade:
        return {
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min,
            'diaria_max': diaria_max,
            'cidade': cidade,
            'limit': limit,
            'offset': offset
        }
    return {
        'estrelas_min': estrelas_min,
        'estrelas_max': estrelas_max,
        'diaria_min': diaria_min,
        'diaria_max': diaria_max,
        'limit': limit,
        'offset': offset
    }

path_params = reqparse.RequestParser()
path_params.add_argument ('cidade', type=str)
path_params.add_argument ('estrelas_min', type=float)
path_params.add_argument ('estrelas_max', type=float)
path_params.add_argument ('diaria_min', type=float)
path_params.add_argument ('diaria_max', type=float)
path_params.add_argument ('limit', type=int)
path_params.add_argument ('offset', type=int)

class Hoteis (Resource):
    def get(self):

        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()
        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            consulta = "SELECT * FROM hoteis \
                WHERE (estrelas >= ? and estrelas <= ? and diaria >= ? and diaria <= ?) LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)
        
        else:
            consulta = "SELECT * FROM hoteis \
                WHERE (estrelas >= ? and estrelas <= ? \
                and diaria >= ? and diaria <= ? and cidade=?) LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)
        
        hoteis = []
        for linha in resultado:
            hoteis.append({
                "hotel_id": linha[0],
                "nome": linha[1],
                "estrelas": linha[2],
                "cidade": linha[3],
                "diaria": linha[4]     
            })
        return {'hoteis': hoteis}
    


class Hotel (Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type= str, required=True, help = "name can't be assigned null")
    atributos.add_argument('estrelas', type=float, required=True)
    atributos.add_argument('diaria', type=float)
    atributos.add_argument('cidade', type=str)

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel is not None: 
            return hotel.json()
        return {'message': 'hotel not found'}, 404 #not found

    @jwt_required
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message'": "Hotel id '{}' already exists".format(hotel_id)}, 400 #bad request

        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {'message': 'internal error trying to save the hotel'},500
        return hotel.json(), 200 #success

    @jwt_required
    def put(self, hotel_id):
        dados = Hotel.atributos.parse_args()
        hotel_encontrado = HotelModel.find_hotel(hotel_id)

        if hotel_encontrado: 
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200 #atualiza

        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {'message': 'internal error trying to save the hotel'}, 500
        return hotel.json(), 200 #success

    @jwt_required
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)

        if hotel:
            try:
                hotel.delete_hotel()  
            except:
                return {'message', 'internal error trying to delete the hotel'}, 500
            return {'message': 'Hotel deleted.'}
        return {'message': 'Hotel not found'}, 404 
