# __copyright__ = "Copyright (C) 2023 IBM Client Engineering US FSM Squad 12"
# __author__ = "Renate Hamrick, Boris Acha, and Ritu Patel"


import re

def split_off_procedure(file_content):
    # Convert both the search string and file content to uppercase for case-insensitive matching
    search_string = "PROCEDURE DIVISION"
    index = file_content.upper().find(search_string.upper())
    
    if index != -1:
        # Adjust the slicing to go back 6 characters before the found index
        before_procedure_division = file_content[max(0, index - 6):index]
        after_procedure_division = file_content[index - 6:]
        
        # You can return the variables if needed
        return after_procedure_division
    else:
        return None, None

def process_cobol_file(file_content):
    lines = file_content.splitlines()
    output = []
    eject_flag = False

    for row in lines:
        row = row[6:72].rstrip()
        if row == "" or row[0] in ('*', '/'):
            continue
        if "EJECT" in row:
            eject_flag = True

        # Append the processed row to the output without joining it
        output.append(row)
        if row[-1] == "." and not eject_flag and (len(row) == 1 or row[-2] == ' '):
            # If it's the end of a sentence with a space before the period, reset eject_flag
            eject_flag = False
        elif eject_flag and "EJECT" in row:
            # If it's an EJECT statement, reset eject_flag
            eject_flag = False
    return output

def split_cbl_code(content):
    cobol_chunks = []
    current_chunk = ""
    try:
        for line in content:
            if " EXIT." in line or "EJECT" in line:
                # If yes, consider it as the end of the current chunk
                current_chunk += line + '\n'
                if len(current_chunk)>3000:
                    #when the current chunk is more then 3000 characters send it to be split to smaller chunks
                    smaller_chunks=split_smaller(current_chunk)
                    #now add that list of smaller chunks and only that to the cobol_chunks list and because each of those elements are now below 3000 characters they should not come back to this section of the loop
                    cobol_chunks.extend(smaller_chunks)
                    current_chunk = ""  # Reset the current chunk for the next iteration
                else:
                    cobol_chunks.append(current_chunk)  # Append the chunk to the list
                    current_chunk = ""  # Reset the current chunk for the next iteration
            else:
                current_chunk += line + '\n'

        if current_chunk:
            cobol_chunks.append(current_chunk)  # Append the last chunk if any

    except Exception as e:
        print(f"Error in split_cbl_code: {e}")

    return cobol_chunks

#split up the large chunks into chunks that are under 3000 characters, making sure to split at a period, but if the chunk is still over 3000 because there is no period split at the word else/ELSE. Then add to the first line of that list of chunks: SPLIT index of length. Return that list
def split_smaller(large_chunk):
    result_chunks = []
    current_chunk = ""
    split_index = 1  # Initialize the split index

    # Split the large chunk at a period
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', large_chunk)
   
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < 3000:
            current_chunk += sentence + '\n'
        else:
            # If the chunk still exceeds 6000 characters, split before the word else/ELSE
            if 'else' in sentence.lower():
                # Split before the word else/ELSE
                chunks = re.split(r'(?i)\belse\b', sentence)
                for chunk in chunks:
                    if len(current_chunk) + len(chunk) < 3000:
                        current_chunk += chunk + '\n'
                    else:
                        # Assemble chunks within the 3000-character limit
                        result_chunks.append(current_chunk)
                        current_chunk = chunk + '\n'
                        split_index += 1
                # Reset current_chunk after processing inner loop
                current_chunk = ""
            else:
                # Assemble chunks within the 3000-character limit
                result_chunks.append(current_chunk)
                current_chunk = sentence + '\n'
                split_index += 1

    # Add the last chunk if any
    if current_chunk:
        result_chunks.append(current_chunk)

    # Add the words "SPLIT" (index of chunk) "of" (length of list of chunks) to each element of the list of chunks
    result_chunks = [f"SPLIT {index} OF {len(result_chunks)}{block} " for index, block in enumerate(result_chunks, start=1)]


    return result_chunks
