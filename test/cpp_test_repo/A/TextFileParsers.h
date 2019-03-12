#pragma once
#include <sstream>
#include "Utility.h"

// ���ڴ�����������ȡһ�У��������
class RowReader
{
private:
	std::stringstream ss;
	char delim;
	bool keepWhitespace;
	std::size_t _LineNumber;
public:
	size_t LineNumber() const { return _LineNumber; }
	void ResetLineNumber() { _LineNumber = 0; }
	const std::stringstream& LineStream() const { return ss; }
public:
	operator bool() const
	{
		return bool(ss);
	}
	bool operator !() const
	{
		return !ss;
	}
	template<typename TStream>
	friend TStream& operator>>(TStream& s, RowReader& reader);
	friend RowReader& operator>>(RowReader& reader, std::string& rhs);
public:
	/**
	 * \brief 
	 * \param delim �зָ���
	 */
	explicit  RowReader(bool keepWhitespace = false, char delim = '\t') : ss(), delim(delim), keepWhitespace(keepWhitespace), _LineNumber(0)
	{
	}
};

// ���������ж���һ�зǿշ�ע���С�
template <typename TStream>
TStream& operator>>(TStream& s, RowReader& reader)
{
	std::string buffer{};
	while (getline(s, buffer))
	{
		reader._LineNumber++;
		// �������Ƿ�Ϊע�͡�
		// status
		//	0	start/���հ�
		//	1	#
		//	2	�����ַ�
		char status = 0;
		for (auto& c : buffer)
		{
			switch (status)
			{
			case 0:
				if (c == '#')
				{
					status = 1;
					goto CHECK_STATUS;
				}
				if (c < 0 || !isspace(c))
				{
					status = 2;
					goto CHECK_STATUS;
				}
				break;
			default:
				assert(false);
				break;
			}
		}
	CHECK_STATUS:
		switch (status)
		{
		case 0:
			// �հ���
			break;
		case 1:
			// ע����
			break;
		case 2:
			goto SET_RESULT;
		default:
			assert(false);
			break;
		}
	}
SET_RESULT:
	reader.ss.str(buffer);
	reader.ss.clear();
	return s;
}

RowReader& operator>>(RowReader& reader, std::string& rhs);

RowReader& operator>>(RowReader& reader, int& rhs);

RowReader& operator>>(RowReader& reader, long& rhs);

RowReader& operator>>(RowReader& reader, float& rhs);

RowReader& operator>>(RowReader& reader, double& rhs);

RowReader& operator>>(RowReader& reader, bool& rhs);

class ConfigurationParser
{
private:
	std::unordered_map<std::string, std::string> entries;
	void Load(std::istream& inputStream);
public:
	std::string GetString(const std::string& key, const std::string& defaultValue) const;
	int GetInt(const std::string& key, int defaultValue) const;
	double GetDouble(const std::string& key, double defaultValue) const;
	bool GetBool(const std::string& key, bool defaultValue) const;
public:
	ConfigurationParser(std::istream& inputStream);
	ConfigurationParser(std::filesystem::path filePath);
};