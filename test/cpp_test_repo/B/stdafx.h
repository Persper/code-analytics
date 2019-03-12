// stdafx.h : 标准系统包含文件的包含文件，
// 或是经常使用但不常更改的
// 特定于项目的包含文件
//

#pragma once

// TODO:  在此处引用程序需要的其他头文件
// 适用于软测使用
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

// 将实验性的 filesystem 命名空间导入 std 中。（2016）
namespace std
{
	namespace filesystem = experimental::filesystem::v1;
}


using complexd = std::complex<double>;