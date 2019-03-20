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
func (v *Vertex) Absp() float64{
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func funcA () {
	fmt.Println("func A is called!")
}

func main() {
	funcA()
	v := Vertex{3, 4}
	fmt.Println(v.Abs())
	p := &Vertex{4,5}
	fmt.Println(p.Absp())
}

