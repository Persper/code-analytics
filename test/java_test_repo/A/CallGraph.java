package testers;

public class CallGraphs
{
    static private A field;
    public static void main(String[] args) {
	field = new B();
	doStuff();
    }

    public static void doStuff() {
	new A().foo();
    }
}


