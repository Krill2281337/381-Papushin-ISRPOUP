from database import Base, engine, SessionLocal
from models import User, Request, Comment

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# пользователи
users = [
User(userID=1,fio="Трубин Никита Юрьевич",phone="89210563128",login="kasoo",password="root",type="Менеджер"),
User(userID=2,fio="Мурашов Андрей Юрьевич",phone="89535078985",login="murashov123",password="qwerty",type="Мастер"),
User(userID=3,fio="Степанов Андрей Викторович",phone="89210673849",login="test1",password="test1",type="Мастер"),
User(userID=7,fio="Баранова Эмилия Марковна",phone="89994563841",login="login2",password="pass2",type="Заказчик"),
]

for u in users:
    db.add(u)

# заявки
requests = [

Request(
requestID=1,
startDate="2023-06-06",
homeTechType="Фен",
homeTechModel="Ладомир ТА112",
problemDescription="Перестал работать",
requestStatus="В процессе ремонта",
masterID=2,
clientID=7
),

Request(
requestID=2,
startDate="2023-05-05",
homeTechType="Тостер",
homeTechModel="Redmond RT-437",
problemDescription="Перестал работать",
requestStatus="В процессе ремонта",
masterID=3,
clientID=7
)

]

for r in requests:
    db.add(r)

# комментарии
comments = [

Comment(
commentID=1,
message="Интересная поломка",
masterID=2,
requestID=1
),

Comment(
commentID=2,
message="Очень странно, будем разбираться",
masterID=3,
requestID=2
)

]

for c in comments:
    db.add(c)

db.commit()
db.close()

print("База создана и заполнена")