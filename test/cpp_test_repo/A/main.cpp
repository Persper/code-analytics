#include "stdafx.h"
#include "TextFileParsers.h"
#include "Utility.h"

using namespace std;

int main(int argc, char* argv[])
{
	auto ifs = OpenAndValidate<ifstream>("config.txt");
	auto parser = ConfigurationParser(ifs);
	cout << parser.GetBool("testBool", false) << endl;
	return 0;
}
