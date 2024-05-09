def keep_generate_till(model,prompt,endstring):
    lastanswer = ""
    while not lastanswer.endswith(endstring):
        answer = ""
        answer = model.invoke(f"{prompt}{lastanswer}")
        # for chunk in model.generate_text(f"{prompt}{lastanswer}"):
        #     answer += chunk
        lastanswer += answer
    return lastanswer

def generate_inputfunction(model, dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a java Value Object class that implement the input requirement:
        -validate the datatype, length, mandatory/optional and other requriement of the field.
        -the value should be captured from OBN table, OBN field.
        -the value should be captured from Requirement Screen.
        -be aware of CUR, FEX, and other requriement of the field.
        -generate the java class only, dont show notes.
            <<SYS>>
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]java:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in model.generate_text(prompt):
        answer += response
    print(answer)
    return answer

raml_style = """#%RAML 1.0
title:
version:
baseUri:

/[servicename]:
  [get or post]:
    description: 
    queryParameters:
      [field name]:
        displayName:
        type:
        description:
        example: 
        required: 
        maxLength: 
        minLength:
    body:
      application/json:
        type: |
          {
              "type": "object",
              "$schema": "http://json-schema.org/draft-03/schema",
              "id": "http://jsonschema.net",
              "required": true,
              "properties": {
                "[field name]": {
                  "type": ,
                  "description": ,
                  "minLength": ,
                  "maxLength": ,
                },
                "[field name]": {
                  "type": "object",
                  "properties": {
                    "[property name]": {
                      "type": ,
                      "description": ,
                      "max": 
                      "min":
                    },
                    "[property name]": {
                      "type": ,
                      "description": ,
                    },
                    "[property name]": {
                      "type": ,
                      "description": ,
                      "maxLength": ,
                      "minLength": ,
                    },
                }
            }
        }
    }
    responses:
      [response code]:
        body:
          application/json:
            type: |
              {
                  "type": "object",
                  "$schema": "http://json-schema.org/draft-03/schema",
                  "id": "http://jsonschema.net",
                  "required": true,
                  "properties": {
                    "[property name]": {
                      "type": ,
                      "description": ,
                      "minLength": ,
                      "maxLength": 
                    },
                    "[property name]": {
                      "type": "object",
                      "properties": {
                        "[property name]": {
                          "type":  ,
                          "description": ,
                          "max": 
                        },
                        "[property name]": {
                          "type": ,
                          "description": 
                        },
                        "[property name]": {
                          "type": ,
                          "description": ,
                          "maxLength": ,
                          "minLength": 
                        },
                      }
                    }
                  }
              }"""

def generate_inquery_raml(model,dfinputinq,dfoutputinq):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate raml that implement the input and output requirement:
        -validate the datatype, length, mandatory/optional and other requriement of the field.
        -the value should be captured from OBN table, OBN field.
        -the value should be captured from Requirement Screen.
        -be aware of CUR, FEX, and other requriement of the field.
        -follow the raml style, replace the bracket name with coreponding name.
        -generate the raml only, dont show notes.
            <<SYS>>
            raml style: `{raml_style}`
            input(inq): `{dfinputinq.to_csv()[:3000]}`
            output(inq): `{dfoutputinq.to_csv()[:3000]}`
            <</SYS>>
            [/INST]raml:```"""
    # print("$$$$"+prompt)

    answer = keep_generate_till(model,prompt,"```")
    # print(answer)
    return answer

def generate_swagger(model,raml):
    prompt = f"""[INST]you are an expert on raml and swagger. please translate the raml to swagger.
            <<SYS>>
            raml: `{raml}`
            <</SYS>>
            [/INST]swagger json:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in model.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_process(model,dfprocessinq,dfprocessmaint,dfprocessvalidate):
    prompt = f"""[INST]<<SYS>>
process(inq): `{dfprocessinq.to_csv()[:3000]}`
process(maint): `{dfprocessmaint.to_csv()[:3000]}`
process(validate): `{dfprocessvalidate.to_csv()[:3000]}`
<</SYS>>
you are a system analyist with good knowledge of functional specification extracted from mainframe, \
please generate a java method that implement the high level process requirement:
-process(inq) is the high level process steps.
-process(maint) is the related maintenance steps.
-process(validate) is the related validate steps.
-for each high level process, generate a method.
-the method should include the steps mention in remarks.
-call common service with mentioned in remarks.
-add a comment line that show the remarks.
-dont miss the variable name mentioned in remarks. create the variable if not exist.
-for maintenance and validate, take care condition if any, insert neccessary maintenance and validate steps.
-for value mention in field "condition if any", do corresponding validation.
-the variable in format of (e.g. C101, C100) be screen.
-leverage related domains.
-generate the java class only
-dont show notes.
[/INST]java:```java"""
    # print("$$$$"+prompt)

    answer = keep_generate_till(model,prompt,"```")
    answer = answer.replace("```","")
    return answer

def generate_journalfunction(model,dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a java class that implement the journal requirement:
        -generate the java class only, dont show notes.
            <<SYS>>
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]java:```"""
    # print("$$$$"+prompt)
    answer = ""
    for response in model.generate_text(prompt):
        answer += response
    # print(answer)
    return answer

def generate_journalfunction_raml(model,dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate raml that implement the journal requirement:
        -follow the raml style, replace the bracket name with coreponding name.
        -generate the raml only, dont show notes.
            <<SYS>>
            raml style: `{raml_style}`
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]raml:```"""
    # print("$$$$"+prompt)
    answer = ""
    for response in model.generate_text(prompt):
        answer += response
    # print(answer)
    return answer

def generate_screenfunction(model,dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a java class that implement the screen requirement:
        -generate the java class only, dont show notes.
            <<SYS>>
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]java:```"""
    # print("$$$$"+prompt)
    answer = ""
    for response in model.generate_text(prompt):
        answer += response
    # print(answer)
    return answer

def generate_screenfunction_raml(model,dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate raml that implement the screen requirement:
        -follow the raml style, replace the bracket name with coreponding name.
        -generate raml only, dont show notes.
            <<SYS>>
            raml style: `{raml_style}`
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]raml:```"""
    # print("$$$$"+prompt)
    answer = ""
    for response in model.generate_text(prompt):
        answer += response
    # print(answer)
    return answer

def generate_factsheet(model, category, funcspec):

    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a factsheet that include essential information:
        -generate factsheet in json
        -the funcspec is about `{category}`.
        -generate the factsheet only, dont show notes.
            <<SYS>>
            funcspec: `{funcspec}`
            <</SYS>>
            [/INST]factsheet in json:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in model.generate_text(prompt):
        answer += response
    print(answer)
    return answer


def buildpromptforDDD(code):
    return f"""Assume you are an expert on java. The code below is in java. 
    Please re-write in the java language with DDD style, keeping the same logic. 

### java Code:
```{code}```

Please re-write the code above in java language with DDD style. 
- add function description with input/output
- add comment on complex logic block
- function name in pattern 'func_HSBC'+business+function name
- variable name in pattern 'var_'+business+variable name

### java code with DDD style:
```java"""

def buildpromptfordoc(code):
    return f"""[INST]
please generate documentation for the java source code in backquoted
<<SYS>>
`{code}`
<<SYS>>
[/INST]
documentation:"""

def buildpromptforconvertpseudocode(pseudocode):
    return f"""Assume you are an expert both in java. 
    The code below is in Pseudo Code. 
    Please re-write in the java language, keeping the same logic.
    ### Pseudo Code:
    ```{pseudocode}```

    Please re-write the code above in java language. 

    Here are the requirements:

    1. Indicate the parent class when you define a public class.
    2. The original code can be a snippet from complete code base. 
    3. If some classes are not provided in the given code snippet, import them from external packages. 
    4. Mark with comments if things may not be correct through direct conversion or things can be missing.
    5. Make sure the code concise, brief and elegant.
    6. Import java classes as few as possible. If necessary use ".*" to represent multiple classes.

    ### java code:
    ```java"""

def buildpromptfortestcase(code):
    return f"""[INST]
please generate testcase in junit for the java source code in backquoted
- test for all conditional case
- test for all possible output
- test for all possible input
- test for exception catching
<<SYS>>
`{code}`
<<SYS>>
[/INST]
testcase:"""

def buildpromptforconvert(code):
    return f"""Assume you are an expert both in COBOL and java. The code below is in COBOL. Please re-write in the java language, keeping the same logic. Replace functions from COBOL with the equivalent in java that makes the most sense. 

### COBOL Code:
```{code}```

Please re-write the code above in java language. 

Here are the requirements:

1. Indicate the parent class when you define a public class.
2. The original code can be a snippet from complete code base. 
3. If some classes are not provided in the given code snippet, import them from external packages. 
4. Mark with comments if things may not be correct through direct conversion or things can be missing.
5. Make sure the code concise, brief and elegant.
6. Import java classes as few as possible. If necessary use ".*" to represent multiple classes.

### java code:
```java"""

def buildpromptforexplaination(code):
    return f"""[INST]you are expert on COBOL programming,
please explain the programming logic for the COBOL source code in backquoted.
- the explaination should show the logic of the code.
- the explaination should be well structure, easy to understand.
- the explaination should be ready for modernize to java language.
<<SYS>>
`{code}`
<<SYS>>
[/INST]
explaination:"""

def generatejavawithstyle(model,javaclass,javastyle):
    prompt = f"""[INST]You are an expert in java. please rewrite the java class, that add the process code below as additional methods to the java class below.
    - align the naming, parameters and return types with the style of reference style provided.
    - add neccessary variable to the java class.
    - add comment before the method.
    <<SYS>>
    java class: `{javaclass}`
    java reference style: `{javastyle}`
    <</SYS>>
    [/INST]revised java class: ```java"""

    answer = keep_generate_till(model,prompt,"```")
    return answer