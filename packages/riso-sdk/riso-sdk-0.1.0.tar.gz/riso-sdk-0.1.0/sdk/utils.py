from diff_match_patch import diff_match_patch


def get_field_diff(old_value, new_value):
    dmp = diff_match_patch()
    diffs = dmp.diff_main(old_value, new_value)
    dmp.diff_cleanupSemantic(diffs)
    return dmp.diff_prettyHtml(diffs)


def make_diffs(old_json, new_json, key_verbose_name={}):  # noqa
    diffs = []
    for key in old_json:
        if key not in new_json:
            diffs.append(
                {
                    "key": key,
                    "old_value": old_json[key],
                    "short_description": "<strong>{}</strong> has been removed from the object".format(
                        key_verbose_name.get(key, key).title()
                    ),
                    "description": f"<span><del style='background:#ffe6e6;'>{old_json[key]}</del></span>",
                }
            )
        elif old_json[key] != new_json[key]:
            if str(old_json[key]).isdigit() and str(new_json[key]).isdigit():
                diffs.append(
                    {
                        "key": key,
                        "old_value": old_json[key],
                        "new_value": new_json[key],
                        "short_description": "<strong>{}</strong> has changed".format(
                            key_verbose_name.get(key, key).title()
                        ),
                        "description": (
                            "<span>from <del style='background:#ffe6e6;'>{}</del> to "
                            "<ins style='background:#e6ffe6;'>{}</ins>.</span>".format(old_json[key], new_json[key])
                        ),
                    }
                )
            elif isinstance(old_json[key], str) and isinstance(new_json[key], str):
                diffs.append(
                    {
                        "key": key,
                        "old_value": old_json[key],
                        "new_value": new_json[key],
                        "short_description": "<strong>{}</strong> has changed".format(
                            key_verbose_name.get(key, key).title()
                        ),
                        "description": (
                            "<span>from <del style='background:#ffe6e6;'>{}</del> to "
                            "<ins style='background:#e6ffe6;'>{}</ins>.</span>".format(old_json[key], new_json[key])
                        ),
                    }
                )
            elif isinstance(old_json[key], list) and isinstance(new_json[key], list):
                added_items = set(new_json[key]) - set(old_json[key])
                removed_items = set(old_json[key]) - set(new_json[key])
                for added_item in added_items:
                    diffs.append(
                        {
                            "key": key,
                            "new_value": added_item,
                            "short_description": "<strong>{}</strong> added an item".format(
                                key_verbose_name.get(key, key).title()
                            ),
                            "description": f"<span><ins style='background:#e6ffe6;'>{added_item}</ins></span>",
                        }
                    )
                for removed_item in removed_items:
                    diffs.append(
                        {
                            "key": key,
                            "old_value": removed_item,
                            "short_description": "<strong>{}</strong> removed item".format(
                                key_verbose_name.get(key, key).title()
                            ),
                            "description": f"<span><del style='background:#ffe6e6;'>{removed_item}</del></span>",
                        }
                    )
            else:
                diffs.append(
                    {
                        "key": key,
                        "old_value": old_json[key],
                        "new_value": new_json[key],
                        "short_description": "<strong>{}</strong> has changed".format(
                            key_verbose_name.get(key, key).title()
                        ),
                        "description": "<span>Cannot display diff for this value</span>",
                    }
                )
    for key in new_json:
        if key not in old_json:
            diffs.append(
                {
                    "key": key,
                    "new_value": new_json[key],
                    "short_description": "<strong>{}</strong> has been added to the object".format(
                        key_verbose_name.get(key, key).title()
                    ),
                    "description": f"<span><ins style='background:#e6ffe6;'>{new_json[key]}</ins></span>",
                }
            )
    return diffs


def field_verbose_name(model):
    field_verbose_name_dict = {}
    for field in model._meta.get_fields():  # noqa
        try:
            field_verbose_name_dict[field.name] = field.verbose_name
        except AttributeError:  # pragma: no cover
            pass
    return field_verbose_name_dict
