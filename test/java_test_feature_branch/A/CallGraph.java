package testers;

public class CallGraphs
{
    public static void main(String[] args) {
	    doStuff();
    }

    public static void doStuff() {
	    new A().foo();
    }

    public static void addFunction(int a, int b){
        int sum = a + b;
        doStuff();
    }
}