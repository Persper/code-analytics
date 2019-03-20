package main
import(
	"fmt"
)


func funcA () bool{
	fmt.Println("func A is called!")
	return true
}

func main() {
	a:= true
	switch a {
	case funcA():
		funcA()
	case false:
		fmt.Println("2")
	}
}

