import re

file_path = "c:/Users/Administrator/Desktop/ps4/app.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "unsafe_allow_html" in line:
        # We need to trace backwards to find the nearest st.markdown or st.sidebar.markdown
        for j in range(i, -1, -1):
            if "st.markdown(" in lines[j] or "st.sidebar.markdown(" in lines[j]:
                lines[j] = lines[j].replace("st.markdown(", "st.html(")
                lines[j] = lines[j].replace("st.sidebar.markdown(", "st.sidebar.html(")
                
                # Now we remove the unsafe_allow_html line
                # It could be `unsafe_allow_html=True,` or `, unsafe_allow_html=True`
                lines[i] = re.sub(r',?\s*unsafe_allow_html\s*=\s*True\s*,?', '', lines[i])
                
                # If the line becomes empty or just whitespace/hanging parenthesis, we can handle it
                if lines[i].strip() == "":
                    lines[i] = ""
                break

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)
    
print("Updated HTML replacements.")