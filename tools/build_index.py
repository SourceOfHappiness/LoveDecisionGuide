import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK_DIR = os.path.join(BASE_DIR, 'book')
OUTPUT_JSON = os.path.join(BASE_DIR, 'data.json')
INDEX_HTML = os.path.join(BASE_DIR, 'index.html')

def parse_markdown_files():
    sections = []
    items = []
    files = sorted([f for f in os.listdir(BOOK_DIR) if f.endswith('.md')])
    
    entry_pattern = re.compile(r'###\s+(\d+)\.\s+(.*?)\n(.*?)(?=\n###|\Z)', re.DOTALL)
    
    for filename in files:
        filepath = os.path.join(BOOK_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        chapter_title = filename.split('.')[0]
        first_line = content.strip().split('\n')[0]
        if first_line.startswith('# '):
            chapter_title = first_line.replace('# ', '').strip()

        sec_m = re.match(r'^(\d+)', chapter_title)
        sec_num = int(sec_m.group(1)) if sec_m else len(sections) + 1
        clean_title = re.sub(r'^\d+[-_、\.]*\s*', '', chapter_title)

        intro_m = re.search(r'^#\s+.*?\n+(.*?)(?=\n+---\n+###|\n+###)', content, re.S)
        intro = intro_m.group(1).strip() if intro_m else ''

        sec_entries = []
        matches = entry_pattern.findall(content)
        for num, title, body in matches:
            item = {
                'id': int(num),
                'sec': sec_num,
                'sec_title': clean_title,
                'title': title.strip(),
                'chapter': chapter_title,
                'file': filename,
                'category': '',
                'cost': '',
                'money': '0',
                'time': '少',
                'will': '否',
                'gain_level': '大',
                'ratio': '高',
                'plain_speak': '',
                'benefits': '',
                'evidence': 'A',
                'academic': '',
                'actions': '',
                'redlines': '',
                'boundaries': '',
                'source': ''
            }

            cost_tag_m = re.search(r'<!--\s*成本标签:\s*(.*?)\s*-->', body)
            if cost_tag_m:
                for kv in cost_tag_m.group(1).split():
                    if '=' in kv:
                        k, v = kv.split('=', 1)
                        if k == '钱': item['money'] = v
                        elif k == '时间': item['time'] = v
                        elif k == '毅力': item['will'] = v
                        elif k == '收益': item['gain_level'] = v

            cost_w = {'money': {'0': 0, '少': 1, '多': 2}, 'time': {'少': 0, '中': 1, '多': 2}, 'will': {'否': 0, '些': 1, '是': 2}}
            cs = cost_w['money'].get(item['money'], 0) + cost_w['time'].get(item['time'], 0) + cost_w['will'].get(item['will'], 0)
            if item['gain_level'] == '大':
                item['ratio'] = '极高' if cs <= 1 else ('高' if cs <= 3 else '一般')
            elif item['gain_level'] == '中':
                item['ratio'] = '高' if cs <= 1 else '一般'
            else:
                item['ratio'] = '一般'
            
            cat_m = re.search(r'-\s+\*\*分类\*\*：(.*?)(?=\n-|\n\n|\Z)', body, re.DOTALL)
            if cat_m: item['category'] = cat_m.group(1).strip()
            
            cost_m = re.search(r'-\s+\*\*成本\*\*：(.*?)(?=\n-|\n\n|\Z)', body, re.DOTALL)
            if cost_m: item['cost'] = cost_m.group(1).strip()
            
            plain_m = re.search(r'-\s+\*\*说人话\*\*：(.*?)(?=\n-|\n\n|\Z)', body, re.DOTALL)
            if plain_m: item['plain_speak'] = plain_m.group(1).strip()
            
            ben_m = re.search(r'-\s+\*\*收益\*\*：(.*?)(?=\n-\s+\*\*|\Z)', body, re.DOTALL)
            if ben_m: item['benefits'] = ben_m.group(1).strip()
            
            ev_m = re.search(r'-\s+\*\*证据等级\*\*：([ABC])', body)
            if ev_m: item['evidence'] = ev_m.group(1).strip()

            acad_m = re.search(r'-\s+\*\*(?:学术依据与实验|学术与法律依据|学术依据)\*\*：(.*?)(?=\n-\s+\*\*|\Z)', body, re.DOTALL)
            if acad_m: item['academic'] = acad_m.group(1).strip()
            
            act_m = re.search(r'-\s+\*\*操作心法\*\*：(.*?)(?=\n-\s+\*\*|\Z)', body, re.DOTALL)
            if act_m: item['actions'] = act_m.group(1).strip()
            
            red_m = re.search(r'-\s+\*\*反面红线\*\*：(.*?)(?=\n-\s+\*\*|\Z)', body, re.DOTALL)
            if red_m: item['redlines'] = red_m.group(1).strip()

            bound_m = re.search(r'-\s+\*\*适用边界与争议\*\*：(.*?)(?=\n-\s+\*\*|\Z)', body, re.DOTALL)
            if bound_m: item['boundaries'] = bound_m.group(1).strip()
            
            src_m = re.search(r'-\s+\*\*来源\*\*：(.*?)(?=\n-|\n\n|\Z)', body, re.DOTALL)
            if src_m: item['source'] = src_m.group(1).strip()
            
            sec_entries.append(item)
            items.append(item)

        sections.append({
            'sec': sec_num,
            'title': clean_title,
            'full_title': chapter_title,
            'intro': intro,
            'entries': sec_entries
        })
            
    items.sort(key=lambda x: x['id'])
    sections.sort(key=lambda x: x['sec'])
    return sections, items

def main():
    sections, items = parse_markdown_files()
    print(f'成功解析 {len(sections)} 个章节，共 {len(items)} 条规范建议。')
    
    # 统计数据
    ev_counts = {'A': 0, 'B': 0, 'C': 0}
    for it in items:
        ev_counts[it['evidence']] = ev_counts.get(it['evidence'], 0) + 1
        
    print(f"证据分级分布: A={ev_counts['A']}, B={ev_counts['B']}, C={ev_counts['C']}")

    # 数据包结构
    payload = {
        'sections': sections,
        'items': items
    }

    # 保存 data.json
    json_str = json.dumps(payload, ensure_ascii=False, indent=2)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        f.write(json_str)
    print(f'已生成数据文件: {OUTPUT_JSON}')

    # 安全注入 index.html
    if os.path.exists(INDEX_HTML):
        with open(INDEX_HTML, 'r', encoding='utf-8') as f:
            html = f.read()

        start_tag = '<script id="embedded-data" type="application/json">'
        end_tag = '</script>'
        start_idx = html.find(start_tag)
        if start_idx != -1:
            end_idx = html.find(end_tag, start_idx + len(start_tag))
            if end_idx != -1:
                new_html = html[:start_idx + len(start_tag)] + json_str + html[end_idx:]
                with open(INDEX_HTML, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                print('已安全嵌入数据至 index.html 中的 #embedded-data 标签！')
            else:
                print('警告: 未找到 </script> 结束标签！')
        else:
            print('警告: 未找到 <script id="embedded-data"> 开始标签！')

if __name__ == '__main__':
    main()
