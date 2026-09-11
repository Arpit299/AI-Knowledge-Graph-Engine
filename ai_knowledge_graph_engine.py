import argparse
import csv
import json
import re
from collections import defaultdict,deque,Counter
from pathlib import Path

class KnowledgeGraph:
    def __init__(self):
        self.nodes={}
        self.edges=defaultdict(set)
        self.reverse=defaultdict(set)
        self.relations=Counter()
    def norm(self,text):
        return re.sub(r"[^a-z0-9]+","_",str(text).lower()).strip("_")
    def add_node(self,name,kind="entity"):
        key=self.norm(name)
        if not key:return ""
        if key not in self.nodes:self.nodes[key]={"name":str(name).strip(),"kind":kind,"mentions":0}
        self.nodes[key]["mentions"]+=1
        return key
    def add_edge(self,source,target,relation):
        if str(source).lower() in {"and","reliable","systems","applications","workloads","the","this","that","with","from"} or str(target).lower() in {"and","reliable","systems","applications","workloads","the","this","that","with","from"}:return
        s=self.add_node(source)
        t=self.add_node(target)
        if not s or not t or s==t:return
        r=self.norm(relation)
        self.edges[s].add((r,t))
        self.reverse[t].add((r,s))
        self.relations[r]+=1
    def search(self,query):
        q=self.norm(query)
        return [v for k,v in self.nodes.items() if q in k or q in self.norm(v["name"])]
    def neighbors(self,name,direction="out"):
        key=self.norm(name)
        data=self.edges if direction=="out" else self.reverse
        result=[]
        for relation,target in data.get(key,set()):result.append({"relation":relation,"entity":self.nodes[target]["name"]})
        return sorted(result,key=lambda x:(x["relation"],x["entity"]))
    def path(self,start,end,max_depth=5):
        s=self.norm(start)
        t=self.norm(end)
        if s not in self.nodes or t not in self.nodes:return []
        queue=deque([(s,[])])
        visited={s}
        while queue:
            node,path=queue.popleft()
            if node==t:return path
            if len(path)>=max_depth:continue
            for relation,target in self.edges.get(node,set()):
                if target in visited:continue
                visited.add(target)
                step={"from":self.nodes[node]["name"],"relation":relation,"to":self.nodes[target]["name"]}
                queue.append((target,path+[step]))
        return []
    def to_dict(self):
        edges=[]
        for source,items in self.edges.items():
            for relation,target in sorted(items):edges.append({"source":self.nodes[source]["name"],"relation":relation,"target":self.nodes[target]["name"]})
        return {"nodes":self.nodes,"edges":edges,"relation_counts":dict(self.relations)}
    def save(self,path):
        Path(path).write_text(json.dumps(self.to_dict(),indent=2),encoding="utf-8")

class Extractor:
    def __init__(self):
        self.entity_patterns=[r"\b(?:python|fastapi|django|flask|postgresql|mysql|sqlite|redis|docker|kubernetes|aws|azure|gcp|tensorflow|pytorch|pandas|numpy|react|javascript|typescript|java|c\+\+)\b",r"\b[A-Z][A-Za-z0-9_-]{2,30}\b"]
        self.relation_patterns=[(r"\b([A-Z][A-Za-z0-9_-]{2,30}|[a-z][a-z0-9_-]{2,30})\s+(?:uses|use|utilizes|utilise)\s+([A-Z][A-Za-z0-9_-]{2,30}|[a-z][a-z0-9_-]{2,30})\b","uses"),(r"\b([A-Z][A-Za-z0-9_-]{2,30})\s+(?:integrates with|integrates)\s+([A-Z][A-Za-z0-9_-]{2,30})\b","integrates_with"),(r"\b([A-Z][A-Za-z0-9_-]{2,30})\s+(?:depends on|relies on)\s+([A-Z][A-Za-z0-9_-]{2,30})\b","depends_on"),(r"\b([A-Z][A-Za-z0-9_-]{2,30})\s+(?:improves|supports|provides|powers)\s+([A-Z][A-Za-z0-9_-]{2,30})\b","relates_to")]
    def entities(self,text):
        found=[]
        for pattern in self.entity_patterns:
            for match in re.finditer(pattern,text,re.I if "(?:python" in pattern else 0):
                value=match.group(0).strip()
                if len(value)>1 and value.lower() not in {"the","and","for","with","from","this","that","reliable","systems","applications","workloads"}:found.append(value)
        result=[]
        seen=set()
        for value in found:
            key=self.clean(value)
            if key not in seen:seen.add(key);result.append(value)
        return result
    def clean(self,value):return re.sub(r"[^a-z0-9]+","_",value.lower()).strip("_")
    def extract(self,text):
        graph=KnowledgeGraph()
        for entity in self.entities(text):graph.add_node(entity)
        for pattern,relation in self.relation_patterns:
            for match in re.finditer(pattern,text,re.I):graph.add_edge(match.group(1),match.group(2),relation)
        for sentence in re.split(r"(?<=[.!?])\s+",text):
            entities=self.entities(sentence)
            if 2<=len(entities)<=6:
                for i,a in enumerate(entities):
                    for b in entities[i+1:]:
                        graph.add_edge(a,b,"mentioned_with")
                        graph.add_edge(b,a,"mentioned_with")
        return graph

def read_documents(paths):
    chunks=[]
    for raw in paths:
        path=Path(raw)
        suffix=path.suffix.lower()
        if suffix in {".txt",".md"}:chunks.append((path.name,path.read_text(encoding="utf-8",errors="ignore")))
        elif suffix==".json":chunks.append((path.name,json.dumps(json.loads(path.read_text(encoding="utf-8")),ensure_ascii=False)))
        elif suffix==".csv":
            with path.open("r",encoding="utf-8-sig",newline="") as file:
                for row_number,row in enumerate(csv.DictReader(file),1):chunks.append((f"{path.name}#row{row_number}"," ".join(f"{k}: {v}" for k,v in row.items() if v)))
        else:raise ValueError(f"Unsupported file format: {path.suffix}")
    return chunks

def merge_graphs(parts):
    graph=KnowledgeGraph()
    for part in parts:
        for node in part.nodes.values():
            for _ in range(node["mentions"]):graph.add_node(node["name"],node["kind"])
        for source,items in part.edges.items():
            for relation,target in items:graph.add_edge(part.nodes[source]["name"],part.nodes[target]["name"],relation)
    return graph

def demo_text():
    return "FastAPI uses Python and integrates with PostgreSQL. Docker supports FastAPI deployments. Redis supports Python applications. Kubernetes manages Docker workloads. PostgreSQL provides reliable data storage for FastAPI systems."

def print_summary(graph,documents):
    print("AI KNOWLEDGE GRAPH ENGINE")
    print("="*60)
    print(f"Documents: {documents}")
    print(f"Entities: {len(graph.nodes)}")
    print(f"Relationships: {sum(graph.relations.values())}")
    print(f"Relation Types: {len(graph.relations)}")
    print("\nENTITIES")
    for node in sorted(graph.nodes.values(),key=lambda x:(-x["mentions"],x["name"]))[:30]:print(f"- {node['name']} | mentions={node['mentions']}")
    print("\nRELATIONS")
    for relation,count in graph.relations.most_common():print(f"- {relation}: {count}")

def main():
    parser=argparse.ArgumentParser(prog="ai_knowledge_graph_engine")
    parser.add_argument("files",nargs="*")
    parser.add_argument("--demo",action="store_true")
    parser.add_argument("--export",default="")
    parser.add_argument("--search",default="")
    parser.add_argument("--neighbors",default="")
    parser.add_argument("--path",nargs=2,metavar=("START","END"))
    args=parser.parse_args()
    try:
        if args.demo:
            graph=Extractor().extract(demo_text());documents=1
        elif args.files:
            docs=read_documents(args.files)
            graph=merge_graphs([Extractor().extract(text) for _,text in docs]);documents=len(docs)
        else:
            entered=input("Enter text or document path: ").strip().strip('"')
            if not entered:raise ValueError("No text or document path supplied.")
            if Path(entered).is_file():
                docs=read_documents([entered]);graph=merge_graphs([Extractor().extract(text) for _,text in docs]);documents=len(docs)
            else:graph=Extractor().extract(entered);documents=1
        print_summary(graph,documents)
        if args.search:
            print("\nSEARCH")
            for item in graph.search(args.search):print(f"{item['name']} | mentions={item['mentions']}")
        if args.neighbors:
            print("\nNEIGHBORS")
            for item in graph.neighbors(args.neighbors):print(f"{item['relation']} -> {item['entity']}")
        if args.path:
            print("\nPATH")
            path=graph.path(args.path[0],args.path[1])
            if path:
                print(path[0]["from"])
                for step in path:print(f"  --{step['relation']}--> {step['to']}")
            else:print("No path found.")
        if args.export:
            graph.save(args.export);print(f"\nExported: {args.export}")
    except Exception as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
if __name__=="__main__":main()
