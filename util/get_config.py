config = {
    # 本地文件上传文件路径.
    "task": {"PROJECT_FILE_PATH" : "uploads/project_file",
             "REQUIREMENT_FILE_PATH" : "uploads/requirement_file"},

    # cdn地址上传路径.
    "upload":{"PIC_UPLOAD_FOLDER": "upload/pic"}
}

def get_config(category, key):
    global config
    return config[category].get(key)