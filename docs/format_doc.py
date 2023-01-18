filename = "testy_quick user doc 98bb247e94d44b87842f2ae764b74f2f.html"

with open(filename, 'r') as f:
    content = f.read()

prefix = "https://www.notion.so/"
pos = 0
pos = content.find(prefix, pos)
while pos > 0:
    end_pos = content.find('"', pos)
    str_to_replace = content[pos:end_pos]
    nb = str_to_replace.split('-')[-1]
    assert len(nb) == 32
    replace_with = "#" + nb[0:8] + '-' \
                   + nb[8:12] + '-' + nb[12:16] + '-' + nb[16:20] + '-' \
                   + nb[20:32]
    content = content.replace(str_to_replace, replace_with)
    pos = content.find(prefix, pos)
with open("user_doc.html", 'w') as f:
    f.write(content)
