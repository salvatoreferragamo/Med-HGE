# %% [markdown]
# ### 给disease-KG补充一些医学知识：（train和dev中的知识）更新并筛选：

# %%
from collections import defaultdict

# %%
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

# %%
# 根据实体识别的结果找到具体实体
def get_entity_bio(seq):
    seq = seq.split(' ')
    chunks = []
    chunk = [-1, -1, -1]
    for indx, tag in enumerate(seq):
        if tag.startswith("B-"):
            if chunk[2] != -1:
                chunks.append(chunk)
            chunk = [-1, -1, -1]
            chunk[1] = indx
            chunk[0] = tag.split('-')[1]
            chunk[2] = indx
            if indx == len(seq) - 1:
                chunks.append(chunk)
        elif tag.startswith('I-') and chunk[1] != -1:
            _type = tag.split('-')[1]
            if _type == chunk[0]:
                chunk[2] = indx

            if indx == len(seq) - 1:
                chunks.append(chunk)
        else:
            if chunk[2] != -1:
                chunks.append(chunk)
            chunk = [-1, -1, -1]
    return chunks

# %%
# 从数据集上构建好一些相关知识的JSON文件：
import json 
medical_json = defaultdict()
# check = defaultdict()
# cure = set()
save_path = './dataset/medical_add.json'
for corpus_type in ['train','dev']:

    read_path = './dataset/' + corpus_type + '.json'
    read_ner_path = './dataset/' + corpus_type + '_sp.json'
    # read_path = read_root_path / f'{corpus_type}.json'
    # save_path = save_root_path / f'{corpus_type}.json'
    # 使用实体识别技术来处理主述部分：
    with open(read_ner_path,'r', encoding='utf-8') as r_f:
        json_ner_data = json.load(r_f)

    with open(read_path,'r', encoding='utf-8') as r_f:
        json_data = json.load(r_f)
        for nid, (pid, sample) in enumerate(json_data.items()):
            if nid != -1:
            # if nid < 10:
            #     print(sample['diagnosis'])    
                disease = sample['diagnosis']  

                if disease not in medical_json.keys():
                    medical_json[disease] = defaultdict()
                    medical_json[disease]['symptom'] = defaultdict()
                    medical_json[disease]['check'] = defaultdict()
                    medical_json[disease]['cure'] = defaultdict()
                    medical_json[disease]['drug'] = defaultdict()

                # 三个类别对应五种实体：(只要归一化之后的)
                imp_symptom = [key for key, value in sample['implicit_info']['Symptom'].items() if int(value) == 1]
                exp_symtom = [value for value in sample['explicit_info']['Symptom']]
                # 疾病对应的一些症状：(记录一下出现频率)
                symptoms = set.union(set(imp_symptom),(set(exp_symtom)))
                for symptom in symptoms:
                    if symptom in medical_json[disease]['symptom'].keys():
                        medical_json[disease]['symptom'][symptom] += 1
                    else:
                        medical_json[disease]['symptom'][symptom] = 1

                # print(symptom)
                
                # if len(symptom) == 0:
                #     print(pid)
                # print(symptom)
                # Drug/Drug_Category
                # drug = set()
                # Medical_Examination	
                # check = set()
                # 加入主述中涉及到的一些实体到知识库中：
                total_dia = [{'sentence':sample['self_report'],'BIO_label':json_ner_data[pid]}] + sample['dialogue']
                for sid, dia_cont in enumerate(total_dia):
                    sent = dia_cont['sentence']
                    labels = dia_cont['BIO_label'] 
                    bio_list = get_entity_bio(labels)
                    if len(bio_list)!= 0:
                        for bio_tri in bio_list:
                            # TODO:需要根据新的数据集进行更新（对于字段中的不一定是对话中的symptom的进行修改）
                            if bio_tri[0] == 'Symptom':
                                # if disease == '小儿消化不良':
                                #     print(sent[bio_tri[1]:bio_tri[-1]+1])
                                # if bio_tri[-1] - bio_tri[1] != 0:
                                # 不要每句话的单独的表达了，这样的话对于后续的utterance和disease连接不利：(dev可以，test不可以)
                                # continue
                                if sent[bio_tri[1]:bio_tri[-1]+1] in medical_json[disease]['symptom'].keys():
                                    medical_json[disease]['symptom'][sent[bio_tri[1]:bio_tri[-1]+1]] += 1
                                else: 
                                    medical_json[disease]['symptom'][sent[bio_tri[1]:bio_tri[-1]+1]] = 1
                            elif bio_tri[0] == 'Medical_Examination':
                                # if disease == '小儿消化不良':
                                #     print(sent[bio_tri[1]:bio_tri[-1]+1])
                                if bio_tri[-1] - bio_tri[1] != 0 and sent[bio_tri[1]:bio_tri[-1]+1] not in ['化验','检查','复查']:
                                    if sent[bio_tri[1]:bio_tri[-1]+1] in medical_json[disease]['check'].keys():
                                        medical_json[disease]['check'][sent[bio_tri[1]:bio_tri[-1]+1]] += 1
                                    else: 
                                        medical_json[disease]['check'][sent[bio_tri[1]:bio_tri[-1]+1]] = 1
                                    # check.update([sent[bio_tri[1]:bio_tri[-1]+1]])
                                    # print(check)
                            elif bio_tri[0] == 'Operation':
                                if bio_tri[-1] - bio_tri[1] != 0:
                                    # cure.update([sent[bio_tri[1]:bio_tri[-1]+1]])
                                    if sent[bio_tri[1]:bio_tri[-1]+1] in medical_json[disease]['cure'].keys():
                                        medical_json[disease]['cure'][sent[bio_tri[1]:bio_tri[-1]+1]] += 1
                                    else: 
                                        medical_json[disease]['cure'][sent[bio_tri[1]:bio_tri[-1]+1]] = 1
                            elif bio_tri[0] == 'Drug' or bio_tri[0] == 'Drug_Category':
                                if bio_tri[-1] - bio_tri[1] != 0:
                                    # cure.update([sent[bio_tri[1]:bio_tri[-1]+1]])
                                    if sent[bio_tri[1]:bio_tri[-1]+1] in medical_json[disease]['drug'].keys():
                                        medical_json[disease]['drug'][sent[bio_tri[1]:bio_tri[-1]+1]] += 1
                                    else: 
                                        medical_json[disease]['drug'][sent[bio_tri[1]:bio_tri[-1]+1]] = 1
                # check = list(check)

                # # 构建知识库：
                # if disease not in medical_json.keys():
                #     medical_json[disease] = defaultdict()
                
                # medical_json[disease]['symptom']
                # medical_json[disease]['check'] = check

                # medical_json[disease].add()

for dkey,dvalue in medical_json.items():
    for key,value in dvalue.items():
        # if key != 'cure':
        sum = 0
        for k,v in value.items():
            sum += v
        for k,v in value.items():
            medical_json[dkey][key][k] = v/sum*100
        # medical_json[dkey][key] = sorted(medical_json[dkey][key].items(), key=lambda x: x[1],reverse=True)

# 将这个医疗字典库存起来：
with open(save_path,'w', encoding='utf-8') as w_f:
    w_f.write(json.dumps(medical_json, indent=4, ensure_ascii=False))

# %%
# 统计一下有多少病例分类会出现错误的样本：
def find_disease(sent2ent,medical_json):
    sym = set()
    dru = set()
    cur = set()
    che = set()
    tot = set()
    all = {'Symptom':sym,'Medical_Examination':che,'Drug':dru,'Drug_Category':dru,'Operation':cur}
    for ikey,ivalue in sent2ent.items():
        for tup in ivalue:
            all[tup[0]].add(tup[1])
            tot.add(tup[1])

    # print(tot)
    # print(all)
    sum = 0
    disease_name = ''
    for dkey,dvalue in medical_json.items():
        curr = 0
        for key,value in dvalue.items():
            # 保证每一个子类都要有
            for k,v in value.items():
                if k in tot:
                    curr += v
                    # print(dkey,v)
        for symptom in sym:
            if symptom not in dvalue['symptom']:
                curr = 0
                break
        for check in che:
            if check not in dvalue['check']:
                curr = 0
                break
        for drug in dru:
            if drug not in dvalue['drug']:
                curr = 0
                break
        for cure in cur:
            if cure not in dvalue['cure']:
                curr= 0
                break
        
        if curr > sum:
            disease_name = dkey
            sum = curr 
    
    # print(disease_name)
    if disease_name != sample['diagnosis']:
        pass
        # print(disease_name,sample['diagnosis'],pid)
    return disease_name

# %%
def judge_ent_label(bio_list,entity_type):
    ent_label = set()
    for bio_tri in bio_list:
        ent_label.add(bio_tri[0])
    if entity_type in list(ent_label):
        return True 
    else:
        return False

# %%
def process(report):
    x = []
    for key, value in report.items():
        x.append(key + '：' + value)
    return ''.join(x)

# %%
import json
# 开始根据概率大小添加边：
instances = 0
unmatch = 0
# for corpus_type in ['train','dev']:
for corpus_type in ['test']:
    read_path = './dataset/' + corpus_type + '.json'
    # read_path = read_root_path / f'{corpus_type}.json'
    save_ap = './dataset/imcs_3re/' + corpus_type

    read_ner_path = './dataset/' + corpus_type + '_sp.json'
    read_ner_all_path = './dataset/' + corpus_type + '_sp1.json'
    # 使用实体识别技术来处理主述部分：
    with open(read_ner_path,'r', encoding='utf-8') as r_f:
        json_ner_data = json.load(r_f)
    
    with open(read_ner_all_path,'r', encoding='utf-8') as r_f:
        json_ner_all_data = json.load(r_f)

    with open(read_path,'r', encoding='utf-8') as r_f:
        json_data = json.load(r_f)
        for nid, (pid, sample) in enumerate(json_data.items()):
            instances += 1
            if nid != -1:
            # if nid < 10:
                tgt_path = save_ap+'.tgt.txt'
                for report in sample['report']:
                    with open(tgt_path,'a+',encoding='utf-8') as fp:
                        fp.write(' '.join(process(report))+'\n')

                content = ['医生','患者']
                text_node = [1,1]
                # type: u-k, k-u, u-s, k-k (待确定) -> u-s 0 , cure 7,8, drug 3,4, check 5,6, symptom 1,2, 以及每一个的反关系
                text_edge = []
                text_edge_ids = []

                # 把患者的主述加进去：（需要对主述进行实体识别：）
                content.append(sample['self_report'])
                text_node.append(3)
                text_edge.append(0)
                text_edge_ids.append((2,1))

                # 构建这个的目的是为了根据症状，药物等找到相关的疾病：
                sent2ent = defaultdict()

                bio_list = get_entity_bio(json_ner_data[pid])
                ent_list = []
                s_num = 0
                for bio_tri in bio_list:
                    if bio_tri[0] == 'Symptom':
                        # TODO: 要使用归一化后的症状：(并分类判断是否属于0，1，2中的类别1)
                        ent_list.append((bio_tri[0],sample['self_report'][bio_tri[1]:bio_tri[-1]+1]))
                        if s_num < len(sample['explicit_info']['Symptom']):
                            ent_list.append(('Symptom',sample['explicit_info']['Symptom'][s_num])) # 训练集是这样：
                        s_num += 1
                    elif bio_tri[0] == 'Medical_Examination':
                        if bio_tri[-1] - bio_tri[1] != 0 and sample['self_report'][bio_tri[1]:bio_tri[-1]+1] not in ['化验','检查','复查']:
                            ent_list.append((bio_tri[0],sample['self_report'][bio_tri[1]:bio_tri[-1]+1]))
                    else:
                        if bio_tri[-1] - bio_tri[1] != 0:
                            ent_list.append((bio_tri[0],sample['self_report'][bio_tri[1]:bio_tri[-1]+1]))
                sent2ent[0] = ent_list

                sid = 1

                sent2id = defaultdict()
                for iid, sent in enumerate(sample['dialogue']):
                    if sent['dialogue_act'] != 'Other' and sent['sentence']!="（空）":
                        sent2id[sent['sentence']] = sid
                        content.append(sent['sentence'])
                        text_node.append(3)
                        text_edge.append(0)
                        if sent['speaker'] == '医生':
                            text_edge_ids.append((sid+2,0))
                        else:
                            text_edge_ids.append((sid+2,1))
                        # bio_list = get_entity_bio(sent['BIO_label'])
                        bio_list = get_entity_bio(json_ner_all_data[pid][str(iid)])
                        ent_list = []
                        s_num = 0
                        for bio_tri in bio_list:
                            if bio_tri[0] == 'Symptom':
                                # TODO: 要使用归一化后的症状：(并分类判断是否属于0，1，2中的类别1)
                                # dev可以这种方式
                                ent_list.append((bio_tri[0],sent['sentence'][bio_tri[1]:bio_tri[-1]+1]))
                                # test只能这种方式
                                # if sent['symptom_type'][s_num] == 1:
                                #     ent_list.append(sent['symptom_norm'][s_num])
                                # s_num += 1
                            elif bio_tri[0] == 'Medical_Examination':
                                if bio_tri[-1] - bio_tri[1] != 0 and sent['sentence'][bio_tri[1]:bio_tri[-1]+1] not in ['化验','检查','复查']:
                                    ent_list.append((bio_tri[0],sent['sentence'][bio_tri[1]:bio_tri[-1]+1]))
                            else:
                                if bio_tri[-1] - bio_tri[1] != 0:
                                    ent_list.append((bio_tri[0],sent['sentence'][bio_tri[1]:bio_tri[-1]+1]))
                        if len(ent_list) != 0:   
                            sent2ent[sid] = ent_list

                        # 找相关的知识，以及设置节点以及边的类型：
                        # tgt: 
                        # tgt1, tgt2 = process(sample['report'][0]), process(sample['report'][1])
                        sid += 1
                # 几种情况：(训练集用gold label, 验证集用概率计算最大，准确率在87%左右)
                    # （1) cure, drug, check, symptom不全的话，取概率最大的疾病并进行utterance的连接，以及知识的补充（和句子的intent相关）
                    # （2）cure, drug, check, symptom都全的话，取概率最大的疾病并进行utterance的连接即可
                # attribute = set()
                # for ikey,ivalue in sent2ent.items():
                #     for tup in ivalue:
                #         attribute.add(tup[0])
                # # attribute.remove('Drug_Category')
                # if len(attribute) >= 4:
                #     if 'Symptom' in attribute and 'Medical_Examination' in attribute and 'Operation' in attribute:
                #         pass
                        # print(sample['diagnosis'],sent2ent)

                # 什么都没有的，无法添加知识库的，只有两例：
                # if len(sent2ent.keys()) == 1:
                #     print(sample['diagnosis'],sent2ent,pid)

                # 加上主述，以及使用不归一化的症状名称，只有203个疾病对不上
                # disease_name = find_disease(sent2ent,medical_json)
                # if disease_name != sample['diagnosis']:
                #     print(sample['diagnosis'],disease_name)

                # if corpus_type == 'train' or corpus_type == 'dev':
                if corpus_type == 'test':
                    disease_name = sample['diagnosis']
                    # disease_name = find_disease(sent2ent,medical_json)
                    content.append(disease_name)
                    disease_id = len(content)-1
                    text_node.append(2)
                    # 进行边以及结点矩阵的构建：(先连接intent，后连接实体出现的utt)
                    # TODO: 后续试一下如果加一些相关的其他知识会不会效果会有提升：（目前只加上疾病名称以及不同类型的边）
                    # 主述部分：（统计了一下下都是症状相关的内容）
                    text_edge.append(1)
                    text_edge_ids.append((2,disease_id))
                    text_edge.append(2)
                    text_edge_ids.append((disease_id,2))
                    # 真正对话部分：
                    gotted_sent = []
                    for iid, sent in enumerate(sample['dialogue']): 
                        # 症状整体有一个清单来判断是否有症状（0，1，2），其他的通过实体识别来判断：
                        # bio_list = get_entity_bio(sent['BIO_label'])
                        bio_list = get_entity_bio(json_ner_all_data[pid][str(iid)])
                        symptpm_flag = False
                        if sent['sentence']!="（空）":
                            if sent['dialogue_act'] in ['Inform-Symptom','Inform-Basic_Information','Inform-Etiology']: 
                                # 如果有症状且有为1的，那么这条边算连上了：
                                for type_ in sent['symptom_type']:
                                    if int(type_) == 1:
                                        symptpm_flag =True
                                        break 
                                if symptpm_flag:
                                    text_edge.append(1)
                                    text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                    text_edge.append(2)
                                    text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                                    gotted_sent.append(sent2id[sent['sentence']])
                                    continue 
                            
                            check_flag, cure_flag = False,False
                            if sent['dialogue_act'] in ['Inform-Existing_Examination_and_Treatment','Inform-Medical_Advice','Inform-Precautions']: # check 和 operation 都可以
                                check_flag = judge_ent_label(bio_list,'Medical_Examination')
                                cure_flag = judge_ent_label(bio_list,'Operation')
                                if check_flag:
                                    # text_edge.append(5)
                                    text_edge.append(1)
                                    text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                    # text_edge.append(6)
                                    text_edge.append(2)
                                    text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                                    gotted_sent.append(sent2id[sent['sentence']])
                                    continue 
                                if cure_flag:
                                    # text_edge.append(7)
                                    text_edge.append(1)
                                    text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                    # text_edge.append(8)
                                    text_edge.append(2)
                                    text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                                    gotted_sent.append(sent2id[sent['sentence']])
                                    continue 
                            
                            drug_flag = False
                            if sent['dialogue_act'] in ['Inform-Existing_Examination_and_Treatment','Inform-Drug_Recommendation','Inform-Precautions']:
                                drug_flag = judge_ent_label(bio_list,'Drug') or judge_ent_label(bio_list,'Drug_Category')
                                if drug_flag:
                                    # text_edge.append(3)
                                    text_edge.append(1)
                                    text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                    # text_edge.append(4)
                                    text_edge.append(2)
                                    text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                                    gotted_sent.append(sent2id[sent['sentence']])
                                    continue 
                            
                            if sent['dialogue_act'] in ['Diagnose']:
                                # text_edge.append(9)
                                text_edge.append(1)
                                text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                # text_edge.append(10)
                                text_edge.append(2)
                                text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                    # 整体检查一遍，有一些类别如果没有这类边的话，直接使用最相关的intent进行添加：
                    # 若果没有症状：
                    if 1 not in text_edge:
                        for sent in sample['dialogue']: 
                            if sent['sentence']!="（空）":
                                if sent['dialogue_act'] in ['Inform-Symptom','Inform-Basic_Information'] and (sent2id[sent['sentence']] not in gotted_sent):
                                    text_edge.append(1)
                                    text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                    text_edge.append(2)
                                    text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                    if 3 not in text_edge:
                        for sent in sample['dialogue']: 
                            if sent['sentence']!="（空）":
                                if sent['dialogue_act'] in ['Inform-Drug_Recommendation'] and (sent2id[sent['sentence']] not in gotted_sent):
                                    # text_edge.append(3)
                                    text_edge.append(1)
                                    text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                    # text_edge.append(4)
                                    text_edge.append(2)
                                    text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                    if 5 not in text_edge:
                        for sent in sample['dialogue']: 
                            if sent['sentence']!="（空）":
                                if sent['dialogue_act'] in ['Inform-Medical_Advice','Inform-Existing_Examination_and_Treatment'] and (sent2id[sent['sentence']] not in gotted_sent):
                                    # text_edge.append(5)
                                    text_edge.append(1)
                                    text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                    # text_edge.append(6)
                                    text_edge.append(2)
                                    text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                    if 7 not in text_edge:
                        for sent in sample['dialogue']: 
                            if sent['sentence']!="（空）":
                                if sent['dialogue_act'] in ['Inform-Precautions'] and (sent2id[sent['sentence']] not in gotted_sent):
                                    # text_edge.append(7)
                                    text_edge.append(1)
                                    text_edge_ids.append((sent2id[sent['sentence']]+2,disease_id))
                                    # text_edge.append(8)
                                    text_edge.append(2)
                                    text_edge_ids.append((disease_id,sent2id[sent['sentence']]+2))
                    
                else:
                    continue
                    # TODO: 也可以尝试一下如果用正确的疾病的话，到时候会不会有效果的更大提升：
                    disease_name = find_disease(sent2ent,medical_json)
                    # assert disease_name != ''
                    if disease_name == '':
                        pass
                        # print(pid)
                # TODO:貌似中文需要分一下词(以及生成部分可以限定一下优先生成词典中的词)
                content = ' [SEP] '.join([' '.join(cont) for cont in content]) + ' [SEP]'
                src_path = save_ap+'.src.txt'
                for i in range(1):
                    with open(src_path,'a+',encoding='utf-8') as fp:
                        fp.write(content+'\n')

                node_path = save_ap+'.node_type.txt'
                text_node = [str(i) for i in text_node]
                for i in range(1):
                    with open(node_path,'a+',encoding='utf-8') as fp:
                        fp.write(' '.join(text_node)+'\n')

                edge_path = save_ap+'.edge_type.txt'
                text_edge = [str(i) for i in text_edge]
                for i in range(1):
                    with open(edge_path,'a+',encoding='utf-8') as fp:
                        fp.write(' '.join(text_edge)+'\n')

                edge_id_path = save_ap+'.edge_index.txt'
                text_edge_ids = [' '.join((str(x),str(y))) for x,y in text_edge_ids]
                for i in range(1):
                    with open(edge_id_path,'a+',encoding='utf-8') as fp:
                        fp.write(' , '.join(text_edge_ids)+'\n')
                # print(content,'\n',text_node,'\n',text_edge,'\n',text_edge_ids,'\n')
                # save 

# %%
with open('./data/test.edge_index.txt','r',encoding='utf-8') as fp:
    a = fp.readlines()
    print(a[0])

# %%
a = [(1,2),(2,3)]
a = [(str(x),str(y)) for x,y in a]
for i in a:
    print(' '.join(i))

# %%
medical_json.keys()

# %%
# set.union(medical_json['小儿消化不良']['check'],medical_json['小儿腹泻']['check'])
# medical_json['小儿腹泻']['check']
# a = sorted(medical_json['小儿支气管炎']['symptom'].items(), key=lambda x: x[1],reverse=True)
a = sorted(medical_json['小儿消化不良']['symptom'].items(), key=lambda x: x[1],reverse=True)
# c = sorted(medical_json['新生儿黄疸']['symptom'].items(), key=lambda x: x[1],reverse=True)
# a = sorted(medical_json['小儿支气管炎']['drug'].items(), key=lambda x: x[1],reverse=True)
# b = sorted(medical_json['上呼吸道感染']['drug'].items(), key=lambda x: x[1],reverse=True)
# c = sorted(medical_json['小儿支气管肺炎']['drug'].items(), key=lambda x: x[1],reverse=True)
# a1 = sorted(medical_json['小儿支气管炎']['symptom'].items(), key=lambda x: x[1],reverse=True)
# b1 = sorted(medical_json['上呼吸道感染']['symptom'].items(), key=lambda x: x[1],reverse=True)
# c1 = sorted(medical_json['小儿支气管肺炎']['symptom'].items(), key=lambda x: x[1],reverse=True)
# a2 = sorted(medical_json['小儿支气管炎']['cure'].items(), key=lambda x: x[1],reverse=True)
# b2 = sorted(medical_json['上呼吸道感染']['cure'].items(), key=lambda x: x[1],reverse=True)
# c2 = sorted(medical_json['小儿支气管肺炎']['cure'].items(), key=lambda x: x[1],reverse=True)
# a = sorted(medical_json['小儿支气管炎']['cure'].items(), key=lambda x: x[1],reverse=True)
b = sorted(medical_json['小儿消化不良']['cure'].items(), key=lambda x: x[1],reverse=True)
c = sorted(medical_json['小儿消化不良']['drug'].items(), key=lambda x: x[1],reverse=True)
# c = sorted(medical_json['新生儿黄疸']['cure'].items(), key=lambda x: x[1],reverse=True)
print(a)
print(b)
print(c)
# print(a1)
# print(b1)
# print(c1)
# print(a2)
# print(b2)
# print(c2)
# medical_json['小儿消化不良']['symptom']
# medical_json['上呼吸道感染']['symptom']
for dkey,dvalue in medical_json.items():
    sum = 0
    for key,value in dvalue.items():
        # 保证每一个子类都要有
        for k,v in value.items():
            if k in ['灌肠']:
                sum += v
                # print(dkey,v)
    # for symptom in ['止咳糖浆']:
    #     if symptom not in dvalue['symptom']:
    #         sum = 0
    #         break
    # if '迪巧' not in dvalue['drug']:
    #     sum = 0
    # if '微量元素' not in dvalue['check']:
    #     sum = 0

    print(dkey,sum)

# %%
instances

# %%
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six
import rouge.rouge_score as rouge_score
import io
import os


class FilesRouge:
    def __init__(self, *args, **kwargs):
        """See the `Rouge` class for args
        """
        self.rouge = Rouge(*args, **kwargs)

    def _check_files(self, hyp_path, ref_path):
        assert(os.path.isfile(hyp_path))
        assert(os.path.isfile(ref_path))

        def line_count(path):
            count = 0
            with open(path, "rb") as f:
                for line in f:
                    count += 1
            return count

        hyp_lc = line_count(hyp_path)
        ref_lc = line_count(ref_path)
        assert(hyp_lc == ref_lc)

    def get_scores(self, hyp_path, ref_path, avg=False, ignore_empty=False):
        """Calculate ROUGE scores between each pair of
        lines (hyp_file[i], ref_file[i]).
        Args:
          * hyp_path: hypothesis file path
          * ref_path: references file path
          * avg (False): whether to get an average scores or a list
        """
        self._check_files(hyp_path, ref_path)

        with io.open(hyp_path, encoding="utf-8", mode="r") as hyp_file:
            hyps = [line[:-1] for line in hyp_file]

        with io.open(ref_path, encoding="utf-8", mode="r") as ref_file:
            refs = [line[:-1] for line in ref_file]

        return self.rouge.get_scores(hyps, refs, avg=avg,
                                     ignore_empty=ignore_empty)


class Rouge:
    DEFAULT_METRICS = ["rouge-1", "rouge-2", "rouge-l"]
    AVAILABLE_METRICS = {
        "rouge-1": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 1, **k),
        "rouge-2": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 2, **k),
        "rouge-3": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 3, **k),
        "rouge-4": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 4, **k),
        "rouge-5": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 5, **k),
        "rouge-l": lambda hyp, ref, **k:
            rouge_score.rouge_l_summary_level(hyp, ref, **k),
    }
    DEFAULT_STATS = ["r", "p", "f"]
    AVAILABLE_STATS = ["r", "p", "f"]

    def __init__(self, metrics=None, stats=None, return_lengths=False,
                 raw_results=False, exclusive=True):
        self.return_lengths = return_lengths
        self.raw_results = raw_results
        self.exclusive = exclusive

        if metrics is not None:
            self.metrics = [m.lower() for m in metrics]

            for m in self.metrics:
                if m not in Rouge.AVAILABLE_METRICS:
                    raise ValueError("Unknown metric '%s'" % m)
        else:
            self.metrics = Rouge.DEFAULT_METRICS

        if self.raw_results:
            self.stats = ["hyp", "ref", "overlap"]
        else:
            if stats is not None:
                self.stats = [s.lower() for s in stats]

                for s in self.stats:
                    if s not in Rouge.AVAILABLE_STATS:
                        raise ValueError("Unknown stat '%s'" % s)
            else:
                self.stats = Rouge.DEFAULT_STATS

    def get_scores(self, hyps, refs, avg=False, ignore_empty=False):
        if isinstance(hyps, six.string_types):
            hyps, refs = [hyps], [refs]

        if ignore_empty:
            # Filter out hyps of 0 length
            hyps_and_refs = zip(hyps, refs)
            hyps_and_refs = [_ for _ in hyps_and_refs
                             if len(_[0]) > 0
                             and len(_[1]) > 0]
            hyps, refs = zip(*hyps_and_refs)

        assert(isinstance(hyps, type(refs)))
        assert(len(hyps) == len(refs))

        if not avg:
            return self._get_scores(hyps, refs)
        return self._get_avg_scores(hyps, refs)

    def _get_scores(self, hyps, refs):
        scores = []
        for hyp, ref in zip(hyps, refs):
            sen_score = {}

            hyp = [" ".join(_.split()) for _ in hyp.split(".") if len(_) > 0]
            ref = [" ".join(_.split()) for _ in ref.split(".") if len(_) > 0]

            for m in self.metrics:
                fn = Rouge.AVAILABLE_METRICS[m]
                sc = fn(
                    hyp,
                    ref,
                    raw_results=self.raw_results,
                    exclusive=self.exclusive)
                sen_score[m] = {s: sc[s] for s in self.stats}

            if self.return_lengths:
                lengths = {
                    "hyp": len(" ".join(hyp).split()),
                    "ref": len(" ".join(ref).split())
                }
                sen_score["lengths"] = lengths
            scores.append(sen_score)
        return scores

    def _get_avg_scores(self, hyps, refs):
        scores = {m: {s: 0 for s in self.stats} for m in self.metrics}
        if self.return_lengths:
            scores["lengths"] = {"hyp": 0, "ref": 0}

        count = 0
        for (hyp, ref) in zip(hyps, refs):
            hyp = [" ".join(_.split()) for _ in hyp.split(".") if len(_) > 0]
            ref = [" ".join(_.split()) for _ in ref.split(".") if len(_) > 0]

            for m in self.metrics:
                fn = Rouge.AVAILABLE_METRICS[m]
                sc = fn(hyp, ref, exclusive=self.exclusive)
                scores[m] = {s: scores[m][s] + sc[s] for s in self.stats}

            if self.return_lengths:
                scores["lengths"]["hyp"] += len(" ".join(hyp).split())
                scores["lengths"]["ref"] += len(" ".join(ref).split())

            count += 1
        avg_scores = {
            m: {s: scores[m][s] / count for s in self.stats}
            for m in self.metrics
        }

        if self.return_lengths:
            avg_scores["lengths"] = {
                k: scores["lengths"][k] / count
                for k in ["hyp", "ref"]
            }

        return avg_scores


# %%
# rouge = Rouge()
rouge_ = Rouge()

# %%
ref = '主诉：阵发性咳嗽，偶有痰，食欲不振。现病史：5岁患儿6月份开始阵发性咳嗽，晨间起床严重，有痰，食欲不振，7天前曾有发烧和淋巴结肿大。辅助检查：血常规。既往史：不详。诊断：支气管炎。建议：免疫调节剂，支原体检查。'
# (0.44318181336841433, 0.21459226991766298, 0.3181818133684143)
chat1 = '主诉：持续咳嗽；既往史：无喘息发作、过敏性体质，无湿疹；最近一个月内经历过发烧和淋巴结肿大，血项正常，未进行胸片检查；目前咳嗽主要集中在早上，夜间没咳嗽，咳痰但咳不出来；有口唇苍白的情况。存在支原体感染和过敏体质的可能。建议进行支原体检查并对肺功能进行检查。使用免疫调节剂需要长时间口服，短时间内效果不明显。'
# 原来的
# (0.44318181336841433, 0.21459226991766298, 0.3181818133684143)
chat2 = '主诉：咳嗽7个月。现病史：患儿自7月份以来断断续续地咳嗽，主要在早上集中表现。无过敏、体质异常等明显表现。没有进行胸片检查。较早前曾发烧、淋巴结肿大等症状。辅助检查：血项正常。诊断：支原体感染或过敏性咳嗽。建议：进行支原体的检查，注意肺功能检查，长期应用免疫调节剂。'
a = ' '.join(ref)
b = ' '.join(chat2)
c = ' '.join(chat1)

rouge_score = rouge_.get_scores(b,a)
# rouge_score_ = rouge_.get_scores(c,a)

# rouge_1 = rouge_score[0]["rouge-1"]["f"]
# rouge_2 = rouge_score[0]["rouge-2"]["f"]
# rouge_l = rouge_score[0]["rouge-l"]["f"]

rouge_1 = rouge_score[0]["rouge-1"]["f"]
rouge_2 = rouge_score[0]["rouge-2"]["f"]
rouge_l = rouge_score[0]["rouge-l"]["f"]

# %%
rouge_1,rouge_2,rouge_l

# %%
rouge_1_,rouge_2_,rouge_l_


