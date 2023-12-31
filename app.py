from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from pymongo import MongoClient
from datetime import timedelta, timezone, datetime
import os
from bson.objectid import ObjectId
import requests
import hashlib

app = Flask(
  __name__,
  static_folder='public',
  static_url_path='/'
)

app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=60)
app.config['SECRET_KEY'] = os.urandom(24)

basedir = os.path.abspath(os.path.dirname(__file__))                 # 獲取當前檔案所在目錄
UPLOAD_FOLDER = basedir+'/public/images'                           # 計算圖片檔案存放目錄
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}     # 設定可上傳圖片字尾 

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
connection_string = "mongodb+srv://samsonm825:g4zo1j6y94@cluster0.ow4o5g4.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
dbs = client.BT

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_image', methods=['POST'])
def upload():
  if request.method == 'POST':
    f = request.files['img']
    name = session['id']
    try:
      if f and allowed_file(f.filename):
        file_path = app.config['UPLOAD_FOLDER'] + f'/{name}'
        if not os.path.exists(file_path):
          os.makedirs(file_path)
        f.save(os.path.join(file_path, f.filename.replace(' ', '').replace('(', '').replace(')', '')))
        return jsonify({
          "status": "success",
          "imgUrl": f"/images/{name}/{f.filename.replace(' ', '').replace('(', '').replace(')', '')}"
        })
      else:
        return jsonify({
          "status": "faild"
        })
    except:
      return jsonify({
        "status": "faild"
      })
@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    print('in post')
    member_data = []
    account = request.form['account']
    password = request.form['password']
    member_data = dbs.jeg_user.find_one({ "account": account })
    print(member_data)
    if member_data == None:
      print('no account')
      return redirect('/')
    
    # password_str = password + member_data["salt"]
    # user_password = hashlib.sha1(password_str.encode('utf-8'))


    # if member_data['password'] == user_password.hexdigest() and member_data['is_verify'] == 1:
    if member_data['password'] == password:
      session.permanent = True
      session["name"] = member_data['name']
      session["id"] = str(member_data["_id"])
      return redirect('home')
    else:
      return redirect('/')
  else:
    if 'id' in session:
      return redirect('home')
    return render_template('index.html')

@app.route('/home',methods=['GET', 'POST'])
def home():
 if 'id' in session:
   return render_template('home.html')
 else :
  return redirect('/')
 
@app.route('/logout',methods=['GET', 'POST'])
def logout():
 if 'id' in session:
   session.clear()
   return redirect('/')


 
@app.route('/checkout',methods=['GET', 'POST'])
def checkout():
 if 'id' in session:
   return render_template('checkout.html')

 

@app.route('/profile',methods=['GET', 'POST'])
def profile():
  if 'id' in session:
    order_data = []
    is_fake = "true"
    if request.method == 'POST':
      order_no = request.form['order_no']
      order_find = dbs.jeg_order.find_one(
        {
          "uid":ObjectId(session["id"]),
          "orderNo": order_no
        }
      )
      order_data.append(order_find)
      is_fake = "false"
    else:
      order_find = dbs.jeg_order.find(
        {
          "uid":ObjectId(session["id"])
        }
      )
      for doc in order_find:
        print(doc)
        order_data.append(doc)
    return render_template('profile.html', order_data=order_data, is_fake=is_fake)
  else :
    return redirect('/')
  


  
@app.route('/detail',methods=['GET', 'POST'])
def detail():
  if 'id' in session:
    oid = request.args.get('oid')
    order_detail = {}
    order_data = dbs.jeg_order.find_one(
      {
        "orderNo": oid
      }
    )
    if 'order_detail' in order_data:
      order_detail = dbs.order_no.find_one(
      {
        "_id": ObjectId(order_data["order_detail"])
      }
    )
    return render_template('detail.html', order_detail=order_detail, oid=oid, order_data=order_data)
  else :
    return redirect('/')
  
@app.route('/details')
def details():
  if 'id' in session:
    oid = request.args.get('oid')
    order_detail = {}
    order_data = {}
    return render_template('detail.html', order_detail=order_detail, oid=oid, order_data=order_data)
  else:
    return redirect('/')

 


@app.route('/search',methods=['GET', 'POST'])
def search():
  if 'id' in session:
    return render_template('search.html')
  else :
    return redirect('/')
  
@app.route('/cart',methods=['GET', 'POST'])
def cart():
  if 'id' in session:
    return render_template('cart.html')
  else :
    return redirect('index')
 

@app.route('/product_detail',methods=['GET', 'POST'])
def product_detail():
  if 'id' in session:
    return render_template('product_detail.html')
  else :
    return redirect('/')

@app.route('/favor',methods=['GET', 'POST'])
def favor():
  if 'id' in session:
    return render_template('favor.html')
  else :
    return redirect('index')
  
@app.route('/search_page',methods=['GET', 'POST'])
def search_page():
  if 'id' in session:
    string = request.args.get('string')
    return render_template('search_page.html', string=string)
  else :
    return redirect('index')
  
@app.route('/sellorder',methods=['GET', 'POST'])
def sellorder():
  if 'id' in session:
    order_data = []
    is_fake = 'false'
    if request.method == 'POST':
      order_no = request.form['order_no']
      order_find = dbs.jeg_order.find(
        {
          "uid":ObjectId(session["id"]),
          "orderNo": {'$regex':order_no},
          "type": "出貨"
        }
      )
      for doc in order_find:
        order_data.append(doc)
    else:
      status = request.args.get('status')



      
      order_find = dbs.jeg_order.find(
          {
            "uid":ObjectId(session["id"]),
            "type": "出貨"
          }
        )
      for doc in order_find:
        if status == None:
          order_data.append(doc)
        elif status == '0' and 'order_detail' not in doc:
          order_data.append(doc)
        elif status == '1' and 'order_detail' in doc:
          order_data.append(doc)
        elif status == '2':
          order_data = []
          is_fake = 'true'
    return render_template('sellorder.html', order_data=order_data, is_fake=is_fake)
  else :
    return redirect('/')
  
@app.route('/buyorder',methods=['GET', 'POST'])
def buyorder():
  if 'id' in session:
    order_data = []
    is_pay = request.args.get('pay')

    if request.method == 'POST':
      is_pay = "true"
      order_no = request.form['order_no']
      order_find = dbs.jeg_order.find(
        {
          "uid":ObjectId(session["id"]),
          "orderNo":{'$regex':order_no},
          "type":"進貨"

        }
      )
      for doc in order_find:
        order_data.append(doc)

    
    else:
      if is_pay == '0':
        print('in is_pay = 0')
        order_data = []
        is_pay = 'false'
      else: 
        order_find = dbs.jeg_order.find(
          {
            "uid":ObjectId(session["id"]),
            "type": "進貨"
          }
        )
        for doc in order_find:
          print(doc)
          order_data.append(doc)
    if is_pay != '0' and is_pay != 'false' and is_pay != None:
      is_pay = 'true'
    elif is_pay == None:
      is_pay = 'false'


    return render_template('buyorder.html', order_data=order_data, is_pay=is_pay)
  else :
    return redirect('/')
  

if __name__ == "__main__":
 app.run(debug=True, use_reloader=False, port = 5501)