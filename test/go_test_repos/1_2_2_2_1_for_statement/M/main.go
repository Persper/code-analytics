package main
import(
	"fmt"
)


func funcA () bool{
	fmt.Println("func A is called!")
	return true
}

func main() {
	for i :=0;i<10;i++{
		funcA()
	}
}

