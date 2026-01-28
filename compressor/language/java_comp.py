import uuid

class Sentence():

    def __init__(self, value, parent):
        self.value = value
        self.parent = parent
        self.child_sentences = None
        self.id = uuid.uuid4()

    def add_child(self, sentence):

        if isinstance(sentence, Sentence):
            if self.child_sentences == None:
                self.child_sentences = [sentence]
            else:
                self.child_sentences.append(sentence)
        elif isinstance(sentence, str):
            if self.child_sentences == None:
                self.child_sentences = [Sentence(sentence, self)]
            else:
                self.child_sentences.append(Sentence(sentence, self))
        else:
            raise ValueError("Unexpected sentence type")

    def remove_child(self, sentence):
        self.child_sentences.remove(sentence)
        
    def get_all_deep(self):
        if self.child_sentences == None or len(self.child_sentences) == 0:
            return [self]
        out = [self]
        for sent in self.child_sentences:
            out.extend(sent.get_all_deep())
        return out

    def __repr__(self):
        out = str(self.value)
        if self.child_sentences:
            for child_sentence in self.child_sentences:
                out += "-" + str(child_sentence)

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

        in_comment = False  # TODO: to be implemented
        in_str = False
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

                    if c == "\"" or c ==  "'":
                        in_str = not in_str
                        continue


                    if not in_str:
                        if c == "{":
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
                            

                        elif c == ";":
                            current_parent_sentence.add_child(current_sentece + "\n")
                            current_sentece = ""

                            sentence_idx += 1

                            if current_sentence_is_changed:
                                full_path = []
                                full_path.extend(current_path)
                                full_path.append(sentence_idx)
                                changed_sentence_paths.append(full_path)
                                current_sentence_is_changed = False

                            
            if len(current_sentece) > 0 and current_sentece[-1] != "\n":
                current_sentece += "\n"


        return root_sentence, changed_sentence_paths



    def _remove_non_path_scopes(root, paths: list):
        can_be_removed = dict()
        for sent in root.get_all_deep():
            can_be_removed[sent] = True
        
        for path in paths:
            prev_node = root
            can_be_removed[root] = False
            for idx in path:
                prev_node = prev_node.child_sentences[idx]
                can_be_removed[prev_node] = False
        
        def recursive_remove(root, can_be_removed):
            if root.child_sentences == None:
                return
            
            for node in root.child_sentences:
                if can_be_removed[node]:
                    root.remove_child(node)
                else:
                    recursive_remove(node, can_be_removed)

        recursive_remove(root, can_be_removed)

        return root