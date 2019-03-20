package main
import(
	"fmt"
	"math"
)

type Vertex struct {
	X, Y float64
}

func (v Vertex) Abs() float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func funcA () {
	fmt.Println("func A is called!")
}

func funcB () {
	fmt.Println("func B is called!")
}

func main() {
	funcA()
	funcB()
	v := Vertex{3, 4}
	fmt.Println(v.Abs())
}

