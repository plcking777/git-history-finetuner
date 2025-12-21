import re


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




class DiffParser():
    """
    Class used for getting useful information from a git diff string:
    - changed files
    - changed lines of code:
        - added lines
        - removed lines
    """
    
    def __init__(self, diff):
        self.diff = diff
        self.files = self._discover_changed_files(diff)


    def parse(self, diff):
        raise NotImplementedError("parse")
    


    def _discover_changed_files(self, diff):
        out = set()

        # check for all lines that start with "+++ " or "--- "
        pattern = r'^(---|\+\+\+)\s.*$'


        lines = diff.split("\n")

        for line in lines:
            match = re.match(pattern, line)
            if match:
                file_path = line[6:]  # removes the "+++ a/" from the path
                out.add(file_path)

        return out
