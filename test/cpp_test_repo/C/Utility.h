#pragma once

#include <iomanip>
#include "Exceptions.h"
#include <functional>
#include "TypeTraits.h"

#define ANSI_COLOR_RED     "\x1b[31m"
#define ANSI_COLOR_GREEN   "\x1b[32m"
#define ANSI_COLOR_YELLOW  "\x1b[33m"
#define ANSI_COLOR_BLUE    "\x1b[34m"
#define ANSI_COLOR_MAGENTA "\x1b[35m"
#define ANSI_COLOR_CYAN    "\x1b[36m"

#define ANSI_COLOR_BRIGHT  "\x1b[1m"
#define ANSI_COLOR_RESET   "\x1b[0m"

namespace std {
	class type_index;
}

template <typename TTest, typename TSrc>
bool dynamic_kind_of(const TSrc* obj)
{
	return dynamic_cast<const TTest*>(obj) != nullptr;
}

template <typename TTest, typename TSrc>
bool pointer_kind_of(const std::shared_ptr<TSrc> obj)
{
	return std::dynamic_pointer_cast<TTest>(obj) != nullptr;
}

template <typename TDest, typename TSrc>
TDest safe_cast(TSrc obj)
{
	if (obj == nullptr) return nullptr;
	auto p = dynamic_cast<TDest>(obj);
	if (p == nullptr) throw InvalidCastException("ָ��������ʱָ������ת������Ч�ġ�");
	return p;
}

template <typename TDest, typename TSrc>
std::shared_ptr<TDest> safe_pointer_cast(const std::shared_ptr<TSrc>& obj)
{
	if (obj == nullptr) return std::shared_ptr<TDest>();
	auto p = std::dynamic_pointer_cast<TDest>(obj);
	if (p == nullptr) throw InvalidCastException("ָ��������ʱָ������ת������Ч�ġ�");
	return p;
}

template <typename TStream>
std::string StreamStatusToString(const TStream& stream)
{
	std::string status = stream.good() ? "good " : "";
	if (stream.eof()) status += "eof ";
	if (stream.bad()) status += "bad ";
	if (stream.fail()) status += "fail ";
	return status;
}

template <typename TStream, typename TPath>
TStream OpenAndValidate(const TPath arg1)
{
	auto fs = TStream(arg1);
	if (!fs) {
		std::stringstream ss;
		ss << "���Դ��ļ�" << arg1 << "ʱ��������" << StreamStatusToString(fs);
		throw Exception(ss.str());
	}
	return fs;
}

// �����״̬����ȷ�ԡ��������ȷ����������쳣��
template <typename TStream>
void ValidateStream(const TStream& stream)
{
	if (!stream) {
		std::stringstream ss;
		ss << "��״̬����" << StreamStatusToString(stream);
		throw Exception(ss.str());
	}
}

// ���ڽ����� map::equal_range �Ⱥ����ķ���ֵת��Ϊ�ɱ� foreach �﷨���ܵĽṹ��
template <typename TIterator>
class _RangeToEnumerable
{
	std::pair<TIterator, TIterator> _Range;
public:
	TIterator begin() { return _Range.first; }
	TIterator end() { return _Range.second; }
	bool empty() { return _Range.first == _Range.second; }
	_RangeToEnumerable(const std::pair<TIterator, TIterator> range)
		: _Range(range)
	{

	}
};

template <typename TIterator>
_RangeToEnumerable<TIterator> RangeToEnumerable(const std::pair<TIterator, TIterator> range)
{
	return _RangeToEnumerable<TIterator>(range);
}

inline std::string to_string(const std::pair<std::string, std::string>& value)
{
	return "[" + value.first + ", " + value.second + "]";
}

enum class StringComparison
{
	None = 0,
	IgnoreSurroudingWhiteSpaces,
	IgnoreCase,
};

template<>
struct is_flags<StringComparison> : std::true_type
{
	
};

bool Equal(const std::string& lhs, const std::string& rhs, StringComparison comparision = StringComparison::None);

// �������÷�Χö�ٵİ�λ����
template<typename TEnum, std::enable_if_t<is_flags_v<TEnum>, int> = 0>
TEnum operator & (TEnum lhs, TEnum rhs)
{
	using T = std::underlying_type_t<TEnum>;
	return static_cast<TEnum>(static_cast<T>(lhs) & static_cast<T>(rhs));
}

template<typename TEnum, std::enable_if_t<is_flags_v<TEnum>, int> = 0>
TEnum operator | (TEnum lhs, TEnum rhs)
{
	using T = std::underlying_type_t<TEnum>;
	return static_cast<TEnum>(static_cast<T>(lhs) | static_cast<T>(rhs));
}

#define _RE_TRACE(iosExpr) //std::cout << "Trace:" << iosExpr << std::endl;

bool Confirm(const std::string& prompt);

struct ReliabilityNetworkEntry;
const char* FriendlyNameOf(const std::type_index& type);
const char* FriendlyNameOf(const type_info& type);
const char* FriendlyNameOf(const ReliabilityNetworkEntry& instance);
template <typename T>
const char* FriendlyNameOf()
{
	return FriendlyNameOf(typeid(T));
}

// ��RAII�����ڵ��û������뿪ĳһ�����ʱ���Զ�ִ��ĳЩ�û�����������߼���
// �÷���
//	����Ҫ�����߼��Ĵ������ʹ��
//		BlockExitHandler cleanupHandler(....);
//	���ɡ�
// ע�⣺
//	��Ҫ�������ͷ������������������ֶΡ�
//	��Ҫ�������Ͷ���Ϊ������������Ϊ�ᱻ�������Ż�����
class BlockExitHandler
{
	std::function<void()> handler;
public:
	explicit BlockExitHandler(const std::function<void()>& handler) : handler(handler)
	{

	}
	BlockExitHandler(const BlockExitHandler&) = delete;
	BlockExitHandler& operator=(const BlockExitHandler&) = delete;
	~BlockExitHandler()
	{
		try
		{
			handler();
		} catch (std::exception& e)
		{
			// �����������������쳣��
			std::cout << "BlockExitHandler: " << e.what() << std::endl;
		}
	}
};

void ReportException(const std::exception& ex, int level = 0);
