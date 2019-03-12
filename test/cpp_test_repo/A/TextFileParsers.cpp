#include "stdafx.h"
#include "TextFileParsers.h"

using namespace std;
using namespace filesystem;

RowReader& operator>>(RowReader& reader, string& rhs)
{
	// ʹ���Ʊ���ָ���
	getline(reader.ss, rhs, reader.delim);
	// ȥ����������Ŀհס�
	if (!reader.keepWhitespace)
	{
		// Left trim
		auto wsEndsAt = find_if(rhs.begin(), rhs.end(), [](char c) {return c < 0 || !isspace(c); });
		rhs.erase(rhs.begin(), wsEndsAt);
		// Right trim
		auto wsStartsAt = find_if(rhs.rbegin(), rhs.rend(), [](char c) {return c < 0 || !isspace(c); });
		rhs.erase(rhs.rbegin().base(), rhs.end());
	}
	return reader;
}

RowReader& operator>>(RowReader& reader, int& rhs)
{
	string buffer{};
	if (reader >> buffer) rhs = stoi(buffer);
	return reader;
}

RowReader& operator>>(RowReader& reader, long& rhs)
{
	string buffer{};
	if (reader >> buffer) rhs = stol(buffer);
	return reader;
}

RowReader& operator>>(RowReader& reader, float& rhs)
{
	string buffer{};
	if (reader >> buffer) rhs = stof(buffer);
	return reader;
}

RowReader& operator>>(RowReader& reader, double& rhs)
{
	string buffer{};
	if (reader >> buffer) rhs = stod(buffer);
	return reader;
}

RowReader& operator>>(RowReader& reader, bool& rhs)
{
	string buffer{};
	if (reader >> buffer)
	{
		if (Equal(buffer, "true", StringComparison::IgnoureCase | StringComparison::IgnoreSurroudingWhiteSpaces))
			rhs = true;
		else if (Equal(buffer, "false", StringComparison::IgnoureCase | StringComparison::IgnoreSurroudingWhiteSpaces))
			rhs = true;
		else
		{
			try
			{
				auto value = stoi(buffer);
				rhs = (value != 0);
			}
			catch (const exception&)
			{
				throw invalid_argument("Cannot convert to bool.");
			}
		}
	}
	return reader;
}

void ConfigurationParser::Load(istream& inputStream)
{
	string buffer{};
	stringstream ss{};
	size_t lineNumber = 0;
	while (getline(inputStream, buffer))
	{
		lineNumber++;
		ss.clear();
		ss.str(buffer);
		string key{};
		char ch;
		if (!(ss >> key)) continue;
		if (key[0] == '#') continue;
		if (!(ss >> ch) || ch != '=')
			throw Exception("��Ч�������С���������=�����У�" + to_string(lineNumber) + "��");
		string value{};
		if (!(ss >> value))
			throw Exception("��Ч�������С�����������ֵ���У�" + to_string(lineNumber) + "��");
		// ISSUE Ŀǰ����ֵ�в��ܰ����ո񣬷�����ڿո񴦽ضϡ�
		entries[key] = value;
	}
}

std::string ConfigurationParser::GetString(const std::string& key, const std::string& defaultValue) const
{
	auto v = entries.find(key);
	if (v == entries.end()) return defaultValue;
	return v->second;
}

int ConfigurationParser::GetInt(const std::string& key, int defaultValue) const
{
	auto v = entries.find(key);
	if (v == entries.end()) return defaultValue;
	try
	{
		return stoi(v->second);
	} catch (const exception&)
	{
		throw_with_nested(Exception("�޷������á�" + key + "��ֵת��Ϊint��"));
	}
}

double ConfigurationParser::GetDouble(const std::string& key, double defaultValue) const
{
	auto v = entries.find(key);
	if (v == entries.end()) return defaultValue;
	try
	{
		return stod(v->second);
	} catch (const exception&)
	{
		throw_with_nested(Exception("�޷������á�" + key + "��ֵת��Ϊdouble��"));
	}
}

bool ConfigurationParser::GetBool(const std::string& key, bool defaultValue) const
{
	auto v = entries.find(key);
	if (v == entries.end()) return defaultValue;
	if (Equal(v->second, "true", StringComparison::IgnoureCase | StringComparison::IgnoreSurroudingWhiteSpaces))
		return true;
	else if (Equal(v->second, "false", StringComparison::IgnoureCase | StringComparison::IgnoreSurroudingWhiteSpaces))
		return false;
	try
	{
		return stod(v->second);
	} catch (const exception&)
	{
		throw_with_nested(Exception("�޷������á�" + key + "��ֵת��Ϊbool��"));
	}
}

ConfigurationParser::ConfigurationParser(istream& inputStream) : entries()
{
	Load(inputStream);
}

ConfigurationParser::ConfigurationParser(path filePath) : entries()
{
	auto ifs = OpenAndValidate<ifstream>(filePath);
	Load(ifs);
}
