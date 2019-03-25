package main
import(
	"fmt"
)

func return_1 () int{
	return 1
}

func funcB (a int) {
	fmt.Println("func A is called!")
}

func main() {
	funcB(return_1())
	var a = 1
	a = a + return_1()

}