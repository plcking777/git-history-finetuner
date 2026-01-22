from compressor.language.java_comp import JavaComp
from compressor.language.text_comp import TextComp
from compressor.language.xml_comp import XMLComp


class MainComp():

    def compress(file_path: str, file_content: str, parsed_diff: dict):
        
        if file_path.endswith(".java"):
            return JavaComp.compress(file_path, file_content, parsed_diff)
        elif file_path.endswith(".xml"):
            return XMLComp.compress(file_path, file_content, parsed_diff)
        else:
            return TextComp.compress(file_path, file_content, parsed_diff)