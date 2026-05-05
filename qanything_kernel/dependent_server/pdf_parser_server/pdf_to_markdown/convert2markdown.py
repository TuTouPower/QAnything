import json
import re


def json2markdown(json_dir, markdown_dir):
    pdf = []
    para_before = ''
    before_patt = ['[a-z]', ',', '，', '-', '\(', '\)', '（', '）']
    after_patt = ['[a-z]', '·', '\(', '\)', '（', '）']
    js = json_dir
    f = json.load(open(js))
    md = markdown_dir
    current_page = None
    for i, section in f.items():
        # 从 section key 中提取页码（格式: "pn-type"）
        try:
            page_num = int(i.split('-')[0])
        except (ValueError, IndexError):
            page_num = 0
        if page_num != current_page:
            current_page = page_num
            pdf.append('## 当前页数:{}\n'.format(current_page))

        text = section['text']
        type = section['type']
        if isinstance(text, dict):
            table = text['table_markdown']
            caption = text['table_caption']
            pdf.append(table)
            pdf.append(caption + '\n\n')
        elif type.startswith('title'):
            pdf.append('## '+text.split('@@')[0])
        elif 'figure' in type:
            pdf.append('![figure]'+'({}.jpg "{}")'.format(type, text) + '\n')
        elif 'equation' in type:
            pdf.append('![equation]'+'({}.jpg)'.format(type) + '\n')
        else:
            para = text.split('@@')[0] + '\n'
            pdf.append(para)
            if para_before:
                if len(para_before) > 1 and any([re.match(p, para_before[-2]) for p in before_patt]) and any([re.match(p, para[0]) for p in after_patt]):
                    pdf.pop(pdf.index(para))
                    pdf.pop(pdf.index(para_before))
                    pdf.append(para_before[:-1] + ' ' + para)
                    para_before = para_before[:-1] + ' ' + para
                else:
                    para_before = para
            else:
                para_before = para
    for p in pdf:
        print(p, file=open(md, 'a'))
    return '\n'.join(pdf)
        
        


if __name__ =='__main__':
    json_dir = '/ssd8/exec/qinhaibo/code/RAG/release/git/document-layout-parser/table_test.json'
    json2markdown(json_dir)