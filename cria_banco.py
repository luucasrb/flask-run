# import sqlite3

# connection = sqlite3.connect('banco.db')
# cursor = connection.cursor()

# cria_tabela = "CREATE TABLE IF NOT EXISTS hoteis (hotel_id text PRIMARY KEY, nome text, estrelas float, diaria real, cidade text, UNIQUE (hotel_id))"

# criar_hotel = "INSERT INTO hoteis VALUES ('alfa', 'Alpha Hotel', 4.3, 345.30, 'Rio de Janeiro')"

# cursor.execute(cria_tabela)
# cursor.execute(criar_hotel)
# connection.commit()
# connection.close()