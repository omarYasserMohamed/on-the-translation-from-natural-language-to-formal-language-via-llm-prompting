# pylint: disable=broad-except
import os
import openai
#from datasets import load_dataset
import json
import datetime

openai.api_key = ""
#dataset = load_dataset("tasksource/folio")

def send_prompt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user" , "content": prompt}],
        max_tokens=1000,
        temperature=0.05
    )
    return response
    



def run(r):
    # reading the data from the folio-v1.json uncomment to use version 1 of the dataset
    f = open('folio-v1.json')
    dataset = json.load(f)
    f.close()
    all_outputs = []
    correct = 0
    wrong = 0
    for example_number in [9, 11, 17, 19, 20, 41, 67, 143]:
        print("++++++++++++++++++++++++++++++++++++++++++++ Example " + str(example_number) + "+++++++++++++++++++++++++++++++++++")
        context = '' 
        for p in  dataset['validation'][example_number]['premises']:
            context = context + " " + p
        question = "Based on the above information , is the following statement true , false , or uncertain?\n" + dataset['validation'][example_number]['conclusion']
        task_description = """ 
Given a problem statement as contexts, the task is to answer a logical reasoning question. 
------
Context:
The Blake McFall Company Building is a commercial warehouse listed on the National Register of Historic Places. The Blake McFall Company Building was added to the National Register of Historic Places in 1990. The Emmet Building is a five-story building in Portland, Oregon. The Emmet Building was built in 1915. The Emmet Building is another name for the Blake McFall Company Building. John works at the Emmet Building.

Question: Based on the above information, is the following statement true, false, or uncertain? The Blake McFall Company Building is located in Portland, Oregon.

Options:
A) True
B) False
C) Uncertain

Reasoning:
The Blake McFall Company Building is another name for the Emmet Building. The Emmet Building is located in Portland, Oregon. Therefore, the Blake McFall Company Building is located in Portland, Oregon.

The correct option is: A
------
Context:
People eat meat regularly or are vegetation. If people eat meat regularly, then they enjoy eating hamburgers and steaks. All people who are vegetarian are conscious of the environment or their health. If people are conscious about the environment or their health, then they do not go to fast food places often. If people have busy schedules without time to cook, then they go to fast food places often. If Jeremy does not both go to fast food places often and is conscious about the environment or their health, then he goes to fast food places often.

Question: Based on the above information, is the following statement true, false, or uncertain? If Jeremy has a busy schedule without time to cook, then Jeremy does not enjoy eating hamburgers and steaks.

Options:
A) True
B) False
C) Uncertain

Reasoning:
If Jeremy has a busy schedule without time to cook or enjoy eating hamburgers and steaks, then Jeremy goes to fast food places often. If people are conscious about the environment or their health, then they do not go to fast food places often. This means that Jeremy is not conscious about the environment or his health. All people who are vegetarian are conscious of the environment or their health. Therefore, Jeremy is not vegetarian. People eat meat regularly or are vegetation. Therefore, Jeremy eats meat regularly. If people eat meat regularly, then they enjoy eating hamburgers and steaks. Therefore, Jeremy enjoys eating hamburgers and steaks. 

The correct option is: B
------
"""
           
        final_prompt = task_description + "\n Context:\n" + context + "\n\n Question: " + question + "\n\n Options:\nA) True\nB) False\nC) Uncertain\n\nReasoning:"
        try:
            res = send_prompt(final_prompt).choices[0].message.content
            label = dataset['validation'][example_number]['label']
            ans = res[len(res)-1]
            if ans == 'A':
                ans = 'True'
            elif ans == 'B':
                ans = 'False'
            elif ans == 'C':
                ans = 'Uncertain'
            else:
                print(res)
            print(res[len(res)-1], ans)
            print(label)
            if ans == label:
                correct+=1
            else:
                wrong +=1
            all_outputs.append(input)
        except Exception as e:
            print(e)
    print("correct: ", correct)
    print("wrong ", wrong)
    return all_outputs


if __name__ == "__main__":
    num_of_examples = 3
    jsn = run(num_of_examples)

