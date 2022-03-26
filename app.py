from flask import Flask,redirect, url_for, render_template, request,jsonify,session
import pymongo,uuid,bcrypt,datetime,json,redis
from bson.json_util import dumps
from celery_task import make_celery

uri = "mongodb+srv://sfkrkmz:asd.123@cluster0.zmqua.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = pymongo.MongoClient(uri)
mydb = client["school_libs"]
mycolUsers = mydb["users.dbo"]
mycolBooks = mydb["books.dbo"]
mycolToLend = mydb["tolendBook.dbo"]




app = Flask(__name__)
app.secret_key = "testing"
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='mongodb+srv://sfkrkmz:asd.123@cluster0.zmqua.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
)
celery = make_celery(app)


#celery task kitabı ödünç al
@celery.task(name="app.insertLend")
def insertLend(data):
    print(data)
    mycolToLend.insert_one(data)
    myquery = { "bookId": data['bookId']}
    newvalues = { "$set": { "inLib": False,"endDate": data['envDate'],"lastUserId":data["userId"] } }
    mycolBooks.update_many(myquery, newvalues)
    return 200

#celery task kitabı geri bırak
@celery.task(name="app.updateDeliver")
def updateDeliver(bookId):

    bookstbl = { "$set": { "inLib": True ,"endDate": datetime.datetime.now()}}
    lendbooktbl = { "$set": { "isGet": True,"endDate": datetime.datetime.now()}}
    mycolBooks.update_many({ "bookId": bookId}, bookstbl)
    mycolToLend.update_many({ "bookId": bookId,"isGet":False}, lendbooktbl)
    return 200

@app.route('/')
def index():
    return render_template('login.html')

#giriş yap
@app.route('/login', methods=['POST','GET'])
def login():
    try:
        if "username" in session:
            return "giriş yapılmış",200
    except:
        pass
    if request.method == 'POST':
        #gelen data json ise
        if request.headers["Content-Type"]=="application/json":
            content = request.get_json()
            username = content["username"]
            pwd = content["password"]
            #gelen data form data ise
        if request.headers["Content-Type"] == "application/x-www-form-urlencoded":
            username = request.form['username']
            pwd = request.form['pwd']
        #gelen kullanıcıyı db den sorgulama
        user = mycolUsers.find_one({"username": username})
        if username and user:
            password = user["password"]
            if bcrypt.checkpw(pwd.encode('utf-8'), password):
                session["username"] = username
                mycolUsers.update_many({ "username": username}, {"lastLogin":datetime.datetime.now()})
                return "giriş yapıldı",200
            else:
                return "şifreyi kontrol ediniz"
        else:
            return "Böyle bir kullanıcı bulunmamaktadır."
    else:
        return render_template('login.html')

#üye ol
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        #gelen data json ise
        if request.headers["Content-Type"] == "application/json":
            content = request.get_json()
            name = content["name"]
            username = content["username"]
            email = content["email"]
            hashed = bcrypt.hashpw(content["password"].encode('utf-8'), bcrypt.gensalt())
            addr = content["addr"]
            phoneNumber = content["phone_number"]
            tcId = content["tc_id"]
        #gelen data form verisi ise
        elif request.headers["Content-Type"] == "application/x-www-form-urlencoded":
            name = request.form["name"]
            username = request.form["username"]
            email = request.form["email"]
            hashed = bcrypt.hashpw(request.form['pwd'].encode('utf-8'), bcrypt.gensalt())
            addr = request.form["addr"]
            phoneNumber = request.form["phone_number"]
            tcId = request.form["tc_id"]

        user_found = mycolUsers.find_one({"username": username})
        email_found = mycolUsers.find_one({"email": email})
        if user_found:
            return 'Daha önce bu kullanıcı adı ile kayıt yapılmıştır.'
        if email_found:
            return 'Daha önce bu email ile kayıt yapılmıştır.'
        else:
            user = {
                "id" : uuid.uuid4().hex,
                "name": name,
                "username": username,
                "password" : hashed,
                "email" : email,
                "phoneNumber":phone_number,
                "address" : addr,
                "tcId" : tcId,
                "createDate":datetime.datetime.now(),
                "lastLogin":datetime.datetime.now()
            }
            mycolUsers.insert_one(user)
            return "Success",200
    else:
        return render_template('register.html')

#kitap ekle
@app.route('/addbook',methods=["POST","GET"])
def addBook():
    if request.method == 'POST':
        if request.headers["Content-Type"]=="application/json":
            content = request.get_json()
            book_name = content["book_name"]
            author_name = content["author_name"]
            nots = content["not"]
            page_count = content["page_count"]
            kitapId = count["book_id"]

        if request.headers["Content-Type"] == "application/x-www-form-urlencoded":
            book_name = request.form["book_name"]
            author_name = request.form["author_name"]
            nots = request.form["not"]
            page_count = request.form["page_count"]
            bookId = request.form["book_id"]
        book = {
            "bookId":bookId,
            "inLib":True,
            "bookName":book_name,
            "authorName":author_name,
            "not":nots,
            "pageCount":page_count,
            "createDate":datetime.datetime.now(),
            "endDate":datetime.datetime.now()
        }
        #gelen kitapid db den sorgulama
        isSaved = mycolBooks.find_one({"bookId": bookId})
        if isSaved:
            return "Aynı kitap id ile başka kitap eklenemez"
        else:
            mycolBooks.insert_one(book)
            return "Success saved", 200
    else:
        return render_template('addbook.html')

#kitap kütüphanede mi
@app.route('/inlib', methods=["POST"])
def inLib():
    if request.method == "POST":
        if request.headers["Content-Type"]=="application/json":
            content = request.get_json()
            query = content["query"]
        if request.headers["Content-Type"] == "application/x-www-form-urlencoded":
            query = request.form["query"]

        myquery = { "bookName": { "$regex": query } }
        mydoc = mycolBooks.find(myquery)
        print(mydoc)
        return render_template('getbook.html', content=mydoc)

#kitabı geri al
@app.route('/searchbook',methods=["POST","GET"])
def searchbook():
    if request.method == "POST":
        return 200
    return render_template('searchbook.html')

#kitabı ödünç ver
@app.route('/tolend', methods=["POST","GET"])
def toLend():
    if request.method == "POST":
        #gelen data json ise
        if request.headers["Content-Type"] == "application/json":
            content = request.get_json()
            bookId = content["book_id"]
        elif request.headers["Content-Type"] == "application/x-www-form-urlencoded":
            if "username" in session:
                try:
                    if request.form['book_id']:
                        bookId = request.form['book_id']
                        book = mycolBooks.find_one({"bookId": bookId})
                        content = {
                            "bookName":book['bookName'],
                            "bookId":book['bookId'],
                            "session":session['username']
                        }
                        return render_template('tolend.html',content=content)
                except:
                    if request.form['bookId']:
                        bookId = request.form['bookId']
                        book = mycolBooks.find_one({"bookId": bookId})
                        user = mycolUsers.find_one({"username":session["username"]})
                        delivery_date = datetime.datetime.fromisoformat(request.form['delivery_date'])
                        data = {
                            "userId":user['id'],
                            "bookId":book['bookId'],
                            "createDate":datetime.datetime.now(),
                            "endDate" : (datetime.datetime.now()+datetime.timedelta(days=10)),
                            "envDate" : delivery_date,
                            "isGet":False
                        }
                        #celery Task e gönder
                        result = insertLend.delay(data)
                        #result.wait()
                        return "Success",200
            else:
                return "Lütfen Giriş yap"

@app.route('/mybooks', methods=["POST","GET"])
def deliverBook():
    if request.method == "GET":
        username = session["username"]
        user = mycolUsers.find_one({"username":username})
        mybooks = mycolToLend.find({"userId":user["id"],"isGet":False})
        books = mycolBooks.find({"lastUserId":user["id"],"inLib":False})
        return render_template("deliverbook.html",user=user,mybooks=mybooks,books=books)
    if request.method == "POST":
        result = updateDeliver.delay(request.form['book_id'])
        #result.wait()
        return "Kitap Bırakılmıştır",200

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5001, debug=True)
