#include "stdafx.h"
#include "TextFileParsers.h"
#include "Utility.h"

using namespace std;

int main(int argc, char* argv[])
{
	auto ifs = OpenAndValidate<ifstream>("config.txt");
	auto parser = ConfigurationParser(ifs);
	cout << parser.GetBool("testBool", false) << endl;
	cout << parser.GetDouble("textDouble", 1.23) << endl;
	cout << parser.GetString("rawValue", "test") << endl;
	return 0;
}
