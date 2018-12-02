#pragma once
#include <type_traits>

template <typename T>
struct is_flags : std::false_type
{
};

template <class T> constexpr bool is_flags_v = is_flags<T>::value;
