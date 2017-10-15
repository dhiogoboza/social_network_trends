import base64

def get_chart(data):
    f = open("zne_icon.png", "rb")
    return base64.b64encode(f.read())
