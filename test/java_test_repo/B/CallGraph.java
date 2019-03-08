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

class A
{
    public void foo() {
	System.out.println("A.foo() executed.");
	bar();
    }

    public void bar() {
	System.out.println("A.bar() executed.");
    }
}
