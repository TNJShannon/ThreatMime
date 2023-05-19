def sanitize(string):
    return string.replace("-","_").replace(":","").replace(";","").replace(",","").replace('"',"'")