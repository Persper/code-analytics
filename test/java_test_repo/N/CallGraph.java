package testers;

public class CallGraphs
{
    public static void main(String[] args) {
	    doStuff();
    }

    public static void doStuff() {
	    new A().foo();
    }

    public static void AddChangeFunction(int a, int b, int c){
        int summation = a + b + c;
        int addition = a + b;
        int subtraction = a - b;
    }

    public static int FunctionCaller(int a, int b, int c){
        int a = 30 + addMore(30);
        addNewNumber(add40(40), 20, 30);
        int a = returnBigValues();
        int b = sumValue(90) + anotherValue(80);
    }
}