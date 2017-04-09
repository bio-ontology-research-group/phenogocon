new File("go-to-pheno.txt").eachLine { line ->
  if (line.indexOf("GO_")>-1) {
    def pat = /cl=<(.*?)>/
    def match = (line =~ pat)
    def cl = ""
    def go = ""
    if (match.size()>0) {
      cl = match[0][1]
    }
    pat = /e=.<(.*?)>./
    match = (line =~ pat)
    if (match.size()>0) {
      go = match[0][1]
    }
    pat = /q=.<(.*?)>./
    match = (line =~ pat)
    if (match.size()>0 && go.size()>0) {
      println "$cl\t$go\t"+match[0][1]
    }
  }
}
