import uuid

class Sentence():

    def __init__(self, value, parent):
        self.value = value
        self.parent = parent
        self.child_sentences = []
        self.id = uuid.uuid4()

    def add_child(self, sentence):

        if isinstance(sentence, Sentence):
            self.child_sentences.append(sentence)
        elif isinstance(sentence, str):
            self.child_sentences.append(Sentence(sentence, self))
        else:
            raise ValueError("Unexpected sentence type")

    def remove_child(self, sentence):
        self.child_sentences.remove(sentence)
        
    def get_all_deep(self):
        if len(self.child_sentences) == 0:
            return [self]
        out = [self]
        for sent in self.child_sentences:
            out.extend(sent.get_all_deep())
        return out

    def __repr__(self):
        out = ""
        if self.value != None:
            out = str(self.value)
        if self.child_sentences:
            for child_sentence in self.child_sentences:
                out += str(child_sentence)

        return out

    def __str__(self):
        return self.__repr__()

    def __eq__(self, obj):
        return self.value == obj.value and self.id == obj.id

    def __hash__(self):
        return hash(self.id)



class JavaComp():

    def compress(file_path: str, file_content: str, parsed_diff: dict):
        # TODO support for removed lines

        parsed, changed_paths = JavaComp._parse_java(file_content, parsed_diff[file_path]["added"])

        return JavaComp._remove_non_path_scopes(parsed, changed_paths)


    def _parse_java(file_content, changed_line):

        in_comment = False
        in_str = False
        in_assign = False
        open_params = 0

        current_sentece = ""

        root_sentence = Sentence(None, None)
        current_parent_sentence = root_sentence


        changed_sentence_paths = []
        current_path = []
        sentence_idx = -1
        current_sentence_is_changed = False
        
        def is_sub_str_at(str, sub, idx):
            l = len(sub)

            if len(str) < idx + l:
                return False

            return str[idx:idx + l] == sub

        def find_first_non_space(str):
            for idx in range(len(str)):
                c = str[idx]
                if c != " " and c != "\t":
                    return idx
                idx += 1

            return 0
        
        lines = file_content.split("\n")

        for line_idx in range(len(lines)):
            line = lines[line_idx]
            for idx in range(len(line)):

                if line_idx + 1 in changed_line:
                    current_sentence_is_changed = True
        
                c = line[idx]

                if not in_str and is_sub_str_at(line, "/*", idx):
                    in_comment = True
                if not in_str and is_sub_str_at(line, "*/", idx):
                    if not in_comment:
                        raise Exception("Found '*/' while not in a string or comment")
                    in_comment = False
                    break

                if not in_comment:

                    if c != "}" or in_str:
                        current_sentece += c

                    if c == "\"" or c ==  "'" and (idx == 0 or line[idx - 1] == "\\"):
                        in_str = not in_str
                        continue


                    if not in_str:

                        if is_sub_str_at(line, "//", idx):
                            break


                        if c == "{" and not in_assign and open_params == 0:
                            new_sentence = Sentence(current_sentece + "\n", current_parent_sentence)
                            current_parent_sentence.add_child(new_sentence)
                            current_parent_sentence = new_sentence

                            sentence_idx += 1
                            current_path.append(sentence_idx)
                            if current_sentence_is_changed:
                                full_path = []
                                full_path.extend(current_path)
                                changed_sentence_paths.append(full_path)
                                current_sentence_is_changed = False
                            sentence_idx = -1

                            current_sentece = ""
                        elif c == "}":
                            
                            if not in_assign and open_params == 0:

                                space_count = find_first_non_space(current_parent_sentence.value)
                                spaces = ""
                                for _ in range(space_count):
                                    spaces += " "

                                current_parent_sentence.add_child(spaces + "}\n")  # note it is still included in the parent sentence
                                current_parent_sentence = current_parent_sentence.parent
                            
                                sentence_idx += 1
                                if current_sentence_is_changed:
                                    full_path = []
                                    full_path.extend(current_path)
                                    full_path.append(sentence_idx)
                                    changed_sentence_paths.append(full_path)
                                    current_sentence_is_changed = False
                                
                                sentence_idx = current_path.pop()
                            
                            else:
                                current_sentece += c

                        elif c == ";":
                            in_assign = False
                            open_params = 0

                            current_parent_sentence.add_child(current_sentece + "\n")
                            current_sentece = ""

                            sentence_idx += 1

                            if current_sentence_is_changed:
                                full_path = []
                                full_path.extend(current_path)
                                full_path.append(sentence_idx)
                                changed_sentence_paths.append(full_path)
                                current_sentence_is_changed = False

                        elif open_params == 0 and c == "=" and not is_sub_str_at(line, "==", idx) and not is_sub_str_at(line, "==", idx - 1):
                            in_assign = True
                        
                        elif c == "(":
                            open_params += 1

                        elif c == ")":
                            in_assign = False
                            open_params -= 1
                            
            if len(current_sentece) > 0 and current_sentece[-1] != "\n":
                current_sentece += "\n"


        return root_sentence, changed_sentence_paths



    def _remove_non_path_scopes(root: Sentence, paths: list):
        can_be_removed = dict()
        for sent in root.get_all_deep():
            can_be_removed[sent] = True

        for path in paths:
            prev_node = root
            can_be_removed[root] = False
            for path_idx in range(len(path)):
                idx = path[path_idx]
                prev_node = prev_node.child_sentences[idx]
                can_be_removed[prev_node] = False

                # if in a scope, make sure to also not remove the closing scope sentence
                if len(prev_node.child_sentences) > 0:
                    closing_scope = prev_node.child_sentences[-1]
                    can_be_removed[closing_scope] = False
                


        def recursive_remove(root, can_be_removed, depth=0):
            MAX_DEPTH = 2
            if root.child_sentences == None:
                return
            
            done = False
            while not done:
                done = True
                for node in root.child_sentences:
                    if can_be_removed[node]:
                        root.remove_child(node)
                        done = False
                        break
                    elif depth + 1 < MAX_DEPTH:
                        recursive_remove(node, can_be_removed, depth + 1)

        recursive_remove(root, can_be_removed)
        




        return root