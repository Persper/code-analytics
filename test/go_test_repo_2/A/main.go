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

func (d dog) printInfo(){
    fmt.Println("a dog")
}

func main() {
    var a animal
    var c cat
    a=c
    a.printInfo()
    //other type 
    var d dog
    a=d
    a.printInfo()
}