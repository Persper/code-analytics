#include "stdafx.h"
#include "Utility.h"

using namespace std;

#define _DECLARE_ENUM(TYPE, MEMBER) case TYPE::MEMBER : return #MEMBER;
#define _DECLARE_ENUM_DEFAULT(TYPE) default : return string(#TYPE) + "::" + to_string((long)v);

bool Equal(const string& lhs, const string& rhs, StringComparison comparision)
{
	if (&lhs == &rhs) return true;
	size_t pos1 = 0, pos2 = 0;
	size_t pos1r = lhs.size(), pos2r = rhs.size();
	if ((comparision & StringComparison::IgnoreSurroudingWhiteSpaces)
		== StringComparison::IgnoreSurroudingWhiteSpaces)
	{
		while (pos1 < lhs.size() && isspace(lhs[pos1])) pos1++;
		while (pos2 < lhs.size() && isspace(lhs[pos2])) pos2++;
		while (pos1 > 0 && isspace(lhs[pos1 - 1])) pos1--;
		while (pos2 > 0 && isspace(lhs[pos2 - 1])) pos2--;
	}
	if (pos1r - pos1 != pos2r - pos2) return false;
	auto ignoreCase = (comparision & StringComparison::IgnoureCase) == StringComparison::IgnoureCase;
	while (pos1 < pos1r)
	{
		if (ignoreCase)
		{
			if (tolower(lhs[pos1]) != tolower(rhs[pos1])) return false;
		} else
		{
			if (lhs[pos1] != rhs[pos1]) return false;
		}
		pos1++;
		pos2++;
	}
	return true;
}

bool Confirm(const std::string& prompt)
{
	cout << prompt << " (Y/N)> " << flush;
	while (true)
	{
		string buffer;
		getline(cin, buffer);
		stringstream ss(buffer);
		if (ss >> buffer)
		{
			transform(buffer.begin(), buffer.end(), buffer.begin(), [](char c) {return tolower(c); });
			if (buffer == "y" || buffer == "yes") return true;
			if (buffer == "n" || buffer == "no") return false;
		}
		cout << "无效的输入。> " << flush;
	}
}

void ReportException(const exception& ex, int level)
{
	if (level > 0)
	{
		cerr << "<-";
		for (int i = 0; i < level; i++) cerr << '-';
		cerr << ' ';
	}
	cerr << "[" << typeid(ex).name() << "] " << ex.what() << endl;
	try {
		rethrow_if_nested(ex);
	}
	catch (const exception& subEx) {
		ReportException(subEx, level + 1);
	}
	catch (...)
	{
		cerr << "[Unknown Exception]" << endl;
	}
}
