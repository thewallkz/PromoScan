from flask import Flask, render_template, request
from bot_engine import buscar_produtos

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    produto = request.form.get('produto')
    preco_str = request.form.get('preco')
    loja = request.form.get('loja')
    
    # Checkbox HTML: Se marcado retorna 'on', se desmarcado retorna None
    # Queremos True se estiver marcado
    somente_novos = request.form.get('novos') is not None
    
    try:
        preco = float(preco_str)
    except:
        preco = 0.0
        
    # Passamos o novo parâmetro 'somente_novos'
    lista_final = buscar_produtos(produto, preco, loja, somente_novos)
    
    # Ordenação
    lista_final.sort(key=lambda x: x['val_sort'])

    return render_template('resultados.html', 
                           produtos=lista_final, 
                           termo=produto)

if __name__ == '__main__':
    app.run(debug=True)