import re
from utils import *


"""
diff --git ...
index ...
--- a/{file1_path}
+++ b/{file1_path}
@@ -{line_nr},{?} +{line_nr},{?} @@
 some_line
 some_line
-removed_line
+added_line
 some_line


"""



class DiffInfo():
    def __init__(self, prev_line_nr, current_line_nr):
        self.prev_line_nr = prev_line_nr
        self.current_line_nr = current_line_nr
    
    def __repr__(self):
        return f"DiffInfo({self.prev_line_nr}, {self.current_line_nr})"

class DiffParser():
    """
    Class used for getting useful information from a git diff string:
    - changed files
    - changed lines of code:
        - added lines
        - removed lines
    """
    
    def __init__(self, repo, diff):
        self.repo = repo
        self.diff = diff
        self.files = self._discover_changed_files(diff)


    def parse(self):

        def get_diff_idx_for_file(diff_lines, file):
            for idx in range(len(diff_lines)):
                line = diff_lines[idx]
                if re.match(f"---\s.\/{file}", line):
                    return idx + 2
                elif re.match(f"\+\+\+\s.\/{file}", line):
                    return idx + 1
            return None
        
        def parse_line_info(line):
            """
            Parses the `@@ -{prev_line_nr},{?} +{current_line_nr},{?} @@` line
            """
            prev_line_nr = ""
            current_line_nr = ""

            idx = 0
            read_prev = False
            read_current = False
            while idx < len(line):
                c = line[idx]

                if read_current:
                    if c == ',':
                        break
                    else:
                        current_line_nr += c

                if read_prev:
                    if c == ',':
                        read_prev = False
                    else:
                        prev_line_nr += c
                elif prev_line_nr != "" and c == '+':
                    read_current = True

                if idx + 4 < len(line) and line[idx:idx + 4] == "@@ -":
                    idx += 4
                    read_prev = True
                    continue
                idx += 1

            return DiffInfo(int(prev_line_nr), int(current_line_nr))



        def find_changed_lines(diff_lines, start_idx):
            out = dict()
            out["added"] = []
            out["removed"] = []

            parse_info = parse_line_info(lines[start_idx])
            line_count = parse_info.current_line_nr

            idx = start_idx + 1

            removedLines = False
            
            while idx < len(diff_lines):
                line = diff_lines[idx]

                if len(line) == 0:
                    idx += 1
                    continue
                op = line[0]


                if line[0:2] == "@@":
                    parse_info = parse_line_info(lines[idx])
                    if removedLines:
                        removedLines = False
                        out["removed"].append((line_count - 1, line_count))
                    line_count = parse_info.current_line_nr
                    idx += 1
                    continue
                elif op != " " and op != "-" and op != "+":
                    break

                if op == " ":
                    if removedLines:
                        removedLines = False
                        out["removed"].append((line_count - 1, line_count))
                    line_count += 1
                elif op == "-":
                    removedLines = True
                    pass
                elif op == "+":
                    out["added"].append(line_count)
                    if removedLines:
                        removedLines = False
                        out["removed"].append((line_count - 1, line_count))
                    line_count += 1

                idx += 1


            return out


        out = dict()

        lines = self.diff.split("\n")



        for file in self.files:
            diff_idx = get_diff_idx_for_file(lines, file)
            out[file] = find_changed_lines(lines, diff_idx)


        return out



    def _discover_changed_files(self, diff):
        out = set()

        # check for all lines that start with "+++ " or "--- "
        #pattern = r'^(---|\+\+\+)\s.*$'
        pattern = r'^(\+\+\+)\s.*$'


        lines = diff.split("\n")

        for line in lines:
            match = re.match(pattern, line)
            if match:
                file_path = line[6:]  # removes the "+++ a/" from the path
                if line[5:] != "dev/null":  # make sure the file is not a removed file
                    out.add(file_path)

        return out


