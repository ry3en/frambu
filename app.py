from flask import Flask, redirect, render_template, request, flash, url_for,Response
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AIzaSyDt7bNzrTYRLUghNhKoiJPIRdQXhZ5f5yE'
# Configuraciones para firebase
cred = credentials.Certificate('serviceAccountKey.json')
fire = firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection('users')
orders_ref = db.collection('orders')
API_KEY = 'AIzaSyDt7bNzrTYRLUghNhKoiJPIRdQXhZ5f5yE'
user_auth = False


def login_firebase(email, password):
    credentials = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(
        'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(API_KEY),
        data=credentials)
    if response.status_code == 200:
        content = response.content
        data = response.json()
        print(data['localId'])
    elif response.status_code == 400:
        print(response.content)

    return response.content


def read_orders(ref):
    docs = ref.get()
    all_orders = []
    for doc in docs:
        order = doc.to_dict()
        order['id'] = doc.id
        all_orders.append(order)
    return all_orders


def create_order(ref, order, can):
    new_order = {'cliente': order,
                 'check': False,
                 'fecha': datetime.datetime.now(),
                 'cantidad': can}
    ref.document().set(new_order)


def update_check(ref, id):
    ref.document(id).update({'check': True})


def update_orden_cantidad(ref, id, cantidad):
    ref.document(id).update({"cantidad": cantidad})


def delete_order(ref, id):
    ref = ref.document(id).delete()

def client(ref):
    docs = ref.get()
    clientes = []
    for doc in docs:
        cliente = doc.to_dict()
        clientes.append(cliente["cliente"])
    return clientes

def repetidos(k):
    return list(dict.fromkeys(k))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        try:
            orders = read_orders(orders_ref)
            completed = []
            incompleted = []
            clientes = repetidos(client(orders_ref))
            for order in orders:
                print(order['check'])

                if order['check'] == True:
                    completed.append(order)
                else:
                    incompleted.append(order)
        except:
            print("Error...")
            orders = []
        response = {'completed': completed,
                    'incompleted': incompleted,
                    'clientes': clientes,
                    'counter1': len(completed),
                    'counter2': len(incompleted),
                    'counter3':len(clientes)}
        return render_template('index.html', response=response)
    else:  # POST
        name = request.form["name"]
        cantidad = request.form["cantidad"]
        print(f"\n{name}\n")
        try:
            create_order(orders_ref, name, cantidad)
            return redirect('/')
        except:
            return render_template('error.html', response='response')


@app.route("/update/<string:id>", methods=['GET'])
def update(id):
    print(f"\nVas a actualizar la tarea: {id}\n")
    try:
        update_check(orders_ref, id)
        return redirect('/')
    except:
        return render_template('error.html', response='response')

@app.route("/update-cant", methods=["POST"])
def update_orden_cantidad():
    id = request.form["id"]
    cantidad = request.form["cantidadModificada"]
    try:
        update_orden_cantidad(users_ref, id, int(cantidad))
        return Response(status=200)
    except:
        return Response(status=400)

@app.route("/delete/<string:id>", methods=['GET'])
def delete(id):
    print(f"\nVas a borrar la tarea: {id}\n")

    try:
        delete_order(orders_ref, id)
        print("Tarea eliminada...")
        return redirect('/')
    except:
        return render_template('error.html', response='response')


if __name__ == '__main__':
    app.run(debug=True)
