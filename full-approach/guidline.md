# Guidline on how the approach in ./full-approach works.
### 1- The first step is to set the number of examples to be translated in the nl-to-fol.py script.

### 2- Run the nl-to-fol.py script.

### 3- The script will translate the examples and update the latest.json file in the temp folder and will save a file with the translations in the permenant folder.

### 4- After the nl-to-fol.py script is done run the prove.py script, that will use the translations in the  updated latest.py file in the temp folder and will prove them.