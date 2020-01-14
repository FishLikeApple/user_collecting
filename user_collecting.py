from environment import *

# database stuffs
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
   
    id = Column(Integer, primary_key=True)
    email_addr = Column(String(250), nullable=False)
    name = Column(String(60))
 
class Item(Base):
    __tablename__ = 'item'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    priority = Column(Integer)

    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User) 

def create_database():
    engine = create_engine('sqlite:///user.db', echo=True)
    Base.metadata.create_all(engine)

#create_database()

engine = create_engine('sqlite:///user.db?check_same_thread=False')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

def create_user(email_addr):
    user = User(email_addr=email_addr)
    session.add(user)
    session.commit()

def create_item(name, user, description=''):
    item = Item(name=name, description=description, user=user)
    session.add(item)
    session.commit()

def read_user(email_addr=None):

    if email_addr!=None:
        reads = session.query(User).filter_by(email_addr=email_addr).all()
        if len(reads)==0:
            return None
        else:
            return reads[0]

    return session.query(User).all()

def delete_user(email_addr):

    no_need = session.query(User).filter_by(email_addr=email_addr).one()
    session.delete(no_need)
    session.commit()

# flask stuffs
@app.route('/user_collecting', methods=["GET", "POST"])
def user_collecting():
    # a welcome page

    if request.method == "POST":
        if read_user(request.form['email_addr']) == None:
            create_user(request.form['email_addr'])
            flash("a new email address is just saved!")
        else:
            flash("welcome back!")
        return redirect(url_for("user_collecting_afterwards", email_addr=request.form['email_addr']))
    else:
        return render_template('user_collecting/user_collecting.html')

@app.route('/waiting_list', methods=["GET"])
def waiting_list():
    # return the waiting list
    
    return render_template('user_collecting/waiting_list.html', users=read_user()[::-1])

@app.route('/user_collecting/afterwards/<string:email_addr>', methods=["GET", "POST"])
def user_collecting_afterwards(email_addr):

    if request.method == "POST":
        user = read_user(email_addr)
        create_item('message', user, request.form['editor'])
        flash("your message is saved!")
 
    return render_template('user_collecting/afterwards.html', email_addr=email_addr)

@app.route('/user_collecting/form', methods=["POST"])
def get_form_respose():
    # wait for a completed form
    
    email_addr = request.get_json()['form_response']['answers'][-1]['email']

    try:
        delete_user(email_addr)
    except:
        pass
    create_user(email_addr)
 
    return email_addr

@app.route('/user_collecting/sharing/<string:type>/<string:email_addr>')
def user_collecting_sharing(type, email_addr):
    # bump up the rank of the user if the user clicks a sharing link.

    delete_user(email_addr)
    create_user(email_addr)

    if type == 'facebook':
        return redirect('https://facebook.com/sharer/sharer.php?u=http%3A%2F%2F180.76.238.148')
    elif type == 'twitter':
        return redirect('https://twitter.com/intent/tweet/?text=Welcome%20to%20my%20page!&amp;url=http%3A%2F%2F180.76.238.148')
    elif type == 'email':
        return redirect('mailto:?subject=Welcome%20to%20my%20page!&amp;body=http%3A%2F%2F180.76.238.148')