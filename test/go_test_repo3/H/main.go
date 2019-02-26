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
type a func()

type Vertex struct {
	X, Y float64
}
type Rect struct{
	width,height float64
}
func (c square) printInfo(){
    fmt.Println("square")
}

func (d rectangle) printInfo(){
    fmt.Println("rectangle")
}

func invoke (a polygon){
	a.printInfo()
}

func (v Rect) Abs() float64{
	return v.width * v.height
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
	a := funcA
	a()
	v := Vertex{3, 4}
	fmt.Println(v.Abs())
	p := &Vertex{4,5}
	fmt.Println(p.Absp())
	var sq square
	var re rectangle
	sq.printInfo()
	re.printInfo()
	invoke(sq)
	invoke(re)
	closure1 := func(i int) int{
		return i * i
	}
	closure2 := func(i int) int{
		return i * i
	}
	fmt.Println(closure1(7))	
	fmt.Println(closure2(8))	
	r := Rect{3,4}
	fmt.Println(r.Abs())
}

