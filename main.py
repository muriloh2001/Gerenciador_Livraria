import os
from pathlib import Path
import sqlite3
import shutil
from datetime import datetime
import csv

base_dir = Path(__file__).resolve().parent
data_dir = base_dir / "data"
backup_dir = base_dir / "backups"
export_dir = base_dir / "exports"

def criar_diretorios():
    for directory in [data_dir, backup_dir, export_dir]:
        directory.mkdir(parents=True, exist_ok=True)

def conectar_banco():
    return sqlite3.connect(data_dir / "livraria.db")

def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS livros (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT NOT NULL,
                        autor TEXT NOT NULL,
                        ano_publicacao INTEGER NOT NULL,
                        preco REAL NOT NULL
                      )''')
    conn.commit()
    conn.close()

def inicializar_sistema():
    criar_diretorios()
    criar_tabelas()

if __name__ == "__main__":
    inicializar_sistema()


def adicionar_livro(titulo, autor, ano_publicacao, preco):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO livros (titulo, autor, ano_publicacao, preco)
                      VALUES (?, ?, ?, ?)''', (titulo, autor, ano_publicacao, preco))
    conn.commit()
    conn.close()
    fazer_backup()
    print(f"Livro '{titulo}' adicionado com sucesso!")

def exibir_livros():
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livros")
        livros = cursor.fetchall()
        conn.close()
        if livros:
            for livro in livros:
                print(livro)
        else:
            print("Nenhum livro cadastrado.")


def atualizar_preco_livro(id_livro, novo_preco):
    conn = sqlite3.connect('data/livraria.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE livros SET preco = ? WHERE id = ?", (novo_preco, id_livro))

    conn.commit()

    conn.close()

    print(f"Preço do livro com ID {id_livro} atualizado para {novo_preco}")


def remover_livro(livro_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()
    fazer_backup()
    print(f"Livro ID {livro_id} removido com sucesso!")


def buscar_livros_por_autor(autor):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros WHERE autor = ?", (autor,))
    livros = cursor.fetchall()
    conn.close()
    if livros:
        for livro in livros:
            print(livro)
    else:
        print(f"Nenhum livro encontrado para o autor {autor}.")


def fazer_backup():
    backup_name = f"backup_livraria_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
    shutil.copy(data_dir / "livraria.db", backup_dir / backup_name)
    limpar_backups_antigos()

def limpar_backups_antigos():
    backups = sorted(backup_dir.glob("*.db"), key=os.path.getmtime)
    if len(backups) > 5:
        for backup in backups[:-5]:
            backup.unlink()

def exportar_para_csv():
    livros = exibir_livros()
    if livros:
        with open(export_dir / "livros_exportados.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Título", "Autor", "Ano de Publicação", "Preço"])
            writer.writerows(livros)
        print("Dados exportados para CSV com sucesso.")

def importar_de_csv(arquivo_csv):
    with open(arquivo_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            adicionar_livro(row['Título'], row['Autor'], int(row['Ano de Publicação']), float(row['Preço']))
    print("Dados importados do CSV com sucesso.")

def menu():
    while True:
        print("""
        1. Adicionar novo livro
        2. Exibir todos os livros
        3. Atualizar preço de um livro
        4. Remover um livro
        5. Buscar livros por autor
        6. Exportar dados para CSV
        7. Importar dados de CSV
        8. Fazer backup do banco de dados
        9. Sair
        """)
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano_publicacao = int(input("Ano de Publicação: "))
            preco = float(input("Preço: "))
            adicionar_livro(titulo, autor, ano_publicacao, preco)
        elif escolha == '2':
            exibir_livros()
        elif escolha == '3':
            livro_id = int(input("ID do livro: "))
            novo_preco = float(input("Novo preço: "))
            atualizar_preco_livro(livro_id, novo_preco)
        elif escolha == '4':
            livro_id = int(input("ID do livro: "))
            remover_livro(livro_id)
        elif escolha == '5':
            autor = input("Autor: ")
            buscar_livros_por_autor(autor)
        elif escolha == '6':
            exportar_para_csv()
        elif escolha == '7':
            arquivo_csv = input("Caminho do arquivo CSV: ")
            importar_de_csv(arquivo_csv)
        elif escolha == '8':
            fazer_backup()
        elif escolha == '9':
            print("Saindo do sistema.")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()

