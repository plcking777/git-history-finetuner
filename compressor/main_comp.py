from compressor.language.text_comp import TextComp


class MainComp():

    def compress(file_path: str, file_content: str, parsed_diff: dict):
        
        if file_path.endswith(".java"):
            raise NotImplementedError("Java compress is not implemented")
        elif file_path.endswith(".xml"):
            raise NotImplementedError("XML compress is not implemented")
        else:
            return TextComp.compress(file_path, file_content, parsed_diff)