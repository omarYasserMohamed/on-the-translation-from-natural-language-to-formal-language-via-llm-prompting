from nltk.inference.prover9 import *
from nltk.inference.mace import *
import json
import datetime

# set the path to the prover9 executable
os.environ['PROVER9'] = '../Prover9/bin'


def prove(argument):
    #checking the validity
    try:
        goal, assumptions = argument
        val_g = Expression.fromstring(goal)
        alist = [Expression.fromstring(a) for a in assumptions]
        val_p = Prover9Command(val_g, assumptions=alist).prove()
        if val_p:
           return "True" 
    except Exception as e:
        print(e)
        return "Error"

    #checking the satisfiability
    try:
        goal, assumptions = argument
        goal = "-(" + goal + ")"
        val_g = Expression.fromstring(goal)
        alist = [Expression.fromstring(a) for a in assumptions]
        val_p = Prover9Command(val_g, assumptions=alist).prove()
        if val_p:
           return "False" 
        else:
            return "Uncertain"
    except Exception as e:
        print(e)
        return "Error"


if __name__ == '__main__':
    data = None
    try:
        #extracting the latest generated translation
        f = open('temp/latest.json')
        data = json.load(f)
    except:
        print("latest.json not found please run nl-to-fol.py file first")
    
    print("Translation generated at: "+str(data["timestamp"]))
    # proving all translations in the latest file
    ex = 0
    non_ex = 0
    correct = 0
    wrong = 0
    temp = []
    non_ex_array = []
    for trans in data['responses']:
        print("----------- Example number: "+ str(trans["example"])+ " -----------")
        p = prove(trans["response"])
        print("reasoner result: " + p)
        print("Label: " + trans["label"])
        if trans["response"][0] == "Error" or p == "Error":
            non_ex+=1
            non_ex_array.append(trans["example"])
        else:
            ex+=1
            if trans["label"] == p:
                correct+=1
            else:
                wrong+=1
                trans["prover-answer"] = p
                temp.append(trans)
    
    current_time = datetime.datetime.now()
    current_time = current_time.strftime('%Y-%m-%d|%H:%M:%S')
    out = json.loads(json.dumps({"timestamp": current_time, "responses": temp}))
    file = "wrong-trans/wrongTransAT" + str(current_time) + ".json"
    json_object = json.dumps(out, indent=4)
    with open(file, "w") as outfile:
        outfile.write(json_object)   
            

    print("nonexecutable: "+str(non_ex))
    print("executable: " + str(ex))
    print("correct: " + str(correct))
    print("wrong: "+ str(wrong))
    print(non_ex_array)
    print(len(non_ex_array))

    
 
    