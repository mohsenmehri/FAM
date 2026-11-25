#!/usr/bin/env python3
"""Auto-fix + validate a curriculum part file (parts/fN.js).
Usage: python3 parts/_pipeline.py parts/f3.js
Fixes: code-context () -> [], notes missing section close, section-key
missing ']', quiz-item missing commas, CJK/Cyrillic chars.
Then runs node eval + 11-section presence check.
"""
import re, sys, subprocess, json

SECKEYS = {'goal','prereq','concept','protocol','ios','diagram','lab','trouble','exercise','quiz','notes','faq'}

def fix_parens(s):
    out=[]; i=0; instr=False; q=None; n=0
    while i < len(s):
        ch = s[i]
        if instr:
            out.append(ch)
            if ch == '\\' and i+1 < len(s):
                out.append(s[i+1]); i += 2; continue
            if ch == q: instr = False
            i += 1; continue
        if ch in '\'"':
            instr = True; q = ch; out.append(ch); i += 1; continue
        if ch == '(': out.append('['); n += 1; i += 1; continue
        if ch == ')': out.append(']'); n += 1; i += 1; continue
        out.append(ch); i += 1
    return ''.join(out), n

def fix_notes(s):
    lines = s.split('\n'); n = 0
    for i, l in enumerate(lines):
        st = l.rstrip()
        if re.match(r'\s*notes:\[\[', st) and st.endswith("']],"):
            lines[i] = st[:-1] + '],'
            n += 1
    return '\n'.join(lines), n

def scan(s):
    stack=[]; i=0; line=0; instr=False; q=None
    while i < len(s):
        ch = s[i]
        if ch == '\n': line += 1
        if instr:
            if ch == '\\': i += 2; continue
            if ch == q: instr = False
            i += 1; continue
        if ch in '\'"':
            instr = True; q = ch; i += 1; continue
        if ch in '[{(':
            stack.append((ch, line)); i += 1; continue
        if ch in ']})':
            if stack: stack.pop()
            else: return ('extra', ch, line)
            i += 1; continue
        m = re.match(r'[A-Za-z_][A-Za-z0-9_]*:', s[i:])
        if m and stack and stack[-1][0] == '[':
            key = m.group(0)[:-1]
            if key in SECKEYS:
                return ('section', key, stack[-1][1], line)
        if m: i += len(m.group(0)); continue
        i += 1
    if stack: return ('eof', stack)
    return None

def fix_sections(s):
    fixes = 0
    for _ in range(100):
        r = scan(s)
        if r is None: break
        if r[0] == 'section':
            _, key, ol, cur = r
            L = s.split('\n'); t = L[ol].rstrip()
            L[ol] = (t[:-1] + '],' if t.endswith(',') else t + ']')
            s = '\n'.join(L); fixes += 1
        else:
            return s, fixes, r
    return s, fixes, None

def fix_quiz_commas(s):
    lines = s.split('\n'); n = 0
    for i in range(len(lines) - 1):
        cur = lines[i].rstrip(); nxt = lines[i+1].strip()
        if cur.endswith('}') and not cur.endswith('},') and not cur.endswith('{') and nxt.startswith('{q:'):
            lines[i] = cur + ','; n += 1
    return '\n'.join(lines), n

def scan_cjk(s):
    return sorted(set(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or '\u3040' <= ch <= '\u30ff'
                      or '\uac00' <= ch <= '\ud7af' or '\u0400' <= ch <= '\u04ff'))

def main():
    path = sys.argv[1]
    s = open(path, encoding='utf-8').read()
    s, n1 = fix_parens(s)
    s, n2 = fix_notes(s)
    s, n3, stuck = fix_sections(s)
    s, n4 = fix_quiz_commas(s)
    if stuck:
        print('STUCK after fixes:', stuck); sys.exit(1)
    open(path, 'w', encoding='utf-8').write(s)
    bad = scan_cjk(s)
    print(f'fixes: parens={n1} notes={n2} sections={n3} quizcommas={n4}; CJK/Cyril={bad if bad else "none"}')
    if bad: sys.exit(1)
    js = """
const fs=require('fs');
const src=fs.readFileSync(process.argv[1],'utf8').trimEnd().replace(/,\\s*$/,'');
const x=eval('('+src+')');
const K=['goal','prereq','concept','protocol','ios','diagram','lab','trouble','exercise','quiz','notes'];
let miss=[];
for(const l of x.lessons){for(const k of K) if(!l.sec||!l.sec[k]) miss.push(l.id+':'+k);
  if(!l.sec.quiz[0][1]||!l.sec.quiz[0][1].length) miss.push(l.id+':emptyquiz');}
if(miss.length){console.log('MISSING',miss.join(','));process.exit(1)}
console.log('NODE OK:',x.id,x.lessons.length,'lessons x 11 sections');
"""
    r = subprocess.run(['node', '-e', js, path], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    sys.exit(r.returncode)

if __name__ == '__main__':
    main()
