// stdafx.h : ��׼ϵͳ�����ļ��İ����ļ���
// ���Ǿ���ʹ�õ��������ĵ�
// �ض�����Ŀ�İ����ļ�
//

#pragma once

// TODO:  �ڴ˴����ó�����Ҫ������ͷ�ļ�
// ���������ʹ��
//#define _DOWNGRADED_DEMO
#define _SILENCE_STDEXT_ALLOCATORS_DEPRECATION_WARNING

#include <cassert>
#include <crtdbg.h>
#include <xutility>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <memory>
#include <unordered_map>
#include <unordered_set>
#include <complex>
#include <filesystem>
#include <algorithm>
#include <typeindex>
#include <allocators>
#include <list>
#include <array>
#include <vector>

// ��ʵ���Ե� filesystem �����ռ䵼�� std �С���2016��
namespace std
{
	namespace filesystem = experimental::filesystem::v1;
}


using complexd = std::complex<double>;