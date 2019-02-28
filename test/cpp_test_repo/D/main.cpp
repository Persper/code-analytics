#include "stdafx.h"
#include "TextFileParsers.h"
#include "Utility.h"

using namespace std;

int main(int argc, char* argv[])
{
	auto ifs = ifstream("config.txt");
	string line{};
	getline(ifs, line);
	cout << line << endl;
	return 0;
}
