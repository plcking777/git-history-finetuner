import xml.etree.ElementTree as ET
import copy


class XMLComp():

    def compress(file_path: str, file_content: str, parsed_diff: dict):
        """
        TODO currently only using the added lines from the diff -> removed lines are ignored
        TODO weird issue with formatting looking weird (wrong amount of spaces)
        TODO remove namespace prefixes in the output
        """

        lines = file_content.split("\n")
        paths = []

        added_lines = parsed_diff[file_path]["added"]



        # if the first line is added just return the full file content
        if 1 in added_lines:
            return file_content

        for line_nr in added_lines:
            new_file_content = ""
            for idx in range(len(lines)):
                line = lines[idx]
                if idx + 1 == line_nr:
                    if XMLComp._is_line_in_element_def(file_content, line_nr):
                        pass  # TODO maybe add an attribute instead ?
                    else:
                        new_file_content += f"<findme findme=\"findme\" />" + "\n"
                new_file_content += line + "\n"


            try:
                root = ET.fromstring(new_file_content)
                found_path = XMLComp._tree_search_path(root, "findme")
            except:
                # if the ET.fromstring fails, the change probably did something "weird" like add a line outside of the root XML component
                # typically a comment => so it just ignored since it is too complex
                found_path = None

            if found_path != None:  # can be None if the findme is placed inside a comment -> but this can just be ignored since we are not intrested in comments
                paths.append(found_path)


        try:
            original_root = ET.fromstring(file_content)
        except:
            return file_content
        
        out = XMLComp._remove_non_path_els(original_root, paths)
        return XMLComp._ET_to_string(out)

        
    def _tree_search_path(root, target_tag):
        def helper(root: ET.Element, target_tag, acc: list):

            # get around the namespace prefix            
            if "findme" in root.attrib and root.attrib["findme"] == target_tag:
                return acc
            
            els = list(root)

            for idx in range(len(els)):
                new_acc = acc.copy()
                new_acc.append(idx)
                res = helper(root[idx], target_tag, new_acc)
                if res != None:
                    return res

            return None


        return helper(root, target_tag, [])
    

    def _remove_non_path_els(root, paths: list):
        def helper(root, new_root, paths, depth):
            to_remove = []
            for idx in range(len(list(root))):
                remove = True
                for path in paths:
                    if depth < len(path) and idx == path[depth]:
                            remove = False
                            break
                if remove:
                    to_remove.append(new_root[idx])
                else:
                    new_paths = [path for path in paths if depth < len(path) and idx == path[depth]]
                    helper(root[idx], new_root[idx], new_paths, depth + 1)

            for item in to_remove:
                new_root.remove(item)



        out = copy.deepcopy(root)
        helper(root, out, paths, 0)
        return out


    def _ET_to_string(element, indent="    "):

        def strip_ns(s):
            if '}' in s:
                return s.split('}')[-1]
            return s
        
        def helper(element, indent, depth=0):
            tag = strip_ns(element.tag)

            attribs = []
            for k, v in element.attrib.items():
                attribs.append(f' {strip_ns(k)}="{v}"')
            attrib_str = ''.join(attribs)
            
            open_scope_tag = f'<{tag}{attrib_str}>'
            close_scope_tag = f'</{tag}>'

            scope_content = []
            for child in element:
                scope_content.append(f'{indent * (depth + 1)}{helper(child, indent, depth + 1)}')
            
            if element.text and element.text.strip():
                scope_content.append(f'{indent * (depth + 1)}{element.text}')
            
            return f"{open_scope_tag}\n{''.join(scope_content)}\n{indent * depth}{close_scope_tag}"

        return helper(element, indent)


    def _is_line_in_element_def(file_content, line_nr):

        in_str_single = False  # '
        in_str_double = False  # "
        in_comment = False

        in_elem_def = False

        def is_sub_str_at(str, sub, idx):
            l = len(sub)

            if len(str) < idx + l:
                return False

            return str[idx:idx + l] == sub

        lines = file_content.split("\n")
        for line_idx in range(len(lines)):
            line = lines[line_idx]



            if line_idx + 1 == line_nr:
                return in_elem_def

            idx = 0
            while idx < len(line):
                
                c = line[idx]


                if c == "'" and not in_str_double and not in_comment:
                    in_str_single = not in_str_single
                
                elif c == '"' and not in_str_single and not in_comment:
                    in_str_double = not in_str_double
                

                elif is_sub_str_at(line, "<!--", idx) and not (in_str_single or in_str_double) and not in_comment:
                    idx += len("<!--")
                    in_comment = True
                    continue

                elif is_sub_str_at(line, "-->", idx) and not (in_str_single or in_str_double) and in_comment:
                    idx += len("-->")
                    in_comment = False
                    continue

                elif c == '<' and not (in_str_single or in_str_double) and not in_comment and not in_elem_def:
                    in_elem_def = True
                
                elif c == '>' and not (in_str_single or in_str_double) and not in_comment and in_elem_def:
                    in_elem_def = False
                

                idx += 1
        return False
        

    


                


