package main

import ("os"
    "fmt"
    "strconv"
    "gitlab.com/meri.co/test/calcproj/src/simplemath")


var Usage = func() {
    fmt.Println("USAGE: calc command [arguments] ...")
    fmt.Println("\nThe commands are:\n\tadd\tAddition of two values.\n\tsqrt\tSquare root of a non-negative value.")
}

func main() {
    args := os.Args
    if args == nil || len(args) < 2 {
        Usage()
        return
    }

    switch args[1] {
    case "add":
        if len(args) != 4 {
            fmt.Println("USAGE: calc add <integer1> <integer2>")
            return
        }

        v1, err1 := strconv.Atoi(args[2])
        v2, err2 := strconv.Atoi(args[3])
        if err1 != nil || err2 != nil {
            fmt.Println("USAGE: calc add <integer1> <integer2>")
            return
        }

        ret := sm.Add(v1, v2)
        fmt.Println("Result: ", ret)
    case "sqrt":
        if len(args) != 3 {
            fmt.Println("USAGE: calc sqrt <integer>")
            return
        }

        v, err := strconv.Atoi(args[2])
        if err != nil {
            fmt.Println("USAGE: calc sqrt <integer>")
            return
        }

        ret := sm.Sqrt(v)
        fmt.Println("Result: ", ret)
    default:
        Usage()
    }
}