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


connection_string = "mongodb+srv://samsonm825:g4zo1j6y94@cluster0.ow4o5g4.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
dbs = client.BT


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
    orderNo_data = []
    page_data = {}
    order_data = []
    match = {}
    order_find = dbs.jeg_order.find(
      {
        "uid":ObjectId(session["id"])
      }
    )
    # if request.method == 'POST':
    #         #條件判斷
    #   oId = request.form['no']
    #   name = request.form['name']
    #   if oId != '':
    #     match['orderNo'] = oId
    #   elif name != '':
    #     match['name'] = name
    #   if request.args.get('methods') == 'setorderno':
    #         oid = request.args.get('oid')
    #         orderNo = request.args.get('orderno')
    #         order_data = dbs.jeg_order.find_one(
    #             {
    #               "_id":ObjectId(oid)
    #             }
    #         )
    #         dbs.jeg_order.update_one(
    #             {
    #                 "_id":ObjectId(oid)
    #             },
    #             {
    #                 "$set":{
    #                     "order_detail": ObjectId(orderNo)
    #                 }
    #             }
    #         )
    #         dbs.order_no.update_one(
    #             {
    #                 "_id":ObjectId(orderNo)
    #             },
    #             {
    #                 "$set":{
    #                     "is_used":True
    #                 },
    #                 "$push":{
    #                     "used_oid":order_data['bankAccount']
    #                 }
    #             }
    #         )
    #         return redirect('profile')
        
    #   current_page = request.args.get('page')
    #   skip = 0
    #   per = 20
    #   if current_page != None:
    #     skip = per * (int(current_page) - 1)
    #   else:
    #     current_page = 1
    #     #判断条件时要加入筛选条件
    #   order_len = dbs.jeg_order.count_documents(match)
    #   if order_len % per == 0:
    #     all_page = order_len // per
    #   else:
    #     all_page = (order_len // per) + 1
    #   page_data['all_page'] = all_page
    #   page_data['current_page'] = current_page
    #     #分页处理结束

    #   if 'name' in match or 'orderNo' in match:
    #     skip = 0
    #     per = 10000
    #     page_data = {}

    #   orderNo_find = dbs.order_no.find()
    #   for doc in orderNo_find:
    #       doc['_id'] = str(doc['_id'])
    #       if 'is_used' not in doc:
    #           orderNo_data.append(doc)
    #   temp_data = dbs.jeg_order.find(match).limit(per).skip(skip)
    #   for doc in temp_data:
    #       doc['_id'] = str(doc['_id'])
    #       doc['_uid'] = str(doc['uid'])
    #       if 'order_detail' not in doc:
    #         doc['order_detail'] = False
    #       order_data.append(doc)
    #   return render_template('profile.html', orderNo_data=orderNo_data, order_data=order_data, page_data=page_data )
    # else:
    #   return redirect('/')









    for doc in order_find:
      print(doc)
      order_data.append(doc)
    return render_template('profile.html', order_data=order_data)
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
    order_find = dbs.jeg_order.find(
      {
        "uid":ObjectId(session["id"]),
        "type": "出貨"
      }
    )
    for doc in order_find:
      print(doc)
      order_data.append(doc)
    return render_template('sellorder.html', order_data=order_data)
  else :
    return redirect('/')
  
@app.route('/buyorder',methods=['GET', 'POST'])
def buyorder():
  if 'id' in session:
    order_data = []
    order_find = dbs.jeg_order.find(
      {
        "uid":ObjectId(session["id"]),
        "type": "進貨"
      }
    )
    for doc in order_find:
      print(doc)
      order_data.append(doc)
    return render_template('buyorder.html', order_data=order_data)
  else :
    return redirect('/')
  

if __name__ == "__main__":
 app.run(debug=True, use_reloader=False, port = 5501)