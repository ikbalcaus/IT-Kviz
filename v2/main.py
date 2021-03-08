from flask import Flask, render_template, request, redirect, session
import random, os, waitress



app=Flask(__name__)
app.secret_key=os.urandom(24)



with open("pitanja.txt","r") as file:
    questions_answers=file.read().splitlines()
questions=[i.split(';')[0] for i in questions_answers]
answers=[i.split(';')[1] for i in questions_answers]



# Exceptions Start
if len(questions)<5:
    print("GRESKA\nDoslo je do pogreske unutar datoteke \"pitanja.txt\"")
    print("__________________________________________________\n")
    print("U datoteci mora postojati minimalno 5 pitanja")
    input()
    exit()


with open("postavke.txt","r") as file:
    try:
        number_of_all_questions=int(file.readline().replace("broj pitanja:",""))
        seconds=int(file.readline().replace("broj sekundi za odgovor:",""))
        number_pass=int(file.readline().replace("broj pitanja za prolaz:",""))
        disable_results=int(file.readline().replace("omoguci korisniku da vidi rezultate (1-da, 0-ne):",""))
        disable_questions=int(file.readline().replace("omoguci korisniku da vidi pitanja (1-da, 0-ne):",""))
        host=int(file.readline().replace("omoguci lan mrezu (1-da, 0-ne):",""))

    except Exception:
        print("GRESKA\nDoslo je do pogreske unutar datoteke \"postavke.txt\"")
        print("_________________________________________________________________________________\n")
        print("1. Provjerite da li ste unijeli slovo umjesto broja")
        print("_________________________________________________________________________________\n")
        print("2. Kopirajte sljedeci tekst i zalijepite ga u datoteku \"postavke.txt\" na pocetak:\n")
        print("broj pitanja:\nbroj sekundi za odgovor:\nbroj pitanja za prolaz:\nomoguci korisniku da vidi rezultate (1-da, 0-ne):\nomoguci korisniku da vidi pitanja (1-da, 0-ne):\nomoguci lan mrezu (1-da, 0-ne):")
        input()
        exit()


if number_of_all_questions<5 or seconds<5 or number_of_all_questions<number_pass or number_pass<1 or len(questions)<number_of_all_questions:
    print("GRESKA\nDoslo je do pogreske unutar datoteke \"postavke.txt\"")
    print("_______________________________________________________\n")
    print("Procitajte upozorenja u datoteci i prepravite varijable")
    input()
    exit()
# Exceptions End



if disable_results==0:
    disable_results="disabled"
    disable_results_forever=True
else:
    disable_results=("disabled" if os.stat("rezultati.txt").st_size==0 else "")
    disable_results_forever=False

disable_questions=("disabled" if disable_questions==0 else "")
host=("127.0.0.1" if host==0 else "0.0.0.0")



# Routes Start
@app.route("/")
def home_route():
    return render_template("home.html",
        disable_results=disable_results,
        disable_questions=disable_questions
    )



@app.route("/exam", methods=["GET", "POST"])
def exam_route():
    global questions, answers, number_pass, disable_results, disable_results_forever

    if request.method=="GET":
        return redirect("/")

    if request.form.get("name"):
        questions_answers=list(zip(questions,answers))
        random.shuffle(questions_answers)
        questions,answers=zip(*questions_answers)

        session["name"]=request.form.get("name")
        session["number_of_question"]=0
        session["result"]=0
        session["questions"]=questions
        session["answers"]=answers

    else:
        if session["answers"][session["number_of_question"]].lower()==request.form.get("answer").replace("Č","C").replace("č","c").replace("Ć","C").replace("ć","c").replace("Š","S").replace("š","s").replace("Ž","Z").replace("ž","z").replace("Đ","D").replace("đ","d").lower():
            session["result"]+=1


    if session["number_of_question"]!=number_of_all_questions:
        session["number_of_question"]+=1

        return render_template("exam.html",
            questions=session["questions"],
            seconds=seconds,
            number_of_question=session["number_of_question"],
            href_disable="#",
            cursor="cursor:default",
            disable_results="disabled",
            disable_questions="disabled"
        )



    else:
        if session["result"]<number_pass:
            info1="Žao mi je "+session["name"]
            info2="Niste zadovoljili zadani kriterij"
            color="danger"

        else:
            info1="Čestitam "+session["name"]
            info2="Zadovoljili ste zadani kriterij"
            color="success"


        with open("rezultati.txt","a") as file:
            if os.stat("rezultati.txt").st_size!=0:
                file.write("\n")
            file.write(session["name"].replace("Č","C").replace("č","c").replace("Ć","C").replace("ć","c").replace("Š","S").replace("š","s").replace("Ž","Z").replace("ž","z").replace("Đ","D").replace("đ","d")+" ; "+str(session["result"])+"/"+str(number_of_all_questions)+" ; "+color)

        if disable_results_forever==False and disable_results=="disabled":
            disable_results=""


        return render_template("finish.html",
            info1=info1,
            info2=info2,
            info3="Imate "+str(session["result"])+"/"+str(number_of_all_questions)+" tačnih odgovora",
            color=color,
            disable_results=disable_results,
            disable_questions=disable_questions
        )



@app.route("/results")
def results_route():
    global disable_results

    if disable_results=="disabled":
        return redirect("/")

    with open("rezultati.txt","r") as file:
        results_all=file.read().splitlines()
    results_all.reverse()
    number_of_lines=sum(1 for line in open("rezultati.txt"))

    result1=[i.split(';')[0] for i in results_all]
    result2=[i.split(';')[1] for i in results_all]
    result3=[i.split(';')[2] for i in results_all]

    return render_template("results.html",
        number_of_lines=number_of_lines,
        result1=result1,
        result2=result2,
        result3=result3,
        active_results="active",
        disable_results=disable_results,
        disable_questions=disable_questions
    )



@app.route("/questions")
def questions_route():
    global disable_questions

    if disable_questions=="disabled":
        return redirect("/")

    with open("pitanja.txt","r") as file:
        questions_answers=file.read().splitlines()
    questions=[i.split(';')[0] for i in questions_answers]

    return render_template("questions.html",
        questions=questions,
        active_questions="active",
        disable_results=disable_results,
        disable_questions=disable_questions
    )
# Routes End



@app.errorhandler(404)
def error(error):
    return redirect("/")



@app.errorhandler(500)
def error(error):
    return render_template("response500.html",
        disable_results=disable_results,
        disable_questions=disable_questions
    )



if __name__=="__main__":
    waitress.serve(app, host=host, port=80)
