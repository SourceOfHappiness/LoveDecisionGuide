import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK_DIR = os.path.join(BASE_DIR, 'book')
OUTPUT_JSON = os.path.join(BASE_DIR, 'data.json')
INDEX_HTML = os.path.join(BASE_DIR, 'index.html')

def parse_markdown_files():
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

        matches = entry_pattern.findall(content)
        for num, title, body in matches:
            item = {
                'id': int(num),
                'title': title.strip(),
                'chapter': chapter_title,
                'file': filename,
                'category': '',
                'cost': '',
                'plain_speak': '',
                'benefits': '',
                'evidence': 'B',
                'actions': '',
                'redlines': '',
                'source': ''
            }
            
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
            
            act_m = re.search(r'-\s+\*\*操作心法\*\*：(.*?)(?=\n-\s+\*\*|\Z)', body, re.DOTALL)
            if act_m: item['actions'] = act_m.group(1).strip()
            
            red_m = re.search(r'-\s+\*\*反面红线\*\*：(.*?)(?=\n-\s+\*\*|\Z)', body, re.DOTALL)
            if red_m: item['redlines'] = red_m.group(1).strip()
            
            src_m = re.search(r'-\s+\*\*来源\*\*：(.*?)(?=\n-|\n\n|\Z)', body, re.DOTALL)
            if src_m: item['source'] = src_m.group(1).strip()
            
            items.append(item)
            
    items.sort(key=lambda x: x['id'])
    return items

def main():
    items = parse_markdown_files()
    print(f'成功解析 {len(items)} 条规范建议。')
    
    # 保存 data.json
    json_str = json.dumps(items, ensure_ascii=False, indent=2)
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
