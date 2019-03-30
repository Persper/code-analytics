package main
import(
	"fmt"
	"math"
)
type polygon interface{
	printInfo()
}
type square int
type rectangle int

type Vertex struct {
	X, Y float64
}

func (c square) printInfo(){
    fmt.Println("square")
}

func (d rectangle) printInfo(){
    fmt.Println("rectangle")
}

func (v Vertex) Abs() float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}
func (v *Vertex) Absp() float64{
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func funcA () {
	fmt.Println("func A is called!")
}

func main() {
	v := Vertex{3, 4}
	fmt.Println(v.Abs())
	p := &Vertex{4,5}
	fmt.Println(p.Absp())
	var sq square
	var re rectangle
	sq.printInfo()
	re.printInfo()
}

