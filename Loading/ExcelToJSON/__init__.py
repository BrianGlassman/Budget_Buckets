def is_json_stale(script_path: str, json_path: str, tag: str = ''):
    """Returns True if the JSON is older than the Excel file or conversion script, False if it's newer"""
    import datetime
    import os
    from BaseLib.logger import delegate_print as print
    from Loading.OpenExcel import excel_path

    excel_mtime = os.path.getmtime(excel_path)
    script_mtime = os.path.getmtime(script_path)
    json_mtime = os.path.getmtime(json_path)

    if (excel_diff := excel_mtime - json_mtime) > 0:
        diff = datetime.timedelta(seconds=excel_diff)
        print(f"{tag.capitalize()} JSON behind Excel by {diff}.")
        return True
    if (script_diff := script_mtime - json_mtime) > 0:
        diff = datetime.timedelta(seconds=script_diff)
        print(f"{tag.capitalize()} JSON behind script by {diff}.")
        return True
    else:
        print(f"{tag.capitalize()} JSON from {datetime.datetime.fromtimestamp(json_mtime).strftime("%D %H:%M:%S")} is up to date.")
        return False
