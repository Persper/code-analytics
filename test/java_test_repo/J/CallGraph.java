package testers;

public class CallGraphs
{
    public static void main(String[] args) {
	    doStuff();
    }

    public static void doStuff() {
	    new A().foo();
    }public static void AddChangeFunction(int a, int b, int c){
        int summation = a + b + c;
        int addition = a + b;
        int subtraction = a - b;
        doStuff();
    }

}