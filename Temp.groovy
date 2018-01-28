def omims = new HashSet<String>();
def mgis = new HashSet<String>();
new File("data/mgi_omim.tab").eachLine { line ->
  if (line.startsWith("#")) return;
    def items = line.split("\t")
    omims.addAll(items[2].split("\\|"))
    mgis.add(items[8])
}

println(mgis)
