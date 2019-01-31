package main
import(
	"fmt"
	"math"
)
type a func()
type b func()
type c func()
type Vertex struct {
	X, Y float64
}
func (v Vertex) Abs() float64 {
	a:=funcA()
	a()
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}
func funcA () {
	fmt.Println("func A is called!")
}
func funcB () {
	funcA()
	print("func B is called!")
}
func main() {
	a := funcA
	b := funcB
	c := a
	b()
	c()
	v := Vertex{3, 4}
	fmt.Println(v.Abs())
}
