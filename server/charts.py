import json

#import base64

def get_chart(data):
    #f = open("zne_icon.png", "rb")
    #return base64.b64encode(f.read())
    #a = {"test": 132, "a": False, "b": "bbbb"}
    
    
    a = ({"cols":[{"label":"Country","type":"string"},{"label":"Popularity","type":"number"}],
            "rows":[
                {"c":[{"v":"Germany"},{"v":200}]},{"c":[{"v":"United States"},{"v":300}]},
                {"c":[{"v":"Brazil"},{"v":400}]},{"c":[{"v":"Canada"},{"v":500}]},
                {"c":[{"v":"France"},{"v":600}]},{"c":[{"v":"RU"},{"v":700}
            ]}
        ]})
    
    return json.dumps(a)
    
    
