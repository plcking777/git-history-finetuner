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

        for line_nr in parsed_diff[file_path]["added"]:
            new_file_content = ""
            for idx in range(len(lines)):
                line = lines[idx]
                if idx + 1 == line_nr:
                    new_file_content += f"<findme findme=\"findme\" />" + "\n"
                new_file_content += line + "\n"

            root = ET.fromstring(new_file_content)
            paths.append(XMLComp._tree_search_path(root, "findme"))


        original_root = ET.fromstring(file_content)

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
