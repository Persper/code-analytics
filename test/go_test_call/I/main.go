package main
import(
	"fmt"
)


func funcA () bool{
	fmt.Println("func A is called!")
	return true
}

func main() {
	if(funcA()){
		fmt.Println("yes")
	}
}
