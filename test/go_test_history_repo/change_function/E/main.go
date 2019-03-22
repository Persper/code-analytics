package main
import(
	"fmt"
)


func funcB (a int) {
	fmt.Println("func A is called!")
}

func main() {
	funcB(1)
}