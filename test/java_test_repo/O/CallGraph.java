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

    public static int FunctionCallerConditionalsSwitch(int a, int b, int c){
        int day = 5;
        String dayString;

        // switch statement with int data type
        switch (day) {
        case 1:
            dayString = "Monday";
            getDay(dayString);
            break;
        case 2:
            dayString = "Tuesday";
            break;
        case 3:
            dayString = "Wednesday";
            break;
        case 4:
            dayString = "Thursday";
            break;
        case getNumDay("Friday"):
            dayString = "Friday";
            break;
        case 6:
            dayString = "Saturday";
            break;
        case 7:
            dayString = "Sunday";
            break;
        default:
            dayString = "Invalid day";
            break;
        }
    }
 }
