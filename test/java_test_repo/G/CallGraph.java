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
        int sum = a + b + c;
        int add = a + b;
        int sub = a - b;
        doStuff();
    }

}