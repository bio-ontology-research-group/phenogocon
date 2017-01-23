import os
import multiprocessing


def worker(q, indir, morbid_omim_to_entrez, rank_to_truepos):
	while True:
		filename = q.get()
		omim = filename.strip(".txt")
		if q.qsize() % 100 == 0:
			print "%d omim's left in queue" % q.qsize()
		with open(indir + filename) as f:
			row = []
			for line in f:
				tabs = line.strip().split('\t')
				if len(tabs) < 2:
					continue
				name = tabs[0].split()[0] # in case of weird duplication in first column
				if "ENTREZ" in name:
					name = name.replace("ENTREZ:", "")
				# else:
					# if name in human_symbol_to_entrez:
						# name = human_symbol_to_entrez[name]
					# else:
						# continue
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
		for rank, pair in enumerate(temp):
			entrez = pair[1]
			if omim in morbid_omim_to_entrez and entrez == morbid_omim_to_entrez[omim]:
				if rank not in rank_to_truepos:
					rank_to_truepos[rank] = 0
				rank_to_truepos[rank] += 1
		
		q.task_done()

		
if __name__ == '__main__':
	multiprocessing.freeze_support()

	original = "sim_original/"
	combined = "sim_combined/"
	solo = "sim_solo/"

	indir = solo

	num_procs = 4

	entrez_to_id = dict()
	id_to_gene = dict()
	entrez_to_gene = dict()
	gene_to_entrez = dict()
	morbid_omim_to_genes = dict()

	mouse_mgi_to_entrez = dict()
	omim_to_entrez = dict()
	# human_omim_to_entrez = dict()
	# human_symbol_to_entrez = dict()

	# table = dict()
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
			elif "human" in tabs[1]:
			    # id_to_gene[tabs[0]] = tabs[3]
			    # entrez_to_gene[tabs[4]] = tabs[3]
			    omim = tabs[7]
			    omim_to_entrez[omim] = entrez
			    # symbol = tabs[3]
			    # human_symbol_to_entrez[symbol] = entrez
	
	morbid_omim_to_entrez = dict()
	print "Reading morbidmap..."
	with open("morbidmap.txt", 'r') as f:
		for line in f:
			if line[0] in "!#":
				continue

			# tabs = line.strip('\n').split('\t')
			# pheno = tabs[0].split()
			# if len(pheno[-2]) == 6:
				# pheno = pheno[-2]
			# else:
				# continue
			# mim = tabs[2]
			# if mim in human_omim_to_entrez:
				# morbid_omim_to_entrez[pheno] = human_omim_to_entrez[mim]
			
			spacetabs = line.strip('\n').split(' ')
			for x in spacetabs:
				if len(x) == 6 and x.isdigit():
					pheno = x
					break
					
			linetabs = line.strip('\n').split('|')
			for x in linetabs:
				if len(x) == 6 and x.isdigit():
					mim = x
					break
					
			if mim in omim_to_entrez:
				morbid_omim_to_entrez[pheno] = omim_to_entrez[mim]

	
	print "Building queue of tasks..."
	q = multiprocessing.JoinableQueue()
	# out_q = multiprocessing.Queue()
	
	counter = 0
	for root, dirs, filenames in os.walk(indir):
		for filename in filenames:
			if counter >= 999999999:
				break
			q.put(filename)
			counter += 1

	print "Queue has %d tasks" % q.qsize()
	
	manager = multiprocessing.Manager()
	rank_to_truepos = manager.dict()
	lock = multiprocessing.Lock()
	
	for i in range(num_procs):
		t = multiprocessing.Process(target=worker, args=(q, indir, morbid_omim_to_entrez, rank_to_truepos))
		t.daemon = True
		t.start()
	q.join()
	
	print "Calculating rates..."
	
	# print rank_to_truepos
	
	max_rank = max(rank_to_truepos.keys())
	total = sum(rank_to_truepos.values())
	true_pos_rate = 0.0
	
	with open("output.txt", 'w') as g:
		for rank in range(max_rank + 1):
			if rank in rank_to_truepos.keys():
				true_pos = rank_to_truepos[rank]
			else:
				true_pos = 0
			true_pos_rate += (float(true_pos)/total)
			result = "%d\t%f\n" % (rank+1, true_pos_rate)
			g.write(result)