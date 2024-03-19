# pylint: disable=broad-except
import os
import openai
import json
import datetime
import re
from pyparsing import infixNotation, opAssoc, Word,  Suppress, printables


openai.api_key = ""

def send_prompt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
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

def prepare_for_prover(fol, con):
    try:
        i = 0
        while i < len(fol):
            trans = fol[i]
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
            fol[i] = trans
            i+=1
        con = con.replace('∧', ' & ')
        con = con.replace('∨', ' | ')
        con = con.replace('.', '_')
        con = con.replace('-', '_')
        con = con.replace('Ś', 'S')
        con = con.replace('ą', 'a')
        con = con.replace('¬', ' -')
        con = con.replace('→', ' -> ')
        con = con.replace('↔', ' <-> ')
        con = con.replace('∀', ' all ')
        con = con.replace('∃', ' exists ')
        con = con.replace('true ', ' $T ')
        con = con.replace('false ', ' $F ')
        con = con.replace('≠', ' != ')
        return (con, fol)
    
    except Exception as e:
        print(e)
        return ("Error", [])
        


def run(r):
    # reading the data from the folio-v1.json uncomment to use version 1 of the dataset
    f = open('folio-v1.json')
    dataset = json.load(f)
    f.close()
    all_outputs = []
    for example_number in range(204):
        if example_number in [91]:
            print("++++++++++++++++++++++++++++++++++++++++++++ Example " + str(example_number) + "+++++++++++++++++++++++++++++++++++")
            try:
                question = dataset['validation'][example_number]['conclusion-FOL']
                print("query:", question)
                for y in dataset['validation'][example_number]['premises-FOL']:
                    print(y)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    num_of_examples = 3
    run(num_of_examples)

    
