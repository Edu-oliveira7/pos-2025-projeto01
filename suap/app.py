from flask import Flask, redirect, request, session, url_for, render_template
import requests


app = Flask(__name__)
app.secret_key = 'chave-super-secreta'

def get_user_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(f'{SUAP_BASE_URL}/api/v2/minhas-informacoes/meus-dados/', headers=headers)
    return resp.json()

def get_boletim(token, ano):
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(f'{SUAP_BASE_URL}/api/v2/minhas-informacoes/boletim/{ano}/', headers=headers)
    return resp.json()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return redirect(
        f"{SUAP_BASE_URL}/o/authorize/?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    )

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    response = requests.post(f'{SUAP_BASE_URL}/o/token/', data=data)
    token_json = response.json()
    access_token = token_json.get('access_token')

    session['token'] = access_token
    session['user'] = get_user_data(access_token)
    return redirect(url_for('perfil'))

@app.route('/perfil')
def perfil():
    if 'token' not in session:
        return redirect(url_for('home'))
    return render_template('perfil.html', user=session['user'])

@app.route('/boletim', methods=['GET', 'POST'])
def boletim():
    if 'token' not in session:
        return redirect(url_for('home'))

    ano = request.args.get('ano', '2024')  # ano padrão
    dados_boletim = get_boletim(session['token'], ano)
    return render_template('boletim.html', boletim=dados_boletim, ano=ano, user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)