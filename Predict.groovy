def rules = [:].withDefault {new HashSet()}
new File("data/rules_prop.txt").splitEachLine("\t") { items ->
    def go = items[0]
    def pheno = items[1]
    def qual = items[2]
    rules[go].add("$pheno\t$qual")
}


def expCodes = ["EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "TAS", "IC"]
def annotations = [:].withDefault{ new HashSet() }
new File("data/goa_human.gaf").splitEachLine("\t") { items ->
    if (items.size() > 1) {
        def gene = items[2]
        if (!(items[6] in expCodes) || items[3] == "NOT") { // Filter out electronic annotations
            return
        }
    	if (items[15] != null && items[15].indexOf("CL:") != -1) { // Filter out annotations for specific cell part
    	    return;
    	}
        if (items[4] != null && items[4].startsWith("GO:")) {
            def go = items[4].replaceAll(":", "_")
            annotations[gene].add(go)
        }
    }

    gene = items[0]
    for (int i = 1; i < items.size(); i++) {
	annotations[gene].add(items[i].replaceAll(":", "_"))
    }
}


out = new PrintWriter(new BufferedWriter(new FileWriter("data/predictions_prop_human.txt")))

annotations.each { gene, gos ->
    gos.each { go ->
	rules[go].each {pred ->
	    if (pred.startsWith('MP_') || pred.startsWith('HP_')) {
		out.println("$gene\t$go\t$pred");
	    }
	}
    }
}

out.flush()
out.close()

