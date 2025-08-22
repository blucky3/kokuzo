import pdb

class ENTRY:
    instances=dict()
    
    def __init__(self,id,lines):
        self.id=id
        self.data=lines
        self.title=lines[1].replace(',','')
        self.nexts=dict()
        if self.title.startswith('"NotDefine'):
            self.title=f'?{id}'
        for line in lines:
            if '/* 次タスク' in line:
                next=line.split(',')[0]
                if not next == '-1':
                    if next in self.nexts:
                        self.nexts[next]+=1
                    else:
                        self.nexts[next]=1

def get_entries(inFile="flow.txt"):
    """
    Flowのエントリインスタンスを登録する
    """
    entries=dict()
    lines=read_data(inFile)
    data=[]
    for line in lines:
        if '{' in line:
            id=line.strip('{ ').strip(',')
            data=[]
        elif '}' in line:
            entries[id]=ENTRY(id,data)
        else:
            data.append(line)
    ENTRY.instances=entries
    print(f'{len(entries)} task read.')

def read_data(inFile):
    """
    改行とタブを除去して文字列の配列を返す
    """
    dd=""
    with open(inFile,"r") as ff:
        dd=ff.readlines()
    return [x.strip().replace('\t','') for x in dd]
        
"""    
19287456["自動編成開始"]-->19322528;
19457992["未準深夜選択"]
19448080["未準深夜＋短時間で深夜勤"]
"""

class EntryColletion:
    collection=[]
    visited=set()
    
"""
TEST PATTERN
19485704,
(FNCPTR)"taskSelectLotOne",
"短時間選択深夜勤範囲",
"""

def collect_entries(root_id="19287456",depthFirst=False):
    """
    root_idを起点として続くタスクチェインを収集する。
    depthFirst True:深さ優先、False:広さ優先
    """
    entries=ENTRY.instances
    EntryColletion.collection=[root_id]
    EntryColletion.visited=set()
    if depthFirst:
        collect_entries_depth(entries,entries[root_id])
    else:
        collect_entries_width(entries,entries[root_id])
    return EntryColletion.collection
    
def collect_entries_width(entries,ent):
    #print(f'{ent.id=},{ent.title=}')
    EntryColletion.visited.add(ent)
    for next_id in ent.nexts.keys():
        if not next_id in EntryColletion.collection:
            EntryColletion.collection.append(next_id)
    for next_id in ent.nexts.keys():
        next_ent=entries[next_id]
        if not next_ent in EntryColletion.visited:
            collect_entries_width(entries,next_ent)

def collect_entries_depth(entries,ent):
    #print(f'{ent.id=},{ent.title=}')
    #print(f'{ent.nexts.keys()=}')
    for next_id in ent.nexts.keys():
        if not next_id in EntryColletion.collection:
            EntryColletion.collection.append(next_id)
            collect_entries_depth(entries,entries[next_id])

def make_mermaid_data(root="19485704",depthFirst=False,max_size=200):
    """
    rootを起点としたタスクチェインのmermaidチャートを生成。
    mermaidの処理限界に応じてmax_sizeを与える。
    """
    entries=ENTRY.instances
    targets=collect_entries(root,depthFirst)[:max_size]
    lines=[]
    lines.append("```mermaid")
    lines.append("graph TD;")

    allTargets=set(targets)
    for id in targets:
        entry=entries[id]
        if len(entry.nexts)>0:
            for next in entry.nexts.keys():
                allTargets.add(next)
    
    for id in allTargets:
        entry=entries[id]
        lines.append(f'{node_label(entry,root)};')
    for id in targets:
        entry=entries[id]
        #pdb.set_trace()
        if len(entry.nexts)>0:
            for next in entry.nexts.keys():
                if entry.nexts[next]==1:
                    lines.append(f'{entry.id}-->{next};')
                else:
                    lines.append(f'{entry.id}-->|{entry.nexts[next]}|{next};')
    for id in allTargets:
        title=entries[id].title.replace('"','')
        lines.append(f'click {id} "{id}" "{title}"')
    lines.append('classDef root fill:#aaffaa,stroke:#333,stroke-width:2px,color:#000')
        
    lines.append("```")
    #print(lines)
    return "\n".join(lines)

def node_label(entry,root):
    """
    起点ラベルの形状と色を変更
    """
    if entry.id==root:
        return f'{entry.id}({entry.title}):::root'
    else:
        return f'{entry.id}[{entry.title}]'
