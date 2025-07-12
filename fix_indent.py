#!/usr/bin/env python3
import re

def fix_indentation():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Handle the admin section specifically
        if 'if user_type == "admin":' in line:
            fixed_lines.append(line)
            i += 1
            
            # Add the tabs line
            if i < len(lines) and 'tab1, tab2, tab3, tab4 = st.tabs' in lines[i]:
                fixed_lines.append('            ' + lines[i].strip())
                i += 1
                
                # Process all tab content
                while i < len(lines):
                    current_line = lines[i]
                    
                    # Stop when we reach the end of the admin section
                    if (current_line.strip() and 
                        not current_line.startswith(' ') and 
                        'with tab' not in current_line and
                        current_line.strip() != ''):
                        break
                    
                    # Handle with tab blocks
                    if 'with tab' in current_line:
                        fixed_lines.append('            ' + current_line.strip())
                    elif current_line.strip() == '':
                        fixed_lines.append('')
                    else:
                        # Regular content inside tabs
                        if current_line.strip():
                            fixed_lines.append('                ' + current_line.strip())
                        else:
                            fixed_lines.append('')
                    i += 1
                continue
        
        fixed_lines.append(line)
        i += 1
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))

if __name__ == '__main__':
    fix_indentation()
    print("Indentación corregida")