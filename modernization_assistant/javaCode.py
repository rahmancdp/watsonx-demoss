# __copyright__ = "Copyright (C) 2023 IBM Client Engineering US FSM Squad 12"
# __author__ = "Renate Hamrick, Boris Acha, and Ritu Patel"


import os
import re
import javalang

def read_java_files(root_folder):
    java_files = []
    for root, dirs, files in os.walk(root_folder):
        for file_name in files:
            if file_name.endswith('.java'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r') as file:
                    content = file.read()
                    # Process the file content as needed
                    java_files.append({
                        "file_path": file_path,
                        "content": content
                    })
    return java_files

def __get_start_end_for_node(node_to_find, tree):
    start = None
    end = None
    for path, node in tree:
        if start is not None and node_to_find not in path:
            end = node.position
            return start, end
        if start is None and node == node_to_find:
            start = node.position
    return start, end

def __get_string(start, end, data):
    if start is None:
        return ""
    end_pos = None
    if end is not None:
        end_pos = end.line - 1
    lines = data.splitlines(True)
    string = "".join(lines[start.line:end_pos])
    string = lines[start.line - 1] + string
    if end is None:
        left = string.count("{")
        right = string.count("}")
        if right - left == 1:
            p = string.rfind("}")
            string = string[:p]
    return string

def split_java_code(java_code):
  # print("java code: ", type(java_code), java_code)
  tree = javalang.parse.parse(java_code)
  methods_body = {}
  class_name = ''
  methods_info = []
  for _, node in tree.filter(javalang.tree.MethodDeclaration):
      start, end = __get_start_end_for_node(node, tree)
      methods_body[node.name] = __get_string(start, end,java_code )
      parameters = [param.type.name for param in node.parameters]
      return_type = node.return_type.name if node.return_type else "void"
      qualifier = ''
      for modifier in node.modifiers:
          if modifier == "private" or modifier == "public" or modifier == "protected":
              qualifier = modifier
      
      method_info = {
              "name": node.name,
              "return_type": return_type,
              "parameters": parameters,
              "qualifier": qualifier,
      }
      methods_info.append(method_info)
      
  
  for path, node in tree:
      if isinstance(node, javalang.tree.ClassDeclaration):
          class_name = node.name   
  
  for path, node in tree.filter(javalang.tree.ConstructorDeclaration):
      start, end = __get_start_end_for_node(node, tree)
      methods_body[node.name] = __get_string(start, end,java_code )

  java_methods_list = []
  for key in methods_body:
      java_methods_list.append(methods_body[key])
      

  return java_methods_list