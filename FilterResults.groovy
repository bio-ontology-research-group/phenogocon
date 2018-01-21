import java.utils.*
import java.io.*

BIOLOGICAL_PROCESS = "GO_0008150"
MOLECULAR_FUNCTION = "GO_0003674"
CELLULAR_COMPONENT = "GO_0005575"

FUNCS = [
    BIOLOGICAL_PROCESS,
    MOLECULAR_FUNCTION,
    CELLULAR_COMPONENT
].toSet()

FILTER = ["increase_inconsistent", "decrease_inconsistent"].toSet()

new File("data/predictions_deep_mouse.txt").eachLine() { line ->
    def items = line.trim().split("\t")
    if (!(items[3] in FILTER)) {
        println(line)
    }
}
