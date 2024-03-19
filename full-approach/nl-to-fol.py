# pylint: disable=broad-except
import os
import openai
from datasets import load_dataset
import json
import datetime
import re
from pyparsing import infixNotation, opAssoc, Word,  Suppress, printables
import winsound

openai.api_key = ""
dataset = load_dataset("tasksource/folio")

def send_prompt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[{"role": "user" , "content": prompt}],
        max_tokens=1000,
        temperature=0.05
    )
    return response
    
def expand_xor(expression_in):
    payload = ""
    expression = expression_in
    if "all x" in expression:
        expression = expression.split("all x")[1]
        payload += "all x "
    if "exists x" in expression:
        expression = expression_in.split("exists x")[1]
        payload += "exists x "
    
    expression = expression.replace(' ','')
    operand = Word(printables)
    operator = Word("⊕")

    expr = infixNotation(operand,
                        [(operator, 2, opAssoc.LEFT),],
                        lpar=Suppress("("),
                        rpar=Suppress(")"))
    parsed_expr = expr.parseString(expression)

    target_operator = "⊕" 
    for item in parsed_expr:
        try:
            if len(item) == 3:
                if item[1] == target_operator:
                    print("*********XOR processing applied********")
                    if payload == "":
                        return f" ( {item[0]} & -{item[2]} ) |  ( -{item[0]} & {item[2]} ) "
                    else:
                        while True:
                            if item[0][0] =='(':
                                item[0] = item[0][1:]
                            else:
                                break
                        while True:
                            if item[2][-2] == ')':
                                item[2] = item[2][:-1]
                            else:
                                break
                        print(item)
                        print(item[0][0])
                        print(item[2][:-2])
                        return f" {payload} ( ( {item[0]} & -{item[2]} ) |  ( -{item[0]} & {item[2]} ) )"

        except Exception as e:
            print(e)
            return expression_in
    
    return expression_in

def remove_spaces_between_quotes(text):
    pattern = re.compile(r'"(.*?)"')
    def replace_spaces(match):
        return match.group(0).replace(' ', '_')
    modified_text = pattern.sub(replace_spaces, text)
    return modified_text

def prepare_for_prover(trans):
    try:
        trans = trans.split('Premises:')[1]
        trans = trans.replace('∧', ' & ')
        trans = trans.replace('∨', ' | ')
        trans = trans.replace('.', '_')
        trans = trans.replace('-', '_')
        trans = trans.replace('Ś', 'S')
        trans = trans.replace('ą', 'a')
        trans = trans.replace('¬', ' -')
        trans = trans.replace('→', ' -> ')
        trans = trans.replace('↔', ' <-> ')
        trans = trans.replace('∀', ' all ')
        trans = trans.replace('∃', ' exists ')
        trans = trans.replace('true ', ' $T ')
        trans = trans.replace('false ', ' $F ')
        trans = trans.replace('≠', ' != ')
        trans = trans.split("Query:")
        prem = trans[0]
        prem = prem.split("\n")
        all_prem = []
        for p in prem:
            temp = p.split(":::")
            if len(temp) == 2:
                mod = temp[0]
                mod = remove_spaces_between_quotes(mod)
                if mod.startswith(" all x") and mod.count("all") == 1:
                    mod = mod.split("all x ")
                    mod[1] = "(" + mod[1] + ")"
                    mod = "all x " + mod[1]
                elif mod.startswith(" exists x") and mod.count("exists") == 1:
                    mod = mod.split("exists x ")
                    mod[1] = "(" + mod[1] + ")"
                    mod = "exists x " + mod[1]
                elif (mod.startswith(" - all x") or mod.startswith("- all x")) and mod.count("all") == 1:
                    mod = mod.split(" - all x ")
                    mod[1] = "(" + mod[1] + ")"
                    mod = "- all x " + mod[1]
                elif (mod.startswith(" - exists x") or mod.startswith("- exists x")) and mod.count("exists") == 1:
                    mod = mod.split("- exists x ")
                    mod[1] = "(" + mod[1] + ")"
                    mod = "- exists x " + mod[1]
                all_prem.append(mod)
        
        con = trans[1]
        con = con.split(" :::")[0]
        con = con.split("\n")
        con = con[len(con)-1]
        con = remove_spaces_between_quotes(con)
        if con.startswith(" all x") and con.count("all") == 1:
            con = con.split("all x ")
            con[1] = "(" + con[1] + ")"
            con = "all x " + con[1]
        elif con.startswith(" exists x") and con.count("exists") == 1:
            con = con.split("exists x ")
            con[1] = "(" + con[1] + ")"
            con = "exists x " + con[1]
        elif (con.startswith(" - all x") or con.startswith("- all x")) and con.count("all") == 1:
            con = con.split(" - all x ")
            con[1] = "(" + con[1] + ")"
            con = "- all x " + con[1]
        elif (con.startswith(" - exists x") or con.startswith("- exists x")) and con.count("exists") == 1:
            con = con.split("- exists x ")
            con[1] = "(" + con[1] + ")"
            con = "- exists x " + con[1]
        i = 0
        while i < len(all_prem):
            p = all_prem[i]
            if "⊕" in p:
                all_prem[i] = expand_xor(p)
            i+=1
        if "⊕" in con:
            con = expand_xor(con)
        return (con, all_prem)
    
    except Exception as e:
        print(e)
        return ("Error", [])
        


def run(r):
    # reading the data from the folio-v1.json uncomment to use version 1 of the dataset
    f = open('folio-v1.json')
    dataset = json.load(f)
    f.close()
    all_outputs = []
    for example_number in range(r):
        print("++++++++++++++++++++++++++++++++++++++++++++ Example " + str(example_number) + "+++++++++++++++++++++++++++++++++++")
        context = '' 
        for p in  dataset['validation'][example_number]['premises']:
            context = context + " " + p
        print(context)
        question = "Based on the above information , is the following statement true , false , or uncertain?\n" + dataset['validation'][example_number]['conclusion']
        task_description = """ 
        Given a text and a question. The task is to use the defined rules of the allowed operators, of constants and variables naming of predicate naming, and of predicate naming to parse every sentence in the text and the question into first-order logic formulas and list all the used predicates and constants as the given examples. Never add the Query to the set of Facts. Translate every information in each sentence.
        The allowed operators are the following:
            1) logical conjunction of expr1 and expr2: expr1 ∧ expr2
            2) logical disjunction of expr1 and expr2: expr1 ∨ expr2
            3) logical negation of expr1: ¬expr1
            4) expr1 implies expr2: expr1 → expr2
            5) expr1 if and only if expr2: expr1 ↔ expr2
            6) logical universal quantification: ∀x
            7) logical existential quantification: ∃x
           Output format for each fact : logic form ::: description

        The rules of the predicates naming are as following:
            1) The predicate names has to be extracted from the verbal phrase of each sentence starting with the main verb followed by the adverb in the form mainVerb_adverb. 
            2) If some verbs have no corresponding adverbs then only give the verb name in the list.
            3) Never use negations like "not" in any combination.
            4) If there is an expression without a verb use the full adjective phrase to form a combination in the form is_adjective_phrase.
            5) If the verb is "am", "is", "are", "was", "were" then the full adjective phrase of the sentence has to be taken instead of the adverb and take "is" instead of the main verb in the form is_adjective_phrase.
            6) Never use the predicates as infix operator such (e.g. x predicate y).
            7) Never use embedded predicates ( e.g. predicate_one(predicate_two(x)) or predicate_one(predicate_two(x), predicate_three(x)) ).
            8) Never use the same predicate with differnt number of arguments (e.g. plays(x) and plays(x, y)).
            

        The rules of constants and variables naming are as following:
            1) All variables have to be a character of the following set of characters {u,v,w,x,y,z}.
            2) The priority order of using the variables is the following order x, y, z, u, v, w.
            3) Never use the same semantic for both the constants and predicates in the first-order logic formulas

            
        Examples to be used as a guidance for the expected input and output would be as following:
                Text:
				All eels are fish. eels eat. No fish are plants. A thing is either a plant or animal. Nothing that breathes is paper. All animals breathe. If a sea eel is either an eel or a plant, then a sea eel is an eel or an animal.
                Question:
                Based on the above information, is the following statement true, false, or uncertain? Sea eel is an eel. 
                ###
                Constants:
                sea_eel ::: represents a sea eel
                Predicates:
				is_eel(x) ::: x is an eel.
				is_fish(x) ::: x is a fish.
				eat(x) ::: x eats.
				is_plant(x) :: x is a plant.
				is_animal(x) ::: x is an animal.
				breathe(x) ::: x breathes.
				is_paper(x) ::: x is paper.
                Premises:
				∀x (is_eel(x) →  is_fish(x)) ::: All eels are fish.
				∀x (is_eel(x) →  eat(x)) ::: eels eat.
				∀x (is_fish(x) → ¬is_plant(x)) ::: No fish are plants.
				∀x ((is_plant(x) ∧ ¬is_animal(x)) ∨ (¬is_plant(x) ∧ is_animal(x))) ::: A thing is either a plant or animal.
				∀x (breathe(x) → ¬is_paper(x)) ::: Nothing that breathes is paper.
				∀x (is_animal(x) →  breathe(x)) ::: All animals breathe.
				((¬is_eel("sea_eel") ∧ is_plant("sea_eel")) ∨ (is_eel("sea_eel") ∧ ¬is_plant("sea_eel"))) → (is_eel("sea_eel") ∨ is_animal("sea_eel")) ::: If a sea eel is either an eel or a plant, then a sea eel is an eel or an animal.
				Query:
                is_eel("sea_eel") :::  Sea eel is an eel.
                ----
                Text: 
                There are five grades in English class: A+, A, B+, B, and C. If a student gets an A+ in English class, then his score is greater than 95. If a student gets an A in English class, then his score is greater than 90 but lower than 95. Zhang got an A in English class. Wang's English class score is better than Zhang's. Wu's English class score is lower than 90. If a student's English class score is lower than 90, then it is not greater than 95 or 90, and lower than 95.
                Question:
                Based on the above information, is the following statement true, false, or uncertain? Zhang's English class score is lower than 95.
                ###
                Constants:
                zhang ::: represents zhang
                wang ::: represents wang
                wu ::: represents wu
                Predicates:
                get_grade(x,y) ::: x got grade y.
                get_score(x,y) ::: x got score y.
                is_student(x) ::: x is a student.
                is_greater_than_95(x) ::: score x is greater than 95.
                is_greater_than_90(x) ::: score x is greater than 90.
                is_lower_than_95(x) ::: score x is lower than 95.
                is_lower_than_90(x) ::: score x is lower than 90.
                is_better_than(x,y) ::: score x is better than score y.
                Premises: 
                ∀x ((get_grade(x, "A+") ∨ get_grade(x, "A") ∨ get_grade(x, "B") ∨ get_grade(x, "C")) ∧ (get_grade(x, "A+") → ¬get_grade(x, "A") ∧ ¬get_grade(x, "B") ∧ ¬get_grade(x, "C")) ∧ (get_grade(x, "A") → ¬get_grade(x, "A+") ∧ ¬get_grade(x, "B") ∧ ¬get_grade(x, "C")) ∧ (get_grade(x, "C") → ¬get_grade(x, "A+") ∧ ¬get_grade("A", x) ∧ ¬get_grade(x, "B"))) ::: There are five grades in English class: A+, A, B+, B, and C.
                ∀x ∀y (is_student(x) ∧ get_grade(x, "A+") → get_score(x,y) ∧ is_greater_than_95(y)) :::  If a student gets an A+ in English class, then his score is greater than 95. 
                ∀x ∀y  (is_student(x) ∧ get_grade(x, "A") → get_score(x,y) ∧ is_greater_than_90(y) ∧ is_lower_than_95(y)) :::  If a student gets an A in English class, then his score is greater than 90 but lower than 95.
                is_student("zhang") ∧ get_grade("zhang", "A") :::  Zhang got an A in English class.
                ∀x ∀y (is_student("wang") ∧ is_student("zhang") ∧ get_score("wang", x) ∧  get_score("zhang", y) ∧ is_better_than(x,y))  :::  Wang's English class score is better than Zhang's. 
                ∀x (is_student("wu") ∧ get_score(x ,"wu") ∧ is_lower_than_90(x)) :::  Wu's English class score is lower than 90.
                ∀x ∀y(is_student(x) ∧ get_score(x,y) ∧ is_lower_than_90(y) → ¬is_greater_than_95(y) ∧ ¬is_greater_than_90(y) ∧ is_lower_than_95(y) :::  If a student's English class score is lower than 90, then it is not greater than 95 or 90, and lower than 95.
                Query:
                ∀x(is_student("zhang") ∧ get_score("zhang", x) ∧ is_lower_than_95(x)) ::: Zhang's English class score is lower than 95.
                ----
                Text:
                All people who regularly drink coffee are dependent on caffeine. People either regularly drink coffee or joke about being addicted to caffeine. No one who jokes about being addicted to caffeine is unaware that caffeine is a drug. Rina Stone is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug. If Rina Stone is not a person dependent on caffeine and a student, then Rina Stone is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student.
                Question:
                Based on the above information, is the following statement true, false, or uncertain? Rina Stone is either a person who jokes about being addicted to caffeine or is unaware that caffeine is a drug.
                ###
                Constants:
                rina_stone ::: represents rina stone
                Predicates:
                dependent(x) ::: x is a person dependent on caffeine.
                drink_regularly(x) ::: x regularly drinks coffee.
                joke_about_addicted(x) ::: x jokes about being addicted to caffeine.
                is_unaware(x) ::: x is unaware that caffeine is a drug.
                is_student(x) ::: x is a student.
                Premises:
                ∀x (drink_regularly(x) → dependent(x)) ::: All people who regularly drink coffee are dependent on caffeine.
                ∀x ((¬drink_regularly(x) ∧ joke_about_addicted(x)) ∨ (drink_regularly(x) ∧ ¬joke_about_addicted(x))) ::: People either regularly drink coffee or joke about being addicted to caffeine.
                ∀x (joke_about_addicted(x) → ¬is_unaware(x)) ::: No one who jokes about being addicted to caffeine is unaware that caffeine is a drug. 
                ((is_student("rina_stone") ∧ is_unaware("rina_stone")) ∧ (is_student("rina_stone") ∨ is_unaware("rina_stone"))) ∨ (¬(is_student("rina_stone") ∧ is_unaware("rina_stone")) ∧ ¬(is_student("rina_stone") ∨ is_unaware("rina_stone"))) ::: Rina Stone is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug. 
                ¬(dependent("rina_stone") ∧ is_student("rina_stone")) → ((dependent("rina_stone") ∧ is_student("rina_stone")) ∧ (dependent("rina_stone") ∨ is_student("rina_stone"))) ∨ (¬(dependent("rina_stone") ∧ is_student("rina_stone")) ∧ ¬(dependent("rina_stone") ∨ is_student("rina_stone"))) ::: If Rina Stone is not a person dependent on caffeine and a student, then Rina Stone is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student.
                Query:
                (¬joke_about_addicted("rina_stone") ∧ is_unaware("rina_stone")) ∨ (¬joke_about_addicted("rina_stone") ∧ is_unaware("rina_stone"))::: Rina Stone is either a person who jokes about being addicted to caffeine or is unaware that caffeine is a drug.
                ----
                Text:
				Edwin Smith was a New Zealand rower from Auckland. Edwin Smith was also known as Ted Smith. Edwin Smith went to Rose Road Primary School, located in Grey Lynn. Edwin Smith was a sergeant who served with the New Zealand 24th battalion in Italy and Egypt. Broadway Sheetmetals was a business run and owned by Edwin Smith, a sheet metal worker.
                Question:
                Based on the above information, is the following statement true, false, or uncertain?  Ted Smith was a sergeant.
                ###
                Constants:
                edwin_smith ::: represents edwin smith
                new_zealand ::: represents new zealand
                auckland ::: represents auckland
                ted_smith ::: represents ted smith
                rose_road_primary_school ::: represents the rose road primary school
                grey_lynn ::: represents grey lynn
                new_zealand_24th_battalion ::: represents the new zealand 24th battalion
                italy ::: represents italy
                egypt ::: represents egypt
                broadway_sheetmetals ::: represents the broadway  sheetmetals
                Predicates:
                is_from(x, y) ::: x is from y.
				is_rower(x) ::: x is rower.
				go_to(x, y) ::: x goes to y.
				located_in(x, y) ::: x is located in y.
				is_sergeant(x) ::: x is sergeant.
				served_with(x,y) ::: x served with y.
				served_in(x,y) ::: x served in y.
				is_business(x) ::: x is a business.
				run(x, y) ::: x runs y.
				own(x, y) ::: x owns y.
				is_sheetmetal_worker(x) ::: x is a sheetmetal worker.
                Premises:
                is_from("edwin_smith", "new_zealand") ∧ is_rower("edwin_smith")  ∧ is_from("edwin_smith", "auckland") ::: Edwin Smith was a New Zealand rower from Auckland.
				"edwin_smith" = "ted_smith" ::: Edwin Smith was also known as Ted Smith.
				go_to("edwin_smith", "rose_road_primary_school") ∧ located_in("rose_road_primary_school", "grey_lynn") ::: Edwin Smith went to Rose Road Primary School, located in Grey Lynn.
				is_sergeant("edwin_smith") ∧ served_with("edwin_smith", "new_zealand_24th_battalion") ∧ served_in("edwin_smith", "italy") ∧ served_in("edwin_smith", "egypt") :::  Edwin Smith was a sergeant who served with the New Zealand 24th battalion in Italy and Egypt.
				is_business("broadway_sheetmetals") ∧ run("edwin_smith", "broadway_sheetmetals") ∧ own("edwin_smith", "broadway_sheetmetals") ∧ is_sheetmetal_worker("edwin_smith") :::  Broadway Sheetmetals was a business run and owned by Edwin Smith, a sheet metal worker.
				Query:
                is_sergeant("ted_smith") :::  Ted Smith was a sergeant.
                ----
                Text:
                Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music. Any choral conductor is a musician. Some musicians love music. Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
                Question:
                Based on the above information, is the following statement true, false, or uncertain? Miroslav Venhoda loved music.
                ###
                Constants:
                miroslav ::: represents miroslav
                renaissance ::: represents the renaissance
                baroque ::: represents the baroque
                music ::: represents music
                method_of_studying_gregorian_chant ::: represents the method of studying gregorian chant
                year_1946 ::: represents the year of 1946
                Predicates:
                is_czech(x) ::: x is a Czech person.
                is_choral_conductor(x) ::: x is a choral conductor.
                is_musician(x) ::: x is a musician.
                loves(x, y) ::: x loves y.
                is_author(x, y) ::: x is the author of y.
                is_book(x) ::: x is a book.
                publishes(x, y) ::: x is published in year y.
                specializes(x, y) ::: x specializes in y.
                Premises:
                is_czech("miroslav") ∧ is_choral_conductor("miroslav") ∧ specializes("miroslav", "renaissance") ∧ specializes("miroslav", "baroque") ::: Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music.
                ∀x (is_choral_conductor(x) → is_musician(x)) ::: Any choral conductor is a musician.
                ∃x (is_musician(x) ∧ loves(x, "music")) ::: Some musicians love music.
                is_book("method_of_studying_gregorian_chant") ∧ is_author("miroslav", "method_of_studying_gregorian_chant") ∧ publishes("method_of_studying_gregorian_chant", "year_1946") ::: Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
                Query:
                loves("miroslav", "music") ::: Miroslav Venhoda loved music.
                ------
"""
            
        final_prompt = task_description + "\n Text: " + context + "\n Question: " + question
        try:
            res = send_prompt(final_prompt).choices[0].message.content
            print(res)
            fol = prepare_for_prover(res)
            input = json.loads(json.dumps({"example": example_number, "response": fol, "label": dataset['validation'][example_number]['label'], "text": res, "problem": context, "question": question}))
            all_outputs.append(input)
        except Exception as e:
            print(e)
    return all_outputs


if __name__ == "__main__":
    num_of_examples = 3
    jsn = run(num_of_examples)
    current_time = datetime.datetime.now()
    current_time = current_time.strftime('%Y-%m-%d|%H:%M:%S')
    out = json.loads(json.dumps({"model":"gpt-3.5-turbo", "timestamp": current_time, "responses": jsn}))
    
    #remove latest.json (if found) to be updated
    try:
        os.remove("temp/latest.json")
    except:
        pass

    #create/update the lates.json to be used by the prover
    json_object = json.dumps(out, indent=4)
    with open("temp/latest.json", "w") as outfile:
        outfile.write(json_object)
    
    #create the permanent file
    current_time = datetime.datetime.now()
    current_time = current_time.strftime('%Y-%m-%d_%H-%M-%S')
    file = "permanent/transAT" + str(current_time) + ".json"
    with open(file, "w") as outfile:
        outfile.write(json_object)    
    
    # uncomment to be notified when the script is done running
    #frequency = 1000  
    #duration = 5000  
    #winsound.Beep(frequency, duration)

