import cleaner
import sys
content = sys.stdin.read()
'''
if True:
  [content, removed] = cleaner.fix_sumniki(content)
  [content, removed] = cleaner.lower(content)
  [content, removed] = cleaner.clean_ng(content)
  [content, removed] = cleaner.remove_repeated_lines(content)
  [content, removed] = cleaner.remove_intro(content)
  [content, removed] = cleaner.remove_lit(content)
  print content

'''
content = cleaner.get_cleaned(content)
print content