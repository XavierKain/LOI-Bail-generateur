"""Fix indentation in app.py - all LOI content should be inside with tab_loi:"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the lines that need fixing
# Everything from "if uploaded_file is not None:" to before "# TAB BAIL"
# should have proper indentation (inside with tab_loi:)

fixed_lines = []
in_loi_block = False
loi_block_indent = 8  # spaces inside with tab_loi:

for i, line in enumerate(lines):
    line_num = i + 1

    # Detect start of LOI uploaded_file block
    if 'if uploaded_file is not None:' in line and line_num < 100:  # LOI block
        in_loi_block = True
        fixed_lines.append(' ' * loi_block_indent + 'if uploaded_file is not None:\n')
        continue

    # Detect end of LOI block (start of BAIL tab)
    if '# TAB BAIL' in line:
        in_loi_block = False
        fixed_lines.append(line)
        continue

    # If in LOI block, add proper indentation
    if in_loi_block:
        # Remove existing indentation and add correct one
        stripped = line.lstrip()
        if stripped:  # Non-empty line
            # Determine the relative indentation
            # Lines that were at column 0 -> now at 8
            # Lines that were at 4 -> now at 12
            # Lines that were at 8 -> now at 16
            # etc.
            original_indent = len(line) - len(stripped)
            new_indent = loi_block_indent + 4 + original_indent  # +4 for the if block
            fixed_lines.append(' ' * new_indent + stripped)
        else:
            # Empty line
            fixed_lines.append('\n')
    else:
        # Not in LOI block, keep as-is
        fixed_lines.append(line)

# Write fixed content
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Indentation fixed in app.py")
