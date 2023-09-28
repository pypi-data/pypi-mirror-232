def get_jsonpath_by_key(obj, search_str, contains_string=True, dot_notation=False):
    path = []
    if isinstance(obj, list):
        if search_str in obj:
            try_val = None
            try:
                try_val = obj.index(search_str)
            except ValueError:
                try_val = None

            if try_val == None:
                return None

            path.append(f"[{try_val}]")

        else:
            for index in range(len(obj)):
                if isinstance(obj[index], (dict, list)):
                    new_path = get_jsonpath_by_key(
                        obj[index], search_str, contains_string, dot_notation
                    )
                    if new_path == None or len(new_path) == 0:
                        continue

                    for np in new_path:  # build path recursively backwards
                        if dot_notation:
                            path.append(f"[{index}]" + "." + np)
                        else:
                            if "[" not in np:
                                path.append(f"[{index}]['{np}']")
                            else:
                                path.append(f"[{index}]{np}")

                elif (str(search_str) in str(obj[index]) and contains_string) or (
                    str(search_str) == str(obj[index]) and not contains_string
                ):
                    if dot_notation:
                        path.append([f"[{index}]"])
                    else:
                        path.append(f"[{index}]")

    elif isinstance(obj, dict):
        new_path = None
        for key, value in obj.items():
            if isinstance(value, (list, dict)):
                new_path = get_jsonpath_by_key(
                    value, search_str, contains_string, dot_notation
                )
                if new_path == None or len(new_path) == 0:
                    continue

                for np in new_path:  # build path recursively backwards
                    if dot_notation:
                        if np[0] == "[":
                            path.append(key + np)
                        else:
                            path.append(key + "." + np)
                    else:
                        if "[" not in np:
                            path.append(f"['{key}']['{np}']")
                        else:
                            path.append(f"['{key}']{np}")

            elif (str(search_str) == str(value) and not contains_string) or (
                str(search_str) in str(value) and contains_string
            ):
                if dot_notation:
                    path.append(key)
                else:
                    path.append(f"['{key}']")

    if len(path) > 0:
        if isinstance(path, list):
            if isinstance(path[0], list) and len(path) == 1:
                return path[0]  # removes redundant inner list within list

        return path
    return None
