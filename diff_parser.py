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
    
    def __init__(self, repo, prev_hash, diff):
        self.repo = repo
        self.prev_hash = prev_hash
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

        out = dict()

        lines = self.diff.split("\n")



        for file in self.files:
            try:
                original_file = get_file_on_hash(self.repo, self.prev_hash, file)
            except subprocess.CalledProcessError:
                # file does not exist on this hash
                # => meaning it is new
                original_file = ""
            
            diff_idx = get_diff_idx_for_file(lines, file)
            print(parse_line_info(lines[diff_idx]))


        return out



    def _discover_changed_files(self, diff):
        out = set()

        # check for all lines that start with "+++ " or "--- "
        pattern = r'^(---|\+\+\+)\s.*$'


        lines = diff.split("\n")

        for line in lines:
            match = re.match(pattern, line)
            if match:
                file_path = line[6:]  # removes the "+++ a/" from the path
                if line[5:] != "dev/null":  # make sure the file is not a removed file
                    out.add(file_path)

        return out
