import PySimpleGUI as sg    #pip3 install pySimpleGUIが必要
import sqlite3              #標準モジュール
import csv

#まずデータベースと接続し、カーソルオブジェクトを作っておく。
conn = sqlite3.connect('question.db')
c = conn.cursor()

#ここのコメントはテーブル作成やデータ挿入ではじめに使ったもの。今はいらない。
#c.execute("CREATE TABLE questions (que text, ans0 text, ans1 text, ans2 text, ans3 text, ansNo real)")
#c.execute("INSERT INTO questions VALUES('What is the largest country in the world?','America','Russia','China','Australia',1)")
#conn.commit()

#グローバル変数をここにおく。
qrows = []   #問題文、回答欄の配列を返す予定
userID = 0  #ID

#print = sg.Print　これも今はいらない。

#テーマを変えることができる。
sg.theme('DarkPurple 3')
comfont = '16pt'

#ここの関数は各画面のレイアウトと遷移を設定する。
def profile_window_read():
    profile_layout = [[sg.Text('Hello! This is Quiz Game.')],
                [sg.Text('ID'), sg.Input()],
                [sg.Text('PW'), sg.Input()],
                [sg.Button('Login')],
                [sg.Button('New User')]]
    profile_window = sg.Window('QuestionPython', profile_layout,font=comfont)
    event, values = profile_window.read()
    global userID   #グローバル変数IDをここで決定しておく。
    userID = values[0]
    password = values[1]
    if event=='Login':
        #UserIDが存在しないなら、ポップアップが現れる。
        if c.execute('SELECT * FROM users WHERE UserID=?', (userID,)).fetchall():
            #UserIDが存在しても、Passwordがなければ、ポップアップが現れる。
            if c.execute('SELECT * FROM users WHERE UserID=? AND Password=?', (userID, password,)).fetchall():
                profile_window.close()
                start_window_read()
            elif c.execute('SELECT * FROM users WHERE UserID=? AND Password=?', (userID, password,)).fetchall()==[]:
                sg.Popup('Password Unmatched!')
                profile_window.close()
                profile_window_read()
        elif c.execute('SELECT * FROM users WHERE UserID=?', (userID,)).fetchall()==[]:
            sg.Popup('UserID not exist!')
            profile_window.close()
            profile_window_read()
    elif event=='New User':
        profile_window.close()
        addition_window_read()
    elif event==sg.WIN_CLOSED:
        profile_window.close()
    else:
        profile_window.close()
        sg.Popup('Unexpected Error Occurred!')

def addition_window_read():
    addition_layout = [[sg.Text('Input your ID and Name.')],
                [sg.Text('ID'), sg.Input()],
                [sg.Text('PW'), sg.Input()],
                [sg.Button('Add')],
                [sg.Button('Return')]]
    addition_window = sg.Window('QuestionPython', addition_layout, font=comfont)
    event, values = addition_window.read()
    if event=='Add':
        try:
            #ここでINSERTを実行するとき、IDが同じだとエラーが発生exceptへ移る。
            c.execute("INSERT INTO users VALUES(?,?)",(values[0], values[1]))
            conn.commit()
            addition_window.close()
            sg.Popup('Your ID is added!')
            profile_window_read()
        except:
            sg.Popup('This UserID is already used.')
            addition_window.close()
            addition_window_read()
    elif event=='Return':
        addition_window.close()
        profile_window_read()
    elif event==sg.WIN_CLOSED:
        addition_window.close()
    else:
        profile_window.close()
        sg.Popup('Unexpected Error Occurred!')
    
def start_window_read():
    print(userID)
    start_layout = [[sg.Text('Hello! This is Quiz Game.')],
                [sg.Button('Start'), sg.Button('Edit')]]
    start_window = sg.Window('QuestionPython', start_layout, font=comfont)
    event, values = start_window.read()
    if event=='Start':
        start_window.close()
        quiz_window_read()
    elif event=='Edit':
        start_window.close()
        edit_window_read()
    elif event==sg.WIN_CLOSED:
        start_window.close()
    else:
        start_window.close()
        sg.Popup('Unexpexted Error Occurred!')
        
def edit_window_read():
    edit_layout = [[sg.Text('Type the question, Answers and AnswerNumber')],
               [sg.Text('Question'),sg.InputText()],
               [sg.Text('Ans0'),sg.Input(),sg.Text('Ans1'),sg.Input()],
               [sg.Text('Ans2'),sg.Input(),sg.Text('Ans3'),sg.Input()],
               [sg.Text('AnsNo'),sg.Input()],
               [sg.Button('Add'), sg.Button('Return'), sg.Button('CSV')]]
    edit_window = sg.Window('EditQuestion', edit_layout, font=comfont)
    event, values = edit_window.read()
    if event=='Add':
        edit_window.close()
        que, ans0, ans1, ans2, ans3, ansNo = values.values()
        c.execute("INSERT INTO questions VALUES(?,?,?,?,?,?,?)",(que, ans0, ans1, ans2, ans3, ansNo, userID))
        conn.commit()
        sg.Popup('Question Added!')
    elif event=='Return':
        edit_window.close()
        start_window_read()
    elif event=='CSV':
        edit_window.close()
        csv_window_read()
    elif event==sg.WIN_CLOSED:
        edit_window.close()
    else:
        edit_window.close()
        sg.Popup('Unexpexted Error Occurred!')

def csv_window_read():
    csv_layout = [[sg.Text('Upload your questions.csv file!')],
                  [sg.InputText(), sg.FileBrowse()],
                  [sg.Button('Upload'), sg.Button('Download'), sg.Button('Return')]]
    csv_window = sg.Window('CSV', csv_layout, font=comfont)
    event, values = csv_window.read()
    if event=='Upload':
        csv_window.close()
        with open(values[0], newline='') as f:
            reader = csv.reader(f)
            reader.__next__()   # 見出し行はnextで飛ばす
            for row in reader:
                que, ans0, ans1, ans2, ans3, ansNo = row
                c.execute("INSERT INTO questions VALUES(?,?,?,?,?,?,?)",(que, ans0, ans1, ans2, ans3, ansNo, userID))
            conn.commit()
            sg.Popup('Question Added!')
            csv_window.close()
            start_window_read()
    elif event=='Download':
        with open('download_questions.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Questions','Answer0','Answer1','Answer2','Answer3','AnswerNo'])
            c.execute("SELECT * FROM questions WHERE UserID=?", (userID,))
            for row in c.fetchall():
                writer.writerow(row[0:6])
            sg.Popup('Download finished!')
            csv_window.close()
            start_window_read()
    elif event=='Return':
        csv_window.close()
        edit_window_read()
    elif event==sg.WIN_CLOSED:
        csv_window.close()
    else:
        csv_window.close()
        sg.Popup('Unexpexted Error Occurred!')

def quiz_window_read():
    c.execute("SELECT * FROM questions WHERE UserID=?", (userID,))
    global qrows     #グローバル変数qrowsをここで決定しておく。
    qrows = c.fetchall()
    for row in qrows:
        que, ans0, ans1, ans2, ans3, ansNo, extra = row
        quiz_layout = [[sg.Text('Q:'+que)],
          [sg.Radio(ans0,'answer'),sg.Radio(ans1,'answer')],
          [sg.Radio(ans2,'answer'),sg.Radio(ans3,'answer')],
          [sg.Button('Submit')]]
        quiz_window = sg.Window('QuestionPython', quiz_layout, font=comfont)
        event, values = quiz_window.read()
        if values[ansNo]==True:
            quiz_window.close()
            sg.Popup('Good Job!')
        elif values[ansNo]==False:
            quiz_window.close()
            sg.Popup('Wrong!')
        elif event==sg.WIN_CLOSED:
            quiz_window.close()

profile_window_read()
