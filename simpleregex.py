def create(pattern):
    regex = []
    split = pattern.split("|")
    for item in split:
        starts = False
        ends = False
        
        item = item.strip()
        
        if item[0] == "*":
            ends = True
            
            if (len(item) > 1):
                item = item[1:]
            
        if item[len(item) - 1] == "*":
            starts = True
            item = item[:-1]
        
        regex.append({"i": item, "s": starts, "e": ends})
    
    return regex

def match(regex, subject):
    for item in regex:
        print(item)
        
        if item["s"] and item["e"]:
            if item["i"] in subject:
                return True
        else:
            if item["s"] and subject.startswith(item["i"]):
                return True
            
            if item["e"] and subject.endswith(item["i"]):
                return True
            
        if item["i"] == subject:
            return True
    
    return False
