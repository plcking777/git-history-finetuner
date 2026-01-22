
class Sentence():

    def __init__(self, value, parent):
        self.value = value
        self.parent = parent
        self.child_sentences = None

    def add_child(self, sentence):
        if self.child_sentences == None:
            self.child_sentences = [sentence]
        else:
            self.child_sentences.append(sentence)

    def find(self, obj):
        pass  # TODO

    def __repr__(self):
        out = str(self.value)
        if self.child_sentences:
            for child_sentence in self.child_sentences:
                out += "-" + str(child_sentence)

        return out

    def __str__(self):
        return self.__repr__()





class JavaComp():

    def compress(file_path: str, file_content: str, parsed_diff: dict):
        pass
    


    def parse_java(file_content):

        in_comment = False  # TODO: to be implemented
        in_str = False
        current_sentece = ""

        root_sentence = Sentence(None, None)
        current_parent_sentence = root_sentence



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

        for line in lines:
            for idx in range(len(line)):

                
                """ TODO
                if idx in changed_line:
                    pass
                """

        
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

                            current_sentece = ""
                        elif c == "}":

                            space_count = find_first_non_space(current_parent_sentence.value)
                            spaces = ""
                            for _ in range(space_count):
                                spaces += " "

                            current_parent_sentence.add_child(spaces + "}\n")  # note it is still included in the parent sentence
                            current_parent_sentence = current_parent_sentence.parent

                        elif c == ";":
                            current_parent_sentence.add_child(current_sentece + "\n")
                            current_sentece = ""
                            
            if len(current_sentece) > 0 and current_sentece[-1] != "\n":
                current_sentece += "\n"


        return root_sentence

