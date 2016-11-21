#include <deque>
#include <iostream>
#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <utility>
#include <vector>

#include <thread>
#include <mutex>
#include <condition_variable>

using namespace std;



int main()
{
	int num_threads = 48;

	string original = "sim_original/";
	string combined = "sim_combined/";
	string solo = "sim_solo/";
	vector<string> folders = { original, combined, solo };

	string line;
	stringstream ss;

	map<string, map<int, vector<pair<double, int> > > > file_to_matrix;
	// maps filename to matrix
	// matrix maps omim to vector of pairs of (score, gene)
	map<string, set<pair<int, int> > > file_to_set;
	// maps filename to set of (gene, disease) pairs
		
	// read morbid map
	map<int, int> morbid_gene_to_disease;
	cout << "Reading morbidmap..." << endl;
	ifstream morbidmap("morbidmap.txt", ios::in);
	while (getline(morbidmap, line))  
	{
		// check if comment
		if (line[0] == '!' || line[0] == '#')
			continue;

		// read tab-separated line into tokens
		istringstream iss(line);
		string token;
		vector<string> tokens;
		while (getline(iss, token, '\t'))
			tokens.push_back(token);

		// read disease OMIM
		size_t pos1 = tokens[0].rfind(',');
		size_t pos2 = tokens[0].rfind('(');
		ss = stringstream(tokens[0].substr(pos1 + 1, pos2));
		int disease;
		ss >> disease;

		// read gene OMIM
		int gene;
		ss = stringstream(tokens[2]);
		ss >> gene;

		// add gene, diease to map
		morbid_gene_to_disease[gene] = disease;
	}
	morbidmap.close();

	// map symbols to omims
	map<string, int> symbol_to_omim;
	cout << "Mapping symbols to omims..." << endl;
	ifstream mousehumanseq("HOM_MouseHumanSequence.rpt", ios::in);
	while (getline(mousehumanseq, line))
	{
		// read tab-separated line into tokens
		istringstream iss(line);
		string token;
		vector<string> tokens;
		while (getline(iss, token, '\t'))
			tokens.push_back(token);

		if (tokens[1].find("human") != string::npos)
		{
			string symbol = tokens[3];
			int gene;
			ss = stringstream(tokens[7]);
			ss >> gene;
			symbol_to_omim[symbol] = gene;
		}
	}
	mousehumanseq.close();
	

	
	//table = dict()
	//table_width = 0
	//
	//print "Building queue of tasks..."
	//q = multiprocessing.JoinableQueue()
	//out_q = multiprocessing.Queue()
	//
	//for root, dirs, filenames in os.walk(solo) :
	//	for filename in filenames :
	//q.put(filename)
	//
	//print "Queue has %d tasks" % q.qsize()
	//
	//def worker(q, output_queue) :
	//	while True :
	//		filename = q.get()
	//		if q.qsize() % 500 == 0 :
	//			print "%d omim's left in queue" % q.qsize()
	//			with open(indir + filename) as f :
	//omim = filename.strip(".txt")
	//row = []
	//for line in f :
	//tabs = line.strip().split('\t')
	//if len(tabs) < 2 :
	//	continue
	//	name = tabs[0].split()[0] # in case of weird duplication in first column
	//	if "ENTREZ" in name :
	//name = name.replace("ENTREZ:", "")
	//	else:
	//		if name in human_symbol_to_entrez :
	//		name = human_symbol_to_entrez[name]
	//		else :
	//			continue
	//			score = float(tabs[1])
	//			row.append((score, name))
	//			closed = set()
	//			temp = []
	//			for pair in row :
	//		if pair[1] in closed :
	//		continue
	//			closed.add(pair[1])
	//			temp.append(pair)
	//			temp.sort(reverse = True)
	//			output_queue.put((omim, temp))
	//			q.task_done()
	//
	//			lock = multiprocessing.Lock()
	//			manager = multiprocessing.Manager()
	//			for i in range(num_procs) :
	//				t = multiprocessing.Process(target = worker, args = (q, out_q, ))
	//				t.daemon = True
	//				t.start()
	//				q.join()
	//
	//				print "Tasks completed"
	//				while out_q.qsize() > 0:
	//		(omim, row) = out_q.get()
	//			table_width = max(table_width, len(row))
	//			table[omim] = row
	//
	//
	//			print "Calculating rates..."
	//			true_pos_rate = 0.0
	//			with open("output.txt", 'w') as g :
	//		for rank in range(table_width) :
	//			total = 0
	//			true_pos = 0
	//			for omim in table :
	//		if len(table[omim]) < rank + 1 :
	//			continue
	//			total += 1
	//			entrez = table[omim][rank][1]
	//			if omim in morbid_omim_to_entrez and entrez == morbid_omim_to_entrez[omim] :
	//				true_pos += 1
	//				# print omim, entrez
	//				true_pos_rate += (float(true_pos) / total)
	//				result = "%d\t%f\n" % (rank + 1, true_pos_rate)
	//				# print result
	//				g.write(result)

	return 0;
}