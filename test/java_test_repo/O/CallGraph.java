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

    public static int FunctionCallerConditionals(int a, int b, int c){
        int a = 30;
        if(a == 30){
            addMoreAgain(30);
        }

        if(add40(30) == 30){
            int a = greater30(30) + anotherValueAgain(90);
        }
    }
 }
