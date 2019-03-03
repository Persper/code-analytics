package main
import(
	"fmt"
)
//This test code is used for test interface function call
type animal interface {
    printInfo()
}

type cat int
type dog int
func (c cat) printInfo(){
    fmt.Println("a cat")
}

func (c dog) printInfo(){
    fmt.Println("a dog")
}
func invoke(a animal){
    a.printInfo()
}
func main() {
    var c cat
	var d dog
	//as value convert
	invoke(c)
	invoke(d)
}
