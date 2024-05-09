import json

def keep_generate_till(model,prompt,endstring):
    lastanswer = ""
    while not lastanswer.endswith(endstring):
        answer = ""
        for chunk in model.generate_text(f"{prompt}{lastanswer}"):
            answer += chunk
        lastanswer += answer
    return lastanswer

def generate_process(model, pseudocodes, domain):
    prompts = []
    print(f"total pseudocode: {len(pseudocodes)}")
    for pseudocode in pseudocodes:
        prompt = f"""[INST]<<SYS>>
                domain: `{domain}`
                pseudo code: `{pseudocode}`
                Mandatory/Optional: `M,O`
                summary format: `{{
                    "Process(Inq)": [],
                    "Process(Maint)": [],
                    "Process(Validate)": [],
                }}`
                -for each Process(Inq) high level process identified, provide the programming logic. generate each process step one by one in layout of:
                {{
                    "High level process": "",
                    "Remarks": ""
                }},
                {{
                    "High level process": "",
                    "Remarks": ""
                }}
                -for each Process(Maint), Process(Validate) process identified, provide the programming logic. generate each process step one by one in layout of:
                {{
                    "Process": "",
                    "Description": "",
                    "Condition if any": "",
                    "Remarks": "",
                    "Related domain": ""
                }},
                {{
                    "Process": "",
                    "Description": "",
                    "Condition if any": "",
                    "Remarks": "",
                    "Related domain": ""
                }}
                <</SYS>>
                you be expert on banking system. please summarize the psudo code in backquoted:
            -read into the pseudo code in detail.
            -identify potential service in the pseudo code.
            -for the field Data Type, only use the data type provided in following list: `Account Num,CCY,String,Count,Date,Indicator,Seq/Tier Num,Array,Integer,Code,Count`
            -refer to the domain provided.
            -follow the high level summary format.
                [/INST]summary json:```vbnet"""

    answer = keep_generate_till(model,prompt,'```')
    return [answer]

def generate_input_output(model, pseudocodes, domain):
    prompts = []
    print(f"total pseudocode: {len(pseudocodes)}")
    for pseudocode in pseudocodes:
        prompt = f"""[INST]<<SYS>>
                domain: `{domain}`
                pseudo code: `{pseudocode}`
                Mandatory/Optional: `M,O`
                summary format: `{{
                    "Input(Inq)": [],
                    "Output(Inq)": [],
                    "Input(Maint)": [],
                    "Journal Conversion": [],
                    "C101": [],
                    "C102": [],
                }}`
                -for each Input(Inq), Input(Maint) identified, describe the purpose, format and potential data source. generate each input one by one in layout of:
                {{
                    "Field Description": "",
                    "Data Type": "",
                    "Length": "",
                    "Mandatory/optional": "",
                    "Sample": "",
                    "Remarks": ""
                }},
                {{
                    "Field Description": "",
                    "Data Type": "",
                    "Length": "",
                    "Mandatory/optional": "",
                    "Sample": "",
                    "Remarks": ""
                }}
                -for each Output(Inq) identified, describe the purpose, format and potential usage. generate each output one by one in layout of:
                {{
                    "Description": "",
                    "DataType": "",
                    "Length": "",
                    "OBN Table": "",
                    "OBN field": "",
                    "Required Screen": "",
                    "CUR": "",
                    "FEX": ""
                }},
                {{
                    "Description": "",
                    "DataType": "",
                    "Length": "",
                    "OBN Table": "",
                    "OBN field": "",
                    "Required Screen": "",
                    "CUR": "",
                    "FEX": ""
                }}
                -for each "Journal Conversion" identified, describe the purpose, format and potential usage. generate each one by one in layout of:
                {{
                    "OBN Journal": "",
                    "Input Field": "",
                    "Input Field Format": "",
                    "Remarks": ""
                }}
                -for each Screen (e.g. C101, C102) identified, describe the purpose, format and potential usage. generate each one by one in layout of:
                {{
                    "Field Name from Service": "",
                    "OBN Journal": "",
                    "Format": "",
                    "Value": ""
                }}
                <</SYS>>
                you be expert on banking system. please summarize the psudo code in backquoted:
            -read into the pseudo code in detail.
            -identify potential service in the pseudo code.
            -for the field Data Type, only use the data type provided in following list: `Account Num,CCY,String,Count,Date,Indicator,Seq/Tier Num,Array,Integer,Code,Count`
            -refer to the domain provided.
            -follow the high level summary format.
                [/INST]summary json:```vbnet"""
        
    answer = keep_generate_till(model,prompt,'```')
    return [answer]

def generate_funcspec(model, pseudocodes, domain):
    prompts = []
    print(f"total pseudocode: {len(pseudocodes)}")
    for pseudocode in pseudocodes:
        prompt = f"""[INST]<<SYS>>
                domain: `{domain}`
                pseudo code: `{pseudocode}`
                Mandatory/Optional: `M,O`
                summary format: `{{
                    "Input(Inq)": [],
                    "Output(Inq)": [],
                    "Process(Inq)": [],
                    "Input(Maint)": [],
                    "Process(Maint)": [],
                    "Process(Validate)": [],
                    "Journal Conversion": [],
                    "C101": [],
                    "C102": [],
                }}`
                -for each Input(Inq), Input(Maint) need to get external input identified, describe the purpose, format and potential data source. generate each input one by one in layout of:
                {{
                    "Field Description": "",
                    "Data Type": "",
                    "Length": "",
                    "Mandatory/optional": "",
                    "Sample": "",
                    "Remarks": ""
                }},
                {{
                    "Field Description": "",
                    "Data Type": "",
                    "Length": "",
                    "Mandatory/optional": "",
                    "Sample": "",
                    "Remarks": ""
                }}
                -for each Output(Inq) need to send to external identified, describe the purpose, format and potential usage. generate each output one by one in layout of:
                {{
                    "Description": "",
                    "DataType": "",
                    "Length": "",
                    "OBN Table": "",
                    "OBN field": "",
                    "Required Screen": "",
                    "CUR": "",
                    "FEX": ""
                }},
                {{
                    "Description": "",
                    "DataType": "",
                    "Length": "",
                    "OBN Table": "",
                    "OBN field": "",
                    "Required Screen": "",
                    "CUR": "",
                    "FEX": ""
                }}
                -for each Process(Inq), Process(Maint), Process(Validate) high level process identified, provide the programming logic. generate each process step one by one in layout of:
                {{
                    "High level process": "",
                    "Remarks": ""
                }},
                {{
                    "High level process": "",
                    "Remarks": ""
                }}
                -for each "Journal Conversion" identified, describe the purpose, format and potential usage. generate each one by one in layout of:
                {{
                    "OBN Journal": "",
                    "Input Field": "",
                    "Input Field Format": "",
                    "Remarks": ""
                }}
                -for each Screen (e.g. C101, C102) identified, describe the purpose, format and potential usage. generate each one by one in layout of:
                {{
                    "Field Name from Service": "",
                    "OBN Journal": "",
                    "Format": "",
                    "Value": ""
                }}
                <</SYS>>
                you be expert on banking system. please summarize the psudo code in backquoted:
            -read into the pseudo code in detail.
            -identify potential service in the pseudo code.
            -for the field Data Type, only use the data type provided in following list: `Account Num,CCY,String,Count,Date,Indicator,Seq/Tier Num,Array,Integer,Code,Count`
            -refer to the domain provided.
            -follow the high level summary format.
                [/INST]summary json:```vbnet"""

    answer = keep_generate_till(model,prompt,'```')
    return [answer]

def generate_funcspec_json(model, pseudocodes,domain):
    prompts = []
    for pseudocode in pseudocodes:
        prompt = f"""[INST]you be expert on banking system. please summarize the psudo code in backquoted:
            -read into the pseudo code in detail.
            -identify potential service in the pseudo code.
            -for each input identified, describe the purpose, format and potential data source.
            -for each output identified, describe the purpose, format and potential usage.
            -summarize the pseudo code as process, group into inquiry, maintenance, validate.
            -for each journal conversion identified, describe the purpose, format and potential data source.
            -for each screen (e.g. C101, C102), describe the field purpose, format and potential data source.
            -refer to the domain provided.
            -all field value should be quote unless it is numeric.
            -double quote for all field value.
            -remove trailing comma
            -dont add extra space.
            -end generation with ```
                <<SYS>>
                pseudo code: `{pseudocode}`
                domain: `{domain}`
                summary format: `{{
                    "Input(Inq)": [
                        {{
                            "Field Description": "",
                            "Data Type": "",
                            "Length": "",
                            "Mandatory or optional": "",
                            "Sample": "",
                            "Remarks": ""
                        }}
                    ],
                    "Output(Inq)": [
                    {{
                            "Description": "",
                            "DataType": "",
                            "Length": "",
                            "OBN Table": "",
                            "OBN field": "",
                            "Required Screen": "",
                            "CUR": "",
                            "FEX": ""
                        }}
                    ],
                    "Process(Inq)": [
                        {{
                            "High level process": "",
                            "Remarks": ""
                        }}
                    ],
                    "Input(Maint)": [
                        {{
                            "Description": "",
                            "Data Type": "",
                            "Length": "",
                            "Mandatory or optional": "",
                            "Sample": "",
                            "Remarks": "",
                            "Required Screen": "",
                            "OBN Table": "",
                            "OBN field": "",
                            "CUR": "",
                            "FEX": ""
                        }}
                    ],
                    "Process(Maint)": [
                        {{
                            "High level process": "",
                            "Remarks": "",
                            "Condition if any": "",
                            "Related Domain": ""
                        }}
                    ],
                    "Process(Validate)": [
                        {{
                            "High level process": "",
                            "Remarks": "",
                            "Condition if any": "",
                            "Related Domain": ""
                        }}
                    ],
                    "Journal Conversion": [
                        {{
                            "OBN Journal": "",
                            "Input Field": "",
                            "Input Field Format": "",
                            "Remarks": ""
                        }}
                    ],
                    "C101": [
                        {{
                            "Field Name from Service": "",
                            "OBN Journal": "",
                            "Format": "",
                            "Value": ""
                        }}
                    ],
                    "C102": [
                        {{
                            "Field Name from Service": "",
                            "OBN Journal": "",
                            "Format": "",
                            "Value": ""
                        }}
                    ],
                }}`
                <</SYS>>
                [/INST]summary json:```"""
        # print("$$$$"+prompt)
        prompts.append(prompt)
    answer = ""
    for response in model.generate_text(prompts):
        answer += response
        # print(f"{len(answers)}/{len(prompts)}")
    print(answer)
    return [answer]

import pandas as pd

def save_to_excel_multiple(filepath, 
                           dfinputinq, 
                           dfoutputinq, 
                           dfprocessinq, 
                           dfinputmaint, 
                           dfprocessmaint, 
                           dfprocessvalidate, 
                           dfjournalconversion, 
                           dfc101, 
                           dfc102):
    # Assuming you have three DataFrames: input_df, output_df, process_df

    # Create an ExcelWriter object and specify the output file name
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')

    # Write each DataFrame to a separate sheet in the Excel file
    dfinputinq.to_excel(writer, sheet_name='Input(Inq)', index=False)
    dfoutputinq.to_excel(writer, sheet_name='Output(Inq)', index=False)
    dfprocessinq.to_excel(writer, sheet_name='Process(Inq)', index=False)
    dfinputmaint.to_excel(writer, sheet_name='Input(Maint)', index=False)
    dfprocessmaint.to_excel(writer, sheet_name='Process(Maint)', index=False)
    dfprocessvalidate.to_excel(writer, sheet_name='Process(Validate)', index=False)
    dfjournalconversion.to_excel(writer, sheet_name='Journal Conversion', index=False)
    dfc101.to_excel(writer, sheet_name='C101', index=False)
    dfc102.to_excel(writer, sheet_name='C102', index=False)

    # Save the Excel file
    writer.close()