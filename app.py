from aioflask import *
from flask_mysqldb import MySQL
from zk import ZK
from os import environ

app = Flask(__name__)
app.config["MYSQL_HOST"] = environ.get("database.default.hostname")
app.config["MYSQL_DB"] = environ.get("database.default.database")
app.config["MYSQL_USER"] = environ.get("database.default.username")
app.config["MYSQL_PASSWORD"] = environ.get("database.default.password")
mysql = MySQL(app=app)


async def show_data(username=None):
  cursor = mysql.connection.cursor()
  if (username is None):
    query = f"SELECT * FROM users"
    cursor.execute(query)
    return cursor.fetchall()
  else:
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()


async def create_data(username):
  data = await show_data(username=username)
  if (data is not None):
    return {
        "message": "Gagal menambahkan user."
    }
  else:
    cursor = mysql.connection.cursor()
    query = f"INSERT INTO users (username) VALUES ('{username}')"
    cursor.execute(query)
    mysql.connection.commit()
    return {
        "message": "Berhasil menambahkan user."
    }


async def update_data(old_username, new_username):
  data = await show_data(username=old_username)
  if (data is None):
    return {
        "message": "Gagal mengupdate user."
    }
  else:
    cursor = mysql.connection.cursor()
    query = f"UPDATE users SET username = '{new_username}' WHERE username = '{old_username}'"
    cursor.execute(query)
    mysql.connection.commit()
    return {
        "message": "Berhasil mengupdate user."
    }


async def delete_data(username):
  data = await show_data(username=username)
  if (data is None):
    return {
        "message": "Gagal menghapus user."
    }
  else:
    cursor = mysql.connection.cursor()
    query = f"DELETE FROM users WHERE username = '{username}'"
    cursor.execute(query)
    mysql.connection.commit()
    return {
        "message": "Berhasil menghapus user."
    }


@app.route("/", methods=["GET"])
async def showData():
  return await list(show_data())


@app.route("/create", methods=["POST"])
async def createData():
  username = request.form["username"]
  return await create_data(username=username)


@app.route("/update", methods=["PUT"])
async def updateData():
  old_username = request.form["old_username"]
  new_username = request.form["new_username"]
  return await update_data(old_username=old_username, new_username=new_username)


@app.route("/delete", methods=["DELETE"])
async def deleteData():
  username = request.form["username"]
  return await delete_data(username=username)


@app.post("/getAttendance")
async def getAttendance():
  date = request.form["date"]

  zk = ZK(
      "192.168.0.99",
      port=4370,
      timeout=30,
      password=0,
      force_udp=False,
      ommit_ping=False,
  )
  conn = zk.connect()
  attendances = conn.get_attendance()
  for attendance in attendances:
    attendance = str(attendance).split()

    # parse data
    attendance_at = attendance[3]
    if (date == attendance_at):
      user_id = attendance[1]
      scan_time = attendance[4]
      scan_time = str(scan_time).split(":")
      scan_time = scan_time[0] + ":" + scan_time[1] + ":00"

      await pyzk(user_id=user_id, scan_time=scan_time, attendance_at=attendance_at)
  mysql.connection.commit()
  return {
      "message": "Berhasil mengambil absensi."
  }


async def pyzk(user_id: int, scan_time: str, attendance_at: str):
  cursor = mysql.connection.cursor()
  query = f"INSERT INTO pyzk (user_id, scan_time, , attendance_at) VALUES ({user_id}, '{scan_time}', '{attendance_at}')"
  return cursor.execute(query)
