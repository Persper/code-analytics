package main
import(
	"fmt"
)


func funcA () bool{
	fmt.Println("func A is called!")
	return true
}

func main() {
	switch 1 {
	case 1:
		funcA()
	case 2:
		fmt.Println("2")
	}
}

