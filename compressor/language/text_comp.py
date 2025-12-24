
class TextComp():

    def compress(file_path: str, file_content: str, parsed_diff: dict):
        out = ""
        for line_nr in parsed_diff[file_path]["added"]:
            out += file_content.split("\n")[line_nr - 1] + "\n"

        return out