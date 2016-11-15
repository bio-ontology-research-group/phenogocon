import os
import multiprocessing


original = "sim_original/"
combined = "sim_combined/"
solo = "sim_solo/"

files = {solo:dict(), combined:dict()}

num_procs = 48

entrez_to_id = dict()
id_to_gene = dict()
entrez_to_gene = dict()
gene_to_entrez = dict()
morbid_omim_to_genes = dict()

mouse_mgi_to_entrez = dict()
human_omim_to_entrez = dict()
human_symbol_to_entrez = dict()

table = dict()
table_width = 0

print "Mapping omims and symbols to entrez ids..."
with open("HOM_MouseHumanSequence.rpt", 'r') as f:
    f.readline()
    for line in f:
        tabs = line.strip('\n').split('\t')
        entrez = tabs[4]
        if "mouse" in tabs[1]:
            # entrez_to_id[tabs[4]] = tabs[0]
            mgi = tabs[5]
            mouse_mgi_to_entrez[mgi] = entrez
        # elif "human" in tabs[1]:
        #     # id_to_gene[tabs[0]] = tabs[3]
        #     # entrez_to_gene[tabs[4]] = tabs[3]
        #     omim = tabs[7]
        #     human_omim_to_entrez[omim] = entrez
        #     symbol = tabs[3]
        #     human_symbol_to_entrez[symbol] = entrez


morbid_omim_to_entrez = dict()
print "Reading morbidmap..."
with open("morbidmap.txt", 'r') as f:
    for line in f:
        if line[0] in "!#":
            continue
        tabs = line.strip('\n').split('\t')
        pheno = tabs[0].split()
        if len(pheno[-2]) == 6:
            pheno = pheno[-2]
        else:
            continue
        mim = tabs[2]
        if mim in human_omim_to_entrez:
            morbid_omim_to_entrez[pheno] = human_omim_to_entrez[mim]


print "Building queue of tasks..."
q = multiprocessing.JoinableQueue()
out_q = multiprocessing.Queue()

for root, dirs, filenames in os.walk(solo):
    for filename in filenames:
        q.put(filename)

print "Queue has %d tasks" % q.qsize()

def worker(q, output_queue):
    while True:
        filename = q.get()
        if q.qsize() % 500 == 0:
            print "%d omim's left in queue" % q.qsize()
        with open(indir + filename) as f:
            omim = filename.strip(".txt")
            row = []
            for line in f:
                tabs = line.strip().split('\t')
                if len(tabs) < 2:
                    continue
                name = tabs[0].split()[0] # in case of weird duplication in first column
                if "ENTREZ" in name:
                    name = name.replace("ENTREZ:", "")
                else:
                    if name in human_symbol_to_entrez:
                        name = human_symbol_to_entrez[name]
                    else:
                        continue
                score = float(tabs[1])
                row.append((score,name))
        closed = set()
        temp = []
        for pair in row:
            if pair[1] in closed:
                continue
            closed.add(pair[1])
            temp.append(pair)
        temp.sort(reverse=True)
        output_queue.put((omim, temp))
        q.task_done()

lock = multiprocessing.Lock()
manager = multiprocessing.Manager()
for i in range(num_procs):
    t = multiprocessing.Process(target=worker, args=(q, out_q,))
    t.daemon = True
    t.start()
q.join()

print "Tasks completed"
while out_q.qsize() > 0:
    (omim, row) = out_q.get()
    table_width = max(table_width, len(row))
    table[omim] = row


print "Calculating rates..."
true_pos_rate = 0.0
with open("output.txt", 'w') as g:
    for rank in range(table_width):
        total = 0
        true_pos = 0
        for omim in table:
            if len(table[omim]) < rank+1:
                continue
            total += 1
            entrez = table[omim][rank][1]
            if omim in morbid_omim_to_entrez and entrez == morbid_omim_to_entrez[omim]:
                true_pos += 1
                # print omim, entrez
        true_pos_rate += (float(true_pos)/total)
        result = "%d\t%f\n" % (rank+1, true_pos_rate)
        # print result
        g.write(result)
