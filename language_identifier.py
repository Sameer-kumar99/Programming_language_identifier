import re
import sys
import json

def identify_language(code):

    clean_code = re.sub(r'\/\/.*|\/\*[\s\S]*?\*\/|#.*', '', code)
    clean_code = clean_code.strip()
    
    if not clean_code:
        return {
            "language": "Empty code snippet", 
            "confidence": "None", 
            "features": []
        }
    
    patterns = {
        "Python": [
            {"regex": r'def\s+\w+\s*\([^)]*\)\s*:', "feature": "Function definition"},
            {"regex": r'import\s+[\w.]+', "feature": "Import statement"},
            {"regex": r'from\s+[\w.]+\s+import', "feature": "From import"},
            {"regex": r'class\s+\w+(\(\w+\))?\s*:', "feature": "Class definition"},
            {"regex": r'^\s{4}[^\s]', "feature": "Indentation-based syntax"},
            {"regex": r'print\(.*\)', "feature": "Print function"},
            {"regex": r'if\s+__name__\s*==\s*[\'"]__main__[\'"]', "feature": "Main execution check"}
        ],
        "JavaScript": [
            {"regex": r'function\s+\w+\s*\([^)]*\)\s*{', "feature": "Function declaration"},
            {"regex": r'(const|let|var)\s+\w+\s*=', "feature": "Variable declaration"},
            {"regex": r'document\.getElementById', "feature": "DOM manipulation"},
            {"regex": r'console\.log\(', "feature": "Console logging"},
            {"regex": r'=>', "feature": "Arrow functions"},
            {"regex": r'import\s+.*\s+from\s+[\'"].*[\'"]', "feature": "ES6 imports"}
        ],
        "Java": [
            {"regex": r'public\s+class\s+\w+', "feature": "Public class"},
            {"regex": r'public\s+static\s+void\s+main', "feature": "Main method"},
            {"regex": r'System\.out\.print', "feature": "System output"},
            {"regex": r'import\s+java\.', "feature": "Java imports"},
            {"regex": r'@Override', "feature": "Method annotation"}
        ],
        "C++": [
            {"regex": r'#include\s*<\w+>', "feature": "Include directive"},
            {"regex": r'std::|::\w+', "feature": "Namespace usage"},
            {"regex": r'int\s+main\s*\(\s*\)', "feature": "Main function"},
            {"regex": r'cout\s*<<', "feature": "Console output"},
            {"regex": r'cin\s*>>', "feature": "Console input"}
        ],
        "PHP": [
            {"regex": r'<\?php', "feature": "PHP opening tag"},
            {"regex": r'\$\w+\s*=', "feature": "Variable assignment"},
            {"regex": r'echo\s+', "feature": "Echo statement"},
            {"regex": r'function\s+\w+\s*\([^)]*\)\s*{', "feature": "Function definition"},
            {"regex": r'->\w+', "feature": "Object property/method access"}
        ],
        "Ruby": [
            {"regex": r'def\s+\w+(\s*\([^)]*\))?\s*\n', "feature": "Method definition"},
            {"regex": r'require\s+[\'"].*[\'"]', "feature": "Require statement"},
            {"regex": r'puts\s+', "feature": "Output statement"},
            {"regex": r'do\s+\|.*\|', "feature": "Block with parameters"},
            {"regex": r'end$|end\s', "feature": "End keyword"}
        ],
        "HTML": [
            {"regex": r'<!DOCTYPE\s+html>', "feature": "DOCTYPE declaration"},
            {"regex": r'<html', "feature": "HTML tag"},
            {"regex": r'<head>', "feature": "Head section"},
            {"regex": r'<body>', "feature": "Body section"},
            {"regex": r'<div', "feature": "Div element"},
            {"regex": r'<script', "feature": "Script tag"}
        ],
        "CSS": [
            {"regex": r'\w+\s*{[^}]*}', "feature": "CSS rule"},
            {"regex": r'@media', "feature": "Media query"},
            {"regex": r'#\w+\s*{', "feature": "ID selector"},
            {"regex": r'\.\w+\s*{', "feature": "Class selector"},
            {"regex": r':\s*hover', "feature": "Pseudo-class"}
        ]
    }
    
    scores = {}
    matched_features = {}
    
    for lang, patterns_list in patterns.items():
        scores[lang] = 0
        matched_features[lang] = []
        
        for pattern in patterns_list:
            if re.search(pattern["regex"], clean_code, re.IGNORECASE | re.MULTILINE):
                scores[lang] += 1
                matched_features[lang].append(pattern["feature"])
    
   
    debug_info = {
        "scores": scores
    }
    
    max_score = 0
    detected_language = "Unknown"
    
    for lang, score in scores.items():
        if score > max_score:
            max_score = score
            detected_language = lang
    
    confidence = "Low"
    if max_score == 0:
        detected_language = "Unknown (possibly plain text)"
        confidence = "None"
    elif max_score == 1:
        confidence = "Very Low"
    elif max_score == 2:
        confidence = "Low"
    elif max_score == 3:
        confidence = "Medium"
    elif max_score == 4:
        confidence = "High"
    else:
        confidence = "Very High"
    return {
        "language": detected_language,
        "confidence": confidence,
        "features": matched_features[detected_language] if detected_language != "Unknown" and detected_language != "Unknown (possibly plain text)" else [],
        "debug": debug_info  
    }
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as file:
            code = file.read()
    except Exception as e:
        print(json.dumps({"error": f"Failed to read file: {str(e)}"}))
        sys.exit(1)
    result = identify_language(code)

    print(json.dumps(result))